"""Real process tests: no model, credentials, network or provider calls."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import Mock, patch

from worker.process_supervisor import JobProcess, WHOLE_JOB_TIMEOUT_SECONDS, atomic_json, read_json


class ProcessSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.jobs = []

    def tearDown(self):
        for job in self.jobs:
            job.close()

    def start(self, code, timeout=3, env=None):
        job = JobProcess({}, command=[sys.executable, '-c', code, '{result}', '{progress}'],
                         timeout_seconds=timeout, env=env)
        self.jobs.append(job)
        return job

    def wait(self, job, timeout=5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = job.poll()
            if result is not None:
                return result
            time.sleep(.01)
        self.fail('Supervisor did not reach a terminal result')

    def assert_stopped(self, pid):
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            # Linux may briefly retain an orphan zombie while init reaps it;
            # our subreaper should normally reap it before this assertion.
            time.sleep(.01)
        self.fail(f'Process {pid} remains after termination')

    def test_import_does_not_import_image_inference_or_firebase_services(self):
        script = ('import sys; from worker import process_supervisor; '
                  'assert not any(x in sys.modules for x in ["PIL", "numpy", "rembg", "firebase_admin"])')
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(WHOLE_JOB_TIMEOUT_SECONDS, 360)

    def test_success_and_atomic_progress(self):
        job = self.start('import json,sys; '
                         'json.dump({"originalStoragePath":"items/id/attempts/a/original.png"},open(sys.argv[2],"w")); '
                         'json.dump({"done":True},open(sys.argv[1],"w"))')
        result = self.wait(job)
        self.assertEqual(result['status'], 'succeeded')
        self.assertTrue(result['result']['done'])
        self.assertIn('originalStoragePath', result['progress'])
        self.assertIs(result, job.poll())

    def test_crash_reports_failure_and_following_job_progresses(self):
        job = self.start('import os; os._exit(19)')
        result = self.wait(job)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['returncode'], 19)
        following = self.start('pass')
        self.assertEqual(self.wait(following)['status'], 'succeeded')

    def test_failed_json_cannot_be_reported_successfully(self):
        job = self.start('import json,sys; json.dump({"status":"failed"},open(sys.argv[1],"w"))')
        self.assertEqual(self.wait(job)['status'], 'failed')

    def test_hang_is_terminated_and_reaped_without_blocking_poll(self):
        job = self.start('import time; time.sleep(30)', timeout=.25)
        before = time.monotonic()
        self.assertIsNone(job.poll())
        self.assertLess(time.monotonic() - before, .1)
        result = self.wait(job)
        self.assertEqual(result['status'], 'timed_out')
        self.assertIsNotNone(job.process.returncode)
        self.assert_stopped(job.pid)
        self.assertEqual(self.wait(self.start('pass'))['status'], 'succeeded')

    def test_deadline_kills_and_reaps_even_when_coordinator_never_polls(self):
        job = self.start('import time; time.sleep(30)', timeout=.15)
        # Simulate a blocked Firestore stream: do not call job/process.poll,
        # wait, terminate, or close until after verifying process disappearance.
        time.sleep(.5)
        with self.assertRaises(ProcessLookupError):
            os.kill(job.pid, 0)
        self.assertIsNotNone(job.process.returncode)
        self.assertEqual(job.poll()['status'], 'timed_out')
        self.assertEqual(self.wait(self.start('pass'))['status'], 'succeeded')

    def test_watchdog_kills_nested_group_while_coordinator_is_blocked(self):
        script = ('import json,sys,time; from worker.process_supervisor import JobProcess; '
                  'child=JobProcess({},command=[sys.executable,"-c","import time; time.sleep(30)"],timeout_seconds=30); '
                  'json.dump({"child":child.pid},open(sys.argv[2],"w")); time.sleep(30)')
        job = self.start(script, timeout=.4)
        time.sleep(.9)
        child = job.read_progress()['child']
        for pid in (job.pid, child):
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)
        self.assertEqual(job.poll()['status'], 'timed_out')

    def test_watchdog_observes_completed_unpolled_job_as_success(self):
        job = self.start('pass', timeout=.2)
        time.sleep(.5)
        self.assertEqual(job.poll()['status'], 'succeeded')

    def test_concurrent_poll_cancel_and_watchdog_settle_only_once(self):
        job = self.start('import time; time.sleep(30)', timeout=.1)
        results = []
        barrier = threading.Barrier(3)
        def terminate():
            barrier.wait()
            results.append(job.terminate())
        def poll():
            barrier.wait()
            time.sleep(.12)
            results.append(job.poll())
        callers = [threading.Thread(target=terminate), threading.Thread(target=poll)]
        for caller in callers:
            caller.start()
        barrier.wait()
        for caller in callers:
            caller.join(timeout=3)
            self.assertFalse(caller.is_alive())
        self.assertEqual(len(results), 2)
        self.assertIs(results[0], results[1])
        self.assertIs(results[0], job.poll())
        self.assert_stopped(job.pid)
        self.assertTrue(job._watchdog.finished.is_set())

    def test_term_ignoring_parent_and_grandchild_are_killed(self):
        script = ('import json,os,signal,subprocess,sys,time; '
                  'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
                  'child=subprocess.Popen([sys.executable,"-c",'
                  '"import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)"]); '
                  'json.dump({"child":child.pid},open(sys.argv[2],"w")); time.sleep(30)')
        job = self.start(script, timeout=.6)
        result = self.wait(job)
        self.assertEqual(result['status'], 'timed_out')
        self.assert_stopped(job.pid)
        self.assert_stopped(result['progress']['child'])

    def test_nested_process_group_is_reaped_after_intermediate_parent_crash(self):
        script = ('import json,os,sys,time; from worker.process_supervisor import JobProcess; '
                  'child=JobProcess({},command=[sys.executable,"-c","import time; time.sleep(30)"],timeout_seconds=30); '
                  'json.dump({"child":child.pid},open(sys.argv[2],"w")); time.sleep(.1); os._exit(23)')
        job = self.start(script)
        result = self.wait(job)
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['returncode'], 23)
        self.assert_stopped(result['progress']['child'])

    def test_explicit_cancel_preserves_progress_then_close_cleans_private_files(self):
        job = self.start('import time; time.sleep(30)')
        atomic_json(job.progress_path, {'originalUrl': 'https://assets.invalid/original.png'})
        self.assertEqual(job.read_progress()['originalUrl'], 'https://assets.invalid/original.png')
        self.assertEqual(job.terminate()['status'], 'cancelled')
        self.assert_stopped(job.pid)
        job.close()
        self.assertFalse(job.workdir.exists())

    def test_custom_flatlay_command_keeps_provider_key(self):
        env = dict(os.environ, OPENAI_API_KEY='non-secret-test-marker')
        job = self.start('import os; assert os.environ.get("OPENAI_API_KEY")=="non-secret-test-marker"', env=env)
        self.assertEqual(self.wait(job)['status'], 'succeeded')

    def test_default_garment_command_strips_provider_key(self):
        process = Mock(pid=999999, returncode=0)
        process.poll.return_value = 0
        with patch('worker.process_supervisor.subprocess.Popen', return_value=process) as popen, \
             patch.object(JobProcess, '_kill_groups'), patch.object(JobProcess, '_reap'):
            job = JobProcess({}, env=dict(os.environ, OPENAI_API_KEY='test-marker'))
            self.assertNotIn('OPENAI_API_KEY', popen.call_args.kwargs['env'])
            job.poll()
            job.close()

    def test_reap_retries_children_still_exiting_after_kill(self):
        job = object.__new__(JobProcess)
        job._groups = lambda: {999999}
        with patch('worker.process_supervisor.os.waitpid', side_effect=[(0, 0), (999999, 0), ChildProcessError]) as wait, \
             patch('worker.process_supervisor.time.sleep'):
            job._reap()
        self.assertEqual(wait.call_count, 3)

    @unittest.skipUnless(sys.platform.startswith('linux'), 'Linux subreaper behavior requires Linux runtime')
    def test_linux_adopted_grandchild_is_reaped_not_only_signalled(self):
        script = ('import json,os,subprocess,sys,time; '
                  'child=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); '
                  'json.dump({"child":child.pid},open(sys.argv[2],"w")); time.sleep(.1); os._exit(17)')
        job = self.start(script)
        result = self.wait(job)
        child = result['progress']['child']
        self.assert_stopped(child)
        with self.assertRaises(ChildProcessError):
            os.waitpid(child, os.WNOHANG)

    def test_invalid_or_partial_progress_is_not_exposed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'partial'
            for text in ('{', '[]', 'null', '"wrong"'):
                path.write_text(text)
                self.assertEqual(read_json(path), {})


if __name__ == '__main__':
    unittest.main()
