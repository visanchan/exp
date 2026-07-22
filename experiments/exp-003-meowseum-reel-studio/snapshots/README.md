# Source snapshots

Frozen HTML from `themeowseum.pages.dev`, fetched **2026-07-22**.

Decision D3: the source agent reads these files, not the live site. Extraction
logic stays real; tests do not break when the live site is edited. The trade is
that a site redesign silently invalidates the fixtures — re-fetch and re-run the
tests to detect that.

| File | URL |
|---|---|
| `collection.html` | `/collection/` |
| `journal.html` | `/journal/` |
| `product-01-cat-the-curator.html` | `/products/01-cat-the-curator/` |
| `product-04-the-colosseum.html` | `/products/04-the-colosseum/` |
| `product-09-mona-lisa.html` | `/products/09-mona-lisa/` |
| `journal-02-the-story-behind-the-parthenon.html` | `/journal/02-the-story-behind-the-parthenon/` |
| `journal-05-why-cats-ignore-new-furniture.html` | `/journal/05-why-cats-ignore-new-furniture/` |

Re-fetch:

```bash
curl -sS -o snapshots/product-09-mona-lisa.html \
  https://themeowseum.pages.dev/products/09-mona-lisa/
```

These pages are public marketing pages. They carry a "prices/specs pending owner
confirmation" notice, which is why every extracted record starts with
`verified_for_marketing = false`.
