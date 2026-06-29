# Sinyor Futbol

**Sinyor Futbol**, futbol gündemini takip eden, yapay zekâ desteğiyle Instagram/TikTok için paylaşmaya hazır post, carousel ve reels içerikleri üreten; ayrıca bu içeriklerin hedef kitle, format, risk, güvenilirlik ve yayın değerini analiz eden masaüstü futbol içerik Ar-Ge panelidir.

Bu paket bir **MVP proje iskeletidir**. Gerçek haber kaynakları, ücretli API'ler, gelişmiş görsel manipülasyon ve LLM entegrasyonu daha sonra bağlanacak şekilde modüler hazırlanmıştır.

## Ne var?

- Bilgisayarda çalışan Streamlit panel
- Gündem / haber toplama simülasyonu
- Kulüp, lig, milli takım ve Dünya Kupası odaklı içerik yapısı
- Post, carousel, reels metni üretim modülü
- Sade-manipülasyon temelli görsel stil motoru
- İçerik Ar-Ge analiz paneli
- AI asistan günlük rapor mantığı
- Export klasör yapısı

## Kurulum

```bash
cd sinyor_futbol_project/app
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Bağımlılıkları kur:

```bash
pip install -r requirements.txt
```

Çalıştır:

```bash
streamlit run app.py
```

Panel açılmazsa tarayıcıdan şu adrese git:

```text
http://localhost:8501
```

## OpenAI / LLM entegrasyonu

Bu MVP varsayılan olarak mock içerik üretir. Gerçek AI kullanmak için `.env.example` dosyasını `.env` olarak kopyalayıp API anahtarını girmen ve `modules/content/ai_writer.py` dosyasındaki ilgili yeri açman gerekir.

## Proje vizyonu

Sinyor Futbol'un nihai hedefi:

> Futbol gündemini takip eden, güncel haberleri analiz eden, marka kimliğine uygun sosyal medya içerikleri üreten ve bu içeriklerin kitleye ulaşma potansiyelini ölçen yapay zekâ destekli futbol medya Ar-Ge paneli olmak.
