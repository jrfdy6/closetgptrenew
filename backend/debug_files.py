#!/usr/bin/env python3
import os
import sys

print("=== Debug Files Script ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")
print(f"Files in current directory:")
for file in os.listdir('.'):
    print(f"  - {file}")

print(f"\nChecking if app.py exists: {os.path.exists('app.py')}")
print(f"Checking if app.py is readable: {os.access('app.py', os.R_OK)}")

if os.path.exists('app.py'):
    print("app.py exists and is accessible!")
else:
    print("app.py NOT FOUND!") 