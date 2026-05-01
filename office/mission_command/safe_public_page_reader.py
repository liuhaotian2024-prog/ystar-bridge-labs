from __future__ import annotations

from dataclasses import asdict, dataclass
from html.parser import HTMLParser
import html
import ipaddress
import re
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from .tier1_public_research import utc_now


STOP_INDICATORS = {
    "login": ["password required", "sign in to continue", "log in to continue", "authentication required"],
    "payment": ["checkout", "credit card", "enter payment", "subscribe to continue", "paywall"],
    "form": ["request access", "complete the captcha", "contact form", "submit payment"],
    "publication": ["publish this", "post now"],
}


@dataclass(frozen=True)
class PublicPageReadResult:
    url: str
    domain: str
    status: int | None
    retrieved_at: str
    title: str
    text_excerpt: str
    safety_errors: List[str]
    blocked_reason: str
    bytes_read: int
    external_action_executed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class _TextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_title = False
        self.title_parts: List[str] = []
        self.text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs):  # type: ignore[no-untyped-def]
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
    def title(self) -> str:
        return " ".join(self.title_parts)

    @property
    def text(self) -> str:
        return html.unescape(" ".join(self.text_parts))


def reject_unsafe_public_url(url: str) -> List[str]:
    parsed = urlparse(url)
    errors: List[str] = []
    if parsed.scheme not in {"http", "https"}:
        errors.append("non_http_scheme")
    if not parsed.hostname:
        errors.append("missing_hostname")
        return errors
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "::1", "0.0.0.0"} or host.endswith(".local"):
        errors.append("private_or_local_url")
    try:
        address = ipaddress.ip_address(host)
        if address.is_private or address.is_loopback or address.is_link_local or address.is_reserved:
            errors.append("private_or_internal_ip")
    except ValueError:
        pass
    return errors


def stop_reason_from_text(text: str) -> str:
    lower = text.lower()
    for reason, indicators in STOP_INDICATORS.items():
        if any(indicator in lower for indicator in indicators):
            return f"blocked_{reason}_indicator"
    return ""


class SafePublicPageReader:
    provider_name = "bridge_labs_stdlib_get_only_page_reader"

    def __init__(self, max_bytes: int = 200_000, timeout_seconds: int = 5) -> None:
        self.max_bytes = max_bytes
        self.timeout_seconds = timeout_seconds

    def available(self) -> bool:
        return True

    def read(self, url: str) -> PublicPageReadResult:
        errors = reject_unsafe_public_url(url)
        domain = (urlparse(url).netloc or "").lower()
        if errors:
            return PublicPageReadResult(
                url=url,
                domain=domain,
                status=None,
                retrieved_at=utc_now(),
                title="",
                text_excerpt="",
                safety_errors=errors,
                blocked_reason=";".join(errors),
                bytes_read=0,
                external_action_executed=False,
            )
        request = Request(url, method="GET", headers={"User-Agent": "ystar-bridge-labs-readonly/0"})
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # nosec B310 - explicit read-only public GET path
                raw = response.read(self.max_bytes + 1)
                clipped = raw[: self.max_bytes]
                parser = _TextParser()
                parser.feed(clipped.decode("utf-8", errors="replace"))
                text = re.sub(r"\s+", " ", parser.text).strip()
                blocked = stop_reason_from_text(text)
                return PublicPageReadResult(
                    url=url,
                    domain=domain,
                    status=getattr(response, "status", None),
                    retrieved_at=utc_now(),
                    title=parser.title,
                    text_excerpt=text[:1000],
                    safety_errors=[],
                    blocked_reason=blocked,
                    bytes_read=len(clipped),
                    external_action_executed=False,
                )
        except HTTPError as exc:
            return PublicPageReadResult(
                url=url,
                domain=domain,
                status=exc.code,
                retrieved_at=utc_now(),
                title="",
                text_excerpt="",
                safety_errors=[],
                blocked_reason=f"http_error_{exc.code}",
                bytes_read=0,
                external_action_executed=False,
            )
        except (URLError, TimeoutError, OSError) as exc:
            return PublicPageReadResult(
                url=url,
                domain=domain,
                status=None,
                retrieved_at=utc_now(),
                title="",
                text_excerpt="",
                safety_errors=[],
                blocked_reason=type(exc).__name__,
                bytes_read=0,
                external_action_executed=False,
            )
