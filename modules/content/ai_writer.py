import re
import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# .env dosyasındaki şifreleri sisteme yükler
load_dotenv()

# OpenAI istemcisini OpenRouter sunucularına yönlendiriyoruz
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY")
)


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<.*?>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&")
    text = text.replace("&#39;", "'")
    return _fix_turkish_encoding(" ".join(text.split()))


def _fix_turkish_encoding(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "Ý": "İ",
        "ý": "ı",
        "Þ": "Ş",
        "þ": "ş",
        "Ð": "Ğ",
        "ð": "ğ",
        "Ä°": "İ",
        "Ä±": "ı",
        "Åž": "Ş",
        "ÅŸ": "ş",
        "ÄŸ": "ğ",
        "Äž": "Ğ",
        "Ã‡": "Ç",
        "Ã§": "ç",
        "Ã–": "Ö",
        "Ã¶": "ö",
        "Ãœ": "Ü",
        "Ã¼": "ü",
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "Â": "",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    word_replacements = {
        "Fransýz": "Fransız",
        "Frans?z": "Fransız",
        "kanalýna": "kanalına",
        "kanal?na": "kanalına",
        "detaylý": "detaylı",
        "detayl?": "detaylı",
        "r?portaj": "röportaj",
        "M?LYON": "MİLYON",
        "M?LL?": "MİLLİ",
        "BE??KTA??": "BEŞİKTAŞ",
        "Be??ikta??": "Beşiktaş",
        "Fenerbah??e": "Fenerbahçe",
        "G??ndem": "Gündem",
        "sakatl??k": "sakatlık",
    }
    for bad, good in word_replacements.items():
        text = text.replace(bad, good)

    return text


def _is_generic_summary(text: str) -> bool:
    lowered = _clean_text(text).lower()
    bad_fragments = [
        "comprehensive up-to-date news coverage",
        "aggregated from sources all over the world",
        "google news",
        "read full articles",
        "coverage, aggregated",
    ]
    return any(fragment in lowered for fragment in bad_fragments)


def _safe_entity(news_item: dict) -> str:
    return news_item.get("entity") or "Genel Futbol"


def _safe_category(news_item: dict) -> str:
    return news_item.get("category") or "Genel Futbol"


def _safe_summary(news_item: dict) -> str:
    candidates = [
        news_item.get("article_summary"),
        news_item.get("summary"),
        news_item.get("title"),
    ]
    for candidate in candidates:
        cleaned = _clean_text(candidate or "")
        if cleaned and not _is_generic_summary(cleaned):
            return cleaned
    return ""


def _is_risky(news_item: dict) -> bool:
    reliability = int(news_item.get("reliability_score", 60))
    category = _safe_category(news_item).lower()
    title = news_item.get("title", "").lower()

    risky_words = [
        "iddia",
        "transfer",
        "anlaştı",
        "imza",
        "gündemine aldı",
        "görüşme",
        "teklif",
    ]

    return reliability < 70 or any(word in title or word in category for word in risky_words)


def _risk_note(news_item: dict) -> str:
    if _is_risky(news_item):
        return (
            "Bu içerikte kesin dil kullanma. "
            "'İmza atıyor', 'anlaştı', 'bitti' gibi ifadeler yerine "
            "'iddia edildi', 'gündeme geldi', 'konuşuluyor' gibi temkinli dil kullan."
        )

    return "Risk düşük. Yine de kaynak ve bağlamı koruyarak net ama abartısız dil kullan."


def _tone_sentence(tone: str) -> str:
    tone = tone.lower()

    if "taraftar" in tone:
        return "Analitik ama taraftarın hissini anlayan, samimi ve net bir ton kullan."
    if "sakin" in tone:
        return "Sakin, temkinli, abartısız ve güven veren bir ton kullan."
    if "heyecanlı" in tone:
        return "Heyecanı yüksek ama kesin hüküm vermeyen bir ton kullan."
    if "ciddi" in tone:
        return "Editoryal, ciddi, net ve profesyonel bir ton kullan."
    if "mizahi" in tone:
        return "Hafif mizahi ama ciddiyeti bozmayan kontrollü bir ton kullan."

    return "Net, sade ve futbolu bilen bir ton kullan."


def _category_angle(news_item: dict) -> dict:
    category = _safe_category(news_item).lower()
    entity_type = news_item.get("type", "")

    if "transfer" in category:
        return {
            "angle": "Transfer iddiası / oyuncu profili",
            "emotion": "Merak + umut + şüphe",
            "main_question": "Bu profil gerçekten ihtiyaçla örtüşüyor mu?",
            "format_advice": "Reels ve tek görsel post güçlü çalışır.",
        }

    if "sakat" in category:
        return {
            "angle": "Kadro etkisi / eksik oyuncu",
            "emotion": "Kaygı + belirsizlik",
            "main_question": "Bu eksik takım planını nasıl etkiler?",
            "format_advice": "Tek görsel post veya kısa story daha uygun.",
        }

    if "milli" in category or "dünya kupası" in category or entity_type in ["national_team", "tournament"]:
        return {
            "angle": "Milli takım / turnuva hikâyesi",
            "emotion": "Gurur + kritik maç hissi + merak",
            "main_question": "Bu gelişme turnuva yolunu nasıl etkiler?",
            "format_advice": "Reels, carousel ve ciddi post formatı uygun.",
        }

    if "teknik" in category:
        return {
            "angle": "Teknik direktör kararı / oyun planı",
            "emotion": "Tartışma + beklenti",
            "main_question": "Bu karar sahadaki dengeyi değiştirir mi?",
            "format_advice": "Carousel analiz formatı güçlü çalışır.",
        }

    if "maç" in category:
        return {
            "angle": "Maç önü / maç sonu kırılma noktası",
            "emotion": "Heyecan + rekabet + beklenti",
            "main_question": "Maçın kaderini hangi detay belirler?",
            "format_advice": "Reels ve maç önü carousel iyi çalışır.",
        }

    return {
        "angle": "Futbol gündemi / genel analiz",
        "emotion": "Merak + tartışma",
        "main_question": "Bu gelişme neden önemli?",
        "format_advice": "Tek görsel post veya carousel uygun.",
    }


def _headline_variants(news_item: dict) -> list[str]:
    entity = _safe_entity(news_item).upper()
    category = _safe_category(news_item).lower()

    if "transfer" in category:
        return [
            f"{entity} İÇİN DOĞRU PROFİL Mİ?",
            "BU TRANSFER OYUNU DEĞİŞTİRİR Mİ?",
            "GÜNDEMDEKİ İSİM NE ANLAMA GELİR?",
            "HEYECAN VAR AMA TEMKİN ŞART",
            "BU PROFİL NEDEN KONUŞULUYOR?",
        ]

    if "milli" in category or "dünya kupası" in category or news_item.get("type") in ["national_team", "tournament"]:
        return [
            "BU MAÇ SADECE 3 PUAN DEĞİL",
            "TÜRKİYE İÇİN KRİTİK EŞİK",
            "GRUBUN DENGESİ DEĞİŞEBİLİR",
            "MİLLİ TAKIMDA ASIL SORU BU",
            "TURNUVA YOLUNDA KIRILMA ANI",
        ]

    if "teknik" in category:
        return [
            "ASIL MESELE SAHADAKİ DENGE",
            "BU KARAR OYUNU DEĞİŞTİRİR Mİ?",
            "HOCA NEYİ DENİYOR?",
            "PLAN TUTARSA DENGE DEĞİŞİR",
            "SAHADAKİ SORU BU",
        ]

    if "sakat" in category:
        return [
            "BU EKSİK PLANI DEĞİŞTİRİR",
            "KADRODA KRİTİK SORU",
            "TAKIM DENGESİ ETKİLENİR Mİ?",
            "BU SAKATLIK NE ANLAMA GELİR?",
            "MAÇ ÖNCESİ KRİTİK GELİŞME",
        ]

    return [
        "BU GELİŞME NEDEN ÖNEMLİ?",
        "ASIL MESELE BU",
        "GÜNDEMİN ARKASINDA NE VAR?",
        "BU BAŞLIK TAKİP EDİLİR",
        "FUTBOLDA BUGÜNÜN NOTU",
    ]


def _choose_main_headline(news_item: dict) -> str:
    return _headline_variants(news_item)[0]


def _build_short_comment(news_item: dict, tone: str) -> str:
    category = _safe_category(news_item).lower()
    angle = _category_angle(news_item)
    summary = _safe_summary(news_item)

    if "transfer" in category:
        return (
            "Bu haber heyecanlandırır ama hemen uçmamak lazım. "
            "Profil doğru görünse bile işin kaynak, maliyet ve sistem uyumu tarafı belirleyici olur."
        )

    if "milli" in category or "dünya kupası" in category or news_item.get("type") in ["national_team", "tournament"]:
        return (
            "Bu tarz gündemler sadece haber değeri taşımaz; duygu, beklenti ve geniş kitle etkisi de üretir. "
            "Bu yüzden daha ciddi, net ve güçlü bir anlatım iyi çalışır."
        )

    if "teknik" in category:
        return (
            "Burada asıl mesele isimlerden çok oyun dengesi. "
            "Kararın sahadaki rol paylaşımına nasıl yansıyacağı içeriğin ana ekseni olmalı."
        )

    if "sakat" in category:
        return (
            "Bu gelişmeyi panik diliyle değil, kadro planına etkisi üzerinden anlatmak daha doğru olur. "
            "Eksik oyuncunun takım dengesine ne değiştirdiği öne çıkarılmalı."
        )

    return (
        f"{angle['main_question']} Bu içerikte haberi sadece aktarmak yerine "
        "neden önemli olduğunu sade ve net biçimde anlatmak daha değerli olur."
    )


def _build_caption(news_item: dict, tone: str) -> str:
    entity = _safe_entity(news_item)
    summary = _safe_summary(news_item)

    if not summary:
        summary = news_item.get("title", "")

    # Yapay zekaya vereceğimiz sistem talimatı (Prompt Engineering)
    system_prompt = f"""
    Sen 'Sinyor Futbol' adında, Instagram'da futbol içerikleri üreten profesyonel bir spor yazarısın. 
    Sana bir futbol haberi özeti ve bu haberin odaklandığı takım/varlık ({entity}) verilecek.
    
    GÖREV:
    Bu haberi okuyup Instagram için detaylı, doyurucu ve dikkat çekici bir açıklama (caption) yaz.
    
    KURALLAR:
    1. Yapı: 
       - İlk olarak haberin ne olduğunu anlatan detaylı bir özet yaz. (DİKKAT: Bu özet kısmı kesinlikle EN AZ 3 CÜMLE olmalı).
       - Ardından haberi değerlendiren, {tone} tonuna uygun bir yorum/analiz paragrafı ekle.
    2. İstenen Ton: {tone}. Yorum kısmını kesinlikle bu tona uygun yaz.
    3. Metnin en sonuna standart olarak şu cümleyi ekle: "Daha fazlası ve güncel futbol içerikleri için bizi takip etmeyi unutma! 👇"
    4. Hashtag kullanma, sadece metni ver.
    """

    try:
        # OpenAI API'sine OpenRouter üzerinden istek atıyoruz
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Haber Özeti: {summary}"}
            ],
            temperature=0.7, 
            max_tokens=450   # Uzun metin üretebilmesi için sınırı 200'den 450'ye çıkardık
        )
        
        caption = response.choices[0].message.content.strip()
        
    except Exception as e:
        # Sorunun ne olduğunu anlamak için hatayı Visual Studio terminaline yazdırıyoruz
        print(f"\n--- OPENAI BAĞLANTI HATASI ---")
        print(e)
        print("------------------------------\n")
        
        # İnternet koparsa veya API limiti biterse sistemin çökmesini engeller
        caption = f"{summary}\n\n(Yapay zeka metni şu an üretilemedi.)\n\nDaha fazlası için takip et! 👇"

    return _fix_turkish_encoding(caption)


