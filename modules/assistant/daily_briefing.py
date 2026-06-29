def build_daily_briefing(news_items, packages):
    """AI asistan için günlük otomasyon özeti üretir."""
    total_news = len(news_items)
    total_packages = len(packages)

    categories = {}
    for item in news_items:
        categories[item["category"]] = categories.get(item["category"], 0) + 1

    top_categories = ", ".join([f"{k}: {v}" for k, v in categories.items()])

    if packages:
        best = max(packages, key=lambda p: p["analysis"]["final_publish_score"])
        best_line = (
            f"Bugünün en güçlü içerik paketi: '{best['headline']}' "
            f"({best['analysis']['final_publish_score']}/100)."
        )
    else:
        best_line = "Henüz içerik paketi üretilmedi."

    return (
        f"Bugün {total_news} futbol gündemi tarandı. "
        f"Kategoriler: {top_categories}. "
        f"Şu ana kadar {total_packages} içerik paketi üretildi. "
        f"{best_line} "
        "Paylaşım modu manuel export olarak ayarlı."
    )
