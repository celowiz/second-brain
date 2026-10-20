import csv
import os
import re
import sys
import requests
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy import LANGUAGES, TAGS, THEMES  # noqa: E402

TEMPLATE = "| ![cover]({cover_url}) | {title} | [![Amazon]({amazon_badge})]({amazon_url}){kindle_link} | {badges} |"
KINDLE_LINK_TEMPLATE = "<br>[![Kindle]({kindle_badge})]({kindle_url})"
DEFAULT_COVER = "https://openlibrary.org/images/icons/avatar_book.png"

# Badge configurations: gerado da taxonomia fechada (scripts/taxonomy.py),
# para que nenhum tema/tag do books.csv seja descartada na tabela.
BADGE_TYPES = {
    **{name: {"prefix": "Theme", "color": color} for name, color in THEMES.items()},
    **{name: {"prefix": "Tag", "color": color} for name, color in TAGS.items()},
    **{name: {"prefix": "Lang", "color": color} for name, color in LANGUAGES.items()},
}

def create_badge(text, config):
    """Create a shields.io badge URL"""
    prefix = config["prefix"]
    color = config["color"]
    encoded_text = quote(text)
    return f"https://img.shields.io/badge/{prefix}-{encoded_text}-{color}"

def get_amazon_badge():
    """Create a small Amazon badge"""
    return "https://img.shields.io/badge/-Buy%20on%20Amazon-black"

def get_kindle_badge():
    """Small secondary badge for the Kindle edition"""
    return "https://img.shields.io/badge/-Kindle-blue"

def add_affiliate_tag(amazon_url):
    """Add Amazon affiliate tag to URL"""
    if not amazon_url:
        return amazon_url
    
    # Add affiliate tag
    separator = "&tag=" if "?" in amazon_url else "?tag="
    return f"{amazon_url}{separator}celowiz05-20"

MIN_COVER_BYTES = 1500  # Open Library and Amazon answer "no cover" with a 1x1 GIF (43 bytes)
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; second-brain-books/1.0; +https://github.com/celowiz/second-brain)"}


def _normalize_isbn(isbn):
    return isbn.replace("-", "").replace(" ", "").strip()


def _isbn13_to_isbn10(isbn13):
    """978-prefixed ISBN-13 -> ISBN-10 (979 ISBNs have no ISBN-10)."""
    if len(isbn13) != 13 or not isbn13.startswith("978"):
        return None
    core = isbn13[3:12]
    total = sum((10 - i) * int(d) for i, d in enumerate(core))
    check = (11 - total % 11) % 11
    return core + ("X" if check == 10 else str(check))


def _extract_asin(amazon_url):
    match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", amazon_url or "", re.I)
    return match.group(1) if match else None


def _is_real_image(url):
    """True only if the URL returns an actual image (not a 404, a 1x1 GIF or a placeholder)."""
    try:
        response = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=10)
    except Exception as e:
        print(f"Warning: could not fetch cover {url}: {e}", file=sys.stderr)
        return False
    final_url = response.url
    content_type = response.headers.get("Content-Type", "")
    return (
        response.status_code == 200
        and content_type.startswith("image/")
        and len(response.content) >= MIN_COVER_BYTES
        and "avatar_book" not in final_url
    )


def _google_books_thumbnail(isbn):
    try:
        response = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": f"isbn:{isbn}"},
            headers=HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            return None
        for item in response.json().get("items", []):
            links = item.get("volumeInfo", {}).get("imageLinks", {})
            thumb = links.get("thumbnail") or links.get("smallThumbnail")
            if thumb:
                return thumb.replace("http://", "https://").replace("&edge=curl", "")
    except Exception as e:
        print(f"Warning: Google Books lookup failed for ISBN {isbn}: {e}", file=sys.stderr)
    return None


def cover_candidates(isbn, amazon_url=None):
    """Cover sources in priority order: Open Library, Google Books, Amazon (ISBN-10, then ASIN)."""
    isbn = _normalize_isbn(isbn)
    yield f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg?default=false"
    thumb = _google_books_thumbnail(isbn)
    if thumb:
        yield thumb
    amazon_ids = []
    for amazon_id in (_isbn13_to_isbn10(isbn), _extract_asin(amazon_url)):
        if amazon_id and amazon_id not in amazon_ids:
            amazon_ids.append(amazon_id)
    for amazon_id in amazon_ids:
        yield f"https://images-na.ssl-images-amazon.com/images/P/{amazon_id}.01._SCLZZZZZZZ_SY270_.jpg"


def get_cover_url(isbn, amazon_url=None):
    """Return the first cover URL that serves a real image, falling back to a placeholder."""
    for url in cover_candidates(isbn, amazon_url):
        if _is_real_image(url):
            return url
    print(f"Warning: no cover found for ISBN {isbn}", file=sys.stderr)
    return DEFAULT_COVER

def generate_table_row(row):
    isbn = row["isbn"].strip()
    title = row["title"].strip()
    raw_amazon_url = row["amazon"].strip()
    amazon_url = add_affiliate_tag(raw_amazon_url)
    categories = [c.strip() for c in row["categories"].split(";") if c.strip()]
    # Coluna opcional: CSVs sem `kindle` continuam funcionando
    raw_kindle_url = (row.get("kindle") or "").strip()
    kindle_link = (
        KINDLE_LINK_TEMPLATE.format(kindle_badge=get_kindle_badge(), kindle_url=add_affiliate_tag(raw_kindle_url))
        if raw_kindle_url
        else ""
    )
    
    # Get cover URL with fallback
    cover_url = get_cover_url(isbn, raw_amazon_url)
    
    # Create badges for each category
    badges = []
    for category in categories:
        if category in BADGE_TYPES:
            badge_url = create_badge(category, BADGE_TYPES[category])
            badges.append(f"![{category}]({badge_url})")
        else:
            print(f"Warning: category '{category}' has no badge (ISBN {isbn})", file=sys.stderr)
    
    # Format the row using the template
    return TEMPLATE.format(
        cover_url=cover_url,
        title=f"**{title}**",
        amazon_badge=get_amazon_badge(),
        amazon_url=amazon_url,
        kindle_link=kindle_link,
        badges=" ".join(badges)
    )

def generate_table_from_csv(csv_path="books.csv"):
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(generate_table_row(row))
    return rows

if __name__ == "__main__":
    # Table header with proper column widths
    print("| Cover | Title | Amazon | Categories |")
    print("|:---:|:---|:---:|:---|")
    try:
        for row in generate_table_from_csv():
            print(row)
    except UnicodeEncodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating table: {e}", file=sys.stderr)
        sys.exit(1)