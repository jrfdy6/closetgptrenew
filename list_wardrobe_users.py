#!/usr/bin/env python3
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("backend/service-account-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def list_wardrobe_user_ids():
    wardrobe_ref = db.collection('wardrobe')
    docs = wardrobe_ref.stream()
    user_ids = set()
    for doc in docs:
        data = doc.to_dict()
        user_id = data.get('userId')
        if user_id:
            user_ids.add(user_id)
    return user_ids

if __name__ == "__main__":
    user_ids = list_wardrobe_user_ids()
    print("Found user IDs in wardrobe collection:")
    for uid in user_ids:
        print(f"- {uid}") 