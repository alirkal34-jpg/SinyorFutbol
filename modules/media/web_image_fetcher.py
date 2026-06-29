from pathlib import Path
from io import BytesIO
from urllib.parse import quote, quote_plus, unquote, urljoin, urlparse
import hashlib
import html
import os
import re

import requests
from bs4 import BeautifulSoup
from PIL import Image
from dotenv import load_dotenv


OUTPUT_DIR = Path("output/media")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

IMAGE_HEADERS = {
    **HEADERS,
    "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
}

NORMALIZED_CLUB_IMAGE_QUERIES = {
    "besiktas": ["Besiktas JK", "Besiktas football club", "Besiktas futbol kulubu"],
    "galatasaray": ["Galatasaray SK", "Galatasaray football club", "Galatasaray futbol kulubu"],
    "fenerbahce": ["Fenerbahce SK", "Fenerbahce football club", "Fenerbahce futbol kulubu"],
    "trabzonspor": ["Trabzonspor", "Trabzonspor football club"],
}

CLUB_IMAGE_QUERIES = {
    "beşiktaş": ["Beşiktaş JK", "Beşiktaş futbol kulübü", "Beşiktaş football club"],
    "besiktas": ["Besiktas JK", "Besiktas football club"],
    "galatasaray": ["Galatasaray SK", "Galatasaray futbol kulübü", "Galatasaray football club"],
    "fenerbahçe": ["Fenerbahçe SK", "Fenerbahçe futbol kulübü", "Fenerbahçe football club"],
    "fenerbahce": ["Fenerbahce SK", "Fenerbahce football club"],
    "trabzonspor": ["Trabzonspor", "Trabzonspor football club"],
}


def _safe_name(value):
    digest = hashlib.md5(value.encode("utf-8", errors="ignore")).hexdigest()[:10]
    return f"web_image_{digest}.jpg"


def _download_image(url, name_hint):
    if not url:
        return None

    response = requests.get(url, headers=IMAGE_HEADERS, timeout=12)
    response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "image" not in content_type:
        return None

    path = OUTPUT_DIR / _safe_name(f"{name_hint}-{url}")
    with Image.open(BytesIO(response.content)) as image:
        image = image.convert("RGB")
        image.save(path, format="JPEG", quality=90)

    return str(path)


def _is_google_url(url):
    host = urlparse(url or "").netloc.lower()
    return "google." in host or "gstatic." in host


def _is_bad_image_url(url, allow_google_thumbnail=False):
    lowered = (url or "").lower()
    blocked_fragments = [
        "googlelogo",
        "/logos/",
        "favicon",
        "gstatic.com/images/branding",
        "schema.org",
    ]
    if allow_google_thumbnail and "encrypted-tbn" in lowered:
        return any(fragment in lowered for fragment in blocked_fragments)
    return _is_google_url(url) or any(fragment in lowered for fragment in blocked_fragments)


def _srcset_urls(value):
    urls = []
    for part in (value or "").split(","):
        url = part.strip().split(" ")[0]
        if url:
            urls.append(url)
    return urls


def _image_score(url, tag=None):
    lowered = (url or "").lower()
    score = 0

    positive = [
        "haber",
        "news",
        "upload",
        "uploads",
        "image",
        "images",
        "photo",
        "photos",
        "media",
        "cdn",
        "content",
        "large",
        "manset",
        "manşet",
    ]
    negative = [
        "logo",
        "logotype",
        "icon",
        "favicon",
        "sprite",
        "avatar",
        "author",
        "default",
        "placeholder",
        "blank",
        "loading",
        "advert",
        "banner",
    ]

    for item in positive:
        if item in lowered:
            score += 2
    for item in negative:
        if item in lowered:
            score -= 20

    if re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", lowered):
        score += 3
    if re.search(r"(1200|1080|800|750|640|600)", lowered):
        score += 2

    if tag is not None:
        for attr in ["width", "height"]:
            try:
                value = int(tag.get(attr, 0))
                if value >= 300:
                    score += 2
            except Exception:
                pass

        alt_title = f"{tag.get('alt', '')} {tag.get('title', '')}".lower()
        if any(item in alt_title for item in negative):
            score -= 4
        if alt_title.strip():
            score += 1

    return score


