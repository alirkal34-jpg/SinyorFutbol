import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "SinyorFutbolPrototype/1.0 (educational project)"
}


def _clean_text(text):
    text = re.sub(r"<.*?>", " ", text or "")
    text = re.sub(r"\s+", " ", text)
    return _fix_turkish_encoding(text.strip())


def _fix_turkish_encoding(text):
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
        "Fransýz": "Fransız",
        "Frans?z": "Fransız",
        "kanalýna": "kanalına",
        "kanal?na": "kanalına",
        "detaylý": "detaylı",
        "detayl?": "detaylı",
        "r?portaj": "röportaj",
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

    return text


def _is_generic_or_bad_summary(text):
    lowered = _clean_text(text).lower()
    bad_fragments = [
        "comprehensive up-to-date news coverage",
        "aggregated from sources all over the world",
        "google news",
        "read full articles",
        "coverage, aggregated",
    ]
    return not lowered or any(fragment in lowered for fragment in bad_fragments)


def _split_sentences(text):
    text = _clean_text(text)
    if _is_generic_or_bad_summary(text):
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 35]


def _meta_description(soup):
    selectors = [
        ("property", "og:description"),
        ("name", "description"),
        ("name", "twitter:description"),
    ]
    for attr, value in selectors:
        tag = soup.find("meta", attrs={attr: value})
        if tag and tag.get("content"):
            return _clean_text(tag["content"])
    return ""


def _is_google_news_url(url):
    host = urlparse(url or "").netloc.lower()
    return "news.google." in host


def _is_publisher_url(url):
    host = urlparse(url or "").netloc.lower()
    blocked_hosts = [
        "google.",
        "gstatic.",
        "schema.org",
        "youtube.",
        "facebook.",
        "twitter.",
        "x.com",
    ]
    return url.startswith("http") and not any(blocked in host for blocked in blocked_hosts)


def _resolve_google_news_url(url):
    if not _is_google_news_url(url):
        return url

    response = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
    response.raise_for_status()

    if response.url and not _is_google_news_url(response.url):
        return response.url

    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if _is_publisher_url(href):
            return href

    candidates = re.findall(r"https?://[^\"'<>\\]+", response.text)
    for candidate in candidates:
        candidate = candidate.replace("\\u003d", "=").replace("\\u0026", "&")
        if _is_publisher_url(candidate):
            return candidate

    return url


def extract_article_summary(url, fallback_text="", max_sentences=2):
    """
    Reads a news page and returns a compact 1-2 sentence summary for captions.
    Falls back to RSS summary/title when the article page cannot be parsed.
    """
    fallback_sentences = [
        sentence
        for sentence in _split_sentences(fallback_text)
        if not _is_generic_or_bad_summary(sentence)
    ]
    fallback = " ".join(fallback_sentences[:max_sentences])
    if not fallback and fallback_text:
        first_part = _clean_text(fallback_text).split(".")[0].strip()
        fallback = "" if _is_generic_or_bad_summary(first_part) else first_part
    if not url:
        return {
            "summary": fallback,
            "source": "feed/headline fallback",
            "status": "fallback",
            "error": "",
        }

    try:
        resolved_url = _resolve_google_news_url(url)
        response = requests.get(resolved_url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        meta = _meta_description(soup)
        meta_sentences = _split_sentences(meta)
        if meta_sentences:
            return {
                "summary": " ".join(meta_sentences[:max_sentences]),
                "source": "article meta description",
                "status": "ok",
                "error": "",
                "resolved_url": resolved_url,
            }

        paragraphs = []
        for paragraph in soup.find_all("p"):
            text = _clean_text(paragraph.get_text(" ", strip=True))
            if len(text) > 60:
                paragraphs.append(text)

        article_text = " ".join(paragraphs[:8])
        sentences = _split_sentences(article_text)
        if sentences:
            return {
                "summary": " ".join(sentences[:max_sentences]),
                "source": "article body",
                "status": "ok",
                "error": "",
                "resolved_url": resolved_url,
            }

        return {
            "summary": fallback,
            "source": "feed/headline fallback",
            "status": "fallback",
            "error": "No readable article text found",
        }
    except Exception as exc:
        return {
            "summary": fallback,
            "source": "feed/headline fallback",
            "status": "fallback",
            "error": str(exc),
        }
