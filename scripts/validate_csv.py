import csv
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from taxonomy import validate_categories  # noqa: E402

CSV_FILE = "books.csv"
REQUIRED_COLUMNS = ["isbn", "title", "amazon", "categories"]
# Coluna opcional: link da edição Kindle (https://www.amazon.com.br/dp/<ASIN>/, sem tag).
OPTIONAL_COLUMNS = ["kindle"]
KINDLE_URL_RE = re.compile(r"https://www\.amazon\.com\.br/dp/[A-Z0-9]{10}/")
ASIN_RE = re.compile(r"/(?:dp|gp/product)/([A-Z0-9]{10})", re.I)


def is_valid_isbn(isbn):
    # ISBN-10 or ISBN-13 basic check (10 or 13 digits, may include dashes)
    isbn_clean = isbn.replace("-", "").strip()
    return bool(re.fullmatch(r"\d{10}|\d{13}", isbn_clean))


def is_valid_isbn13(isbn):
    """ISBN-13 com prefixo 978/979 e dígito verificador correto."""
    digits = isbn.replace("-", "").strip()
    if not re.fullmatch(r"97[89]\d{10}", digits):
        return False
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits[:12]))
    return (10 - total % 10) % 10 == int(digits[12])


def extract_asin(url):
    match = ASIN_RE.search(url or "")
    return match.group(1).upper() if match else None


def is_valid_url(url):
    # Just check if the domain is amazon.com
    return "amazon.com" in (url or "").lower()


def validate_csv(filename):
    errors = []
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames or []
        for col in REQUIRED_COLUMNS:
            if col not in headers:
                errors.append(f"Error: required column '{col}' not found in CSV")
                return errors
        for col in headers:
            if col not in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
                errors.append(f"Error: unknown column '{col}' (allowed: {REQUIRED_COLUMNS + OPTIONAL_COLUMNS})")

        seen_isbns = {}
        seen_asins = {}
        for i, row in enumerate(reader, start=2):
            isbn = (row.get("isbn") or "").strip()
            if not isbn or not is_valid_isbn(isbn):
                errors.append(f"Line {i}: Invalid or empty ISBN -> '{isbn}'")
            elif not is_valid_isbn13(isbn):
                errors.append(f"Line {i}: ISBN-13 inválido (prefixo 978/979 ou dígito verificador) -> '{isbn}'")
            norm_isbn = isbn.replace("-", "")
            if norm_isbn:
                if norm_isbn in seen_isbns:
                    errors.append(f"Line {i}: ISBN duplicado (já na linha {seen_isbns[norm_isbn]}) -> '{isbn}'")
                seen_isbns.setdefault(norm_isbn, i)

            if not (row.get("title") or "").strip():
                errors.append(f"Line {i}: Empty title")

            amazon = (row.get("amazon") or "").strip()
            if amazon and not is_valid_url(amazon):
                errors.append(f"Line {i}: Invalid or inaccessible Amazon URL -> '{amazon}'")
            if "tag=" in amazon:
                errors.append(f"Line {i}: amazon não deve ter tag de afiliado (aplicada pelos scripts) -> '{amazon}'")
            amazon_asin = extract_asin(amazon)
            if amazon_asin:
                if amazon_asin in seen_asins:
                    errors.append(f"Line {i}: link amazon duplicado (já na linha {seen_asins[amazon_asin]}) -> '{amazon}'")
                seen_asins.setdefault(amazon_asin, i)

            kindle = (row.get("kindle") or "").strip()
            if kindle:
                if not KINDLE_URL_RE.fullmatch(kindle):
                    errors.append(f"Line {i}: kindle deve ser https://www.amazon.com.br/dp/<ASIN>/ sem tag -> '{kindle}'")
                elif extract_asin(kindle) == amazon_asin:
                    errors.append(f"Line {i}: kindle aponta para o mesmo produto do link amazon -> '{kindle}'")

            categories = (row.get("categories") or "").strip()
            if not categories:
                errors.append(f"Line {i}: Empty categories")
            else:
                for err in validate_categories(categories):
                    errors.append(f"Line {i}: {err}")

    return errors


if __name__ == "__main__":
    erros = validate_csv(CSV_FILE)
    if erros:
        print("Erros encontrados na validação do CSV:")
        for erro in erros:
            print(f" - {erro}")
        sys.exit(1)
    print("Validação concluída sem erros.")
