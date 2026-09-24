"""Original-reference preparation checks without credentials, HTTP or Firebase."""
from io import BytesIO
import struct
import unittest
from unittest.mock import patch
import zlib

from PIL import Image
from worker import flatlay_reference_images as references


def png(mode="RGB", size=(20, 30), color=None):
    image = Image.new(mode, size, color if color is not None else ((15, 60, 120, 128) if mode == "RGBA" else "navy"))
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


class NotFound(Exception):
    pass


class FakeBlob:
    def __init__(self, data, *, size=None, generation=123, error=None):
        self.data = data
        self.size = len(data) if size is None and data is not None else size
        self.generation = generation
        self.error = error
        self.metadata_reads = []
        self.downloads = []

    def reload(self, **kwargs):
        self.metadata_reads.append(kwargs)
        if self.error:
            raise self.error
        if self.data is None:
            raise NotFound("secret storage URL and details")

    def download_as_bytes(self, **kwargs):
        self.downloads.append(kwargs)
        return self.data


class FakeBucket:
    def __init__(self, blobs):
        self.blobs = blobs
        self.requested_paths = []

    def blob(self, path):
        self.requested_paths.append(path)
        return self.blobs.get(path, FakeBlob(None))


class ReferencePreparationTests(unittest.TestCase):
    def setUp(self):
        self.first = png()
        self.second = png("RGBA")
        self.items = [
            {"id": "shirt_1", "name": "Wide stripe shirt", "type": "shirt", "color": "light blue",
             "backgroundRemovedUrl": "https://never-follow.invalid/processed", "imageUrl": "https://never-follow.invalid/original"},
            {"id": "shoes-2", "name": "Derby shoes", "type": "shoes", "color": "brown"},
        ]
        self.blobs = {"items/shirt_1/original.png": FakeBlob(self.first),
                      "items/shoes-2/original.png": FakeBlob(self.second)}
        self.bucket = FakeBucket(self.blobs)

    def assert_code(self, code, function, *args):
        with self.assertRaises(references.ReferenceImageError) as caught:
            function(*args)
        self.assertEqual(caught.exception.code, code)
        self.assertNotIn("secret", str(caught.exception))
        self.assertNotIn("http", str(caught.exception))

    def test_exact_original_paths_rgb_and_rgba_bytes_are_unchanged(self):
        result = references.prepare_original_references(self.items, self.bucket)
        self.assertEqual(self.bucket.requested_paths, list(self.blobs))
        self.assertEqual([entry["image_bytes"] for entry in result], [self.first, self.second])
        self.assertIs(result[0]["image_bytes"], self.first)
        self.assertEqual([entry["id"] for entry in result], ["shirt_1", "shoes-2"])
        self.assertEqual(result[0]["source"], self.items[0])
        self.assertIsNot(result[0]["source"], self.items[0])
        for blob in self.blobs.values():
            self.assertEqual(blob.metadata_reads, [{"timeout": 30, "retry": None}])
            self.assertEqual(blob.downloads, [{"timeout": 30, "retry": None, "if_generation_match": 123}])

    def test_missing_one_original_fails_whole_request_without_processed_fallback(self):
        self.blobs.pop("items/shoes-2/original.png")
        self.blobs["items/shoes-2/processed.png"] = FakeBlob(self.second)
        self.assert_code("original_image_missing", references.prepare_original_references, self.items, self.bucket)
        self.assertEqual(self.bucket.requested_paths, ["items/shirt_1/original.png", "items/shoes-2/original.png"])

    def test_reserved_attempt_original_is_read_even_when_legacy_pixels_differ(self):
        path = "items/shirt_1/attempts/attempt-one/original.png"
        self.items[0]["originalStoragePath"] = path
        self.blobs[path] = FakeBlob(self.second)
        result = references.prepare_original_references(self.items, self.bucket)
        self.assertEqual(self.bucket.requested_paths, [path, "items/shoes-2/original.png"])
        self.assertEqual(result[0]["image_bytes"], self.second)

    def test_untrusted_original_paths_cannot_escape_item_or_use_processed_pixels(self):
        for path in ("items/shoes-2/attempts/a/original.png", "items/shirt_1/attempts/a/nobg.png",
                     "items/shirt_1/attempts/../original.png", "https://attacker.invalid/photo",
                     "items/shirt_1/attempts/a/original.png?key=value", 12, ""):
            with self.subTest(path=path):
                self.assert_code("invalid_original_path", references.prepare_original_references,
                                 [{"id": "shirt_1", "originalStoragePath": path}], self.bucket)
        self.assertEqual(self.bucket.requested_paths, [])

    def test_missing_reserved_original_never_falls_back_to_legacy_object(self):
        self.assert_code("original_image_missing", references.prepare_original_references,
                         [{"id": "shirt_1", "originalStoragePath": "items/shirt_1/attempts/missing/original.png"}],
                         self.bucket)
        self.assertEqual(self.bucket.requested_paths, ["items/shirt_1/attempts/missing/original.png"])

    def test_prepared_original_is_bound_to_item_and_current_flatlay_request(self):
        path = "items/shirt_1/flatlay-requests/request-one/original.png"
        item = {"id": "shirt_1", "originalStoragePath": path}
        self.blobs[path] = FakeBlob(self.second)
        result = references.prepare_original_references([item], self.bucket, request_id="request-one")
        self.assertEqual(result[0]["image_bytes"], self.second)
        for request_id in (None, "request-two", "../request-one"):
            with self.subTest(request_id=request_id):
                with self.assertRaises(references.ReferenceImageError) as caught:
                    references.prepare_original_references([item], self.bucket, request_id=request_id)
                self.assertEqual(caught.exception.code, "invalid_original_path")

    def test_invalid_ids_duplicates_and_scalar_items_fail_before_storage_access(self):
        cases = [
            ([{"id": "../outside"}], "invalid_reference_id"),
            ([{"id": "bad/path"}], "invalid_reference_id"),
            ([{"id": "bad\\path"}], "invalid_reference_id"),
            ([{"id": "bad%2fpath"}], "invalid_reference_id"),
            ([{"id": "bad\npath"}], "invalid_reference_id"),
            ([{"id": "shirt_1", "itemId": "shoes-2"}], "conflicting_reference_id"),
            ([{"id": "shirt_1"}, {"item_id": "shirt_1"}], "duplicate_reference_id"),
            (["shirt_1"], "invalid_reference_item"),
            ("shirt_1", "invalid_reference_count"),
            ([], "invalid_reference_count"),
            ([{"id": f"item-{index}"} for index in range(17)], "invalid_reference_count"),
        ]
        for items, code in cases:
            with self.subTest(items=items):
                self.assert_code(code, references.prepare_original_references, items, self.bucket)
        self.assertEqual(self.bucket.requested_paths, [])

    def test_supported_identifier_alias_and_sixteen_item_cap(self):
        items = [{"itemId": f"item-{index}"} for index in range(16)]
        bucket = FakeBucket({f"items/item-{index}/original.png": FakeBlob(self.first) for index in range(16)})
        self.assertEqual(len(references.prepare_original_references(items, bucket)), 16)

    def test_declared_oversize_stops_before_download(self):
        self.blobs["items/shirt_1/original.png"].size = references.MAX_IMAGE_BYTES
        self.assert_code("original_image_too_large", references.prepare_original_references, self.items, self.bucket)
        self.assertEqual(self.blobs["items/shirt_1/original.png"].downloads, [])

    def test_aggregate_file_limit_stops_before_next_download(self):
        with patch.object(references, "MAX_TOTAL_REFERENCE_BYTES", len(self.first) + len(self.second) - 1):
            self.assert_code("reference_images_too_large", references.prepare_original_references, self.items, self.bucket)
        self.assertEqual(self.blobs["items/shoes-2/original.png"].downloads, [])

    def test_changed_size_and_missing_generation_are_rejected(self):
        self.blobs["items/shirt_1/original.png"].size += 1
        self.assert_code("original_image_changed", references.prepare_original_references, self.items, self.bucket)
        self.blobs["items/shirt_1/original.png"].size -= 1
        self.blobs["items/shirt_1/original.png"].generation = None
        self.assert_code("original_image_unavailable", references.prepare_original_references, self.items, self.bucket)

    def test_invalid_truncated_non_png_and_grayscale_inputs_have_no_fallback(self):
        jpeg = BytesIO()
        Image.new("RGB", (20, 20), "red").save(jpeg, format="JPEG")
        cases = [(b"not-an-image", "invalid_original_image"),
                 (self.first[:-12], "invalid_original_image"),
                 (jpeg.getvalue(), "unsupported_original_image"),
                 (png("L", color=120), "unsupported_original_image")]
        for data, code in cases:
            with self.subTest(code=code):
                self.bucket.blobs["items/shirt_1/original.png"] = FakeBlob(data)
                self.assert_code(code, references.prepare_original_references, self.items, self.bucket)

    def test_pixel_and_total_pixel_limits_prevent_unsafe_decode(self):
        with patch.object(references, "MAX_IMAGE_PIXELS", 500):
            self.assert_code("original_image_dimensions_too_large", references.prepare_original_references, self.items, self.bucket)
        with patch.object(references, "MAX_TOTAL_REFERENCE_PIXELS", 1199):
            self.assert_code("reference_images_dimensions_too_large", references.prepare_original_references, self.items, self.bucket)

    def test_png_decompression_bomb_header_is_rejected_safely(self):
        header = struct.pack(">IIBBBBB", 100000, 100000, 8, 2, 0, 0, 0)
        def chunk(kind, content):
            return struct.pack(">I", len(content)) + kind + content + struct.pack(">I", zlib.crc32(kind + content) & 0xffffffff)
        bomb = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"")) + chunk(b"IEND", b"")
        self.bucket.blobs["items/shirt_1/original.png"] = FakeBlob(bomb)
        self.assert_code("original_image_dimensions_too_large", references.prepare_original_references, self.items, self.bucket)

    def test_animated_png_is_rejected_instead_of_taking_first_frame(self):
        output = BytesIO()
        Image.new("RGB", (20, 30), "red").save(output, format="PNG", save_all=True,
                                               append_images=[Image.new("RGB", (20, 30), "blue")], duration=100)
        self.bucket.blobs["items/shirt_1/original.png"] = FakeBlob(output.getvalue())
        self.assert_code("animated_original_image", references.prepare_original_references, self.items, self.bucket)

    def test_storage_failure_never_exposes_exception_details(self):
        self.bucket.blobs["items/shirt_1/original.png"].error = RuntimeError("secret https://storage.invalid/token")
        self.assert_code("original_image_unavailable", references.prepare_original_references, self.items, self.bucket)

    def test_fully_transparent_original_is_rejected_by_loader_and_payload_builder(self):
        invisible = png("RGBA", color=(30, 60, 90, 0))
        self.bucket.blobs["items/shirt_1/original.png"] = FakeBlob(invisible)
        self.assert_code("empty_original_image", references.prepare_original_references, self.items, self.bucket)
        self.assert_code("empty_original_image", references.build_reference_edit_payload,
                         [{"id": "shirt_1", "source": self.items[0], "image_bytes": invisible,
                           "mime_type": "image/png"}], "test-model")

    def test_repeated_multipart_fields_preserve_every_original_byte_and_omit_quality(self):
        prepared = references.prepare_original_references(self.items, self.bucket)
        payload = references.build_reference_edit_payload(prepared, "gpt-image-2.5-flare")
        images = [value for key, value in payload if key == "image[]"]
        fields = dict((key, value) for key, value in payload if key != "image[]")
        self.assertEqual(len(images), 2)
        self.assertEqual([entry[1] for entry in images], [self.first, self.second])
        self.assertIs(images[0][1], self.first)
        self.assertTrue(all(entry[2] == "image/png" for entry in images))
        self.assertNotIn("image", fields)
        self.assertNotIn("quality", fields)
        self.assertEqual(fields["model"], (None, "gpt-image-2.5-flare"))
        self.assertEqual(fields["size"], (None, "1024x1024"))
        self.assertEqual(fields["n"], (None, "1"))
        prompt = fields["prompt"][1]
        for wording in ("every wardrobe item exactly once", "photos are the source of truth",
                        "stripe width and spacing", "buttons, buttonholes, eyelets", "never invent",
                        "do not force folds", "choose one view", "never turn the alternate view into a second garment",
                        "single-shoe or pair presentation", "do not invent another shoe"):
            self.assertIn(wording, prompt)
        self.assertIn("Wide stripe shirt", prompt)

    def test_quality_is_explicit_and_invalid_models_or_quality_are_rejected(self):
        prepared = references.prepare_original_references(self.items, self.bucket)
        for quality in ("low", "medium", "high", "auto"):
            with self.subTest(quality=quality):
                self.assertEqual(dict(references.build_reference_edit_payload(prepared, "test-model", quality))["quality"], (None, quality))
        self.assert_code("invalid_reference_quality", references.build_reference_edit_payload, prepared, "test-model", "cheapest")
        self.assert_code("invalid_reference_model", references.build_reference_edit_payload, prepared, "https://invalid/model")

    def test_builder_rejects_partial_scalar_and_invalid_references(self):
        prepared = references.prepare_original_references(self.items, self.bucket)
        cases = [("not-an-array", "invalid_reference_count"),
                 ([{"id": "shirt_1"}], "incomplete_original_reference"),
                 ([{**prepared[0], "image_bytes": b"invalid"}], "invalid_original_image"),
                 ([{**prepared[0], "mime_type": "image/jpeg"}], "incomplete_original_reference"),
                 ([prepared[0], prepared[0]], "duplicate_reference_id")]
        for value, code in cases:
            with self.subTest(code=code):
                self.assert_code(code, references.build_reference_edit_payload, value, "test-model")


if __name__ == "__main__":
    unittest.main()
