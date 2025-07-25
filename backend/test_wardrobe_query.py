#!/usr/bin/env python3

import asyncio
import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

CORRECT_USER_ID = "dANqjiI0CKgaitxzYtw1bhtvQrG3"


def scan_wardrobe():
    # Initialize Firebase (if not already initialized)
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate("service-account-key.json")
        firebase_admin.initialize_app(cred)
    db = firestore.client()

    print("Scanning wardrobe collection...")
    all_wardrobe_ref = db.collection('wardrobe')
    all_docs = all_wardrobe_ref.stream()

    user_id_counts = {}
    missing_user_id = []
    wrong_user_id = []
    total_items = 0
    for doc in all_docs:
        total_items += 1
        item_data = doc.to_dict()
        uid = item_data.get('userId')
        if not uid:
            missing_user_id.append(doc.id)
        else:
            user_id_counts[uid] = user_id_counts.get(uid, 0) + 1
            if uid != CORRECT_USER_ID:
                wrong_user_id.append((doc.id, uid))
    print(f"Total items in wardrobe collection: {total_items}")
    print("User ID counts:")
    for uid, count in user_id_counts.items():
        print(f"  {uid}: {count}")
    print(f"Items missing userId: {len(missing_user_id)}")
    print(f"Items with wrong userId: {len(wrong_user_id)}")
    return missing_user_id, wrong_user_id

def fix_wardrobe(missing_user_id, wrong_user_id):
    db = firestore.client()
    # Fix missing userId
    for doc_id in missing_user_id:
        doc_ref = db.collection('wardrobe').document(doc_id)
        doc_ref.update({'userId': CORRECT_USER_ID})
        print(f"Set userId for {doc_id}")
    # Fix wrong userId
    for doc_id, old_uid in wrong_user_id:
        doc_ref = db.collection('wardrobe').document(doc_id)
        doc_ref.update({'userId': CORRECT_USER_ID})
        print(f"Updated userId for {doc_id} from {old_uid} to {CORRECT_USER_ID}")
    print("All fixes applied.")

if __name__ == "__main__":
    missing, wrong = scan_wardrobe()
    if missing or wrong:
        ans = input(f"\nFix {len(missing)} missing and {len(wrong)} wrong userId items? (y/N): ")
        if ans.strip().lower() == 'y':
            fix_wardrobe(missing, wrong)
        else:
            print("No changes made.")
    else:
        print("No missing or wrong userId fields found. All good!") 