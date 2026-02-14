"""Seed script to populate RSS sources across 12 industry categories."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import async_session
from app.models.rss_source import RSSSource
from sqlalchemy import select

SOURCES = [
    # Finance
    {"url": "https://feeds.reuters.com/reuters/businessNews", "name": "Reuters Business", "category": "finance"},
    {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg Markets", "category": "finance"},
    {"url": "https://www.cnbc.com/id/10001147/device/rss/rss.html", "name": "CNBC Finance", "category": "finance"},
    {"url": "https://feeds.ft.com/rss/home/us", "name": "Financial Times", "category": "finance"},
    {"url": "https://seekingalpha.com/feed.xml", "name": "Seeking Alpha", "category": "finance"},

    # Technology
    {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "category": "technology"},
    {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "category": "technology"},
    {"url": "https://feeds.arstechnica.com/arstechnica/index", "name": "Ars Technica", "category": "technology"},
    {"url": "https://www.wired.com/feed/rss", "name": "Wired", "category": "technology"},
    {"url": "https://news.ycombinator.com/rss", "name": "Hacker News", "category": "technology"},
    {"url": "https://feeds.feedburner.com/venturebeat/SZYF", "name": "VentureBeat", "category": "technology"},

    # Commercial Space
    {"url": "https://spacenews.com/feed/", "name": "SpaceNews", "category": "commercial_space"},
    {"url": "https://www.nasaspaceflight.com/feed/", "name": "NASASpaceFlight", "category": "commercial_space"},
    {"url": "https://www.space.com/feeds/all", "name": "Space.com", "category": "commercial_space"},
    {"url": "https://spacepolicyonline.com/feed/", "name": "Space Policy Online", "category": "commercial_space"},

    # New Energy
    {"url": "https://cleantechnica.com/feed/", "name": "CleanTechnica", "category": "new_energy"},
    {"url": "https://www.greentechmedia.com/feed", "name": "GreenTech Media", "category": "new_energy"},
    {"url": "https://electrek.co/feed/", "name": "Electrek", "category": "new_energy"},
    {"url": "https://reneweconomy.com.au/feed/", "name": "RenewEconomy", "category": "new_energy"},
    {"url": "https://www.utilitydive.com/feeds/news/", "name": "Utility Dive", "category": "new_energy"},

    # Healthcare
    {"url": "https://www.fiercebiotech.com/rss/xml", "name": "Fierce Biotech", "category": "healthcare"},
    {"url": "https://www.statnews.com/feed/", "name": "STAT News", "category": "healthcare"},
    {"url": "https://www.biopharmadive.com/feeds/news/", "name": "BioPharma Dive", "category": "healthcare"},
    {"url": "https://medcitynews.com/feed/", "name": "MedCity News", "category": "healthcare"},
    {"url": "https://www.healthcaredive.com/feeds/news/", "name": "Healthcare Dive", "category": "healthcare"},

    # Agriculture
    {"url": "https://www.agfundernews.com/feed", "name": "AgFunder News", "category": "agriculture"},
    {"url": "https://www.agriculture.com/rss/all", "name": "Agriculture.com", "category": "agriculture"},
    {"url": "https://www.fooddive.com/feeds/news/", "name": "Food Dive", "category": "agriculture"},

    # Consumer
    {"url": "https://www.retaildive.com/feeds/news/", "name": "Retail Dive", "category": "consumer"},
    {"url": "https://www.modernretail.co/feed/", "name": "Modern Retail", "category": "consumer"},
    {"url": "https://techcrunch.com/tag/e-commerce/feed/", "name": "TechCrunch E-Commerce", "category": "consumer"},
    {"url": "https://www.eater.com/rss/index.xml", "name": "Eater", "category": "consumer"},

    # Real Estate
    {"url": "https://therealdeal.com/feed/", "name": "The Real Deal", "category": "real_estate"},
    {"url": "https://www.bisnow.com/national/news/rss/", "name": "Bisnow", "category": "real_estate"},
    {"url": "https://www.globest.com/feed/", "name": "GlobeSt", "category": "real_estate"},

    # Manufacturing
    {"url": "https://www.therobotreport.com/feed/", "name": "The Robot Report", "category": "manufacturing"},
    {"url": "https://www.automationworld.com/rss.xml", "name": "Automation World", "category": "manufacturing"},
    {"url": "https://3dprintingindustry.com/feed/", "name": "3D Printing Industry", "category": "manufacturing"},
    {"url": "https://www.supplychaindive.com/feeds/news/", "name": "Supply Chain Dive", "category": "manufacturing"},

    # Crypto
    {"url": "https://cointelegraph.com/rss", "name": "CoinTelegraph", "category": "crypto"},
    {"url": "https://www.theblock.co/rss.xml", "name": "The Block", "category": "crypto"},
    {"url": "https://decrypt.co/feed", "name": "Decrypt", "category": "crypto"},
    {"url": "https://bitcoinmagazine.com/.rss/full/", "name": "Bitcoin Magazine", "category": "crypto"},
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "name": "CoinDesk", "category": "crypto"},

    # Macro Economy
    {"url": "https://feeds.reuters.com/reuters/economicNews", "name": "Reuters Economy", "category": "macro_economy"},
    {"url": "https://www.economist.com/finance-and-economics/rss.xml", "name": "The Economist", "category": "macro_economy"},
    {"url": "https://www.imf.org/en/News/RSS", "name": "IMF News", "category": "macro_economy"},
    {"url": "https://www.federalreserve.gov/feeds/press_all.xml", "name": "Federal Reserve", "category": "macro_economy"},

    # Regulation
    {"url": "https://www.reginfo.gov/public/do/XMLViewFileAction?f=Agenda_202310.xml", "name": "RegInfo", "category": "regulation"},
    {"url": "https://www.lawfaremedia.org/feed", "name": "Lawfare", "category": "regulation"},
    {"url": "https://techpolicy.press/feed/", "name": "Tech Policy Press", "category": "regulation"},
]


async def seed():
    async with async_session() as db:
        async with db.begin():
            existing = await db.execute(select(RSSSource.url))
            existing_urls = set(existing.scalars().all())

            added = 0
            for src in SOURCES:
                if src["url"] not in existing_urls:
                    db.add(RSSSource(**src))
                    added += 1

            print(f"Seeded {added} new sources ({len(SOURCES)} total, {len(existing_urls)} already existed)")


if __name__ == "__main__":
    asyncio.run(seed())
