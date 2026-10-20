"""Taxonomia fechada da estante (books.csv -> coluna `categories`).

Regra: `Tema;Tag secundária (0-3);Idioma`
  - 1ª posição: exatamente um tema principal (THEMES);
  - meio: até 3 tags secundárias (TAGS);
  - última posição: idioma (LANGUAGES).
Os códigos são estáveis e em inglês; a tradução para exibição fica no portfólio.
Não use ',' (o portfólio junta/separa por vírgula), nem '-' ou '_' (separadores do shields.io).
"""

# tema principal -> cor do badge
THEMES = {
    "Quant": "lightblue",
    "Investing": "orange",
    "Economics": "yellowgreen",
    "Software": "brightgreen",
    "Behavior": "lightgrey",
    "Data Science": "blue",
    "Fiction & Philosophy": "blueviolet",
}

# tags secundárias -> cor do badge
TAGS = {
    "Trading": "informational",
    "Systematic": "informational",
    "Statistical Arbitrage": "informational",
    "Derivatives": "informational",
    "Portfolio": "informational",
    "Machine Learning": "informational",
    "Python": "yellow",
    "Data Engineering": "informational",
    "Software Architecture": "informational",
    "Software Craft": "informational",
    "Value Investing": "informational",
    "Personal Finance": "informational",
    "Risk & Probability": "informational",
    "Economic History": "informational",
    "Macro & Policy": "informational",
    "Brazil": "informational",
    "Biography": "informational",
    "Market Stories": "informational",
    "Classic": "red",
    "Fiction": "informational",
    "Philosophy": "informational",
}

# idioma -> cor do badge
LANGUAGES = {
    "PT": "green",
    "EN": "blue",
}

MAX_SECONDARY_TAGS = 3


def split_categories(raw):
    return [c.strip() for c in (raw or "").split(";") if c.strip()]


def validate_categories(raw):
    """Lista de erros (vazia se `raw` segue a regra Tema;tags;Idioma)."""
    cats = split_categories(raw)
    if len(cats) < 2:
        return [f"categories precisa de pelo menos tema e idioma -> '{raw}'"]
    errors = []
    theme, *middle, lang = cats
    if theme not in THEMES:
        errors.append(f"1ª categoria '{theme}' não é um tema válido ({', '.join(THEMES)})")
    if lang not in LANGUAGES:
        errors.append(f"última categoria '{lang}' não é um idioma válido ({', '.join(LANGUAGES)})")
    if len(middle) > MAX_SECONDARY_TAGS:
        errors.append(f"mais de {MAX_SECONDARY_TAGS} tags secundárias -> {middle}")
    for tag in middle:
        if tag not in TAGS:
            errors.append(f"tag secundária desconhecida '{tag}'")
    if len(set(cats)) != len(cats):
        errors.append(f"categoria repetida -> {cats}")
    return errors
