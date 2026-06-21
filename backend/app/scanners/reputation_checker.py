"""
Reputation checker — Mock provider (Phase 4).

In production (Phase 5+), this will call Google Safe Browsing or similar.
The mock returns "clean" for all domains except a small test blocklist.
"""

from app.scanners.result import ReputationCheckResult

# Hardcoded test domains for demo/development only.
# A real implementation queries an external reputation API.
_MOCK_SUSPICIOUS: frozenset[str] = frozenset(
    {
        "phishing-test.example.com",
        "malware-test.example.com",
        "suspicious-demo.invalid",
    }
)


async def check_reputation(domain: str) -> ReputationCheckResult:
    domain_lower = domain.lower()
    if domain_lower in _MOCK_SUSPICIOUS:
        return ReputationCheckResult(status="suspicious")
    return ReputationCheckResult(status="clean")