def _collect_article_image_candidates(soup, resolved_url):
    candidates = []

    meta_selectors = [
        ("property", "og:image"),
        ("property", "og:image:url"),
        ("property", "og:image:secure_url"),
        ("name", "twitter:image"),
        ("property", "twitter:image"),
    ]
    for attr, value in meta_selectors:
        tag = soup.find("meta", attrs={attr: value})
        if tag and tag.get("content"):
            image_url = urljoin(resolved_url, tag["content"])
            candidates.append((20 + _image_score(image_url), image_url))

    image_attrs = [
        "src",
        "data-src",
        "data-original",
        "data-lazy-src",
        "data-image",
        "data-url",
        "data-img",
        "lazy-src",
    ]
    for image in soup.find_all(["img", "source"]):
        for attr in image_attrs:
            if image.get(attr):
                image_url = urljoin(resolved_url, image[attr])
                candidates.append((_image_score(image_url, image), image_url))

        for attr in ["srcset", "data-srcset"]:
            for srcset_url in _srcset_urls(image.get(attr)):
                image_url = urljoin(resolved_url, srcset_url)
                candidates.append((_image_score(image_url, image) + 1, image_url))

    seen = set()
    filtered = []
    for score, image_url in candidates:
        if image_url in seen:
            continue
        seen.add(image_url)
        if _is_bad_image_url(image_url):
            continue
        filtered.append((score, image_url))

    filtered.sort(reverse=True, key=lambda item: item[0])
    return [image_url for _, image_url in filtered]


def _is_publisher_url(url):
    if not url or not url.startswith("http"):
        return False
    host = urlparse(url).netloc.lower()
    blocked_hosts = [
        "google.",
        "gstatic.",
        "youtube.",
        "facebook.",
        "twitter.",
        "x.com",
        "instagram.",
        "schema.org",
    ]
    return not any(blocked in host for blocked in blocked_hosts)


def _resolve_article_url(article_url):
    if not article_url:
        return ""

    if not _is_google_url(article_url):
        return article_url

    response = requests.get(article_url, headers=HEADERS, timeout=12, allow_redirects=True)
    response.raise_for_status()

    if response.url and _is_publisher_url(response.url):
        return response.url

    page_html = html.unescape(response.text)
    soup = BeautifulSoup(page_html, "html.parser")

    for link in soup.find_all("a", href=True):
        href = urljoin(article_url, link["href"])
        if _is_publisher_url(href):
            return href

    candidates = re.findall(r"https?://[^\"'<>\\ ]+", page_html)
    for candidate in candidates:
        candidate = candidate.replace("\\u003d", "=").replace("\\u0026", "&").replace("\\/", "/")
        candidate = unquote(candidate)
        if _is_publisher_url(candidate):
            return candidate

    return ""


def _article_image_urls(article_url):
    if not article_url:
        return []

    resolved_url = _resolve_article_url(article_url)
    if not resolved_url:
        return []

    response = requests.get(resolved_url, headers=HEADERS, timeout=12)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    return _collect_article_image_candidates(soup, resolved_url)


def _article_image_url(article_url):
    candidates = _article_image_urls(article_url)
    return candidates[0] if candidates else None


def _wikipedia_search_title(query):
    endpoint = "https://tr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1,
    }
    response = requests.get(endpoint, params=params, headers=HEADERS, timeout=12)
    response.raise_for_status()
    results = response.json().get("query", {}).get("search", [])
    if not results:
        return None
    return results[0].get("title")


def _wikipedia_thumbnail_url(query):
    title = _wikipedia_search_title(query)
    if not title:
        return None

    endpoint = f"https://tr.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    response = requests.get(endpoint, headers=HEADERS, timeout=12)
    response.raise_for_status()
    data = response.json()

    thumbnail = data.get("thumbnail", {})
    return thumbnail.get("source")


def _normalize_google_candidate(url):
    if not url:
        return None

    url = html.unescape(url)
    url = url.encode("utf-8").decode("unicode_escape", errors="ignore")
    url = url.replace("\\/", "/")
    url = unquote(url)

    if not url.startswith("http"):
        return None

    lowered = url.lower()
    blocked = [
        "base64",
    ]
    if _is_bad_image_url(url, allow_google_thumbnail=True) or any(item in lowered for item in blocked):
        return None

    return url


def _google_image_candidates_from_html(page_html):
    decoded = html.unescape(page_html)
    decoded = decoded.replace("\\u003d", "=").replace("\\u0026", "&").replace("\\/", "/")

    patterns = [
        r'"ou":"(https?://[^"]+)"',
        r'\["(https?://[^"]+?\.(?:jpg|jpeg|png|webp)[^"]*)"',
        r'(https?://encrypted-tbn\d?\.gstatic\.com/images\?[^"\'<>\\ ]+)',
        r'(https?://[^"\'<>\\ ]+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\'<>\\ ]*)?)',
    ]

    candidates = []
    for pattern in patterns:
        for match in re.findall(pattern, decoded, flags=re.IGNORECASE):
            candidate = _normalize_google_candidate(match)
            if candidate and candidate not in candidates:
                candidates.append(candidate)
    return candidates


