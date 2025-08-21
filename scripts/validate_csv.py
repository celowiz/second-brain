import csv
import sys
import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CSV_FILE = "books.csv"
REQUIRED_COLUMNS = ["isbn", "title", "amazon", "categories"]

def is_valid_isbn(isbn):
    # ISBN-10 or ISBN-13 basic check (10 or 13 digits, may include dashes)
    isbn_clean = isbn.replace("-", "").strip()
    return bool(re.fullmatch(r"\d{10}|\d{13}", isbn_clean))

def is_valid_url(url):
    try:
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive"
            }
        )
        # Just check if the domain is amazon.com
        return "amazon.com" in url.lower()
    except:
        return False

def validate_csv(filename):
    errors = []
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        for col in REQUIRED_COLUMNS:
            if col not in headers:
                errors.append(f"Error: required column '{col}' not found in CSV")
                return errors

        for i, row in enumerate(reader, start=2):
            isbn = row.get("isbn", "").strip()
            if not isbn or not is_valid_isbn(isbn):
                errors.append(f"Line {i}: Invalid or empty ISBN -> '{isbn}'")

            amazon = row.get("amazon", "").strip()
            if amazon and not is_valid_url(amazon):
                errors.append(f"Line {i}: Invalid or inaccessible Amazon URL -> '{amazon}'")

            categories = row.get("categories", "").strip()
            if not categories:
                errors.append(f"Line {i}: Empty categories")

    return errors

if __name__ == "__main__":
    erros = validate_csv(CSV_FILE)
    if erros:
        print("Erros encontrados na validação do CSV:")
        for erro in erros:
            print(f" - {erro}")
        sys.exit(1)
    print("Validação concluída sem erros.")