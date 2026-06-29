def choose_style(news_item, content_format):
    """İçeriğin kategorisine göre görsel stil seçer."""
    if news_item["type"] == "national_team":
        accent = "#E30A17"
        template = "national_team_serious"
    elif news_item["type"] == "tournament":
        accent = "#D6B56D"
        template = "world_cup_global"
    elif news_item["category"] == "Transfer":
        accent = "#D72638"
        template = "club_transfer"
    else:
        accent = "#4C78A8"
        template = "editorial_analysis"

    return {
        "template": template,
        "background": "#111111",
        "text": "#F2F2F2",
        "accent": accent,
        "style_name": "Minimal Editorial Football",
        "principles": [
            "sade",
            "manipülasyon temelli",
            "net başlık",
            "az renk",
            "yüksek okunabilirlik",
        ],
    }
