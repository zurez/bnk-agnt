import re
import unicodedata

BLOCKED_PATTERNS = [
    # Financial crimes
    r'\b(money\s*launder|launder\s*money)\b',
    r'\b(tax\s*evasion|evade\s*tax)\b',
    r'\b(fraud|scam|ponzi)\b',
    r'\b(illegal\s*transfer|transfer\s*illegal)\b',
    r'\b(hide\s*money|conceal\s*funds)\b',
    
    # System command injection attempts
    r'[\;\|\&]\s*(rm|del|format|shutdown|reboot|kill|wget|curl)\b',
    r'\$\((.*?)\)',  # Command substitution
    r'`[^`]*`',  # Backtick command execution
    r'\b(eval|exec|system|shell_exec|passthru|popen)\s*\(',
    r'<\s*script[^>]*>',  # Script injection
    
    # Jailbreak attempts
    r'\b(ignore\s*(previous|all|above|prior)\s*(instruction|prompt|rule|direction)s?)\b',
    r'\b(disregard|forget|override)\s*(previous|all|your)\s*(instruction|prompt|rule)s?\b',
    r'\bact\s*as\s*(if|though|like)?\s*(you|your)\s*(are|have)\s*(no|without)\s*(restriction|limit|rule)s?\b',
    r'\b(pretend|imagine)\s*(you|your)\s*(are|have|can)\s*(not|no)\s*(constraint|limitation|filter)s?\b',
    r'\bnow\s*(you|your)\s*(are|can|should)\s*(free|unrestricted|unfiltered)\b',
    r'\brole\s*play\s*(as|mode|without)\b',
    r'\bDAN\s*(mode|prompt)?\b',  # Do Anything Now jailbreak
    r'\bdev\s*mode\b',
    r'\bgrandma\s*(exploit|trick)\b',
    
    # Prompt injection
    r'</?(system|instruction|prompt|context|rule)>',
    r'\[SYSTEM\]|\[INST\]|\[/INST\]',
    r'---\s*(end|ignore|new)\s*(instruction|prompt|context)s?\s*---',
    r'\bstart\s*new\s*(instruction|prompt|session)\b',
    
    # Unauthorized actions
    r'\b(execute|run)\s*(code|script|command|program|binary)\b',
    r'\b(download|fetch|retrieve)\s*(and\s*)?(execute|run|install)\b',
    r'\bos\.(system|exec|popen|spawn)',
    r'\bsubprocess\.(call|run|Popen)',
    r'\b__import__\s*\(',
    r'\bimport\s*(os|sys|subprocess|socket|requests)\b',
    
    # Data exfiltration attempts
    r'\b(extract|exfiltrate|leak|steal)\s*(data|information|credential)s?\b',
    r'\bsend\s*(to|data|credential)s?\s*(external|outside|attacker)\b',
    
    # Privilege escalation
    r'\b(sudo|su|admin|root|privilege)\s*(access|mode|rights?)\b',
    r'\belevate\s*privilege',
]

# Additional context-aware checks
SUSPICIOUS_PATTERNS = [
    # Multiple encoding attempts
    r'(base64|hex|url|unicode)\s*(encode|decode)',
    # Obfuscation techniques
    r'[A-Za-z0-9+/]{50,}={0,2}',  # Long base64-like strings
    # Excessive special characters (potential obfuscation)
    r'[^a-zA-Z0-9\s]{20,}',
]

def validate_query(query: str) -> bool:
  """_summary_

    valifates query and returns a bool

    """
    query_normalized = unicodedata.normalize('NFKC', query)
    query_lower = query_normalized.lower()
    
    
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return False
           
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, query_normalized, re.IGNORECASE):
            return False

    if len(query_normalized) > 10000:
        return False
    

    if re.search(r'(.{10,})\1{10,}', query_normalized):
        return False
    
    return True