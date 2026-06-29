import feedparser
import requests
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=tr&gl=TR&ceid=TR:tr"


DIRECT_RSS_FEEDS = [
    ("TRT Spor", "https://www.trtspor.com.tr/rss/futbol.xml"),
    ("TRT Haber Spor", "https://www.trthaber.com/sondakika_articles.rss"),
    ("NTV Spor", "https://www.ntv.com.tr/spor.rss"),
    ("NTV", "https://www.ntv.com.tr/rss"),
    ("Fanatik", "https://www.fanatik.com.tr/rss/futbol"),
    ("Fotomac", "https://www.fotomac.com.tr/rss/anasayfa.xml"),
]


DIRECT_HTML_SOURCES = [
    ("TRT Spor", "https://www.trtspor.com.tr/haber/futbol/"),
    ("TRT Haber Spor", "https://www.trthaber.com/spor/"),
    ("NTV Spor", "https://www.ntv.com.tr/spor"),
    ("Fanatik", "https://www.fanatik.com.tr/futbol"),
    ("Fotomac", "https://www.fotomac.com.tr/futbol"),
    ("Sporx", "https://www.sporx.com/futbol/"),
    ("Ajansspor", "https://ajansspor.com/futbol"),
]


REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


DEFAULT_QUERIES = [
    "Beşiktaş futbol",
    "Galatasaray futbol",
    "Fenerbahçe futbol",
    "Trabzonspor futbol",
    "Süper Lig futbol",
    "A Milli Takım futbol",
    "Türkiye Dünya Kupası elemeleri futbol",
    "Dünya Kupası futbol",
    "Champions League football",
    "Premier League football",
    "La Liga football",
    "Serie A football",
    "Bundesliga football",
]


FOOTBALL_KEYWORDS = [
    "futbol",
    "süper lig",
    "transfer",
    "beşiktaş",
    "galatasaray",
    "fenerbahçe",
    "trabzonspor",
    "milli takım",
    "dünya kupası",
    "şampiyonlar ligi",
    "premier league",
    "la liga",
    "serie a",
    "bundesliga",
    "maç",
    "teknik direktör",
    "oyuncu",
    "gol",
    "kadro",
    "sakatlık",
]

FOOTBALL_KEYWORDS.extend(
    [
        "football",
        "süper lig",
        "super lig",
        "beşiktaş",
        "besiktas",
        "fenerbahçe",
        "fenerbahce",
        "milli takım",
        "dünya kupası",
        "dunya kupasi",
        "şampiyonlar ligi",
        "sampiyonlar ligi",
        "maç",
        "mac",
        "teknik direktör",
        "sakatlık",
    ]
)

NON_FOOTBALL_KEYWORDS = [
    "basketbol",
    "basketball",
    "voleybol",
    "volleyball",
    "tenis",
    "tennis",
    "formula 1",
    "f1",
    "motogp",
    "nba",
    "euroleague",
    "hentbol",
    "handball",
    "atletizm",
    "yüzme",
    "yuzme",
    "güreş",
    "gures",
    "boks",
    "boxing",
    "bisiklet",
    "cycling",
    "olimpiyat",
    "olympic",
]


def _guess_category(text: str) -> str:
    t = text.lower()

    if any(k in t for k in ["transfer", "bonservis", "imza", "anlaştı", "kiralık"]):
        return "Transfer"

    if any(k in t for k in ["sakat", "sakatlık", "tedavi", "ameliyat"]):
        return "Sakatlık"

    if any(k in t for k in ["milli takım", "a milli", "dünya kupası", "eleme"]):
        return "Milli Takım / Dünya Kupası"

    if any(k in t for k in ["teknik direktör", "hoca", "antrenör"]):
        return "Teknik Direktör"

    if any(k in t for k in ["maç", "derbi", "fikstür", "puan durumu"]):
        return "Maç Gündemi"

    return "Genel Futbol"


