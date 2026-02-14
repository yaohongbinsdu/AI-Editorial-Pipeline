"""T076: Unit tests for content scraper service."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.content_scraper import ContentScraper, ScrapedContent


class TestContentScraper:
    """Tests for ContentScraper class."""

    def test_class_exists(self):
        scraper = ContentScraper()
        assert hasattr(scraper, "scrape_article")
        assert hasattr(scraper, "scrape_with_firecrawl")
        assert hasattr(scraper, "scrape_with_iframely")
        assert hasattr(scraper, "scrape_with_gemini")

    @pytest.mark.asyncio
    async def test_select_best_content_prefers_longest(self):
        """_select_best_content should pick the longest content."""
        short = ScrapedContent(content="Short", source="firecrawl")
        long = ScrapedContent(content="This is much longer content from gemini", source="gemini")

        result = ContentScraper._select_best_content(long, short)
        assert result == long.content

    @pytest.mark.asyncio
    async def test_scrape_article_handles_failures(self):
        """If one scraper fails, others should still provide results."""
        scraper = ContentScraper()

        with patch.object(scraper, "scrape_with_firecrawl", new_callable=AsyncMock) as fc, \
             patch.object(scraper, "scrape_with_iframely", new_callable=AsyncMock) as ifr, \
             patch.object(scraper, "scrape_with_gemini", new_callable=AsyncMock) as gem:

            fc.side_effect = Exception("Firecrawl down")
            ifr.return_value = ScrapedContent(title="IFR Title", content="IFR content", source="iframely")
            gem.return_value = ScrapedContent(title="Gem Title", content="Gem content text", source="gemini")

            result = await scraper.scrape_article("https://example.com/test")
            assert result is not None
            assert result.get("final_title") or result.get("final_content")
