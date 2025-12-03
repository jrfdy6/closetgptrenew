#!/bin/bash
# Quick validation script for complete flow testing

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  OUTFIT GENERATION - COMPLETE FLOW VALIDATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Testing:"
echo "  ✓ Occasion-first filtering"
echo "  ✓ Session tracking"
echo "  ✓ Exploration ratio (3:1)"
echo "  ✓ Favorites mode"
echo "  ✓ Wear decay"
echo ""
echo "Test Cases:"
echo "  1. Gym + Classic        → Gym-appropriate classic items"
echo "  2. Casual + Classic     → Classic-casual items (chinos, loafers)"
echo "  3. Gym + Minimalist     → Fallback expansion (sport, athletic)"
echo "  4. Sleep + Cozy         → Sleep items, allow overlaps"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Run validation
python3 validate_complete_flow.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "═══════════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo "  ✅ VALIDATION COMPLETE - ALL TESTS PASSED"
else
    echo "  ⚠️ VALIDATION COMPLETE - SOME TESTS FAILED"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

exit $EXIT_CODE

