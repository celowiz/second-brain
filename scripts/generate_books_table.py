import csv
import sys
import requests
from urllib.parse import quote

TEMPLATE = "| ![cover]({cover_url}) | {title} | [![Amazon]({amazon_badge})]({amazon_url}) | {badges} |"
DEFAULT_COVER = "https://openlibrary.org/images/icons/avatar_book.png"

# Badge configurations
BADGE_TYPES = {
    # Topics
    "Finance": {"prefix": "Topic", "color": "orange"},
    "Psychology": {"prefix": "Topic", "color": "lightgrey"},
    "Quant": {"prefix": "Topic", "color": "lightblue"},
    "Statistics": {"prefix": "Topic", "color": "blue"},
    "Design Patterns": {"prefix": "Topic", "color": "yellowgreen"},
    "Data Science": {"prefix": "Topic", "color": "orange"},
    "Data Engineering": {"prefix": "Topic", "color": "grey"},
    
    # Types
    "Programming": {"prefix": "Type", "color": "brightgreen"},
    
    # Languages
    "Python": {"prefix": "Language", "color": "yellow"},
    "Java": {"prefix": "Language", "color": "blue"},
    "C/C++": {"prefix": "Language", "color": "blue"},
    
    # Genres
    "Biography": {"prefix": "Genre", "color": "blueviolet"},
    
    # Levels
    "Advanced": {"prefix": "Level", "color": "red"},
    "Intermediate": {"prefix": "Level", "color": "lightblue"},
    
    # Special tags
    "Classic": {"prefix": "Classic", "color": "red"},
    
    # Authors
    "Author": {"prefix": "Author", "color": "informational"}
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

def add_affiliate_tag(amazon_url):
    """Add Amazon affiliate tag to URL"""
    if not amazon_url:
        return amazon_url
    
    # Add affiliate tag
    separator = "&tag=" if "?" in amazon_url else "?tag="
    return f"{amazon_url}{separator}celowiz-20"

def get_cover_url(isbn):
    """Get the cover URL, falling back to placeholder if needed"""
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
    try:
        # Make GET request with allow_redirects to get final URL
        response = requests.get(url, allow_redirects=True, timeout=5)
        # If final URL contains 'default' or '-S.jpg', there's no cover
        final_url = response.url
        if '-S.jpg' in final_url or 'avatar_book' in final_url:
            return DEFAULT_COVER
        return url
    except Exception as e:
        print(f"Warning: Could not check cover for ISBN {isbn}: {str(e)}", file=sys.stderr)
        return DEFAULT_COVER

def generate_table_row(row):
    isbn = row["isbn"].strip()
    title = row["title"].strip()
    amazon_url = add_affiliate_tag(row["amazon"].strip())
    categories = [c.strip() for c in row["categories"].split(";")]
    
    # Get cover URL with fallback
    cover_url = get_cover_url(isbn)
    
    # Create badges for each category
    badges = []
    for category in categories:
        if category in BADGE_TYPES:
            badge_url = create_badge(category, BADGE_TYPES[category])
            badges.append(f"![{category}]({badge_url})")
    
    # Format the row using the template
    return TEMPLATE.format(
        cover_url=cover_url,
        title=f"**{title}**",
        amazon_badge=get_amazon_badge(),
        amazon_url=amazon_url,
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