def _build_reels_script(news_item: dict, tone: str) -> dict:
    entity = _safe_entity(news_item)
    category = _safe_category(news_item)
    angle = _category_angle(news_item)

    if "transfer" in category.lower():
        hook = f"{entity} için konuşulan bu profil gerçekten doğru tercih mi?"
        scenes = [
            {
                "scene": 1,
                "screen_text": "GÜNDEMDEKİ PROFİL",
                "voice": f"{entity} için yeni bir oyuncu profili konuşuluyor.",
            },
            {
                "scene": 2,
                "screen_text": "İHTİYAÇLA UYUŞUYOR MU?",
                "voice": "Burada mesele sadece oyuncunun ismi değil, takımın ihtiyaç duyduğu role uyup uymaması.",
            },
            {
                "scene": 3,
                "screen_text": "HEYECAN VAR, TEMKİN ŞART",
                "voice": "Haber iddia seviyesindeyse kesin konuşmak doğru olmaz. Kaynak ve maliyet tarafı belirleyici.",
            },
            {
                "scene": 4,
                "screen_text": "SENCE?",
                "voice": "Sence bu profil takıma seviye atlatır mı?",
            },
        ]
    elif news_item.get("type") in ["national_team", "tournament"] or "dünya kupası" in category.lower():
        hook = "Bu gelişme turnuva yolundaki bütün dengeyi değiştirebilir."
        scenes = [
            {
                "scene": 1,
                "screen_text": "KRİTİK EŞİK",
                "voice": "Milli takım için bu gündem sadece bugünü değil, turnuva yolunu da ilgilendiriyor.",
            },
            {
                "scene": 2,
                "screen_text": "KADRO VE DENGE",
                "voice": "Kadro tercihleri, form durumu ve rakip analizi burada belirleyici olacak.",
            },
            {
                "scene": 3,
                "screen_text": "SADECE 3 PUAN DEĞİL",
                "voice": "Böyle maçlar bazen puandan fazlasını değiştirir: özgüven, hava ve grup dengesi.",
            },
            {
                "scene": 4,
                "screen_text": "SENCE?",
                "voice": "Sence bu süreçte en kritik karar ne?",
            },
        ]
    else:
        hook = "Bu gelişmenin asıl etkisi sahada ortaya çıkacak."
        scenes = [
            {
                "scene": 1,
                "screen_text": "GÜNDEMDE NE VAR?",
                "voice": "Bugünün futbol gündeminde dikkat çeken bir gelişme var.",
            },
            {
                "scene": 2,
                "screen_text": "NEDEN ÖNEMLİ?",
                "voice": angle["main_question"],
            },
            {
                "scene": 3,
                "screen_text": "SAHAYA ETKİSİ",
                "voice": "Bu tarz gelişmeler, takımın rol dağılımını ve oyun planını doğrudan etkileyebilir.",
            },
            {
                "scene": 4,
                "screen_text": "SENCE?",
                "voice": "Bu gelişmeyi nasıl okuyorsun?",
            },
        ]

    full_voiceover = " ".join(scene["voice"] for scene in scenes)

    return {
        "hook": hook,
        "scenes": scenes,
        "full_voiceover": full_voiceover,
        "estimated_duration": "25-35 saniye",
    }


