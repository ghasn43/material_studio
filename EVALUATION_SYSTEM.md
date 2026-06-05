# MaterialGenesis Automated Evaluation & Self-Check System

## Overview

A comprehensive automated evaluation system for MaterialGenesis that:
- Tests 100 golden material design prompts across 14 material domains
- Validates domain detection and category classification
- Performs AI-assisted review of failures
- Requires human approval before any production changes
- **Never automatically modifies the production registry**

## Architecture

```
┌─ test_cases/material_category_golden_set.json (100 test cases)
│
├─ eval_runner.py (Run evaluation)
│  └─ Outputs:
│     ├─ eval_results/eval_report.json (detailed results)
│     ├─ eval_results/eval_summary.md (human-readable summary)
│     └─ proposed_fixes/{case_id}.json (failures for review)
│
├─ ai_reviewer.py (AI-assisted failure analysis)
│  └─ Uses Claude 3.5 Sonnet to analyze each failure
│     └─ Outputs: Updated proposed_fixes/{case_id}.json with ai_review
│
└─ apply_approved_fixes.py (APPROVAL-ONLY fix application)
   └─ Applies ONLY fixes moved to proposed_fixes/approved/
      ├─ Backups registry before changes
      └─ Logs all modifications
```

## Directory Structure

```
material_studio_1/
├── test_cases/
│   └── material_category_golden_set.json      # 100 golden test cases
├── eval_results/
│   ├── eval_report.json                       # Detailed evaluation results
│   ├── eval_summary.md                        # Summary (readable)
│   └── apply_fixes_log_*.json                 # Fix application logs
├── proposed_fixes/
│   ├── {case_id}.json                         # Pending fixes (proposed by AI)
│   └── approved/
│       └── {case_id}.json                     # Human-approved fixes
├── registry_backups/
│   └── category_registry_*.py                 # Auto-backups before fix application
├── eval_runner.py
├── ai_reviewer.py
└── apply_approved_fixes.py
```

## Golden Test Cases: 14 Material Domains (100 total)

### 1. **Battery Electrode** (10 cases)
- Sodium-ion battery anode
- Lithium-ion cathode
- Solid-state electrolyte
- Potassium-ion battery
- Silicon-dominant anode
- Zinc-air battery
- Lithium metal anode
- Manganese oxide cathode

### 2. **Phosphate Recovery** (7 cases)
- Agricultural wastewater phosphate recovery
- Industrial wastewater with LDH/MOF
- Ion-exchange phosphate recovery
- Biochar-based adsorbent
- Swine manure recovery
- Dual-functional P & N recovery
- Activated carbon hybrid

### 3. **Carbon Capture** (7 cases)
- Amine-functionalized CO2 sorbent
- Direct air capture (DAC)
- Metal-organic framework (MOF)
- Zeolite-based CO2 sorbent
- Carbon-based adsorbent
- Humidity-swing adsorbent
- Supported ionic liquid

### 4. **Oil & Gas Produced Water** (7 cases)
- Pre-treatment media for oil removal
- BTEX adsorbent
- Coalescer media
- Ion-exchange desalination
- Sulfide oxidation catalyst
- Scale-inhibitor media
- Multi-stage treatment system

### 5. **Desalination Pretreatment** (7 cases)
- Multimedia filter for RO pretreatment
- Cartridge filter media
- Granular activated carbon (GAC)
- Coagulation/flocculation pretreatment
- Biofouling prevention
- Iron-manganese oxidation
- Oil spill response media

### 6. **Fabric Cleaning** (7 cases)
- Oil-stain removal composite
- Enzyme-based stain remover
- Soil-release finish
- Stain-resistant treatment
- Grease-cutting laundry additive
- Ultrasonic fabric cleaning
- Eco-friendly stain remover

### 7. **Roof Waterproofing** (7 cases)
- Cool roof coating
- Self-healing coating
- Green roof system
- Liquid-applied membrane
- Photocatalytic self-cleaning
- Multi-layer thermal insulation

### 8. **Atmospheric Water Harvesting** (7 cases)
- Hygroscopic salt-based AWH
- Metal-organic framework (MOF)
- Polymer-based sorbent
- Passive radiative cooling + harvesting
- Desiccant wheel system
- Bio-inspired water harvesting
- Ion-exchange resin-based system

### 9. **Photocatalytic Water Treatment** (7 cases)
- TiO2-based photocatalyst
- Graphene oxide + TiO2 composite
- Bismuth vanadate (BiVO4)
- Plasmonic photocatalyst
- Heterojunction photocatalyst
- Photocatalytic membrane
- Z-scheme photocatalyst

