#!/usr/bin/env python3
"""Quick verification that routes are properly defined"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("🔍 Verifying Route Structure...")
print("=" * 50)

# Check files exist
routes_to_check = [
    'backend/src/routes/prospects.py',
    'backend/src/routes/prospects_manual.py',
    'backend/src/routes/outreach.py',
    'backend/src/routes/outreach_manual.py',
    'backend/src/routes/tracking.py',
    'backend/src/routes/prospects_phases.py',
]

print("\n1️⃣ Checking route files exist...")
for route_file in routes_to_check:
    if os.path.exists(route_file):
        print(f"   ✅ {route_file}")
    else:
        print(f"   ❌ {route_file} - MISSING")

# Check route definitions
print("\n2️⃣ Checking route definitions...")
import re

manual_routes = {
    'prospects_manual.py': [
        r'@router\.post\("/prompts/analyze"',
        r'@router\.post\("/manual/upload-analysis"',
        r'@router\.post\("/prompts/preview-analyze"',
    ],
    'outreach_manual.py': [
        r'@router\.post\("/prompts/generate"',
        r'@router\.post\("/manual/upload"',
    ],
    'prospects_phases.py': [
        r'@router\.post\("/phase1/metrics"',
        r'@router\.post\("/phase2/metrics"',
        r'@router\.post\("/phase2/engagement"',
        r'@router\.get\("/phase-status"',
    ],
}

for file_name, patterns in manual_routes.items():
    file_path = f'backend/src/routes/{file_name}'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        for pattern in patterns:
            if re.search(pattern, content):
                route_name = pattern.split('"')[1] if '"' in pattern else pattern
                print(f"   ✅ {file_name}: {route_name}")
            else:
                print(f"   ⚠️  {file_name}: Missing {pattern}")

# Check app.py registration
print("\n3️⃣ Checking route registration in app.py...")
app_py = 'backend/app.py'
if os.path.exists(app_py):
    with open(app_py, 'r') as f:
        content = f.read()
    
    routes_to_check_registration = [
        'prospects_manual',
        'outreach_manual',
        'prospects_phases',
    ]
    
    for route_name in routes_to_check_registration:
        if route_name in content:
            print(f"   ✅ {route_name} is registered")
        else:
            print(f"   ❌ {route_name} NOT registered")

print("\n" + "=" * 50)
print("✅ Route verification complete!")
print("\n📝 To test:")
print("   1. Start backend: cd backend && python3 -m uvicorn app:app --reload --port 3001")
print("   2. Run test script: ./test_endpoints.sh")
print("   3. Or follow: QUICK_TEST.md")
