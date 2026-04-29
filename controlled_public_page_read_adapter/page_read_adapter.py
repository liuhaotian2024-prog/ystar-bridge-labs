#!/usr/bin/env python3
"""Controlled public page-read adapter for L6.11.

Fixture mode is deterministic and local-only. The stdlib HTTP adapter is GET-only
and remains behind explicit configuration and safety preflight.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from controlled_search_backend_adapters.controlled_search_backends import (
    ControlledBackendConfig,
    SearchBudgetEnvelope,
)


FORBIDDEN_SCHEMES = {"file", "ftp", "data", "chrome", "extension"}
FORBIDDEN_HOSTS = {"localhost", "127.0.0.1", "::1", "0.0.0.0"}
STOP_INDICATORS = {
    "login": ["login", "sign in", "password"],
    "payment": ["payment", "checkout", "credit card", "subscribe to continue"],
    "form": ["<form", "submit"],
    "private_sensitive": ["social security", "private account", "inbox"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def source_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def reject_private_or_internal_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return "unsupported_or_forbidden_scheme"
    if parsed.scheme in FORBIDDEN_SCHEMES:
        return "forbidden_scheme"
    host = (parsed.hostname or "").lower()
    if not host:
        return "missing_hostname"
    if host in FORBIDDEN_HOSTS or host.endswith(".local"):
        return "private_or_internal_host"
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return None
    if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
        return "private_or_internal_ip"
    return None


class TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self.in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        clean = " ".join(data.split())
        if not clean:
            return
        if self.in_title:
            self.title_parts.append(clean)
        self.text_parts.append(clean)

    @property
    def title(self) -> str | None:
        return " ".join(self.title_parts) or None

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)


def extract_text_and_title(raw: str) -> tuple[str | None, str]:
    parser = TitleParser()
    parser.feed(raw)
    text = html.unescape(parser.text)
    return parser.title, text


def extract_claim_candidates(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    candidates = []
    for sentence in sentences:
        trimmed = sentence.strip()
        if 40 <= len(trimmed) <= 240:
            candidates.append(trimmed)
        if len(candidates) >= 3:
            break
    return candidates


def stop_reason_from_text(raw: str) -> str | None:
    lower = raw.lower()
    for reason, indicators in STOP_INDICATORS.items():
        if any(indicator in lower for indicator in indicators):
            return f"stop_on_{reason}_indicator"
    return None


@dataclass(frozen=True)
class PageReadEnvelope:
    page_read_id: str
    url: str
    final_url: str | None
    source_domain: str | None
    http_status: int | None
    content_type: str | None
    bytes_read: int
    title_if_available: str | None
    text_excerpt: str
    extracted_claim_candidates: list[str]
    safety_flags: dict[str, Any]
    stop_reason_if_any: str | None
    evidence_eligible: bool
    read_at_utc: str
    adapter_name: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ControlledPageReadAdapter:
    adapter_name = "base"

    def read_pages(
        self,
        urls: list[str],
        config: ControlledBackendConfig,
        budget: SearchBudgetEnvelope,
    ) -> list[PageReadEnvelope]:
        raise NotImplementedError


class DisabledPageReadAdapter(ControlledPageReadAdapter):
    adapter_name = "disabled"

    def read_pages(
        self,
        urls: list[str],
        config: ControlledBackendConfig,
        budget: SearchBudgetEnvelope,
    ) -> list[PageReadEnvelope]:
        return [
            PageReadEnvelope(
                page_read_id="disabled_page_read_001",
                url=url,
                final_url=None,
                source_domain=None,
                http_status=None,
                content_type=None,
                bytes_read=0,
                title_if_available=None,
                text_excerpt="",
                extracted_claim_candidates=[],
                safety_flags={"read_only": True, "network_used": False},
                stop_reason_if_any="controlled_public_page_read_adapter_not_configured",
                evidence_eligible=False,
                read_at_utc=utc_now(),
                adapter_name=self.adapter_name,
            )
            for url in urls[:1]
        ]


class FixturePageReadAdapter(ControlledPageReadAdapter):
    adapter_name = "fixture"

    def read_pages(
        self,
        urls: list[str],
        config: ControlledBackendConfig,
        budget: SearchBudgetEnvelope,
    ) -> list[PageReadEnvelope]:
        fixture_path = Path(config.fixture_pages_path or "")
        fixture_pages = {
            item["url"]: item for item in json.loads(fixture_path.read_text(encoding="utf-8")).get("pages", [])
        }
        envelopes: list[PageReadEnvelope] = []
        domain_counts: dict[str, int] = {}
        for url in urls:
            if len(envelopes) >= budget.max_pages_opened:
                break
            domain = source_domain(url)
            if len(domain_counts) >= budget.max_domains and domain not in domain_counts:
                continue
            if domain_counts.get(domain, 0) >= budget.max_pages_per_domain:
                continue
            page = fixture_pages.get(url)
            if not page:
                continue
            text = str(page.get("text", ""))
            excerpt = text[:500]
            envelopes.append(
                PageReadEnvelope(
                    page_read_id=str(page.get("page_read_id", f"fixture_page_{len(envelopes) + 1:03d}")),
                    url=url,
                    final_url=url,
                    source_domain=domain,
                    http_status=200,
                    content_type="text/html; charset=utf-8",
                    bytes_read=len(text.encode("utf-8")),
                    title_if_available=str(page.get("title", "")),
                    text_excerpt=excerpt,
                    extracted_claim_candidates=list(page.get("claim_candidates", []))[:3]
                    or extract_claim_candidates(text),
                    safety_flags={
                        "fixture_demo": True,
                        "read_only": True,
                        "network_used": False,
                        "no_login": True,
                        "no_payment": True,
                        "no_form_submission": True,
                    },
                    stop_reason_if_any=None,
                    evidence_eligible=True,
                    read_at_utc=utc_now(),
                    adapter_name=self.adapter_name,
                )
            )
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        return envelopes


class StdlibPublicHttpPageReadAdapter(ControlledPageReadAdapter):
    adapter_name = "stdlib_public_http"

    def read_pages(
        self,
        urls: list[str],
        config: ControlledBackendConfig,
        budget: SearchBudgetEnvelope,
    ) -> list[PageReadEnvelope]:
        if not config.page_read_network_allowed:
            return []
        envelopes: list[PageReadEnvelope] = []
        domain_counts: dict[str, int] = {}
        max_bytes = 200_000
        for url in urls:
            if len(envelopes) >= budget.max_pages_opened:
                break
            rejection = reject_private_or_internal_url(url)
            if rejection:
                envelopes.append(
                    PageReadEnvelope(
                        page_read_id=f"blocked_page_read_{len(envelopes) + 1:03d}",
                        url=url,
                        final_url=None,
                        source_domain=source_domain(url),
                        http_status=None,
                        content_type=None,
                        bytes_read=0,
                        title_if_available=None,
                        text_excerpt="",
                        extracted_claim_candidates=[],
                        safety_flags={"rejected": True, "reason": rejection},
                        stop_reason_if_any=rejection,
                        evidence_eligible=False,
                        read_at_utc=utc_now(),
                        adapter_name=self.adapter_name,
                    )
                )
                continue
            domain = source_domain(url)
            if len(domain_counts) >= budget.max_domains and domain not in domain_counts:
                continue
            if domain_counts.get(domain, 0) >= budget.max_pages_per_domain:
                continue
            request = Request(url, method="GET", headers={"User-Agent": "ystar-controlled-readonly/0"})
            with urlopen(request, timeout=5) as response:  # nosec B310 - guarded explicit opt-in path
                raw_bytes = response.read(max_bytes + 1)
                clipped = raw_bytes[:max_bytes]
                raw_text = clipped.decode("utf-8", errors="replace")
                title, text = extract_text_and_title(raw_text)
                stop_reason = stop_reason_from_text(raw_text)
                envelopes.append(
                    PageReadEnvelope(
                        page_read_id=f"stdlib_page_read_{len(envelopes) + 1:03d}",
                        url=url,
                        final_url=response.geturl(),
                        source_domain=domain,
                        http_status=getattr(response, "status", None),
                        content_type=response.headers.get("content-type"),
                        bytes_read=len(clipped),
                        title_if_available=title,
                        text_excerpt=text[:500],
                        extracted_claim_candidates=extract_claim_candidates(text),
                        safety_flags={"read_only": True, "network_used": True, "method": "GET"},
                        stop_reason_if_any=stop_reason,
                        evidence_eligible=stop_reason is None and bool(text.strip()),
                        read_at_utc=utc_now(),
                        adapter_name=self.adapter_name,
                    )
                )
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        return envelopes


class ControlledPageReadAdapterRegistry:
    def __init__(self, config: ControlledBackendConfig):
        self.config = config

    def adapter(self) -> ControlledPageReadAdapter:
        if self.config.page_read_backend_mode == "fixture":
            return FixturePageReadAdapter()
        if self.config.page_read_backend_mode == "stdlib_public_http":
            return StdlibPublicHttpPageReadAdapter()
        return DisabledPageReadAdapter()

    def read_pages(self, urls: list[str], budget_payload: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        budget = SearchBudgetEnvelope.from_mapping(budget_payload)
        return [
            envelope.to_dict()
            for envelope in self.adapter().read_pages(urls, self.config, budget)
        ]


__all__ = [
    "ControlledPageReadAdapterRegistry",
    "DisabledPageReadAdapter",
    "FixturePageReadAdapter",
    "PageReadEnvelope",
    "StdlibPublicHttpPageReadAdapter",
    "reject_private_or_internal_url",
]