### 10. **Self-Cleaning Building Coating** (7 cases)
- TiO2 photocatalytic coating
- Superhydrophobic coating
- Biocidal antimicrobial coating
- Hybrid photocatalytic + hydrophobic
- Lotus-leaf-inspired surface
- Smart switchable wettability
- Transparent self-cleaning coating

### 11. **Heavy Metal Adsorption** (7 cases)
- Pb/Cd/Zn adsorbent
- Arsenic/Chromium removal with chitosan
- Iron oxide nanoparticles
- Mercury/Gold removal with thiol groups
- MOF adsorbent
- Graphene oxide composite
- Biochar for radionuclides

### 12. **Potassium Brine Separation** (7 cases)
- K-selective ion-exchange resin
- Zeolite/LDH adsorbent
- Solvent extraction with ionic liquid
- K-selective membrane
- Crystallization from mineral brines
- Nano-adsorbent
- Electrochemical extraction

### 13. **Membrane Water Treatment** (7 cases)
- Reverse osmosis (RO) membrane
- Ultrafiltration (UF) membrane
- Nanofiltration (NF) membrane
- Forward osmosis (FO) membrane
- Microfiltration (MF) membrane
- Ceramic membrane
- Ion-exchange membrane

### 14. **Thermal Insulation** (7 cases)
- Polyurethane foam
- Mineral wool
- Phenolic foam
- Aerogel composite
- Vacuum insulation panel (VIP)
- Composite insulation board
- Bio-based thermal insulation

### **Edge Cases** (1 case)
- Unknown/space application

**TOTAL: 100 test cases**

## Test Case Format

```json
{
  "id": "battery_001",
  "domain": "battery_electrode",
  "request": "Design a sodium-ion battery anode composite using hard carbon...",
  "expected_domain": "battery_electrode",
  "expected_category": "sodium_ion_battery_anode_composite",
  "must_include_terms": ["hard carbon", "specific capacity", "coulombic efficiency"],
  "must_not_include_terms": ["thermal insulation", "fabric cleaning"],
  "expected_sections": ["composition", "processing_method", "validation_plan"],
  "forbidden_sections": ["thermal_conductivity_rating"],
  "severity_if_failed": "critical|high|medium|low"
}
```

## Workflow

### Step 1: Run Evaluation

```bash
python eval_runner.py
```

**Output:**
- ✅ 100/100 tests run
- Detailed results: `eval_results/eval_report.json`
- Summary: `eval_results/eval_summary.md`
- Failures: `proposed_fixes/{case_id}.json` (only if failed)

**Exit Codes:**
- `0`: ✅ PASSED (≥95% pass rate)
- `1`: ⚠️  WARNING (80-95% pass rate)
- `2`: ❌ FAILED (<80% pass rate)

### Step 2: AI-Assisted Review

```bash
python ai_reviewer.py [optional: case_id]
```

**Output:**
- Updates `proposed_fixes/{case_id}.json` with AI review
- Each review includes:
  - `is_correct`: Is the app correct?
  - `confidence`: 0-100% confidence
  - `detected_problem`: What went wrong
  - `correct_domain`: Recommended domain
  - `correct_category`: Recommended category
  - `suggested_fix_type`: Type of fix needed
  - `suggested_fix`: Specific recommendation
  - `reasoning`: Explanation

**Example:**
```bash
# Review all failures
python ai_reviewer.py

# Review specific case
python ai_reviewer.py battery_001

# View pending fixes
python apply_approved_fixes.py --status
```

### Step 3: Manual Approval

```bash
# Review each proposed_fixes/{case_id}.json
# If you approve the fix, move it to approved/
mv proposed_fixes/battery_001.json proposed_fixes/approved/battery_001.json
```

**OR use the status command:**
```bash
python apply_approved_fixes.py --status
```

### Step 4: Apply Approved Fixes

```bash
python apply_approved_fixes.py
```

**Safety Features:**
- ✅ Validates all fixes before applying
- ✅ Creates backup: `registry_backups/category_registry_YYYYMMDD_HHMMSS.py`
- ✅ Logs all changes: `eval_results/apply_fixes_log_*.json`
- ❌ NEVER modifies production without explicit approval
- ❌ NEVER auto-applies any fixes

### Step 5: Verify & Commit

```bash
# Review changes
git diff category_registry.py

# Commit
git add -A
git commit -m "Fix: Applied approved evaluation fixes"
git push
```

## Success Criteria

### Pass Thresholds