def _build_carousel(news_item: dict, tone: str) -> list[dict]:
    category = _safe_category(news_item)
    entity = _safe_entity(news_item)
    summary = _safe_summary(news_item)
    angle = _category_angle(news_item)

    return [
        {
            "slide": 1,
            "title": _choose_main_headline(news_item),
            "body": "Gündemin arkasındaki asıl soruya bakalım.",
        },
        {
            "slide": 2,
            "title": "OLAY NE?",
            "body": summary[:220],
        },
        {
            "slide": 3,
            "title": "NEDEN ÖNEMLİ?",
            "body": angle["main_question"],
        },
        {
            "slide": 4,
            "title": "SİNYOR YORUMU",
            "body": _build_short_comment(news_item, tone),
        },
        {
            "slide": 5,
            "title": "SENCE?",
            "body": f"{entity} tarafında bu gelişme nasıl okunmalı?",
        },
    ]


def _build_tiktok_text(news_item: dict, tone: str) -> dict:
    reels = _build_reels_script(news_item, tone)

    return {
        "opening_line": reels["hook"],
        "short_script": reels["full_voiceover"],
        "caption": (
            f"{reels['hook']}\n\n"
            "Sence bu konu abartılıyor mu, gerçekten önemli mi?"
        ),
        "comment_bait": "Sen olsan bu gelişmeyi nasıl yorumlardın?",
    }


