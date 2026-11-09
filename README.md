# brief-gate

> **The deterministic quality gate for AI marketing output. Evaluates generated ad copy, landing pages, emails, or blog posts against briefs using rule-based constraint and policy checks — returning Pass / Fix / Block with line-level findings.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Rule-Based Evals](https://img.shields.io/badge/Evals-Deterministic%20QA-purple.svg)](https://github.com/darhaiderimam/brief-gate)

---

## The Problem: Generation is Solved. Verification is Not.

Every marketing skill generates copy. Very few systems verify whether the output adhered to constraints:
- Did the copy violate Meta §4.6 personal attribute rules (*"Are you tired of being overweight?"*) which trigger ad account bans?
- Did it miss mandatory regulatory disclosures (FDA supplement disclaimers, FTC endorsements)?
- Did it exceed character or word count limits?
- Did it contain brand-forbidden words or unsupported medical claims?

**`brief-gate` provides the verification layer that runs after any text generator.**
Instead of relying on fuzzy, non-deterministic LLM prompting to grade LLM output, `brief-gate` executes deterministic regex patterns, keyword sets, word count boundaries, and policy heuristics. Code computes every number deterministically.

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

### 1. Install from Source
```bash
git clone https://github.com/darhaiderimam/brief-gate.git
cd brief-gate
pip install .
```

### 2. Run Evaluation
```bash
brief-gate evaluate --brief examples/sample_brief.json --asset examples/sample_asset.md
```
*(Or run directly without installation: `python -m brief_gate.cli evaluate --brief examples/sample_brief.json --asset examples/sample_asset.md`)*

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

## How It Plugs into Marketing Workflows

`brief-gate` works alongside any copywriting skill or script to enforce a pre-publication quality gate:

```bash
# Example inside Claude Code or Cursor:
claude "Run @creative-brief to generate ad copy, then pipe the markdown output into brief-gate"
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
MIT © [Imam Haider (@darhaiderimam)](https://github.com/darhaiderimam)
