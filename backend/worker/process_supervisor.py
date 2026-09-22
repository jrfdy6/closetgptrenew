"""Small process supervisor; importing it does not initialize image/AI services.

JobProcess(payload, command=None, timeout_seconds=360) starts immediately.
Custom command arguments can contain {manifest}, {result}, and {progress}.
poll() is nonblocking while work is active; termination uses bounded signal
and reap waits. It returns None while running, otherwise a cached terminal summary. read_progress()
returns the last atomic JSON manifest. terminate() kills and reaps owned work;
close() additionally removes the private temporary directory. An independent
daemon watchdog enforces the deadline even if the coordinator stops polling.

Nested supervisors register their process groups before their launch barrier
opens. The outer job consequently kills inference groups and their descendants,
even if its direct child crashes instead of running a cleanup handler.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from typing import Callable, Sequence

WHOLE_JOB_TIMEOUT_SECONDS = 360
MAX_MANIFEST_BYTES = 2_000_000
_REGISTRY_ENV = 'EASYOUTFIT_JOB_GROUP_REGISTRY'


def atomic_json(path: Path | str, value: dict) -> None:
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def read_json(path: Path | str) -> dict:
    try:
        path = Path(path)
        if path.stat().st_size > MAX_MANIFEST_BYTES:
            return {}
        value = json.loads(path.read_text())
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError, UnicodeError):
        return {}


def _enable_subreaper() -> None:
    # Reap grandchildren after their parent crashes on Linux containers. Other
    # platforms delegate orphan reaping to init; process groups still kill them.
    if sys.platform.startswith('linux'):
        try:
            import ctypes
            ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0)
        except (AttributeError, OSError):
            pass


class JobProcess:
    def __init__(self, payload: dict, *, command: Sequence[str] | None = None,
                 timeout_seconds: float = WHOLE_JOB_TIMEOUT_SECONDS,
                 env: dict | None = None, work_root: str | Path | None = None,
                 clock: Callable[[], float] = time.monotonic):
        if timeout_seconds <= 0:
            raise ValueError('A finite positive process deadline is required')
        import math
        if not math.isfinite(timeout_seconds):
            raise ValueError('A finite positive process deadline is required')
        self.clock = clock
        self._lock = threading.RLock()
        self._watchdog = None
        self.workdir = Path(tempfile.mkdtemp(prefix='easyoutfit-job-', dir=work_root))
        self.manifest_path = self.workdir / 'manifest.json'
        self.result_path = self.workdir / 'result.json'
        self.progress_path = self.workdir / 'progress.json'
        self.log_path = self.workdir / 'job.log'
        self._terminal = None
        self._closed = False
        child_env = dict(os.environ if env is None else env)
        inherited_registry = child_env.get(_REGISTRY_ENV)
        self._owns_registry = not inherited_registry
        self.registry_path = Path(inherited_registry) if inherited_registry else self.workdir / 'groups'
        self.registry_path.mkdir(mode=0o700, exist_ok=True)
        child_env[_REGISTRY_ENV] = str(self.registry_path)
        if command is None:
            command = [sys.executable, str(Path(__file__).with_name('garment_job.py')),
                       '--manifest', '{manifest}', '--result', '{result}', '--progress', '{progress}']
            child_env.pop('OPENAI_API_KEY', None)
        paths = {'{manifest}': str(self.manifest_path), '{result}': str(self.result_path),
                 '{progress}': str(self.progress_path)}
        argv = [paths.get(str(argument), str(argument)) for argument in command]
        if not argv:
            raise ValueError('A process command is required')
        atomic_json(self.manifest_path, payload)
        barrier = self.workdir / 'registered'
        wrapper = [sys.executable, str(Path(__file__).resolve()), '--launch', str(barrier), *argv]
        _enable_subreaper()
        self.started_at = clock()
        self.deadline = self.started_at + timeout_seconds
        self._log = self.log_path.open('wb')
        try:
            self.process = subprocess.Popen(wrapper, stdin=subprocess.DEVNULL, stdout=self._log,
                                            stderr=subprocess.STDOUT, env=child_env, start_new_session=True)
            self.pid = self.process.pid
            # Each live group owns a separate entry; cleanup cannot race another launch.
            (self.registry_path / str(self.pid)).touch(mode=0o600)
            barrier.touch()
            self._arm_watchdog()
        except BaseException:
            with self._lock:
                if self._watchdog is not None:
                    self._watchdog.cancel()
                if hasattr(self, 'process'):
                    self._kill_groups(signal.SIGKILL)
                    self.process.wait(timeout=2)
                self._terminal = {'status': 'failed', 'error': 'launch_failed'}
                self._log.close()
                shutil.rmtree(self.workdir, ignore_errors=True)
            raise

    def read_progress(self) -> dict:
        return read_json(self.progress_path)

    def _groups(self) -> set[int]:
        groups = {self.pid}
        if self._owns_registry:
            try:
                groups.update(int(entry.name) for entry in self.registry_path.iterdir()
                              if entry.name.isdigit() and int(entry.name) > 1)
            except OSError:
                pass
        return groups

    def _kill_groups(self, sig: int) -> None:
        for group in self._groups():
            if group == os.getpgrp():
                continue
            try:
                os.killpg(group, sig)
            except ProcessLookupError:
                pass

    def _reap(self) -> None:
        deadline = time.monotonic() + .2
        pending = self._groups()
        while pending:
            for group in tuple(pending):
                try:
                    child, _ = os.waitpid(-group, os.WNOHANG)
                    if child:
                        continue
                except ChildProcessError:
                    pending.remove(group)
            if not pending or time.monotonic() >= deadline:
                break
            time.sleep(.005)

    def _arm_watchdog(self) -> None:
        # Called while constructing the job or while holding its reentrant lock.
        # Timer waits use monotonic time and do not depend on coordinator I/O.
        self._watchdog = threading.Timer(max(0, self.deadline - self.clock()), self._watchdog_expired)
        self._watchdog.daemon = True
        self._watchdog.start()

    def _watchdog_expired(self) -> None:
        with self._lock:
            if self._terminal is not None:
                return
            # A timer may wake slightly early. Re-arm against the same deadline,
            # never extend the budget and never depend on a later external poll.
            if self.clock() < self.deadline:
                self._arm_watchdog()
                return
            self.poll()

    def _summary(self, status: str, error: str | None = None) -> dict:
        with self._lock:
            if self._terminal is not None:
                return self._terminal
            if self._watchdog is not None:
                self._watchdog.cancel()
            self._log.close()
            try:
                (self.registry_path / str(self.pid)).unlink(missing_ok=True)
            except OSError:
                pass
            self._terminal = {'status': status, 'returncode': self.process.returncode,
                              'result': read_json(self.result_path), 'progress': self.read_progress(),
                              'error': error}
            return self._terminal

    def poll(self) -> dict | None:
        with self._lock:
            if self._terminal is not None:
                return self._terminal
            code = self.process.poll()
            if code is not None:
                # Even a successful leader may leave child processes behind.
                self._kill_groups(signal.SIGKILL)
                self._reap()
                result = read_json(self.result_path)
                failed = code != 0 or result.get('status') == 'failed'
                return self._summary('failed' if failed else 'succeeded', 'child_failed' if failed else None)
            if self.clock() >= self.deadline:
                return self.terminate('timed_out')
            return None

    def terminate(self, reason: str = 'cancelled') -> dict:
        with self._lock:
            if self._terminal is not None:
                return self._terminal
            self._kill_groups(signal.SIGTERM)
            try:
                self.process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                pass
            # Reread the registry in case a child was being registered at TERM.
            self._kill_groups(signal.SIGKILL)
            self.process.wait(timeout=2)
            self._reap()
            return self._summary(reason, reason)

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            if self._terminal is None:
                self.terminate()
            if self._watchdog is not None:
                self._watchdog.cancel()
            shutil.rmtree(self.workdir, ignore_errors=True)
            self._closed = True


def _launch() -> None:
    # No command runs until its group is known to the outer supervisor. If the
    # launching parent dies in this tiny window, the barrier expires harmlessly.
    barrier = Path(sys.argv[2])
    deadline = time.monotonic() + 2
    while not barrier.exists():
        if time.monotonic() >= deadline:
            raise SystemExit(74)
        time.sleep(0.01)
    argv = sys.argv[3:]
    os.execvpe(argv[0], argv, os.environ)


if __name__ == '__main__':
    if len(sys.argv) >= 4 and sys.argv[1] == '--launch':
        _launch()
    else:
        raise SystemExit('Only --launch is supported')
