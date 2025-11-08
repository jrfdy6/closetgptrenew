#!/usr/bin/env python3
"""
Inspect wardrobe items for material metadata and image storage.

Usage:
    python backend/scripts/inspect_wardrobe_items.py --user USER_ID [--limit 5]
"""

import argparse
import base64
import os
from pprint import pprint

import firebase_admin
from firebase_admin import credentials, firestore, storage


def init_firebase(bucket_suffix: str | None = None):
    """Initialize Firebase Admin SDK using environment variables."""
    if firebase_admin._apps:
        return

    required = [
        "FIREBASE_PROJECT_ID",
        "FIREBASE_PRIVATE_KEY",
        "FIREBASE_CLIENT_EMAIL",
        "FIREBASE_CLIENT_ID",
        "FIREBASE_CLIENT_X509_CERT_URL",
        "FIREBASE_PRIVATE_KEY_ID",
    ]
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        raise RuntimeError(f"Missing required env vars: {missing}")

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.environ["FIREBASE_PROJECT_ID"],
        "private_key_id": os.environ["FIREBASE_PRIVATE_KEY_ID"],
        "private_key": os.environ["FIREBASE_PRIVATE_KEY"].replace("\\n", "\n"),
        "client_email": os.environ["FIREBASE_CLIENT_EMAIL"],
        "client_id": os.environ["FIREBASE_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ["FIREBASE_CLIENT_X509_CERT_URL"],
    })

    bucket_name = os.environ.get("FIREBASE_STORAGE_BUCKET")
    if not bucket_name:
        project_id = os.environ["FIREBASE_PROJECT_ID"]
        bucket_name = f"{project_id}.firebasestorage.app"
        if bucket_suffix:
            bucket_name = bucket_suffix

    firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})


def normalize_item(doc):
    data = doc.to_dict() or {}
    data["id"] = doc.id
    return data


def extract_material(data: dict) -> str | None:
    metadata = data.get("metadata") or {}
    va = metadata.get("visualAttributes") or {}
    return va.get("material") or va.get("fabric") or data.get("material")


def inspect_items(user_id: str, limit: int = 5, download_image: bool = False):
    db = firestore.client()
    bucket = storage.bucket()

    query = (
        db.collection("wardrobe")
        .where("userId", "==", user_id)
        .limit(limit)
    )

    docs = list(query.stream())
    if not docs:
        print(f"No wardrobe items found for user {user_id}")
        return

    print(f"Found {len(docs)} wardrobe items for user {user_id}\n")

    for doc in docs:
        item = normalize_item(doc)
        item_id = item["id"]
        material = extract_material(item)
        image_url = item.get("backgroundRemovedUrl") or item.get("processedUrl") or item.get("imageUrl")

        print(f"Item: {item.get('name') or item_id}")
        print(f"  ID: {item_id}")
        print(f"  Type: {item.get('type')}")
        print(f"  Material: {material or 'N/A'}")
        print(f"  backgroundRemovedUrl: {item.get('backgroundRemovedUrl')}")
        print(f"  processedUrl: {item.get('processedUrl')}")
        print(f"  imageUrl: {item.get('imageUrl')}")

        if not image_url:
            print("  ⚠️  No image URL stored.")
        else:
            path = image_url.split("/o/", 1)[-1].split("?")[0]
            blob_path = path.replace("%2F", "/")
            print(f"  Storage blob path: {blob_path}")

            blob = bucket.blob(blob_path)
            exists = blob.exists()
            print(f"  Blob exists: {exists}")

            if exists and download_image:
                data = blob.download_as_bytes()
                sample = base64.b64encode(data[:24]).decode("utf-8")
                print(f"  Downloaded bytes: {len(data)} (base64 sample: {sample}...)")

        if item.get("metadata"):
            print("  metadata.visualAttributes:")
            pprint(item["metadata"].get("visualAttributes"), indent=4)

        print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Inspect wardrobe items in Firestore.")
    parser.add_argument("--user", required=True, help="User ID (Firebase UID)")
    parser.add_argument("--limit", type=int, default=5, help="Number of items to inspect")
    parser.add_argument("--download-image", action="store_true", help="Download image bytes to confirm availability")
    parser.add_argument("--bucket", help="Optional override for storage bucket name")
    args = parser.parse_args()

    init_firebase(bucket_suffix=args.bucket)
    inspect_items(args.user, limit=args.limit, download_image=args.download_image)


if __name__ == "__main__":
    main()

