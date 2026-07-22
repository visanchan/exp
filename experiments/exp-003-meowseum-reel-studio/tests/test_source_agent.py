"""Tests for the Meowseum source agent.

Run from the experiment folder:

    python -m unittest discover -s tests -t .
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import source_agent as sa  # noqa: E402

MONA = "https://themeowseum.pages.dev/products/09-mona-lisa/"
CURATOR = "https://themeowseum.pages.dev/products/01-cat-the-curator/"
FURNITURE = (
    "https://themeowseum.pages.dev/journal/05-why-cats-ignore-new-furniture/"
)


class TestHostGuard(unittest.TestCase):
    """Case 3 — an off-site URL is refused before anything is read."""

    def test_foreign_host_refused(self):
        for url in (
            "https://example.com/products/09-mona-lisa/",
            "https://themeowseum.pages.dev.evil.test/products/09-mona-lisa/",
            "https://evil.test/?x=themeowseum.pages.dev",
        ):
            with self.subTest(url=url):
                with self.assertRaises(sa.SourceError):
                    sa.verify_host(url)

    def test_non_http_scheme_refused(self):
        with self.assertRaises(sa.SourceError):
            sa.verify_host("file:///C:/Windows/win.ini")

    def test_guard_runs_before_any_read(self):
        """extract() must raise on the host, not on a missing snapshot."""
        with self.assertRaises(sa.SourceError) as caught:
            sa.extract("https://example.com/products/09-mona-lisa/")
        self.assertIn("not", str(caught.exception))
        self.assertNotIn("snapshot", str(caught.exception))

    def test_meowseum_host_accepted(self):
        self.assertEqual(sa.verify_host(MONA), "/products/09-mona-lisa/")


class TestProductExtraction(unittest.TestCase):
    """Case 1 — a product page yields a usable structured record."""

    @classmethod
    def setUpClass(cls):
        cls.record = sa.extract(MONA)

    def test_type_and_titles(self):
        self.assertEqual(self.record.source_type, "product")
        self.assertEqual(self.record.title, "Mona Lisa")
        self.assertEqual(self.record.thai_title, "โมนาลิซา")

    def test_bilingual_summary(self):
        self.assertIn("Da Vinci", self.record.summary["en"])
        self.assertTrue(self.record.summary["th"])

    def test_image_is_this_piece_only(self):
        """The related-pieces carousel must not leak into images."""
        self.assertTrue(self.record.images)
        self.assertIn("09-mona-lisa", self.record.images[0])
        for url in self.record.images:
            self.assertNotIn("venus", url.lower())
            self.assertNotIn("starry-night", url.lower())

    def test_story_fields_present(self):
        self.assertEqual(self.record.fields["room"]["en"], "Masterpieces")
        self.assertEqual(self.record.fields["product_number"], "No.013")
        self.assertIn("corrugated", self.record.fields["material"]["en"])
        self.assertIn("smile", self.record.fields["museum_label"]["en"])

    def test_other_product_extracts_too(self):
        other = sa.extract(CURATOR)
        self.assertEqual(other.title, "Cat the Curator")
        self.assertTrue(other.thai_title)
        self.assertTrue(other.images)


class TestJournalExtraction(unittest.TestCase):
    """Case 2 — a journal article yields sections and practical points."""

    @classmethod
    def setUpClass(cls):
        cls.record = sa.extract(FURNITURE)

    def test_type_and_titles(self):
        self.assertEqual(self.record.source_type, "journal")
        self.assertIn("ignores new furniture", self.record.title)
        self.assertTrue(self.record.thai_title)

    def test_category_and_date(self):
        self.assertEqual(self.record.fields["category"], "cat behavior")
        self.assertEqual(self.record.fields["published"], "2026-07-02")

    def test_sections_have_headings_and_points(self):
        sections = self.record.fields["sections"]
        self.assertGreaterEqual(len(sections), 3)
        for section in sections:
            self.assertTrue(section["heading"])
            self.assertTrue(section["points"])


class TestTransactionalQuarantine(unittest.TestCase):
    """Case 4 — C3. Commercial claims cannot reach a story agent."""

    @classmethod
    def setUpClass(cls):
        cls.record = sa.extract(MONA)

    def test_preview_page_is_not_verified_for_marketing(self):
        self.assertFalse(self.record.verified_for_marketing)

    def test_commercial_values_are_quarantined_not_dropped(self):
        """The data is still extracted — it is withheld, not lost."""
        self.assertEqual(self.record.transactional["price_thb"], "890")
        self.assertTrue(self.record.transactional["in_stock"])
        self.assertIn("cm", self.record.transactional["dimensions"])

    def test_story_context_hides_the_whole_block(self):
        context = self.record.story_context()
        self.assertNotIn("transactional", context)

    def test_no_price_survives_anywhere_in_story_context(self):
        """The adversarial check: serialize everything, hunt for the number."""
        import json

        blob = json.dumps(self.record.story_context(), ensure_ascii=False)
        for forbidden in ("890", "฿", "In stock", "700 g", "Free shipping"):
            self.assertNotIn(forbidden, blob)

    def test_allowed_basis_excludes_transactional_fields(self):
        basis = self.record.story_context()["allowed_basis"]
        self.assertIn("fields.museum_label", basis)
        self.assertIn("title", basis)
        self.assertFalse([b for b in basis if b.startswith("transactional.")])

    def test_verified_flag_unlocks_the_block(self):
        """When the owner confirms, the same record exposes the numbers."""
        self.record.verified_for_marketing = True
        try:
            context = self.record.story_context()
            self.assertEqual(context["transactional"]["price_thb"], "890")
            self.assertIn("transactional.price_thb", context["allowed_basis"])
        finally:
            self.record.verified_for_marketing = False


if __name__ == "__main__":
    unittest.main(verbosity=2)
