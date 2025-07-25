#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.firebase import db

def list_users():
    """List all users in the database."""
    try:
        print("Fetching users from database...")
        users = db.collection('users').stream()
        
        user_list = []
        for user in users:
            user_data = user.to_dict()
            user_id = user.id
            user_name = user_data.get('name', 'Unknown')
            user_email = user_data.get('email', 'No email')
            user_list.append({
                'id': user_id,
                'name': user_name,
                'email': user_email
            })
        
        print(f"Found {len(user_list)} users:")
        for i, user in enumerate(user_list, 1):
            print(f"  {i}. {user['name']} ({user['email']}) - ID: {user['id']}")
        
        return user_list
        
    except Exception as e:
        print(f"Error listing users: {e}")
        return []

if __name__ == "__main__":
    list_users() 