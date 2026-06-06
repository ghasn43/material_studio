#!/usr/bin/env python
import sys
import traceback

print("Python version:", sys.version)
print("Python path:", sys.executable)
print()

try:
    print("Step 1: Import category_registry module...")
    import category_registry
    print("✅ Import successful")
    
    print("\nStep 2: Check for CATEGORY_TO_DOMAIN...")
    if hasattr(category_registry, 'CATEGORY_TO_DOMAIN'):
        print(f"✅ CATEGORY_TO_DOMAIN exists - type: {type(category_registry.CATEGORY_TO_DOMAIN)}")
        print(f"   Keys count: {len(category_registry.CATEGORY_TO_DOMAIN)}")
    else:
        print("❌ CATEGORY_TO_DOMAIN NOT FOUND")
        print(f"   Available exports: {[x for x in dir(category_registry) if not x.startswith('_')][:10]}")
    
    print("\nStep 3: Try from import...")
    from category_registry import CATEGORY_TO_DOMAIN
    print(f"✅ from import successful - type: {type(CATEGORY_TO_DOMAIN)}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    traceback.print_exc()
