#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI REVIEWER: MaterialGenesis Failure Analysis
==============================================
Uses ChatGPT/Claude to review failed test cases and propose fixes.
Returns structured JSON recommendations for human approval.

Reviewer checks:
1. Is the app correct or the test case wrong?
2. What's the actual problem?
3. What domain/category should it be?
4. What fix is needed?
5. How confident is the recommendation?

Output:
- proposed_fixes/{case_id}.json (updated with ai_review field)
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  Install anthropic SDK: pip install anthropic")

from category_registry import CATEGORY_REGISTRY, CATEGORY_TO_DOMAIN


def get_ai_client():
    """Get Anthropic client from environment."""
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("Anthropic SDK not installed. Run: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    return anthropic.Anthropic(api_key=api_key)


def review_failure(case_id: str, failure_data: dict) -> Optional[dict]:
    """
    Send a failed test case to AI reviewer for analysis.
    
    Returns dict with:
    {
        "is_correct": bool,  # Is app correct?
        "confidence": 0-100,
        "detected_problem": str,
        "correct_domain": str,
        "correct_category": str,
        "wrong_terms_found": list,
        "missing_terms": list,
        "suggested_fix_type": str,  # domain_rule | category_preset | formatting | validation_plan
        "suggested_fix": str,
        "reasoning": str
    }
    """
    
    try:
        client = get_ai_client()
    except (ImportError, ValueError) as e:
        print(f"❌ Cannot initialize AI reviewer: {str(e)}")
        print("   Skipping AI review for this case.")
        return None
    
    # Prepare the review prompt
    review_prompt = f"""
You are an expert materials science AI system reviewer. Analyze this failed test case:

TEST CASE ID: {case_id}
SEVERITY: {failure_data.get('severity', 'unknown')}
DOMAIN: {failure_data.get('domain', 'unknown')}

EXPECTED:
- Domain: {failure_data.get('expected_domain')}
- Category: {failure_data.get('expected_category')}

ACTUAL RESULTS:
- Detected Domain: {failure_data.get('detected_domain')} ({failure_data.get('detected_confidence')}% confidence)
- Selected Category: {failure_data.get('selected_category')} ({failure_data.get('category_confidence')}% confidence)
- Verification Status: {failure_data.get('verification_status')}

FAILURES:
{json.dumps(failure_data.get('failures', []), indent=2)}

MISSING TERMS: {failure_data.get('must_include_failures', [])}
UNWANTED TERMS: {failure_data.get('must_not_include_failures', [])}
MISSING SECTIONS: {failure_data.get('expected_sections_missing', [])}
FORBIDDEN SECTIONS: {failure_data.get('forbidden_sections_present', [])}

AVAILABLE DOMAINS:
{json.dumps(list(set(CATEGORY_TO_DOMAIN.values())), indent=2)}

AVAILABLE CATEGORIES:
{json.dumps(list(CATEGORY_REGISTRY.keys()), indent=2)}

---

ANALYSIS TASK:
1. Is the app's classification CORRECT despite the failure?
2. If not, what's the actual problem?
3. Should the expected domain/category be corrected?
4. What type of fix is needed (domain rule, category preset, validation)?
5. Provide specific fix recommendation.

RESPOND WITH VALID JSON ONLY (no markdown, no explanation):
{{
    "is_correct": <boolean>,
    "confidence": <0-100>,
    "detected_problem": "<concise problem description>",
    "correct_domain": "<domain if wrong, or same as detected>",
    "correct_category": "<category if wrong, or same as selected>",
    "wrong_terms_found": <list of incorrectly rejected terms>,
    "missing_terms": <list of terms that should be added to preset>,
    "suggested_fix_type": "<domain_rule | category_preset | formatting | validation_plan | test_case_wrong>",
    "suggested_fix": "<specific recommendation>",
    "reasoning": "<brief explanation>"
}}
"""
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": review_prompt
                }
            ]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON from response
        try:
            review_result = json.loads(response_text)
            return review_result
        except json.JSONDecodeError:
            print(f"⚠️  Could not parse AI response as JSON for {case_id}")
            # Try to extract JSON from markdown code block
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                try:
                    review_result = json.loads(json_str)
                    return review_result
                except json.JSONDecodeError:
                    pass
            return None
            
    except Exception as e:
        print(f"❌ AI review error for {case_id}: {str(e)}")
        return None


