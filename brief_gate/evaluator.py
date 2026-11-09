import json
from typing import Dict, Any, List
from .rules import (
    RuleFinding,
    check_word_count,
    check_forbidden_terms,
    check_mandatory_keywords,
    check_required_disclaimers,
    check_personal_attributes
)

class EvaluationResult:
    def __init__(self, score: int, verdict: str, findings: List[RuleFinding], brief_meta: Dict[str, Any]):
        self.score = max(0, min(100, score))
        self.verdict = verdict  # PASS, FIX, BLOCK
        self.findings = findings
        self.brief_meta = brief_meta

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "verdict": self.verdict,
            "brief": self.brief_meta,
            "total_findings": len(self.findings),
            "critical_violations": sum(1 for f in self.findings if f.status == "FAIL"),
            "findings": [f.to_dict() for f in self.findings]
        }

    def render_markdown(self) -> str:
        md = []
        md.append(f"# brief-gate Quality Audit Report")
        md.append(f"**Verdict:** `{self.verdict}` | **Deterministic Quality Score:** `{self.score}/100`\n")
        
        if self.verdict == "PASS":
            md.append("> **GATE PASSED:** Asset adheres to brief constraints, legal requirements, and brand guardrails.\n")
        elif self.verdict == "FIX":
            md.append("> **ACTION REQUIRED (FIX):** Asset has minor constraint violations or missing disclosures that must be resolved before flight.\n")
        else:
            md.append("> **GATE BLOCKED:** Critical compliance or constraint failure detected. Do NOT publish to ad accounts.\n")

        md.append("## Rule Findings Summary")
        md.append("| Status | Rule | Message | Line | Penalty |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for f in self.findings:
            line_str = str(f.line_number) if f.line_number else "-"
            penalty_str = f"-{f.penalty}" if f.penalty > 0 else "0"
            status_icon = "PASS" if f.status == "PASS" else ("WARN" if f.status == "WARN" else "FAIL")
            md.append(f"| {status_icon} | `{f.rule_name}` | {f.message} | {line_str} | {penalty_str} |")
        
        failures = [f for f in self.findings if f.status == "FAIL" and f.line_number]
        if failures:
            md.append("\n## Line-Level Code Violations")
            for fail in failures:
                md.append(f"- **Line {fail.line_number}:** `{fail.line_content}`")
                md.append(f"  *Resolution:* {fail.message}")

        return "\n".join(md)

def evaluate_asset(brief_data: Dict[str, Any], asset_content: str) -> EvaluationResult:
    findings: List[RuleFinding] = []
    current_score = 100

    # 1. Word count constraint
    min_words = brief_data.get("min_words", 0)
    max_words = brief_data.get("max_words", 0)
    if min_words or max_words:
        f_wc = check_word_count(asset_content, min_words, max_words)
        findings.extend(f_wc)

    # 2. Forbidden words
    forbidden = brief_data.get("forbidden_words", [])
    disclaimers = brief_data.get("mandatory_disclaimers", [])
    if forbidden:
        f_fb = check_forbidden_terms(asset_content, forbidden, disclaimers)
        findings.extend(f_fb)

    # 3. Mandatory brand keywords
    keywords = brief_data.get("mandatory_keywords", [])
    if keywords:
        f_kw = check_mandatory_keywords(asset_content, keywords)
        findings.extend(f_kw)

    # 4. Mandatory disclaimers
    if disclaimers:
        f_disc = check_required_disclaimers(asset_content, disclaimers)
        findings.extend(f_disc)

    # 5. Ad Policy checks (Personal attributes)
    f_pa = check_personal_attributes(asset_content)
    findings.extend(f_pa)

    # Deduct penalties
    total_penalty = sum(f.penalty for f in findings)
    final_score = max(0, 100 - total_penalty)

    # Determine verdict
    has_critical_failure = any(f.penalty >= 25 for f in findings)
    if final_score >= 85 and not has_critical_failure:
        verdict = "PASS"
    elif final_score >= 60 and not has_critical_failure:
        verdict = "FIX"
    else:
        verdict = "BLOCK"

    return EvaluationResult(
        score=final_score,
        verdict=verdict,
        findings=findings,
        brief_meta={
            "brief_title": brief_data.get("brief_title", "Marketing Brief"),
            "brand": brief_data.get("brand", "Client Brand")
        }
    )
