# brief-gate

> **The deterministic quality gate for AI marketing output. Checks any generated ad copy, landing page, email, or blog post against the brief — returning Pass / Fix / Block with line-level findings.**

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Evals for Marketing](https://img.shields.io/badge/Evals-Marketing%20QA-purple.svg)](https://github.com/darimamhaider/brief-gate)

---

## The Problem: Generation is Solved. Verification is Not.

Every open-source marketing skill generates copy. Nobody checks whether the output actually followed the brief:
- Did the AI use a forbidden claim that gets your Meta ad account banned?
- Did it miss the mandatory FDA or FTC disclaimer?
- Did it blow past the 90-character Google Ads headline limit?
- Did it commit a Meta §4.6 personal attribute violation (*"Are you tired of being overweight?"*)?

**`brief-gate` is the verification layer that plugs in after every AI marketing generator.**
The LLM provides evidence; the Python code computes every number deterministically.

```
[Prompt] -> [Claude / GPT Generator] -> [Asset] -> [ brief-gate ] -> [ PASS / FIX / BLOCK ]
                                                          |
                                           +--------------+--------------+
                                           | Line-level rule findings    |
                                           | Ad policy violation checks  |
                                           | Deterministic scoring (0-100)|
                                           +-----------------------------+
```

---

## 30-Second Quickstart

### 1. Install
```bash
pip install brief-gate
```
*(Or clone and run locally: `python -m brief_gate.cli`)*

### 2. Run Evaluation
```bash
brief-gate evaluate --brief examples/sample_brief.json --asset examples/sample_asset.md
```

### 3. Real Output
```markdown
# brief-gate Quality Audit Report
**Verdict:** `PASS` | **Deterministic Quality Score:** `100/100`

> **GATE PASSED:** Asset adheres to brief constraints, legal requirements, and brand guardrails.

## Rule Findings Summary
| Status | Rule | Message | Line | Penalty |
| :--- | :--- | :--- | :--- | :--- |
| PASS | `word_count` | Word count (84) satisfies required bounds (20 - 120). | - | 0 |
| PASS | `forbidden_terms` | No prohibited words or claims detected. | - | 0 |
| PASS | `mandatory_keywords` | All 4 required keywords are present. | - | 0 |
| PASS | `required_disclaimers` | All required legal/regulatory disclaimers found. | - | 0 |
```

If a forbidden claim or personal attribute is detected:
```markdown
# brief-gate Quality Audit Report
**Verdict:** `BLOCK` | **Deterministic Quality Score:** `45/100`

> **GATE BLOCKED:** Critical compliance or constraint failure detected. Do NOT publish to ad accounts.

## Line-Level Code Violations
- **Line 4:** `Are you embarrassed by your thinning hair?`
  *Resolution:* Direct personal attribute question violates Meta Advertising Standards §4.6.
```

---

## How It Plugs into Existing Marketing Stacks

`brief-gate` does not compete with Corey Haines' `marketingskills` or Daniel Agrici's `claude-blog` — **it audits them**.

```bash
# Example inside Claude Code or Cursor:
claude "Run @copywriting to write Meta ad copy, then pipe the output through brief-gate"
```

---

## Schema: Brief JSON Specification

```json
{
  "brief_title": "Summer Campaign Ad Set",
  "brand": "Apex Labs",
  "min_words": 25,
  "max_words": 100,
  "mandatory_keywords": ["electrolyte", "Apex", "runners"],
  "forbidden_words": ["miracle", "cure", "cheap", "instant fix"],
  "mandatory_disclaimers": ["*These statements have not been evaluated by the FDA"]
}
```

---

## CLI Options

| Flag | Description |
| :--- | :--- |
| `--brief, -b` | Path to the brief JSON specification file. |
| `--asset, -a` | Path to the generated markdown or text asset file. |
| `--json` | Output machine-readable JSON for CI/CD integration. |
| `--version` | Print current package version. |

---

## Exit Codes (For CI/CD Pipelines)
- `0`: **PASS** (Score $\ge$ 85, zero critical violations)
- `1`: **FIX** (Score 60-84, minor constraint warnings)
- `2`: **BLOCK** (Score < 60 or critical compliance breach)

---

## License
MIT © [Haider (@darimamhaider)](https://github.com/darimamhaider)
