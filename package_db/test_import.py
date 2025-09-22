#!/usr/bin/env python3
"""
Test script to verify package import functionality
"""
import sys
import os

# Add the current directory to sys.path to test local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing firebird_package import...")
print("=" * 50)

try:
    # Test importing the package
    import firebird_package
    print("✅ Package imported successfully!")
    print(f"   Package version: {getattr(firebird_package, '__version__', 'Unknown')}")
    print(f"   Package author: {getattr(firebird_package, '__author__', 'Unknown')}")

except ImportError as e:
    print(f"❌ Package import failed: {e}")
    print("   This is expected if 'api' dependencies are not available")

try:
    # Test importing individual functions
    from firebird_package import (
        insert_transcript,
        get_completed_interview_ids,
        get_conversation_by_interview,
        update_interview_status_to_processed,
        delete_transcripts_by_interview_id,
        get_processed_interview_ids
    )

    print("✅ Successfully imported all functions from firebird_package!")
    print("Available functions:")
    print("  - insert_transcript")
    print("  - get_completed_interview_ids")
    print("  - get_conversation_by_interview")
    print("  - update_interview_status_to_processed")
    print("  - delete_transcripts_by_interview_id")
    print("  - get_processed_interview_ids")

    # Test function signatures
    print("\n🔍 Function signatures:")
    print(f"  insert_transcript: {insert_transcript.__doc__.split('.')[0] if insert_transcript.__doc__ else 'No docstring'}")

except ImportError as e:
    print(f"❌ Function import failed: {e}")
    if "api" in str(e):
        print("   Issue: Missing 'api' module dependency")
        print("   Suggestion: Ensure api.database.db_connection and api.core.loggerconfig are available")
    else:
        print("   Make sure to install the package first: pip install -e .")

print("\n" + "=" * 50)
print("Test completed!")