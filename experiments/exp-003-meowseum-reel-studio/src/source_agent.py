"""Meowseum source agent.

Turns one page of themeowseum.pages.dev into a structured source record.

Two rules are enforced structurally rather than by prompting, because a prompt
is a request and a data structure is a guarantee:

1.  Host allowlist. A URL that is not on ALLOWED_HOST never reaches a loader.
2.  Transactional quarantine. Price, stock, shipping, weight and dimensions are
    parsed into a separate ``transactional`` block. ``story_context()`` drops
    that block, so the downstream story agents are never shown a number they
    could narrate. See criterion C3 in the experiment README.

Standard library only.
"""

from __future__ import annotations

import html as html_module
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOST = "themeowseum.pages.dev"
SNAPSHOT_DIR = Path(__file__).resolve().parent.parent / "snapshots"

#: Marker the site puts on pages whose commercial data is not owner-confirmed.
PREVIEW_MARKER = "pending owner confirmation"


class SourceError(Exception):
    """Raised when a page cannot be accepted or parsed."""


# ---------------------------------------------------------------------------
# host + loading
# ---------------------------------------------------------------------------


def verify_host(url: str) -> str:
    """Return the URL path, or raise if the URL is not a Meowseum page.

    Checked before any read, so an off-site URL cannot cause a fetch.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SourceError(f"unsupported scheme: {parsed.scheme!r}")
    if parsed.hostname != ALLOWED_HOST:
        raise SourceError(
            f"refused: {parsed.hostname!r} is not {ALLOWED_HOST!r}"
        )
    return parsed.path


def snapshot_path(url: str, snapshot_dir: Path | None = None) -> Path:
    """Map a Meowseum URL onto its committed snapshot file."""
    path = verify_host(url).strip("/")
    directory = snapshot_dir or SNAPSHOT_DIR
    parts = path.split("/")
    if len(parts) == 2 and parts[0] in ("products", "journal"):
        prefix = "product" if parts[0] == "products" else "journal"
        return directory / f"{prefix}-{parts[1]}.html"
    if len(parts) == 1 and parts[0] in ("collection", "journal"):
        return directory / f"{parts[0]}.html"
    raise SourceError(f"no snapshot mapping for path: /{path}/")


def load_html(url: str, snapshot_dir: Path | None = None) -> str:
    """Read the committed snapshot for a URL.

    Deliberately offline (decision D3): extraction logic stays real, while the
    tests do not break when the live site is edited.
    """
    target = snapshot_path(url, snapshot_dir)
    if not target.exists():
        raise SourceError(
            f"no snapshot for {url} — expected {target.name} in snapshots/"
        )
    return target.read_text(encoding="utf-8")


def detect_type(url: str) -> str:
    """Return 'product' or 'journal' from the URL shape."""
    path = verify_host(url)
    if path.startswith("/products/"):
        return "product"
    if path.startswith("/journal/") and path.strip("/") != "journal":
        return "journal"
    raise SourceError(f"not a source page: {path}")


# ---------------------------------------------------------------------------
# html helpers
# ---------------------------------------------------------------------------

_TAG = re.compile(r"<[^>]+>")
_DROP = re.compile(r"<(script|style|svg)\b.*?</\1>", re.S | re.I)


def strip_tags(fragment: str) -> str:
    """Plain text from an HTML fragment, entities resolved, spaces collapsed."""
    text = _DROP.sub(" ", fragment)
    text = _TAG.sub(" ", text)
    text = html_module.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def main_section(page: str) -> str:
    match = re.search(r"<main\b.*?</main>", page, re.S | re.I)
    if not match:
        raise SourceError("page has no <main> element")
    return _DROP.sub(" ", match.group(0))


def bilingual(fragment: str) -> dict[str, str]:
    """Pull the en/th pair out of a fragment.

    The site marks translations two ways: ``lang="en" data-bi`` spans for prose,
    and ``class="lang-only-en"`` spans for UI labels. Both are read.
    """
    out: dict[str, str] = {}
    for lang in ("en", "th"):
        spans = re.findall(
            rf'<span[^>]*lang="{lang}"[^>]*data-bi[^>]*>(.*?)</span>',
            fragment,
            re.S,
        )
        if not spans:
            spans = re.findall(
                rf'<span[^>]*class="lang-only-{lang}"[^>]*>(.*?)</span>',
                fragment,
                re.S,
            )
        text = " ".join(strip_tags(s) for s in spans).strip()
        if text:
            out[lang] = re.sub(r"\s+", " ", text)
    return out


# ---------------------------------------------------------------------------
# records
# ---------------------------------------------------------------------------


@dataclass
class SourceRecord:
    """One extracted page.

    ``transactional`` is the quarantine. Nothing in it reaches a story agent
    unless ``verified_for_marketing`` is True.
    """

    source_type: str
    source_url: str
    title: str = ""
    thai_title: str = ""
    summary: dict[str, str] = field(default_factory=dict)
    images: list[str] = field(default_factory=list)
    fields: dict[str, object] = field(default_factory=dict)
    transactional: dict[str, object] = field(default_factory=dict)
    verified_for_marketing: bool = False

    def story_context(self) -> dict[str, object]:
        """The only view the story agents are allowed to see.

        Drops the transactional block entirely while it is unverified, and
        lists the field names that survived so a shot's ``source_basis`` can
        be checked against something concrete.
        """
        context = {
            "source_type": self.source_type,
            "source_url": self.source_url,
            "title": self.title,
            "thai_title": self.thai_title,
            "summary": self.summary,
            "fields": dict(self.fields),
        }
        if self.verified_for_marketing:
            context["transactional"] = dict(self.transactional)
        context["allowed_basis"] = allowed_basis(context)
        return context

    def to_json(self, **kwargs) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, **kwargs)


def allowed_basis(context: dict[str, object]) -> list[str]:
    """Every field name a shot may legitimately cite as ``source_basis``."""
    names = ["title", "thai_title", "summary"]
    names += [f"fields.{key}" for key in sorted(context.get("fields", {}))]
    if "transactional" in context:
        names += [
            f"transactional.{key}"
            for key in sorted(context["transactional"])  # type: ignore[index]
        ]
    return names


# ---------------------------------------------------------------------------
# product extraction
# ---------------------------------------------------------------------------

#: Spec labels the site renders in its <dl>, and where each one belongs.
#: Dimensions and weight are commercial claims, so they are quarantined.
_SPEC_ROUTING = {
    "Material": ("fields", "material"),
    "Care": ("fields", "care"),
    "Dimensions": ("transactional", "dimensions"),
    "Weight": ("transactional", "weight"),
}


def extract_product(page: str, url: str) -> SourceRecord:
    body = main_section(page)
    record = SourceRecord(source_type="product", source_url=url)

    heading = re.search(r"<h1\b.*?</h1>", body, re.S)
    if not heading:
        raise SourceError("product page has no <h1>")
    names = bilingual(heading.group(0))
    record.title = names.get("en", "")
    record.thai_title = names.get("th", "")
    if not record.title:
        raise SourceError("could not read product title")

    # Room + catalogue number sit in the eyebrow line above the heading.
    eyebrow = body[: heading.start()]
    room = bilingual(eyebrow[eyebrow.rfind("<p") :]) if "<p" in eyebrow else {}
    if room:
        record.fields["room"] = room
    number = re.search(r">\s*(No\.\d+)\s*<", eyebrow)
    if number:
        record.fields["product_number"] = number.group(1)

    # Only the gallery images. A bare <img> sweep also catches the "more from
    # this room" carousel, which shows a different piece entirely.
    gallery = re.findall(
        r'<img[^>]*\bdata-gallery-(?:main-img|thumb)[^>]*>'
        r'|<img[^>]*\bdata-gallery-lightbox-img[^>]*>',
        body,
    )
    for tag in gallery:
        src = re.search(r'\bsrc="([^"]+)"', tag)
        if not src:
            continue
        value = src.group(1)
        record.images.append(
            f"https://{ALLOWED_HOST}{value}" if value.startswith("/") else value
        )
    record.images = list(dict.fromkeys(record.images))[:3]

    # Short description: the first data-bi paragraph after the price block.
    for para in re.findall(r"<p\b[^>]*>.*?</p>", body, re.S):
        text = bilingual(para)
        if text.get("en") and "max-w-prose" in para and "pending owner" not in para:
            record.summary = text
            break

    for block in re.findall(r"<div>\s*<dt\b.*?</dd>\s*</div>", body, re.S):
        label_match = re.search(
            r'<span class="lang-only-en">(.*?)</span>', block, re.S
        )
        if not label_match:
            continue
        label = strip_tags(label_match.group(1))
        route = _SPEC_ROUTING.get(label)
        if not route:
            continue
        value_match = re.search(r"<dd\b[^>]*>(.*?)</dd>", block, re.S)
        if not value_match:
            continue
        raw = value_match.group(1)
        value: object = bilingual(raw) or strip_tags(raw)
        target, key = route
        getattr(record, target)[key] = value

    label_match = re.search(
        r"museum label\s*</p>(.*?)</div>", body, re.S | re.I
    )
    if label_match:
        museum = bilingual(label_match.group(1))
        if museum:
            record.fields["museum_label"] = museum

    price = re.search(r"฿\s*([\d,]+)", body)
    if price:
        record.transactional["price_thb"] = price.group(1).replace(",", "")
    stock = re.search(r'>\s*In stock\s*<', body)
    record.transactional["in_stock"] = bool(stock)
    if "Free shipping within Thailand" in body:
        record.transactional["shipping"] = "Free shipping within Thailand"

    record.verified_for_marketing = PREVIEW_MARKER not in body
    return record


# ---------------------------------------------------------------------------
# journal extraction
# ---------------------------------------------------------------------------


def extract_journal(page: str, url: str) -> SourceRecord:
    body = main_section(page)
    record = SourceRecord(source_type="journal", source_url=url)

    heading = re.search(r"<h1\b.*?</h1>", body, re.S)
    if not heading:
        raise SourceError("journal page has no <h1>")
    names = bilingual(heading.group(0))
    record.title = names.get("en", "")
    record.thai_title = names.get("th", "")
    if not record.title:
        raise SourceError("could not read article title")

    published = re.search(r'<time datetime="([^"]+)"', body)
    if published:
        record.fields["published"] = published.group(1)

    eyebrow = re.search(r"<p\b[^>]*tracking-eyebrow.*?</p>", body, re.S)
    if eyebrow:
        tags = [
            strip_tags(s)
            for s in re.findall(r"<span\b[^>]*>(.*?)</span>", eyebrow.group(0), re.S)
        ]
        tags = [t for t in tags if t]
        if tags:
            record.fields["tags"] = tags
            record.fields["category"] = tags[0]

    lede = re.search(r"</h1>\s*<p\b.*?</p>", body, re.S)
    if lede:
        record.summary = bilingual(lede.group(0))

    for src in re.findall(r'<img[^>]*\bsrc="([^"]+)"', body):
        if src.startswith("/"):
            record.images.append(f"https://{ALLOWED_HOST}{src}")
    record.images = list(dict.fromkeys(record.images))[:3]

    article = re.search(r'<div class="article[^"]*".*?</article>', body, re.S)
    if article:
        sections = []
        chunks = re.split(r"<h2\b[^>]*>", article.group(0))
        for chunk in chunks[1:]:
            head, _, rest = chunk.partition("</h2>")
            paragraphs = [
                strip_tags(p)
                for p in re.findall(r"<(?:p|li)\b[^>]*>(.*?)</(?:p|li)>", rest, re.S)
            ]
            sections.append(
                {
                    "heading": strip_tags(head),
                    "points": [p for p in paragraphs if p][:6],
                }
            )
        if sections:
            record.fields["sections"] = sections

    # An article carries no price or stock, so nothing is quarantined and its
    # prose is safe to narrate as written.
    record.verified_for_marketing = PREVIEW_MARKER not in body
    return record


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def extract(url: str, snapshot_dir: Path | None = None) -> SourceRecord:
    """Host-check, load, detect and extract one Meowseum page."""
    kind = detect_type(url)
    page = load_html(url, snapshot_dir)
    if kind == "product":
        return extract_product(page, url)
    return extract_journal(page, url)


def list_snapshots(snapshot_dir: Path | None = None) -> list[str]:
    """URLs that currently have a committed snapshot."""
    directory = snapshot_dir or SNAPSHOT_DIR
    urls = []
    for path in sorted(directory.glob("*.html")):
        if path.stem.startswith("product-"):
            urls.append(f"https://{ALLOWED_HOST}/products/{path.stem[8:]}/")
        elif path.stem.startswith("journal-"):
            urls.append(f"https://{ALLOWED_HOST}/journal/{path.stem[8:]}/")
    return urls


if __name__ == "__main__":
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    targets = sys.argv[1:] or list_snapshots()
    for target in targets:
        print(extract(target).to_json())
