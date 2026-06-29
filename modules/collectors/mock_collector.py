from datetime import datetime

def collect_mock_news():
    """MVP için örnek futbol gündemi üretir. Gerçek kaynaklar sonradan buraya bağlanacak."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        {
            "title": "Beşiktaş sağ kanat transferi için yeni bir profili gündemine aldı",
            "entity": "Beşiktaş",
            "type": "club",
            "category": "Transfer",
            "source": "Mock Sports",
            "published_at": now,
            "reliability_score": 62,
            "summary": "Haber iddia seviyesinde. Oyuncu profili çizgi kullanımı ve bire bir oyunla öne çıkıyor.",
        },
        {
            "title": "A Milli Takım Dünya Kupası elemeleri öncesi kritik kadro kararına hazırlanıyor",
            "entity": "Türkiye A Milli Takımı",
            "type": "national_team",
            "category": "Dünya Kupası Elemeleri",
            "source": "Mock Federation",
            "published_at": now,
            "reliability_score": 78,
            "summary": "Kadro tercihleri ve bazı oyuncuların form durumu tartışma yaratabilir.",
        },
        {
            "title": "Premier League'de teknik direktör değişikliği gündemi sarsıyor",
            "entity": "Premier League",
            "type": "league",
            "category": "Teknik Direktör",
            "source": "Mock UK Football",
            "published_at": now,
            "reliability_score": 70,
            "summary": "Teknik direktör değişikliği ligde güç dengelerini etkileyebilir.",
        },
        {
            "title": "Dünya Kupası hazırlıklarında favori takımların kadro planı netleşiyor",
            "entity": "Dünya Kupası",
            "type": "tournament",
            "category": "Turnuva",
            "source": "Mock Global Football",
            "published_at": now,
            "reliability_score": 81,
            "summary": "Favori ülkelerin kadro planları ve yıldız oyuncu durumları içerik potansiyeli taşıyor.",
        },
        {
            "title": "Galatasaray orta saha rotasyonunda yeni plan deniyor",
            "entity": "Galatasaray",
            "type": "club",
            "category": "Taktik Analiz",
            "source": "Mock Türkiye Futbol",
            "published_at": now,
            "reliability_score": 74,
            "summary": "Teknik ekip orta saha dengesini değiştirebilecek bir plan üstünde çalışıyor.",
        },
    ]