def _build_hashtags(news_item: dict) -> str:
    entity = _safe_entity(news_item)
    category = _safe_category(news_item)

    tags = [
        "#SinyorFutbol",
        "#Futbol",
    ]

    entity_tags = {
        "Beşiktaş": "#Beşiktaş",
        "Galatasaray": "#Galatasaray",
        "Fenerbahçe": "#Fenerbahçe",
        "Trabzonspor": "#Trabzonspor",
        "Türkiye A Milli Takımı": "#MilliTakım",
        "Dünya Kupası": "#DünyaKupası",
    }

    if entity in entity_tags:
        tags.append(entity_tags[entity])

    if "transfer" in category.lower():
        tags.extend(["#Transfer", "#SüperLig"])
    elif "dünya kupası" in category.lower():
        tags.extend(["#WorldCup", "#DünyaKupası"])
    elif "milli" in category.lower():
        tags.extend(["#BizimÇocuklar", "#MilliTakım"])
    elif "maç" in category.lower():
        tags.extend(["#MaçGünü", "#FutbolAnaliz"])
    else:
        tags.extend(["#FutbolGündemi", "#Reels"])

    return " ".join(dict.fromkeys(tags))


def _build_content_value_notes(news_item: dict) -> list[str]:
    angle = _category_angle(news_item)
    reliability = int(news_item.get("reliability_score", 60))

    notes = [
        f"İçerik açısı: {angle['angle']}",
        f"Duygusal tetik: {angle['emotion']}",
        f"Format önerisi: {angle['format_advice']}",
        f"Güvenilirlik skoru: {reliability}/100",
    ]

    if _is_risky(news_item):
        notes.append("Dikkat: Kesin dil yerine iddia/temkin dili kullanılmalı.")

    return notes


