def analyze_content(package, news_item):
    """MVP skorlayıcı. Sonraki sürümde gerçek veri ve performansla kalibre edilecek."""
    base = 70
    reliability = int(news_item.get("reliability_score", 60))

    category = news_item["category"]
    content_value = base + (10 if category in ["Transfer", "Dünya Kupası Elemeleri", "Turnuva"] else 4)
    engagement = base + (15 if category == "Transfer" else 8)
    virality = base + (12 if news_item["type"] in ["national_team", "tournament"] else 7)
    headline = 88 if "?" in package["headline"] or "DEĞİL" in package["headline"] else 78
    brand_fit = 90
    visual_clarity = 82

    risk_level = "Düşük"
    if reliability < 65:
        risk_level = "Orta"
    if reliability < 45:
        risk_level = "Yüksek"

    risk_penalty = 8 if risk_level == "Orta" else 16 if risk_level == "Yüksek" else 0

    final_publish_score = round(
        content_value * 0.25
        + engagement * 0.20
        + virality * 0.15
        + headline * 0.15
        + brand_fit * 0.10
        + visual_clarity * 0.10
        + reliability * 0.05
        - risk_penalty
    )

    if final_publish_score >= 85 and risk_level == "Düşük":
        recommendation = "Yayınla"
    elif risk_level == "Orta":
        recommendation = "İddia diliyle yayınla / onayla"
    elif final_publish_score >= 75:
        recommendation = "Revize et"
    else:
        recommendation = "Beklet"

    audience = []
    if news_item["type"] == "club":
        audience += [f"{news_item['entity']} taraftarı", "Süper Lig takipçileri"]
    if news_item["type"] == "national_team":
        audience += ["Milli takım takipçileri", "Genel futbol kitlesi"]
    if news_item["type"] == "tournament":
        audience += ["Dünya Kupası takipçileri", "Global futbol kitlesi"]
    audience += ["Reels tüketicileri", "Futbol tartışma kitlesi"]

    reasoning = (
        f"Bu içerik {category} kategorisinde olduğu için etkileşim potansiyeli taşıyor. "
        f"Güvenilirlik skoru {reliability}/100. "
        f"Risk seviyesi {risk_level}. Başlık ve görsel dil Sinyor Futbol'un sade, net ve kararlı çizgisine uygun."
    )

    return {
        "content_value_score": min(content_value, 100),
        "engagement_score": min(engagement, 100),
        "virality_score": min(virality, 100),
        "audience_fit_score": 86,
        "format_score": 84,
        "headline_score": headline,
        "visual_clarity_score": visual_clarity,
        "brand_fit_score": brand_fit,
        "reliability_score": reliability,
        "risk_level": risk_level,
        "final_publish_score": final_publish_score,
        "recommendation": recommendation,
        "audience_segments": audience,
        "reasoning": reasoning,
    }
