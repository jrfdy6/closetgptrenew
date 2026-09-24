"""Owned original URL admission is pure parsing, without cloud access."""
import subprocess
import sys
import unittest
from urllib.parse import quote

from worker.original_source import (
    DEFAULT_BUCKET_NAME, is_owned_upload_path, owned_upload_source, request_original_path,
)


BUCKET = DEFAULT_BUCKET_NAME
OWNER = "verified-user"
RAW = f"wardrobe/{OWNER}/76138ff3-6ec6-4e3c-a612-10b2899142c8_White_tee.jpg.jpg"


def gcs(path=RAW, bucket=BUCKET):
    return f"https://storage.googleapis.com/{bucket}/{quote(path, safe='/')}"


def firebase(path=RAW, bucket=BUCKET):
    return f"https://firebasestorage.googleapis.com/v0/b/{bucket}/o/{quote(path, safe='')}?alt=media&token=download-token"


class OriginalSourceTests(unittest.TestCase):
    def test_backend_public_and_frontend_token_formats_resolve_same_owned_object(self):
        for url in (gcs(), firebase()):
            with self.subTest(url=url):
                self.assertEqual(owned_upload_source(url, OWNER), {"bucket": BUCKET, "sourceStoragePath": RAW})
        short = f"wardrobe/{OWNER}/76138ff3-6ec6-4e3c-a612-10b2899142c8.jpg"
        self.assertEqual(owned_upload_source(firebase(short), OWNER)["sourceStoragePath"], short)

    def test_single_unicode_space_and_punctuation_filename_retained_exactly(self):
        path = f"wardrobe/{OWNER}/76138ff3-6ec6-4e3c-a612-10b2899142c8_青い shirt #1?.png"
        for url in (gcs(path), firebase(path)):
            self.assertEqual(owned_upload_source(url, OWNER)["sourceStoragePath"], path)

    def test_foreign_user_prefix_or_nested_leaf_never_admitted(self):
        for path in ("wardrobe/other/shirt.jpg", f"wardrobe/{OWNER}-other/shirt.jpg",
                     f"wardrobe/{OWNER}/nested/shirt.jpg", f"users/{OWNER}/wardrobe/shirt.jpg",
                     f"items/{OWNER}/original.png", f"wardrobe/{OWNER}/", f"wardrobe/{OWNER}/ "):
            for url in (gcs(path), firebase(path)):
                self.assertIsNone(owned_upload_source(url, OWNER), path)

    def test_only_configured_bucket_allowed(self):
        for bucket in ("other.firebasestorage.app", "closetgptrenew.appspot.com", BUCKET + ".evil"):
            self.assertIsNone(owned_upload_source(gcs(bucket=bucket), OWNER))
            self.assertIsNone(owned_upload_source(firebase(bucket=bucket), OWNER))
        alternate = "configured-bucket.example"
        self.assertEqual(owned_upload_source(gcs(bucket=alternate), OWNER, alternate),
                         {"bucket": alternate, "sourceStoragePath": RAW})

    def test_host_scheme_userinfo_ports_fragments_and_redirect_query_rejected(self):
        invalid = [gcs().replace("https:", "http:"), gcs().replace("https:", "ftp:"),
                   gcs().replace("storage.googleapis.com", "storage.googleapis.com.evil"),
                   gcs().replace("storage.googleapis.com", "storage.googleapis.com."),
                   gcs().replace("storage.googleapis.com", "name@storage.googleapis.com"),
                   gcs().replace("storage.googleapis.com", "storage.googleapis.com:443"),
                   gcs() + "#fragment", gcs() + "#", gcs() + "?redirect=https://elsewhere.test",
                   firebase() + "&redirect=https://elsewhere.test", gcs().replace("https://", "//"),
                   "https://[broken", "https://evil.test/image.jpg", "data:image/png;base64,AA=="]
        for url in invalid:
            with self.subTest(url=url):
                self.assertIsNone(owned_upload_source(url, OWNER))

    def test_traversal_encoded_separators_and_multiple_decoding_cannot_change_owner(self):
        for path in (f"wardrobe/{OWNER}/../other.jpg", f"wardrobe/{OWNER}/.",
                     f"wardrobe/{OWNER}/..", f"wardrobe/{OWNER}/back\\slash.jpg",
                     f"wardrobe/{OWNER}/%2e%2e%2fother.jpg", f"wardrobe/{OWNER}/shirt%2Fother.jpg",
                     f"wardrobe/{OWNER}/shirt\x00.jpg", f"wardrobe/{OWNER}/shirt\n.jpg"):
            for url in (gcs(path), firebase(path)):
                self.assertIsNone(owned_upload_source(url, OWNER), path)
        for suffix in ("%", "%zz", "%FF", "%C0%AF", "%252Fother.jpg", "%2Fother.jpg"):
            url = f"https://storage.googleapis.com/{BUCKET}/wardrobe/{OWNER}/{suffix}"
            self.assertIsNone(owned_upload_source(url, OWNER), suffix)

    def test_malformed_firebase_routes_and_queries_rejected(self):
        for url in (firebase().replace("/v0/", "/v1/"), firebase().replace("/o/", "/objects/"),
                    firebase() + "&token=second", firebase() + "&alt=media",
                    firebase().replace("alt=media", "alt=json"), firebase().replace("token=download-token", "token="),
                    firebase().replace("token=download-token", "token=%FF"),
                    firebase().replace("token=download-token", "token=%ZZ"),
                    firebase().replace("token=download-token", "token=%0A"),
                    firebase().replace("token=download-token", "malformed")):
            self.assertIsNone(owned_upload_source(url, OWNER), url)
        no_token = firebase().split("?", 1)[0]
        self.assertIsNotNone(owned_upload_source(no_token, OWNER))
        self.assertIsNotNone(owned_upload_source(no_token + "?alt=media", OWNER))

    def test_invalid_values_fail_closed_and_descriptor_path_is_never_decoded(self):
        for value in (None, 3, {}, "", " " + gcs(), gcs() + " ", gcs() + "\n", "https://" + "x" * 9000):
            self.assertIsNone(owned_upload_source(value, OWNER))
        for owner in (None, 3, "", ".", "..", OWNER + "/other", OWNER + "%", " " + OWNER):
            self.assertIsNone(owned_upload_source(gcs(), owner))
        self.assertTrue(is_owned_upload_path(RAW, OWNER))
        self.assertFalse(is_owned_upload_path(quote(RAW, safe=""), OWNER))
        self.assertFalse(is_owned_upload_path(RAW.replace(OWNER, "other"), OWNER))

    def test_request_paths_are_safe_deterministic_and_request_specific(self):
        self.assertEqual(request_original_path("item-123.v2", "request_1"),
                         "items/item-123.v2/flatlay-requests/request_1/original.png")
        self.assertNotEqual(request_original_path("shirt", "one"), request_original_path("shirt", "two"))
        for value in (None, 3, "", ".", "..", "a/b", "a\\b", "a%2Fb", "a b", "a#b", "x" * 129):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    request_original_path(value, "request")
                with self.assertRaises(ValueError):
                    request_original_path("item", value)

    def test_import_does_not_initialize_cloud_or_image_libraries(self):
        script = ("import sys; import worker.original_source; "
                  "assert not any(name in sys.modules for name in "
                  "['firebase_admin','requests','PIL','numpy','rembg'])")
        completed = subprocess.run([sys.executable, "-c", script], capture_output=True, timeout=5)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())


if __name__ == "__main__":
    unittest.main()