def generate_content_package(news_item, tone, content_format):
    """
    Sinyor Futbol içerik üretim motoru.
    Şimdilik kural tabanlı çalışır. Sonraki sürümde LLM bağlantısı buraya eklenecek.
    """
    headline = _choose_main_headline(news_item)
    headline_variants = _headline_variants(news_item)
    short_comment = _build_short_comment(news_item, tone)
    caption = _build_caption(news_item, tone)
    reels_script = _build_reels_script(news_item, tone)
    carousel = _build_carousel(news_item, tone)
    tiktok = _build_tiktok_text(news_item, tone)
    hashtags = _build_hashtags(news_item)
    notes = _build_content_value_notes(news_item)

    export_text = f"""
SINYOR FUTBOL İÇERİK PAKETİ
Tarih: {datetime.now().strftime("%Y-%m-%d %H:%M")}

Konu:
{news_item.get("title", "")}

Format:
{content_format}

Ton:
{tone}

Ana Başlık:
{headline}

Alternatif Başlıklar:
{chr(10).join("- " + h for h in headline_variants)}

Kısa Yorum:
{short_comment}

Caption:
{caption}

Hashtag:
{hashtags}

Reels Hook:
{reels_script["hook"]}

Reels Seslendirme:
{reels_script["full_voiceover"]}

Carousel:
{chr(10).join(f'Slide {s["slide"]}: {s["title"]} - {s["body"]}' for s in carousel)}

TikTok Açılış:
{tiktok["opening_line"]}

Risk / Değer Notları:
{chr(10).join("- " + n for n in notes)}
""".strip()

    return {
        "source_news": news_item,
        "format": content_format,
        "tone": tone,
        "headline": headline,
        "headline_variants": headline_variants,
        "short_comment": short_comment,
        "caption": caption,
        "hashtags": hashtags,
        "reels_hook": reels_script["hook"],
        "reels_script": reels_script,
        "carousel_flow": [f"Slide {s['slide']}: {s['title']} — {s['body']}" for s in carousel],
        "carousel_slides": carousel,
        "tiktok": tiktok,
        "content_value_notes": notes,
        "risk_note": _risk_note(news_item),
        "export_text": export_text,
    }