def _google_image_url(query):
    api_key = os.getenv("GOOGLE_CSE_API_KEY", "").strip()
    search_engine_id = os.getenv("GOOGLE_CSE_ID", "").strip()
    if api_key and search_engine_id:
        api_url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "searchType": "image",
            "num": 1,
            "safe": "active",
        }
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=12)
        response.raise_for_status()
        items = response.json().get("items", [])
        if items and items[0].get("link"):
            return items[0]["link"]

    search_urls = [
        f"https://www.google.com/search?tbm=isch&hl=tr&safe=active&q={quote_plus(query)}",
        f"https://www.google.com/search?udm=2&hl=tr&safe=active&q={quote_plus(query)}",
    ]

    session = requests.Session()
    session.cookies.set("CONSENT", "YES+cb.20240101-17-p0.tr+FX+410")

    last_html = ""
    for search_url in search_urls:
        response = session.get(search_url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        last_html = response.text

        if "consent.google" in response.url or "Before you continue" in response.text:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for image in soup.find_all("img"):
            src = image.get("data-src") or image.get("src")
            candidate = _normalize_google_candidate(src)
            if candidate:
                return candidate

        for candidate in _google_image_candidates_from_html(response.text):
            return candidate

    for candidate in _google_image_candidates_from_html(last_html):
        return candidate
    return None


def _normalize_lookup_key(value):
    value = (value or "").lower().strip()
    mojibake_map = {
        "beåÿiktaåÿ": "besiktas",
        "beåŸiktaåŸ": "besiktas",
        "fenerbahã§e": "fenerbahce",
        "fenerbahÃ§e".lower(): "fenerbahce",
        "beÅŸiktaÅŸ".lower(): "besiktas",
    }
    if value in mojibake_map:
        return mojibake_map[value]

    value = value.replace("ı", "i").replace("İ", "i")
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    ascii_value = re.sub(r"[^a-z0-9]+", "", ascii_value)
    if "be" in ascii_value and "ikta" in ascii_value:
        return "besiktas"
    if ascii_value.startswith("fenerbah"):
        return "fenerbahce"
    return ascii_value


def _candidate_queries(news_item, preferred_query=None):
    title = news_item.get("title", "")
    entity = news_item.get("entity") or ""
    candidates = []

    if preferred_query:
        candidates.append(preferred_query.strip())

    if entity and entity != "Genel Futbol":
        candidates.append(entity)

    words = title.replace("-", " ").replace("'", " ").split()
    name_parts = []
    for word in words:
        cleaned = "".join(ch for ch in word if ch.isalpha() or ch in "ÇĞİÖŞÜçğıöşü")
        if cleaned[:1].isupper() and len(cleaned) > 2:
            name_parts.append(cleaned)
        elif len(name_parts) >= 2:
            break
        else:
            name_parts = []

    if len(name_parts) >= 2:
        candidates.append(" ".join(name_parts[:3]))

    candidates.append(title)

    unique = []
    for candidate in candidates:
        if candidate and candidate not in unique:
            unique.append(candidate)
    return unique


def fetch_relevant_image(news_item, preferred_query=None):
    """
    Finds and stores a relevant web image for a news item.
    Priority: Google Images by headline, article image, Wikipedia/entity image, then no image.
    """
    title = news_item.get("title", "")
    queries = _candidate_queries(news_item, preferred_query)
    query = queries[0] if queries else title

    attempts = []

    try:
        image_url = _google_image_url(title)
        attempts.append(f"google images: {title}")
        image_path = _download_image(image_url, title)
        if image_path:
            return {
                "image_path": image_path,
                "image_url": image_url,
                "source": "google images",
                "query": title,
                "status": "ok",
                "attempts": attempts,
            }
    except Exception as exc:
        attempts.append(f"google images failed ({title}): {exc}")

    try:
        attempts.append("article metadata")
        for image_url in _article_image_urls(news_item.get("url", ""))[:8]:
            try:
                image_path = _download_image(image_url, title)
                if image_path:
                    return {
                        "image_path": image_path,
                        "image_url": image_url,
                        "source": "article metadata",
                        "query": query,
                        "status": "ok",
                        "attempts": attempts,
                    }
            except Exception as image_exc:
                attempts.append(f"article image candidate failed: {image_exc}")
    except Exception as exc:
        attempts.append(f"article failed: {exc}")

    for candidate in queries:
        try:
            image_url = _wikipedia_thumbnail_url(candidate)
            attempts.append(f"wikipedia thumbnail: {candidate}")
            image_path = _download_image(image_url, candidate)
            if image_path:
                return {
                    "image_path": image_path,
                    "image_url": image_url,
                    "source": "wikipedia thumbnail",
                    "query": candidate,
                    "status": "ok",
                    "attempts": attempts,
                }
        except Exception as exc:
            attempts.append(f"wikipedia failed ({candidate}): {exc}")

    return {
        "image_path": "",
        "image_url": "",
        "source": "fallback placeholder",
        "query": query,
        "status": "fallback",
        "attempts": attempts,
    }
