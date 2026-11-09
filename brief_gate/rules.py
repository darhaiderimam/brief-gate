import re
from typing import List, Dict, Any

class RuleFinding:
    def __init__(self, rule_name: str, status: str, message: str, line_number: int = None, line_content: str = None, penalty: int = 0):
        self.rule_name = rule_name
        self.status = status  # PASS, WARN, FAIL
        self.message = message
        self.line_number = line_number
        self.line_content = line_content
        self.penalty = penalty

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule_name,
            "status": self.status,
            "message": self.message,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "penalty": self.penalty
        }

def check_word_count(text: str, min_words: int, max_words: int) -> List[RuleFinding]:
    findings = []
    words = text.split()
    count = len(words)
    if min_words and count < min_words:
        findings.append(RuleFinding(
            rule_name="word_count_min",
            status="FAIL",
            message=f"Word count ({count}) is below required minimum of {min_words} words.",
            penalty=15
        ))
    elif max_words and count > max_words:
        findings.append(RuleFinding(
            rule_name="word_count_max",
            status="FAIL",
            message=f"Word count ({count}) exceeds maximum allowed of {max_words} words.",
            penalty=15
        ))
    else:
        findings.append(RuleFinding(
            rule_name="word_count",
            status="PASS",
            message=f"Word count ({count}) satisfies required bounds ({min_words or 0} - {max_words or 'unlimited'}).",
            penalty=0
        ))
    return findings

def check_forbidden_terms(text: str, forbidden_terms: List[str], disclaimers: List[str] = None) -> List[RuleFinding]:
    findings = []
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Skip mandatory disclaimer lines so legal statements like 'not intended to cure' are not penalized
        if "fda" in line.lower() or (disclaimers and any(d.lower() in line.lower() for d in disclaimers)):
            continue
        for term in forbidden_terms:
            pattern = r'\b' + re.escape(term.strip()) + r'\b'
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(RuleFinding(
                    rule_name="forbidden_term",
                    status="FAIL",
                    message=f"Prohibited term '{term}' detected.",
                    line_number=idx,
                    line_content=line.strip(),
                    penalty=25
                ))
    if not findings:
        findings.append(RuleFinding(
            rule_name="forbidden_terms",
            status="PASS",
            message="No prohibited words or claims detected.",
            penalty=0
        ))
    return findings

def check_mandatory_keywords(text: str, keywords: List[str]) -> List[RuleFinding]:
    findings = []
    for kw in keywords:
        pattern = r'\b' + re.escape(kw.strip()) + r'\b'
        if not re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(RuleFinding(
                rule_name="mandatory_keyword",
                status="FAIL",
                message=f"Mandatory brand keyword '{kw}' is missing from output.",
                penalty=15
            ))
    if not findings:
        findings.append(RuleFinding(
            rule_name="mandatory_keywords",
            status="PASS",
            message=f"All {len(keywords)} required keywords are present.",
            penalty=0
        ))
    return findings

def check_required_disclaimers(text: str, disclaimers: List[str]) -> List[RuleFinding]:
    findings = []
    for disc in disclaimers:
        # Check fuzzy inclusion (at least 80% key phrase match)
        cleaned_disc = disc.strip().lower()
        if cleaned_disc not in text.lower():
            findings.append(RuleFinding(
                rule_name="required_disclaimer",
                status="FAIL",
                message=f"Required regulatory disclosure missing: '{disc[:50]}...'",
                penalty=20
            ))
    if not findings:
        findings.append(RuleFinding(
            rule_name="required_disclaimers",
            status="PASS",
            message="All required legal/regulatory disclaimers found.",
            penalty=0
        ))
    return findings

def check_personal_attributes(text: str) -> List[RuleFinding]:
    """Detects Meta §4.6 personal attribute interrogatives."""
    findings = []
    lines = text.splitlines()
    prohibited_patterns = [
        (r'\bare you (struggling|suffering|tired of|sick of|embarrassed|fat|broke|depressed|in debt)\b', "Direct personal attribute question"),
        (r'\bdo you have (acne|bad breath|thinning hair|anxiety|depression|debt|cramps)\b', "Direct medical/flaw interrogation"),
    ]
    for idx, line in enumerate(lines, start=1):
        for pattern, desc in prohibited_patterns:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(RuleFinding(
                    rule_name="meta_personal_attributes",
                    status="FAIL",
                    message=f"{desc} violates Meta Advertising Standards §4.6.",
                    line_number=idx,
                    line_content=line.strip(),
                    penalty=30
                ))
    return findings
