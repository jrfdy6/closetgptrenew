#!/bin/bash

# Script to update all backend URLs in frontend
# From: closetgptrenew-backend-production.up.railway.app
# To: closetgptrenew-production.up.railway.app

OLD_URL="closetgptrenew-backend-production.up.railway.app"
NEW_URL="closetgptrenew-production.up.railway.app"

echo "=== Updating Backend URLs in Frontend ==="
echo "Old URL: $OLD_URL"
echo "New URL: $NEW_URL"
echo ""

# Find and replace in all frontend files
cd "$(dirname "$0")/frontend"

# Count occurrences first
echo "Found $(grep -r "$OLD_URL" . 2>/dev/null | wc -l) occurrences to update"
echo ""

# Perform the replacement
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -exec sed -i '' "s|$OLD_URL|$NEW_URL|g" {} +
else
    # Linux
    find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -exec sed -i "s|$OLD_URL|$NEW_URL|g" {} +
fi

echo "✅ URLs updated!"
echo ""
echo "Verify changes:"
echo "Old URL occurrences remaining: $(grep -r "$OLD_URL" . 2>/dev/null | wc -l)"
echo "New URL occurrences: $(grep -r "$NEW_URL" . 2>/dev/null | wc -l)"