| Metric | Target | Current |
|--------|--------|---------|
| Overall Pass Rate | ≥95% | ? |
| Critical Failures | 0 | ? |
| Domain Detection | 100% | ? |
| Category Match | 100% | ? |
| Section Validation | 100% | ? |
| No Forbidden Terms | 100% | ? |

### Quality Gates

- ✅ 100/100 domain matches
- ✅ 100/100 category matches
- ✅ 0 preset contamination (wrong sections present)
- ✅ All required sections present
- ✅ No forbidden terms in output

## Configuration

### Environment Variables

```bash
# Required for AI reviewer
export ANTHROPIC_API_KEY="sk-..."
```

### Test Case Severity Levels

- **Critical**: Essential functionality (batteries, heavy metals, etc.)
- **High**: Important features (phosphate recovery, roof waterproofing)
- **Medium**: Standard features (fabric cleaning, thermal insulation)
- **Low**: Edge cases or experimental domains

## Troubleshooting

### Eval runner fails
```bash
# Check imports
python -c "from category_registry import detect_prompt_domain"

# Run single test
python -c "
from eval_runner import evaluate_single_case
case = {'id': 'battery_001', 'request': '...', ...}
result = evaluate_single_case(case)
print(result)
"
```

### AI reviewer can't connect
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Test import
python -c "import anthropic; print('OK')"

# Install if needed
pip install anthropic
```

### Fixes won't apply
```bash
# Validate fix structure
python -c "
import json
with open('proposed_fixes/case_id.json') as f:
    data = json.load(f)
print(json.dumps(data, indent=2))
"

# Check backup
ls -la registry_backups/
```

## Metrics & Reporting

### eval_report.json

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_cases": 100,
  "passed": 98,
  "failed": 2,
  "pass_rate": 98.0,
  "results": [
    {
      "id": "battery_001",
      "passed": true,
      "detected_domain": "battery_electrode",
      "selected_category": "sodium_ion_battery_anode_composite",
      ...
    }
  ]
}
```

### eval_summary.md

```markdown
# MaterialGenesis Golden Set Evaluation Report

**Timestamp:** 2024-01-15 10:30:00

## Summary
- **Total Cases:** 100
- **Passed:** 98
- **Failed:** 2
- **Pass Rate:** 98.0%

## Failures by Severity
- **Critical:** 0
- **High:** 2
- **Medium:** 0
- **Low:** 0

## Failed Cases
### battery_001 (Severity: high)
- Expected Domain: battery_electrode
- Detected Domain: battery_electrode (100%)
- ...
```

## Best Practices

### ✅ Do

1. **Review all AI recommendations** before approving fixes
2. **Keep test cases updated** as domain knowledge evolves
3. **Backup registry** before applying fixes (auto-done)
4. **Run evaluation before deployment** to catch regressions
5. **Log all changes** for audit trail
6. **Test fixes locally** before production deployment

### ❌ Don't

1. **Never auto-apply fixes** - require human approval always
2. **Don't modify registry directly** - use the approval workflow
3. **Don't trust AI 100%** - human review is mandatory
4. **Don't skip backups** - they're created automatically
5. **Don't commit unapproved fixes** - only merge after review

## Integration with CI/CD

```yaml
# Example GitHub Actions workflow
name: Evaluation & Fixes
on: [push]

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      
      - name: Run evaluation
        run: python eval_runner.py
      
      - name: AI review failures
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python ai_reviewer.py
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: eval-results
          path: eval_results/
      
      - name: Check pass rate
        run: |
          PASS_RATE=$(jq '.pass_rate' eval_results/eval_report.json)
          if (( $(echo "$PASS_RATE < 95" | bc -l) )); then
            echo "⚠️  Pass rate below 95%: $PASS_RATE%"
            exit 1
          fi
```

## Support & Maintenance

### Regular Maintenance

- **Weekly**: Run evaluation suite
- **Monthly**: Review and approve pending fixes
- **Quarterly**: Update test cases with new material domains
- **As Needed**: Address critical failures immediately

### Escalation

- **Critical**: Block deployment, fix immediately
- **High**: Fix before next release cycle
- **Medium**: Address in planned maintenance
- **Low**: Backlog for future improvement

## References

- [MaterialGenesis Category Registry](category_registry.py)
- [Golden Test Cases](test_cases/material_category_golden_set.json)
- [Evaluation Results](eval_results/)
- [Proposed Fixes](proposed_fixes/)

---

**System Status:** ✅ Ready for deployment

**Last Updated:** 2024-01-15
