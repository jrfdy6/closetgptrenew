"""Coordinator regressions without image models, credentials or cloud writes."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock

from worker.coordinator import WorkerCoordinator


class Process:
    def __init__(self):
        self.progress = {}
        self.outcome = None
        self.closed = False
        self.terminated = None

    def read_progress(self):
        return self.progress

    def poll(self):
        return self.outcome

    def terminate(self, reason):
        self.terminated = reason
        self.outcome = {"status": reason, "result": {}, "progress": self.progress}

    def close(self):
        self.closed = True


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.pending = ["white-tee", "next-garment"]
        self.eligible = set(self.pending)
        self.flat_pending = ["first-look", "next-look"]
        self.garments = []
        self.flatlays = []
        self.expiry = Mock()
        self.recover = Mock()
        self.publish = Mock(return_value=True)
        self.finish = Mock(return_value=True)

        def claim(identifier):
            if identifier not in self.eligible:
                return None
            self.eligible.remove(identifier)
            return {"garment_id": identifier, "attempt_id": "attempt-1", "attempt_count": 1}

        def start_garment(claim):
            process = Process()
            self.garments.append((claim["garment_id"], process))
            return process

        def start_flatlay(identifier):
            self.flat_pending.remove(identifier)
            process = Process()
            self.flatlays.append((identifier, process))
            return process

        self.coordinator = WorkerCoordinator(
            expire_flatlays=self.expiry, recover_garments=self.recover,
            garment_candidates=lambda: self.pending, claim_garment=claim,
            start_garment=start_garment, publish_original=self.publish,
            finish_garment=self.finish, flatlay_candidates=lambda: list(self.flat_pending),
            start_flatlay=start_flatlay,
        )

    def test_hung_garment_never_starves_flatlay_start_or_expiry(self):
        for _ in range(6):
            self.coordinator.tick()
        self.assertEqual(self.expiry.call_count, 6)
        self.assertEqual(self.recover.call_count, 6)
        self.assertEqual([item for item, _ in self.garments], ["white-tee"])
        self.assertEqual([item for item, _ in self.flatlays], ["first-look"])
        self.finish.assert_not_called()

    def test_expired_child_is_settled_then_next_garment_and_flatlay_progress(self):
        self.coordinator.tick()
        self.garments[0][1].outcome = {"status": "timed_out", "progress": {}, "result": {}}
        self.flatlays[0][1].outcome = {"status": "succeeded"}
        self.coordinator.tick()
        self.finish.assert_called_once_with("white-tee", "attempt-1", result=None,
                                            error_code="worker_timeout")
        self.assertTrue(self.garments[0][1].closed)
        self.assertEqual(self.garments[1][0], "next-garment")
        self.assertEqual(self.flatlays[1][0], "next-look")
        self.assertEqual(self.expiry.call_count, 2)

    def test_original_is_published_before_cutout_and_retained_after_failure(self):
        self.coordinator.tick()
        job = self.garments[0][1]
        original = {"originalStoragePath": "items/white-tee/attempts/attempt-1/original.png",
                    "originalUrl": "https://assets.invalid/original"}
        job.progress = original
        self.coordinator.tick()
        self.publish.assert_called_once_with("white-tee", "attempt-1", original)
        self.finish.assert_not_called()
        job.outcome = {"status": "failed", "result": {}, "progress": original}
        self.coordinator.tick()
        self.assertEqual(self.publish.call_count, 1)
        self.finish.assert_called_once()

    def test_stale_original_stops_child_without_publishing_result(self):
        self.coordinator.tick()
        job = self.garments[0][1]
        job.progress = {"originalStoragePath": "path", "originalUrl": "url"}
        self.publish.return_value = False
        self.coordinator.tick()
        self.assertEqual(job.terminated, "superseded")
        self.finish.assert_called_once_with("white-tee", "attempt-1", result=None,
                                            error_code="item_changed")

    def test_storage_failure_retains_terminal_result_for_safe_commit_retry(self):
        self.coordinator.tick()
        job = self.garments[0][1]
        job.outcome = {"status": "failed", "result": {}, "progress": {}}
        self.finish.side_effect = [RuntimeError("db unavailable"), True]
        self.coordinator.tick()
        self.assertFalse(job.closed)
        self.assertEqual(len(self.garments), 1)
        self.coordinator.tick()
        self.assertTrue(job.closed)
        self.assertEqual(len(self.garments), 2)
        self.assertEqual(self.expiry.call_count, 3)

    def test_original_publication_failure_cannot_prevent_process_polling(self):
        self.coordinator.tick()
        job = self.garments[0][1]
        job.progress = {"originalStoragePath": "path", "originalUrl": "url"}
        job.poll = Mock(wraps=job.poll)
        self.publish.side_effect = RuntimeError("db unavailable")
        for _ in range(3):
            self.coordinator.tick()
        self.assertEqual(job.poll.call_count, 3)
        self.assertEqual(self.expiry.call_count, 4)
        self.assertFalse(job.closed)

    def test_storage_failure_in_one_sweep_does_not_block_other_lanes(self):
        self.recover.side_effect = RuntimeError("db unavailable")
        self.coordinator.tick()
        self.assertEqual(len(self.garments), 1)
        self.assertEqual(len(self.flatlays), 1)
        self.expiry.assert_called_once()

    def test_shutdown_terminates_both_lanes_without_guessing_paid_settlement(self):
        self.coordinator.tick()
        self.coordinator.close()
        self.assertEqual(self.garments[0][1].terminated, "shutdown")
        self.assertEqual(self.flatlays[0][1].terminated, "shutdown")
        self.finish.assert_not_called()

    def test_coordinator_entry_has_no_inference_or_numerical_import(self):
        root = Path(__file__).resolve().parents[1] / "worker"
        for name in ("main.py", "coordinator.py", "process_supervisor.py"):
            tree = ast.parse((root / name).read_text())
            for node in ast.walk(tree):
                modules = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                           else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                self.assertFalse(any(module.split(".")[0] in {"rembg", "numpy", "onnxruntime"}
                                     for module in modules), (name, modules))

    def test_worker_and_api_lifecycle_mirrors_are_identical(self):
        root = Path(__file__).resolve().parents[1]
        for filename in ("garment_lifecycle.py", "flatlay_lifecycle.py", "original_source.py"):
            self.assertEqual((root / "worker" / filename).read_bytes(),
                             (root / "src" / "services" / filename).read_bytes())


if __name__ == "__main__":
    unittest.main()
