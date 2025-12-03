#!/usr/bin/env python3
"""
Wrapper script to run backfill with proper environment setup
This script ensures all imports work correctly by setting up the Python path
"""

import os
import sys

# Add the backend directory to the Python path so "src." imports work
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Now run the backfill script
if __name__ == "__main__":
    # Import the backfill script's main function
    scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    sys.path.insert(0, scripts_dir)
    
    # Import after path is set
    from backfill_normalize import main
    
    # Run it
    sys.exit(main())