def review_all_failures(only_case_id: Optional[str] = None):
    """Review all failed test cases in proposed_fixes/."""
    
    print("\n" + "="*80)
    print("AI REVIEWER: MaterialGenesis Failure Analysis")
    print("="*80)
    
    proposed_dir = "proposed_fixes"
    if not os.path.exists(proposed_dir):
        print(f"No proposed_fixes directory found. Run eval_runner.py first.")
        return 0
    
    # Find all failure JSON files
    failure_files = list(Path(proposed_dir).glob("*.json"))
    
    # Filter if specific case requested
    if only_case_id:
        failure_files = [f for f in failure_files if only_case_id in f.name]
    
    if not failure_files:
        print(f"No failure cases found to review.")
        return 0
    
    print(f"\nFound {len(failure_files)} failed cases to review")
    print(f"Using AI reviewer: Claude 3.5 Sonnet\n")
    
    reviewed_count = 0
    approved_count = 0
    rejected_count = 0
    skipped_count = 0
    
    for i, failure_file in enumerate(failure_files, 1):
        with open(failure_file, "r") as f:
            failure_data = json.load(f)
        
        case_id = failure_data["case_id"]
        print(f"[{i}/{len(failure_files)}] Reviewing {case_id}...", end=" ", flush=True)
        
        # Call AI reviewer
        review_result = review_failure(case_id, failure_data)
        
        if review_result is None:
            print("⏭️  SKIPPED (AI error)")
            skipped_count += 1
            continue
        
        # Update failure file with review
        failure_data["ai_review"] = review_result
        failure_data["review_status"] = "completed"
        
        # Determine recommendation
        if review_result.get("is_correct"):
            failure_data["ai_recommendation"] = "APPROVED"
            failure_data["approved"] = True
            approved_count += 1
            print("✅ APPROVED by AI")
        else:
            failure_data["ai_recommendation"] = "REJECTED"
            failure_data["approved"] = False
            rejected_count += 1
            print("❌ REJECTED by AI")
        
        # Save updated failure file
        with open(failure_file, "w") as f:
            json.dump(failure_data, f, indent=2)
        
        reviewed_count += 1
        
        # Print AI recommendation
        if "suggested_fix" in review_result:
            print(f"   Fix: {review_result['suggested_fix'][:80]}...")
    
    # Summary
    print("\n" + "="*80)
    print("AI REVIEW SUMMARY")
    print("="*80)
    print(f"Cases Reviewed: {reviewed_count}")
    print(f"Approved (app is correct): {approved_count}")
    print(f"Rejected (fix needed): {rejected_count}")
    print(f"Skipped (errors): {skipped_count}")
    
    if rejected_count > 0:
        print(f"\n⚠️  {rejected_count} cases need fixes:")
        for failure_file in failure_files:
            with open(failure_file, "r") as f:
                data = json.load(f)
            if data.get("approved") == False and data.get("ai_review"):
                print(f"  - {data['case_id']}: {data['ai_review'].get('suggested_fix_type', 'unknown')}")
    
    print("\n" + "="*80)
    print("Next Step: Review proposed_fixes/ and move approved fixes to proposed_fixes/approved/")
    print("Then run: python apply_approved_fixes.py")
    print("="*80)
    
    return reviewed_count


if __name__ == "__main__":
    only_case = sys.argv[1] if len(sys.argv) > 1 else None
    
    if only_case:
        print(f"Reviewing single case: {only_case}")
    
    count = review_all_failures(only_case_id=only_case)
    exit(0 if count > 0 else 1)
