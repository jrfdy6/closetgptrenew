"""Coordinator regressions without image models, credentials or cloud writes."""
import ast
import copy
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from worker.coordinator import WorkerCoordinator


def flatlay_candidates_under_test(db):
    """Load the production selector closure without worker credentials/models."""
    path = Path(__file__).resolve().parents[1] / "worker" / "main.py"
    tree = ast.parse(path.read_text())
    worker = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == "run_worker")
    selector = next(node for node in worker.body
                    if isinstance(node, ast.FunctionDef) and node.name == "flatlay_candidates")
    cursor = next(node for node in worker.body if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "flatlay_cursor"
                          for target in node.targets))
    factory = ast.parse("def factory():\n    return flatlay_candidates\n")
    factory.body[0].body[:0] = [cursor, selector]
    environment = {"db": db, "REQUESTS_COLLECTION": "flat_lay_requests",
                   "FieldFilter": lambda *args: args}
    exec(compile(ast.fix_missing_locations(factory), str(path), "exec"), environment)
    return environment["factory"]()


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


class QueueDatabase:
    """Small query fake; this suite must run with the standard library only."""
    def __init__(self, rows):
        self.rows = rows
        self.queries = []

    def collection(self, name):
        if name != "flat_lay_requests":
            raise AssertionError("Unexpected queue collection")
        return QueueQuery(self)


class QueueQuery:
    def __init__(self, db):
        self.db = db
        self.cursor = None

    def where(self, *, filter):
        self.filter = filter
        return self

    def order_by(self, field):
        self.order = field
        return self

    def limit(self, maximum):
        self.maximum = maximum
        return self

    def start_after(self, snapshot):
        self.cursor = snapshot
        return self

    def stream(self, **options):
        field, operator, minimum = self.filter
        if operator != ">=":
            raise AssertionError("Unexpected queue filter")
        rows = [(key, row) for key, row in self.db.rows.items()
                if isinstance(row.get(field), (int, float)) and row[field] >= minimum]
        rows.sort(key=lambda entry: (entry[1][self.order], entry[0]))
        if self.cursor is not None:
            position = (self.cursor.to_dict()[self.order], self.cursor.id)
            rows = [(key, row) for key, row in rows if (row[self.order], key) > position]
        rows = rows[:self.maximum]
        self.db.queries.append((self.maximum, options, len(rows)))
        for key, row in rows:
            yield SimpleNamespace(id=key, to_dict=lambda row=copy.deepcopy(row): copy.deepcopy(row))


class FlatlayQueueProgressTests(unittest.TestCase):

    def test_many_held_rows_advance_with_bounded_reads_then_wrap(self):
        identifiers = [f"held-{index:02d}" for index in range(30)] + ["valid-last"]
        db = QueueDatabase({
            identifier: {"queued_at": 1100, "status": "pending"} for identifier in identifiers
        })
        candidates = flatlay_candidates_under_test(db)
        seen = [candidates() for _ in identifiers]
        self.assertEqual(seen, [[identifier] for identifier in identifiers])
        self.assertEqual(candidates(), [])
        self.assertEqual(candidates(), [identifiers[0]])
        self.assertEqual(len(db.queries), len(identifiers) + 2)
        self.assertTrue(all(limit == 1 and count <= 1 for limit, _, count in db.queries))
        self.assertTrue(all(options == {"timeout": 10, "retry": None} for _, options, _ in db.queries))

    def test_cursor_survives_deleted_or_dequeued_row_and_revisits_earlier_arrival(self):
        ledger = {identifier: {"queued_at": 1100} for identifier in ("a", "b", "c")}
        candidates = flatlay_candidates_under_test(QueueDatabase(ledger))
        self.assertEqual(candidates(), ["a"])
        del ledger["a"]
        self.assertEqual(candidates(), ["b"])
        ledger["b"]["queued_at"] = None
        ledger["earlier-arrival"] = {"queued_at": 1099}
        self.assertEqual(candidates(), ["c"])
        self.assertEqual(candidates(), [])
        self.assertEqual(candidates(), ["earlier-arrival"])


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

    def test_failure_diagnostics_are_reprojected_before_operational_reporting(self):
        report = Mock()
        self.coordinator.report = report
        self.coordinator.tick()
        job = self.garments[0][1]
        job.outcome = {'status': 'failed', 'progress': {}, 'result': {
            'error_code': 'processing_failed', 'diagnostics': [
                {'stage': 'alpha_model_download', 'category': 'http_error', 'http_status': 503,
                 'message': 'private-token', 'url': 'https://private.invalid', 'item_id': 'private-id'},
                {'stage': 'fallback_removal', 'category': 'runtime_error', 'http_status': True},
                {'stage': 'job', 'category': 'unknown'},
            ]}}
        self.coordinator.tick()
        fields = [call.args[1] for call in report.call_args_list if call.args[0] == 'garment_finished'][0]
        self.assertEqual(fields['diagnostics'], [
            {'stage': 'alpha_model_download', 'category': 'http_error', 'http_status': 503},
            {'stage': 'fallback_removal', 'category': 'runtime_error'},
        ])
        self.assertNotIn('private', str(fields))
        self.finish.assert_called_once_with('white-tee', 'attempt-1', result=None,
                                            error_code='processing_failed')
        self.assertTrue(job.closed)

    def test_malformed_diagnostic_fields_never_escape_receiving_boundary(self):
        from worker.garment_errors import safe_diagnostics
        for value in (None, 'https://private.invalid', {'stage': 'job'},
                      [{'stage': ['private'], 'category': 'unknown'}],
                      [{'stage': 'job', 'category': 'private-token'}],
                      [{'stage': 'private-id', 'category': 'unknown'}]):
            with self.subTest(value=value):
                self.assertEqual(safe_diagnostics(value), [])
        for value in (True, '503', 399, 600, ['private-token']):
            self.assertEqual(safe_diagnostics([{'stage': 'job', 'category': 'unknown', 'http_status': value}]),
                             [{'stage': 'job', 'category': 'unknown'}])

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