def _guess_entity(text: str) -> tuple[str, str]:
    t = text.lower()

    clubs = {
        "Beşiktaş": ["beşiktaş", "bjk"],
        "Galatasaray": ["galatasaray", "gs"],
        "Fenerbahçe": ["fenerbahçe", "fb"],
        "Trabzonspor": ["trabzonspor"],
    }

    for club, keys in clubs.items():
        if any(k in t for k in keys):
            return club, "club"

    if any(k in t for k in ["milli takım", "a milli", "türkiye", "dünya kupası elemeleri"]):
        return "Türkiye A Milli Takımı", "national_team"

    if any(k in t for k in ["dünya kupası", "world cup"]):
        return "Dünya Kupası", "tournament"

    if any(k in t for k in ["premier league", "la liga", "serie a", "bundesliga", "champions league"]):
        return "Avrupa Futbolu", "league"

    return "Genel Futbol", "general"


def _is_relevant(title: str, summary: str) -> bool:
    combined = f"{title} {summary}".lower()
    return any(keyword in combined for keyword in FOOTBALL_KEYWORDS)


def _is_non_football(title: str, summary: str) -> bool:
    combined = f"{title} {summary}".lower()
    return any(keyword in combined for keyword in NON_FOOTBALL_KEYWORDS)


def _clean_summary(summary: str) -> str:
    text = BeautifulSoup(summary or "", "html.parser").get_text(" ", strip=True)
    text = _fix_turkish_encoding(text)
    generic_fragments = [
        "Comprehensive up-to-date news coverage",
        "aggregated from sources all over the world",
        "Google News",
    ]
    if any(fragment.lower() in text.lower() for fragment in generic_fragments):
        return ""
    return " ".join(text.split())


def _fix_turkish_encoding(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "Ý": "İ",
        "ý": "ı",
        "Þ": "Ş",
        "þ": "ş",
        "Ð": "Ğ",
        "ð": "ğ",
        "Ä°": "İ",
        "Ä±": "ı",
        "Åž": "Ş",
        "ÅŸ": "ş",
        "ÄŸ": "ğ",
        "Äž": "Ğ",
        "Ã‡": "Ç",
        "Ã§": "ç",
        "Ã–": "Ö",
        "Ã¶": "ö",
        "Ãœ": "Ü",
        "Ã¼": "ü",
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "Â": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    word_replacements = {
        "M?LYON": "MİLYON",
        "M?LL?": "MİLLİ",
        "BE??KTA??": "BEŞİKTAŞ",
        "Be??ikta??": "Beşiktaş",
        "Fenerbah??e": "Fenerbahçe",
        "G??ndem": "Gündem",
        "sakatl??k": "sakatlık",
    }
    for bad, good in word_replacements.items():
        text = text.replace(bad, good)

    if any(char in text for char in ["Ã", "Ä", "Å"]):
        try:
            repaired = text.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
            if repaired and len(repaired) >= len(text) * 0.7:
                text = repaired
        except Exception:
            pass

    return text


def _parse_published_dt(value):
    if not value:
        return datetime.now()

    if isinstance(value, datetime):
        return value.replace(tzinfo=None)

    try:
        parsed = parsedate_to_datetime(str(value))
        return parsed.replace(tzinfo=None)
    except Exception:
        pass

    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d.%m.%Y %H:%M",
        "%d/%m/%Y %H:%M",
    ]
    for date_format in formats:
        try:
            return datetime.strptime(str(value)[:19], date_format)
        except Exception:
            continue

    return datetime.now()


def _format_published(value):
    parsed = _parse_published_dt(value)
    return parsed.strftime("%Y-%m-%d %H:%M"), parsed.timestamp()


def _parse_google_source(entry) -> str:
    source = getattr(entry, "source", None)
    if source and isinstance(source, dict):
        return source.get("title", "Google News")
    return "Google News"


def _append_news_item(results, seen_links, title, link, summary, source_name, published=None, force_relevant=False):
    title = _fix_turkish_encoding(title or "").strip()
    link = (link or "").strip()
    summary = _clean_summary(summary or "")
    source_name = _fix_turkish_encoding(source_name or "").strip()

    if not title or not link:
        return

    if len(title) < 18:
        return

    if link in seen_links:
        return

    if _is_non_football(title, summary):
        return

    if not force_relevant and not _is_relevant(title, summary):
        return

    seen_links.add(link)

    combined = f"{title} {summary}"
    category = _guess_category(combined)
    entity, entity_type = _guess_entity(combined)

    published_text, sort_ts = _format_published(published)

    results.append(
        {
            "title": title,
            "entity": entity,
            "type": entity_type,
            "category": category,
            "source": source_name,
            "published_at": published_text,
            "_sort_ts": sort_ts,
            "reliability_score": 72 if source_name != "Google News" else 65,
            "summary": summary[:500] if summary else title,
            "url": link,
        }
    )


