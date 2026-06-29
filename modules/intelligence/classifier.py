def classify_news_item(text):
    """Basit kategori sınıflandırma yeri. İleride NLP modeli bağlanacak."""
    lowered = text.lower()
    if "transfer" in lowered:
        return "Transfer"
    if "milli" in lowered or "dünya kupası" in lowered:
        return "Milli Takım / Turnuva"
    if "taktik" in lowered:
        return "Taktik Analiz"
    return "Genel Futbol"
