#!/usr/bin/env python3
"""Comprehensive endpoint validation test"""
import json
import os
import sys

print("=" * 60)
print("🧪 PROSPECTING WORKFLOW ENDPOINT VALIDATION")
print("=" * 60)
print()

# Test 1: File Structure
print("1️⃣ Checking file structure...")
required_files = [
    "backend/src/routes/prospects.py",
    "backend/src/routes/prospects_manual.py",
    "backend/src/routes/outreach.py",
    "backend/src/routes/outreach_manual.py",
    "backend/src/routes/tracking.py",
    "backend/src/routes/prospects_phases.py",
    "backend/app.py",
]

all_exist = True
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
    else:
        print(f"   ❌ {file_path} - MISSING")
        all_exist = False

print()

# Test 2: Route Definitions
print("2️⃣ Checking route definitions...")
import re

routes_to_verify = {
    "prospects_manual.py": [
        ("POST", "/prompts/analyze", "Generate analysis prompt"),
        ("POST", "/manual/upload-analysis", "Upload ChatGPT results"),
        ("POST", "/prompts/preview-analyze/{prospect_id}", "Preview prompt"),
    ],
    "outreach_manual.py": [
        ("POST", "/prompts/generate", "Generate outreach prompt"),
        ("POST", "/manual/upload", "Upload outreach drafts"),
    ],
    "prospects_phases.py": [
        ("POST", "/phase1/metrics", "Track Phase 1 metrics"),
        ("POST", "/phase2/metrics", "Track Phase 2 metrics"),
        ("POST", "/phase2/engagement", "Track engagement"),
        ("POST", "/phase-status", "Update phase status"),
        ("GET", "/phase-status/{user_id}", "Get phase status"),
        ("GET", "/phase1/summary/{user_id}", "Get Phase 1 summary"),
        ("GET", "/phase2/summary/{user_id}", "Get Phase 2 summary"),
        ("POST", "/phase3/prompt-refinement", "Save prompt refinement"),
        ("POST", "/phase3/knowledge", "Add knowledge entry"),
        ("GET", "/phase3/knowledge", "Get knowledge base"),
    ],
}

for file_name, routes in routes_to_verify.items():
    file_path = f"backend/src/routes/{file_name}"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        for method, path, description in routes:
            # Convert path to regex pattern
            pattern = path.replace("{", "\\{").replace("}", "\\}")
            route_pattern = f'@router\\.{method.lower()}\\("{pattern}"'
            if re.search(route_pattern, content):
                print(f"   ✅ {method} {path} - {description}")
            else:
                # Try alternative pattern
                alt_pattern = f'@router\\.{method.lower()}\\("{re.escape(path)}"'
                if re.search(alt_pattern, content):
                    print(f"   ✅ {method} {path} - {description}")
                else:
                    print(f"   ⚠️  {method} {path} - May need verification")

print()

# Test 3: Route Registration
print("3️⃣ Checking route registration in app.py...")
if os.path.exists("backend/app.py"):
    with open("backend/app.py", 'r') as f:
        content = f.read()
    
    expected_routes = [
        ("prospects_manual", "/api/prospects/manual"),
        ("outreach_manual", "/api/outreach/manual"),
        ("prospects_phases", "/api/phases"),
    ]
    
    for route_name, prefix in expected_routes:
        if route_name in content and prefix in content:
            print(f"   ✅ {route_name} registered at {prefix}")
        else:
            print(f"   ❌ {route_name} NOT properly registered")

print()

# Test 4: Manual Mode Features
print("4️⃣ Checking manual mode features...")
if os.path.exists("backend/src/routes/prospects_manual.py"):
    with open("backend/src/routes/prospects_manual.py", 'r') as f:
        content = f.read()
    
    features = [
        ("full_prompt", "Generates copy-paste prompt"),
        ("upload-analysis", "Accepts manual ChatGPT results"),
        ("ChatGPT", "Mentions ChatGPT in comments/docs"),
    ]
    
    for feature, desc in features:
        if feature in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - May need verification")

print()

# Test 5: Phase Tracking Features
print("5️⃣ Checking phase tracking features...")
if os.path.exists("backend/src/routes/prospects_phases.py"):
    with open("backend/src/routes/prospects_phases.py", 'r') as f:
        content = f.read()
    
    features = [
        ("Phase1Metrics", "Phase 1 metrics model"),
        ("Phase2Metrics", "Phase 2 metrics model"),
        ("EngagementMetrics", "Engagement tracking model"),
        ("PromptRefinement", "Prompt refinement model"),
        ("ai_knowledge_base", "AI knowledge base storage"),
    ]
    
    for feature, desc in features:
        if feature in content:
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚠️  {desc} - May need verification")

print()

# Test 6: Documentation
print("6️⃣ Checking documentation...")
docs = [
    "TESTING_GUIDE.md",
    "QUICK_TEST.md",
    "MANUAL_WORKFLOW_GUIDE.md",
    "PHASED_APPROACH_GUIDE.md",
    "PROSPECTING_WORKFLOW.md",
]

for doc in docs:
    if os.path.exists(doc):
        print(f"   ✅ {doc}")
    else:
        print(f"   ⚠️  {doc} - Missing")

print()
print("=" * 60)
print("✅ VALIDATION COMPLETE")
print("=" * 60)
print()
print("📝 To actually test with running backend:")
print("   1. Install dependencies: cd backend && pip install -r requirements.txt")
print("   2. Start backend: python3 -m uvicorn app:app --reload --port 3001")
print("   3. Run: ./test_endpoints.sh")
print()