def _append_entry(results, seen_links, entry, source_name):
    title = getattr(entry, "title", "").strip()
    link = getattr(entry, "link", "").strip()
    summary = _clean_summary(getattr(entry, "summary", "") or getattr(entry, "description", ""))

    published = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if not published and getattr(entry, "published_parsed", None):
        published = datetime(*entry.published_parsed[:6])
    if not published and getattr(entry, "updated_parsed", None):
        published = datetime(*entry.updated_parsed[:6])
    _append_news_item(results, seen_links, title, link, summary, source_name, published)


def _looks_like_article_url(url):
    lowered = (url or "").lower()
    blocked = [
        "javascript:",
        "mailto:",
        "#",
        "/canli",
        "/video",
        "/galeri",
        "/foto-galeri",
        "/yazar",
        "/puan-durumu",
        "/fikstur",
        "/takim/",
        "/kategori/",
    ]
    if any(item in lowered for item in blocked):
        return False

    article_markers = [
        "haber",
        "spor",
        "futbol",
        "super-lig",
        "transfer",
        "son-dakika",
        "-",
    ]
    return any(marker in lowered for marker in article_markers)


def _extract_link_title(link_tag):
    text = _fix_turkish_encoding(link_tag.get_text(" ", strip=True))
    if len(text) >= 24:
        return text

    for attr in ["title", "aria-label"]:
        value = _fix_turkish_encoding(link_tag.get(attr, "")).strip()
        if len(value) >= 24:
            return value

    image = link_tag.find("img")
    if image:
        for attr in ["alt", "title"]:
            value = _fix_turkish_encoding(image.get(attr, "")).strip()
            if len(value) >= 24:
                return value

    return text


def _collect_html_source(results, seen_links, source_name, source_url, max_items):
    response = requests.get(source_url, headers=REQUEST_HEADERS, timeout=12)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    added = 0
    force_relevant = "futbol" in source_url.lower()
    for link_tag in soup.find_all("a", href=True):
        if added >= max_items:
            break

        link = urljoin(source_url, link_tag["href"])
        if not _looks_like_article_url(link):
            continue

        title = _extract_link_title(link_tag)
        if len(title) < 24:
            continue

        summary = ""
        # 1. "div" aramasını kaldırdık. Sadece çok spesifik olan article ve li'ye bakıyoruz.
        parent = link_tag.find_parent(["article", "li"])
        if parent:
            summary = parent.get_text(" ", strip=True)
            if title in summary:
                summary = summary.replace(title, " ", 1)
            
            # 2. Güvenlik kilidi: Eğer özet çok uzunsa (muhtemelen başka haberler de karışmıştır),
            # özeti sıfırlıyoruz. Çünkü zaten uygulaman haberin içine girip asıl özeti sonradan çıkaracak.
            if len(summary) > 250:
                summary = ""
            else:
                summary = _clean_summary(summary)

        before_count = len(results)
        _append_news_item(
            results,
            seen_links,
            title,
            link,
            summary,
            source_name,
            force_relevant=force_relevant,
        )
        if len(results) > before_count:
            added += 1


def _sort_newest_first(results):
    return sorted(results, key=lambda item: item.get("_sort_ts", 0), reverse=True)


def collect_rss_news(queries=None, max_per_query=8):
    queries = queries or DEFAULT_QUERIES

    results = []
    seen_links = set()

    for source_name, feed_url in DIRECT_RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:max_per_query]:
                _append_entry(results, seen_links, entry, source_name)
        except Exception:
            continue

    for source_name, source_url in DIRECT_HTML_SOURCES:
        try:
            _collect_html_source(results, seen_links, source_name, source_url, max_per_query)
        except Exception:
            continue

    if len(results) >= 12:
        return _sort_newest_first(results)

    for query in queries:
        url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
        feed = feedparser.parse(url)

        for entry in feed.entries[:max_per_query]:
            _append_entry(results, seen_links, entry, _parse_google_source(entry))

    return _sort_newest_first(results)
