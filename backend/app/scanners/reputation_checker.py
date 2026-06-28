"""
Reputation checker.

Provider selection is controlled by the REPUTATION_PROVIDER environment variable
(default: "mock"). A startup warning is emitted when the mock provider is active
so it is visible in production logs if accidentally deployed without a real provider.

To integrate a real provider, add a new async function and wire it to the
REPUTATION_PROVIDER value below. The interface (check_reputation) stays unchanged.
"""

import logging

from app.core.config import settings
from app.scanners.result import ReputationCheckResult

logger = logging.getLogger(__name__)

if settings.reputation_provider == "mock":
    logger.warning(
        "REPUTATION_PROVIDER=mock — all domains except test entries return 'clean'. "
        "Set REPUTATION_PROVIDER to a real provider before public launch."
    )

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
    if settings.reputation_provider != "mock":
        logger.error(
            "Unknown REPUTATION_PROVIDER=%r — falling back to mock",
            settings.reputation_provider,
        )
    domain_lower = domain.lower()
    if domain_lower in _MOCK_SUSPICIOUS:
        return ReputationCheckResult(status="suspicious")
    return ReputationCheckResult(status="clean")
