"""Seed authoritative RSS sources across all categories."""
import httpx
import sys

API = "http://localhost:8001/api/v1"

SOURCES = [
    # ── Finance ──────────────────────────────────
    {"url": "https://feeds.bbci.co.uk/news/business/rss.xml", "name": "BBC Business", "category": "finance"},
    {"url": "https://www.ft.com/rss/home", "name": "Financial Times", "category": "finance"},
    {"url": "https://feeds.reuters.com/reuters/businessNews", "name": "Reuters Business", "category": "finance"},
    {"url": "https://feeds.bloomberg.com/markets/news.rss", "name": "Bloomberg Markets", "category": "finance"},
    {"url": "https://feeds.a]wsj.com/wsj/xml/rss/3_7085.xml", "name": "Wall Street Journal", "category": "finance"},
    {"url": "https://www.cnbc.com/id/10001147/device/rss/rss.html", "name": "CNBC Finance", "category": "finance"},
    {"url": "https://feeds.marketwatch.com/marketwatch/topstories", "name": "MarketWatch", "category": "finance"},

    # ── Technology ───────────────────────────────
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "name": "NYT Technology", "category": "technology"},
    {"url": "https://feeds.arstechnica.com/arstechnica/technology-lab", "name": "Ars Technica", "category": "technology"},
    {"url": "https://www.theverge.com/rss/index.xml", "name": "The Verge", "category": "technology"},
    {"url": "https://www.wired.com/feed/rss", "name": "Wired", "category": "technology"},
    {"url": "https://techcrunch.com/feed/", "name": "TechCrunch", "category": "technology"},
    {"url": "https://feeds.feedburner.com/TheHackersNews", "name": "The Hacker News", "category": "technology"},
    {"url": "https://www.technologyreview.com/feed/", "name": "MIT Technology Review", "category": "technology"},
    {"url": "https://9to5mac.com/feed/", "name": "9to5Mac", "category": "technology"},
    {"url": "https://www.zdnet.com/news/rss.xml", "name": "ZDNet", "category": "technology"},

    # ── Commercial Space ─────────────────────────
    {"url": "https://spacenews.com/feed/", "name": "SpaceNews", "category": "commercial_space"},
    {"url": "https://www.space.com/feeds/all", "name": "Space.com", "category": "commercial_space"},
    {"url": "https://www.nasaspaceflight.com/feed/", "name": "NASASpaceFlight", "category": "commercial_space"},

    # ── New Energy ───────────────────────────────
    {"url": "https://cleantechnica.com/feed/", "name": "CleanTechnica", "category": "new_energy"},
    {"url": "https://reneweconomy.com.au/feed/", "name": "RenewEconomy", "category": "new_energy"},
    {"url": "https://electrek.co/feed/", "name": "Electrek", "category": "new_energy"},
    {"url": "https://www.greentechmedia.com/feed", "name": "GreenTech Media", "category": "new_energy"},

    # ── Healthcare ───────────────────────────────
    {"url": "https://www.statnews.com/feed/", "name": "STAT News", "category": "healthcare"},
    {"url": "https://www.fiercebiotech.com/rss/xml", "name": "FierceBiotech", "category": "healthcare"},
    {"url": "https://www.healthcareitnews.com/feed", "name": "Healthcare IT News", "category": "healthcare"},
    {"url": "https://medicalxpress.com/rss-feed/", "name": "Medical Xpress", "category": "healthcare"},

    # ── Agriculture ──────────────────────────────
    {"url": "https://www.agweb.com/rss/news", "name": "AgWeb", "category": "agriculture"},
    {"url": "https://www.feedstuffs.com/rss.xml", "name": "Feedstuffs", "category": "agriculture"},

    # ── Consumer ─────────────────────────────────
    {"url": "https://www.retaildive.com/feeds/news/", "name": "Retail Dive", "category": "consumer"},
    {"url": "https://www.fooddive.com/feeds/news/", "name": "Food Dive", "category": "consumer"},

    # ── Real Estate ──────────────────────────────
    {"url": "https://www.housingwire.com/feed/", "name": "HousingWire", "category": "real_estate"},
    {"url": "https://therealdeal.com/feed/", "name": "The Real Deal", "category": "real_estate"},

    # ── Manufacturing ────────────────────────────
    {"url": "https://www.industryweek.com/rss", "name": "IndustryWeek", "category": "manufacturing"},
    {"url": "https://www.manufacturingdive.com/feeds/news/", "name": "Manufacturing Dive", "category": "manufacturing"},

    # ── Crypto ───────────────────────────────────
    {"url": "https://cointelegraph.com/rss", "name": "CoinTelegraph", "category": "crypto"},
    {"url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "name": "CoinDesk", "category": "crypto"},
    {"url": "https://decrypt.co/feed", "name": "Decrypt", "category": "crypto"},
    {"url": "https://thedefiant.io/feed", "name": "The Defiant", "category": "crypto"},

    # ── Macro Economy ────────────────────────────
    {"url": "https://feeds.reuters.com/reuters/economicNews", "name": "Reuters Economy", "category": "macro_economy"},
    {"url": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml", "name": "NYT Economy", "category": "macro_economy"},
    {"url": "https://www.economist.com/finance-and-economics/rss.xml", "name": "The Economist", "category": "macro_economy"},
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "name": "BBC World News", "category": "macro_economy"},

    # ── Regulation ───────────────────────────────
    {"url": "https://www.sec.gov/news/pressreleases.rss", "name": "SEC Press Releases", "category": "regulation"},
    {"url": "https://www.federalreserve.gov/feeds/press_all.xml", "name": "Federal Reserve", "category": "regulation"},
    {"url": "https://www.reginfo.gov/public/do/PRAXML?xmlFile=202301.xml", "name": "RegInfo.gov", "category": "regulation"},
]


def main():
    added = 0
    skipped = 0
    failed = 0

    with httpx.Client(timeout=10) as client:
        for s in SOURCES:
            try:
                r = client.post(f"{API}/sources", json=s)
                if r.status_code == 201:
                    added += 1
                    print(f"  + {s['name']} ({s['category']})")
                elif r.status_code == 409:
                    skipped += 1
                    print(f"  ~ {s['name']} (already exists)")
                else:
                    failed += 1
                    print(f"  ! {s['name']} -> {r.status_code}: {r.text[:100]}")
            except Exception as e:
                failed += 1
                print(f"  ! {s['name']} -> ERROR: {e}")

    print(f"\nDone: {added} added, {skipped} skipped, {failed} failed")

    # Verify total
    r = httpx.get(f"{API}/sources")
    total = len(r.json())
    print(f"Total sources in DB: {total}")


if __name__ == "__main__":
    main()
