"""
Internal data structures for scan results.

These classes are NEVER serialized directly to API responses.
The trust_score module reads them and produces safe TrustReport objects.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class HTTPSCheckResult:
    available: bool = False
    redirects_from_http: bool = False
    hsts_present: bool = False
    error: str | None = None


@dataclass
class SSLCheckResult:
    valid: bool = False
    expiry_warning: bool = False  # True if cert expires in < 30 days
    # We intentionally store NO other cert fields (issuer, CN, serial, SANs)
    error: str | None = None


@dataclass
class HeadersCheckResult:
    csp_present: bool = False
    x_frame_options_present: bool = False
    x_content_type_options_present: bool = False
    referrer_policy_present: bool = False
    permissions_policy_present: bool = False
    error: str | None = None

    @property
    def score(self) -> int:
        return sum([
            self.csp_present,
            self.x_frame_options_present,
            self.x_content_type_options_present,
            self.referrer_policy_present,
            self.permissions_policy_present,
        ])

    MAX_SCORE: int = 5


@dataclass
class DNSCheckResult:
    resolves: bool = False
    error: str | None = None


ReputationStatus = Literal["clean", "suspicious", "unknown"]


@dataclass
class ReputationCheckResult:
    status: ReputationStatus = "unknown"
    error: str | None = None


@dataclass
class ScanData:
    """Full internal scan data. Never returned directly from the API."""
    domain: str = ""
    https: HTTPSCheckResult = field(default_factory=HTTPSCheckResult)
    ssl: SSLCheckResult = field(default_factory=SSLCheckResult)
    headers: HeadersCheckResult = field(default_factory=HeadersCheckResult)
    dns: DNSCheckResult = field(default_factory=DNSCheckResult)
    reputation: ReputationCheckResult = field(default_factory=ReputationCheckResult)
