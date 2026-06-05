#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EVALUATION RUNNER: MaterialGenesis Golden Set Evaluation
=========================================================
Runs 100 golden test cases against the app's classification pipeline.
Does NOT use Streamlit UI - runs classification logic directly.

Output:
- eval_results/eval_report.json (detailed results for each test case)
- eval_results/eval_summary.md (human-readable summary)
- proposed_fixes/*.json (failures for review)
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Import MaterialGenesis functions
from category_registry import (
    detect_prompt_domain,
    classify_material_hierarchically,
    validate_domain_category_alignment,
    run_three_stage_verification,
    clear_previous_preset_fields,
    apply_category_preset,
    CATEGORY_TO_DOMAIN,
    CATEGORY_REGISTRY,
)


def load_golden_set():
    """Load the 100 golden test cases."""
    with open("test_cases/material_category_golden_set.json", "r") as f:
        data = json.load(f)
    return data["test_cases"]


def evaluate_single_case(test_case):
    """
    Evaluate a single test case.
    
    Returns dict with:
    - passed: bool
    - detected_domain: str
    - detected_confidence: int
    - selected_category: str
    - category_confidence: int
    - domain_category_aligned: bool
    - verification_status: str
    - must_include_failures: list
    - must_not_include_failures: list
    - expected_sections_missing: list
    - forbidden_sections_present: list
    - errors: list
    """
    case_id = test_case["id"]
    request = test_case["request"]
    expected_domain = test_case["expected_domain"]
    expected_category = test_case["expected_category"]
    
    result = {
        "id": case_id,
        "passed": True,
        "failures": [],
        "detected_domain": None,
        "detected_confidence": 0,
        "selected_category": None,
        "category_confidence": 0,
        "domain_category_aligned": False,
        "verification_status": None,
        "must_include_failures": [],
        "must_not_include_failures": [],
        "expected_sections_missing": [],
        "forbidden_sections_present": [],
        "errors": [],
    }
    
    try:
        # Step 1: Detect domain
        domain_result = detect_prompt_domain(request)
        detected_domain = domain_result["domain"]
        domain_confidence = domain_result["confidence"]
        
        result["detected_domain"] = detected_domain
        result["detected_confidence"] = domain_confidence
        
        # Check domain match
        if detected_domain != expected_domain:
            result["passed"] = False
            result["failures"].append(
                f"Domain mismatch: expected {expected_domain}, got {detected_domain}"
            )
        
        # Step 2: Classify category
        hier_result = classify_material_hierarchically(request)
        selected_category = hier_result.get("specific_preset", "other_material")
        category_confidence = hier_result.get("confidence_score", 0)
        
        result["selected_category"] = selected_category
        result["category_confidence"] = category_confidence
        
        # Check category match
        if selected_category != expected_category:
            result["passed"] = False
            result["failures"].append(
                f"Category mismatch: expected {expected_category}, got {selected_category}"
            )
        
        # Step 3: Verify domain-category alignment
        alignment = validate_domain_category_alignment(detected_domain, selected_category)
        result["domain_category_aligned"] = alignment.get("aligned", False)
        
        if not alignment.get("aligned"):
            result["passed"] = False
            result["failures"].append(
                f"Domain-category misalignment: {detected_domain} vs {selected_category}"
            )
        
        # Step 4: Run verification
        material_data = {
            "material_category": selected_category,
            "material_category_display": CATEGORY_REGISTRY.get(selected_category, {}).get("display_name", selected_category),
        }
        material_data = apply_category_preset(material_data, selected_category)
        
        verification_result = run_three_stage_verification(
            user_request=request,
            selected_category=selected_category,
            material_data=material_data,
            stored_confidence=None
        )
        
        result["verification_status"] = verification_result["overall_status"]
        
        # Step 5: Check must_include_terms
        request_lower = request.lower()
        for term in test_case.get("must_include_terms", []):
            if term.lower() not in request_lower and term.lower() not in material_data.get("composition", "").lower():
                # Allow if it's in material parameters
                is_present = False
                for param_val in material_data.get("category_specific_parameters", {}).values():
                    if isinstance(param_val, str) and term.lower() in param_val.lower():
                        is_present = True
                        break
                if not is_present:
                    result["must_include_failures"].append(term)
                    result["passed"] = False
        
        # Step 6: Check must_not_include_terms
        for term in test_case.get("must_not_include_terms", []):
            if term.lower() in request_lower:
                result["must_not_include_failures"].append(term)
                result["passed"] = False
        
        # Step 7: Check expected sections
        for section in test_case.get("expected_sections", []):
            if section not in material_data and not material_data.get(section):
                result["expected_sections_missing"].append(section)
                result["passed"] = False
        
        # Step 8: Check forbidden sections
        for section in test_case.get("forbidden_sections", []):
            if section in material_data and material_data[section]:
                result["forbidden_sections_present"].append(section)
                result["passed"] = False
        
    except Exception as e:
        result["passed"] = False
        result["errors"].append(str(e))
        result["failures"].append(f"Exception during evaluation: {str(e)}")
    
    return result


def run_evaluation():
    """Run full evaluation suite."""
    print("\n" + "="*80)
    print("MATERIALGENESIS GOLDEN SET EVALUATION")
    print("="*80)
    print(f"\nStarting evaluation at {datetime.now()}")
    
    # Load test cases
    test_cases = load_golden_set()
    print(f"Loaded {len(test_cases)} golden test cases")
    
    # Run evaluations
    results = []
    passed_count = 0
    failed_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        case_id = test_case["id"]
        severity = test_case.get("severity_if_failed", "medium")
        
        print(f"\n[{i}/{len(test_cases)}] Evaluating {case_id}...", end=" ")
        
        result = evaluate_single_case(test_case)
        result["severity"] = severity
        result["expected_domain"] = test_case["expected_domain"]
        result["expected_category"] = test_case["expected_category"]
        result["domain"] = test_case["domain"]
        
        results.append(result)
        
        if result["passed"]:
            passed_count += 1
            print("✅ PASS")
        else:
            failed_count += 1
            print("❌ FAIL")
            print(f"    Failures: {', '.join(result['failures'][:2])}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Cases: {len(test_cases)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Pass Rate: {100.0 * passed_count / len(test_cases):.1f}%")
    
    # Count by severity
    critical_failures = sum(1 for r in results if not r["passed"] and r["severity"] == "critical")
    high_failures = sum(1 for r in results if not r["passed"] and r["severity"] == "high")
    medium_failures = sum(1 for r in results if not r["passed"] and r["severity"] == "medium")
    low_failures = sum(1 for r in results if not r["passed"] and r["severity"] == "low")
    
    print(f"\nFailures by Severity:")
    print(f"  Critical: {critical_failures}")
    print(f"  High: {high_failures}")
    print(f"  Medium: {medium_failures}")
    print(f"  Low: {low_failures}")
    
    # Save results
    os.makedirs("eval_results", exist_ok=True)
    
    # Write detailed JSON report
    report_file = "eval_results/eval_report.json"
    with open(report_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_cases": len(test_cases),
            "passed": passed_count,
            "failed": failed_count,
            "pass_rate": 100.0 * passed_count / len(test_cases),
            "results": results
        }, f, indent=2)
    print(f"\n✅ Detailed report saved: {report_file}")
    
    # Write summary markdown
    summary_file = "eval_results/eval_summary.md"
    with open(summary_file, "w") as f:
        f.write("# MaterialGenesis Golden Set Evaluation Report\n\n")
        f.write(f"**Timestamp:** {datetime.now()}\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Total Cases:** {len(test_cases)}\n")
        f.write(f"- **Passed:** {passed_count}\n")
        f.write(f"- **Failed:** {failed_count}\n")
        f.write(f"- **Pass Rate:** {100.0 * passed_count / len(test_cases):.1f}%\n\n")
        
        f.write(f"## Failures by Severity\n")
        f.write(f"- **Critical:** {critical_failures}\n")
        f.write(f"- **High:** {high_failures}\n")
        f.write(f"- **Medium:** {medium_failures}\n")
        f.write(f"- **Low:** {low_failures}\n\n")
        
        f.write("## Failed Cases\n\n")
        for result in results:
            if not result["passed"]:
                f.write(f"### {result['id']} (Severity: {result['severity']})\n")
                f.write(f"- Expected Domain: {result['expected_domain']}\n")
                f.write(f"- Detected Domain: {result['detected_domain']} ({result['detected_confidence']}%)\n")
                f.write(f"- Expected Category: {result['expected_category']}\n")
                f.write(f"- Selected Category: {result['selected_category']} ({result['category_confidence']}%)\n")
                f.write(f"- Verification Status: {result['verification_status']}\n")
                if result["must_include_failures"]:
                    f.write(f"- Missing Terms: {', '.join(result['must_include_failures'])}\n")
                if result["must_not_include_failures"]:
                    f.write(f"- Unwanted Terms: {', '.join(result['must_not_include_failures'])}\n")
                if result["expected_sections_missing"]:
                    f.write(f"- Missing Sections: {', '.join(result['expected_sections_missing'])}\n")
                if result["forbidden_sections_present"]:
                    f.write(f"- Forbidden Sections Present: {', '.join(result['forbidden_sections_present'])}\n")
                f.write(f"- Failures: {', '.join(result['failures'])}\n\n")
    
    print(f"✅ Summary report saved: {summary_file}")
    
    # Save failures to proposed_fixes for AI review
    os.makedirs("proposed_fixes", exist_ok=True)
    for result in results:
        if not result["passed"]:
            fix_file = f"proposed_fixes/{result['id']}.json"
            with open(fix_file, "w") as f:
                json.dump({
                    "case_id": result["id"],
                    "severity": result["severity"],
                    "domain": result["domain"],
                    "expected_domain": result["expected_domain"],
                    "detected_domain": result["detected_domain"],
                    "detected_confidence": result["detected_confidence"],
                    "expected_category": result["expected_category"],
                    "selected_category": result["selected_category"],
                    "category_confidence": result["category_confidence"],
                    "failures": result["failures"],
                    "must_include_failures": result["must_include_failures"],
                    "must_not_include_failures": result["must_not_include_failures"],
                    "expected_sections_missing": result["expected_sections_missing"],
                    "forbidden_sections_present": result["forbidden_sections_present"],
                    "status": "pending_review",
                    "ai_review": None,
                    "approved": False,
                }, f, indent=2)
    
    failed_fixes = sum(1 for r in results if not r["passed"])
    print(f"✅ {failed_fixes} failure cases saved to proposed_fixes/ for AI review")
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80)
    
    return results


if __name__ == "__main__":
    results = run_evaluation()
    
    # Exit with code based on pass rate
    pass_rate = sum(1 for r in results if r["passed"]) / len(results)
    if pass_rate >= 0.95:
        print("\n✅ Evaluation PASSED (>95% pass rate)")
        exit(0)
    elif pass_rate >= 0.80:
        print("\n⚠️  Evaluation WARNING (80-95% pass rate)")
        exit(1)
    else:
        print("\n❌ Evaluation FAILED (<80% pass rate)")
        exit(2)
