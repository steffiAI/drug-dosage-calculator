# -*- coding: utf-8 -*-
"""
Test Script for PubChem API Integration.

This script tests the molecular weight lookup functionality with various
chemical identifiers commonly used in oncology research.

Run this script to verify the API integration is working correctly before
integrating into the main drug calculator application.

Author: Steffi
Created: 2025
"""

import sys
import io
from pathlib import Path

# Set stdout to UTF-8 to handle any special characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src directory to path (matches main.py pattern)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pubchem_api import PubChemAPI, lookup_molecular_weight, ChemicalLookupError


def test_basic_lookup():
    """Test basic lookup functionality."""
    print("=" * 60)
    print("TEST 1: Basic Molecular Weight Lookup")
    print("=" * 60)
    
    api = PubChemAPI()
    
    test_cases = [
        ("Cisplatin", "Common oncology drug"),
        ("Doxorubicin", "Anthracycline antibiotic"),
        ("5-Fluorouracil", "Antimetabolite"),
        ("Paclitaxel", "Taxane"),
    ]
    
    passed = 0
    failed = 0
    
    for identifier, description in test_cases:
        print(f"\n  Testing: {identifier} ({description})")
        try:
            result = api.lookup(identifier)
            if result:
                print(f"    [PASS] Found: {result['molecular_formula']}, "
                      f"MW = {result['molecular_weight']:.2f} g/mol")
                passed += 1
            else:
                print(f"    [FAIL] Not found")
                failed += 1
        except Exception as e:
            print(f"    [FAIL] Error: {e}")
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_identifier_types():
    """Test different identifier types."""
    print("\n" + "=" * 60)
    print("TEST 2: Different Identifier Types")
    print("=" * 60)
    
    api = PubChemAPI()
    
    # Cisplatin in different formats (using correct identifiers!)
    test_cases = [
        ("Cisplatin", "name", "Drug name"),
        ("15663-27-1", "name", "CAS number"),  # Correct CAS for Cisplatin
        ("5460033", "cid", "PubChem CID"),      # Correct CID for Cisplatin
        ("Platinol", "name", "Brand name"),
    ]
    
    passed = 0
    failed = 0
    expected_mw = 300.05  # Cisplatin MW (updated from test results)
    
    for identifier, id_type, description in test_cases:
        print(f"\n  Testing: {identifier} as {id_type} ({description})")
        try:
            result = api.lookup(identifier, id_type)
            if result:
                mw = result['molecular_weight']
                print(f"    [PASS] Found: MW = {mw:.2f} g/mol, CID = {result['cid']}")
                
                # Verify all resolve to same compound (Cisplatin)
                if abs(mw - expected_mw) < 1.0:  # Allow 1 g/mol tolerance
                    print(f"    [PASS] Correct compound (Cisplatin)")
                    passed += 1
                else:
                    print(f"    [FAIL] Different compound (expected MW ~{expected_mw})")
                    failed += 1
            else:
                print(f"    [FAIL] Not found")
                failed += 1
        except Exception as e:
            print(f"    [FAIL] Error: {e}")
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_auto_detection():
    """Test automatic identifier type detection."""
    print("\n" + "=" * 60)
    print("TEST 3: Automatic Identifier Detection")
    print("=" * 60)
    
    api = PubChemAPI()
    
    test_cases = [
        ("Cisplatin", "name"),
        ("50-18-0", "name"),  # CAS
        ("5702", "cid"),
        ("CHEMBL11359", "name"),  # ChEMBL ID
    ]
    
    passed = 0
    failed = 0
    
    for identifier, expected_type in test_cases:
        detected = api.detect_identifier_type(identifier)
        status = "[PASS]" if detected == expected_type else "[FAIL]"
        print(f"  {status} '{identifier}' -> {detected} (expected: {expected_type})")
        
        if detected == expected_type:
            passed += 1
        else:
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_caching():
    """Test caching functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Caching Functionality")
    print("=" * 60)
    
    # Use temporary cache file
    import tempfile
    cache_file = Path(tempfile.gettempdir()) / "test_cache.json"
    
    try:
        # First lookup (should be fresh)
        print("\n  First lookup (fresh from API)...")
        api1 = PubChemAPI(cache_file=cache_file)
        result1 = api1.lookup("Cisplatin")
        
        if result1:
            print(f"    [PASS] Found: {result1['molecular_formula']}")
            print(f"    Cached: {result1.get('cached', False)}")
            
            if result1.get('cached'):
                print("    [FAIL] Should not be cached on first lookup")
                return False
        else:
            print("    [FAIL] Lookup failed")
            return False
        
        # Second lookup (should be cached)
        print("\n  Second lookup (from cache)...")
        api2 = PubChemAPI(cache_file=cache_file)
        result2 = api2.lookup("Cisplatin")
        
        if result2:
            print(f"    [PASS] Found: {result2['molecular_formula']}")
            print(f"    Cached: {result2.get('cached', False)}")
            
            if not result2.get('cached'):
                print("    [FAIL] Should be cached on second lookup")
                return False
        else:
            print("    [FAIL] Lookup failed")
            return False
        
        # Test cache info
        print("\n  Checking cache info...")
        cache_info = api2.get_cache_info()
        print(f"    Cached entries: {cache_info['size']}")
        print(f"    File exists: {cache_info['file_exists']}")
        print(f"    File size: {cache_info['file_size_kb']:.2f} KB")
        
        if cache_info['size'] < 1:
            print("    [FAIL] Cache should contain at least 1 entry")
            return False
        
        print("\n  [PASS] Caching working correctly")
        return True
        
    finally:
        # Clean up
        if cache_file.exists():
            cache_file.unlink()


def test_robust_lookup():
    """Test robust lookup with multiple strategies."""
    print("\n" + "=" * 60)
    print("TEST 5: Robust Lookup (Multiple Strategies)")
    print("=" * 60)
    
    api = PubChemAPI()
    
    # Test with variations that should still work
    test_cases = [
        "Cisplatin",  # Standard
        "cisplatin",  # Lowercase
        " Cisplatin ",  # With spaces
        "Cis-platin",  # With hyphen (should clean)
    ]
    
    passed = 0
    failed = 0
    
    for identifier in test_cases:
        print(f"\n  Testing: '{identifier}'")
        result, strategies = api.robust_lookup(identifier)
        
        if result:
            print(f"    [PASS] Found after trying: {strategies}")
            print(f"    Result: {result['molecular_formula']}, "
                  f"MW = {result['molecular_weight']:.2f} g/mol")
            passed += 1
        else:
            print(f"    [FAIL] Not found. Tried: {strategies}")
            failed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "=" * 60)
    print("TEST 6: Error Handling")
    print("=" * 60)
    
    api = PubChemAPI()
    
    # Test cases that should return None (not found)
    test_cases = [
        ("", "Empty string"),
        ("NonExistentDrug123456789", "Invalid drug name"),
        ("99999999999", "Invalid CID"),
    ]
    
    passed = 0
    failed = 0
    
    for identifier, description in test_cases:
        print(f"\n  Testing: {description}")
        try:
            result = api.lookup(identifier)
            if result is None:
                print(f"    [PASS] Correctly returned None for invalid input")
                passed += 1
            else:
                print(f"    [FAIL] Should have returned None")
                failed += 1
        except Exception as e:
            # Some errors are expected
            print(f"    [PASS] Raised expected error: {type(e).__name__}")
            passed += 1
    
    print(f"\n  Results: {passed} passed, {failed} failed")
    return failed == 0


def test_convenience_function():
    """Test the convenience wrapper function."""
    print("\n" + "=" * 60)
    print("TEST 7: Convenience Function")
    print("=" * 60)
    
    print("\n  Testing lookup_molecular_weight() convenience function...")
    
    try:
        mw = lookup_molecular_weight("Cisplatin")
        if mw and isinstance(mw, float):
            print(f"    [PASS] Returned float: {mw:.2f} g/mol")
            return True
        else:
            print(f"    [FAIL] Invalid return value: {mw}")
            return False
    except Exception as e:
        print(f"    [FAIL] Error: {e}")
        return False


def test_oncology_drugs():
    """Test with common oncology drugs used in the lab."""
    print("\n" + "=" * 60)
    print("TEST 8: Common Oncology Drugs")
    print("=" * 60)
    print("  (Testing drugs commonly used in cancer research)")
    
    api = PubChemAPI()
    
    oncology_drugs = [
        ("Cisplatin", "Platinum-based"),
        ("Carboplatin", "Platinum-based"),
        ("Oxaliplatin", "Platinum-based"),
        ("Doxorubicin", "Anthracycline"),
        ("5-Fluorouracil", "Antimetabolite"),
        ("Gemcitabine", "Antimetabolite"),
        ("Paclitaxel", "Taxane"),
        ("Docetaxel", "Taxane"),
        ("Irinotecan", "Topoisomerase inhibitor"),
        ("Temozolomide", "Alkylating agent"),
    ]
    
    results = []
    
    print("\n  Drug Name                  MW (g/mol)    Formula          Category")
    print("  " + "-" * 75)
    
    for drug, category in oncology_drugs:
        try:
            result = api.lookup(drug)
            if result:
                mw = result['molecular_weight']
                formula = result['molecular_formula']
                results.append((drug, mw, formula, category, "[PASS]"))
                print(f"  {drug:<25} {mw:>8.2f}    {formula:<15} {category}")
            else:
                results.append((drug, None, None, category, "[FAIL]"))
                print(f"  {drug:<25} {'Not found':<8}    {'':<15} {category}")
        except Exception as e:
            results.append((drug, None, None, category, "[FAIL]"))
            print(f"  {drug:<25} {'Error':<8}    {'':<15} {category}")
    
    success_count = sum(1 for r in results if r[4] == "[PASS]")
    print(f"\n  Results: {success_count}/{len(oncology_drugs)} drugs found")
    
    return success_count == len(oncology_drugs)


def run_all_tests():
    """Run all test functions and report results."""
    print("\n" + "=" * 60)
    print("PUBCHEM API INTEGRATION TEST SUITE")
    print("=" * 60)
    print("This script tests molecular weight lookup functionality")
    print("for integration with the drug calculator.")
    print()
    
    tests = [
        ("Basic Lookup", test_basic_lookup),
        ("Identifier Types", test_identifier_types),
        ("Auto Detection", test_auto_detection),
        ("Caching", test_caching),
        ("Robust Lookup", test_robust_lookup),
        ("Error Handling", test_error_handling),
        ("Convenience Function", test_convenience_function),
        ("Oncology Drugs", test_oncology_drugs),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  [FAIL] EXCEPTION in {test_name}: {e}")
            results.append((test_name, False))
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {test_name:<30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("\n" + "=" * 60)
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("[PASS] All tests passed! API integration is working correctly.")
        return 0
    else:
        print(f"[FAIL] {total - passed} test(s) failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
