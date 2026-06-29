import streamlit as st
import pandas as pd

from modules.collectors.mock_collector import collect_mock_news
from modules.collectors.rss_collector import collect_rss_news
from modules.collectors.match_stats_collector import (
    build_news_item_from_match_stats,
    collect_match_stats,
)
from modules.content.ai_writer import generate_content_package
from modules.design.style_engine import choose_style
from modules.design.image_composer import create_post_image
from modules.research_center.content_analyzer import analyze_content
from modules.assistant.daily_briefing import build_daily_briefing
from modules.media.article_summarizer import extract_article_summary
from modules.media.web_image_fetcher import fetch_relevant_image
from modules.vision.key_moment_detector import (
    create_demo_football_frame,
    process_key_visual_moment,
)

st.set_page_config(
    page_title="Sinyor Futbol",
    page_icon="⚽",
    layout="wide",
)

# --- STANDART STREAMLIT İMZALARINI GİZLEME CSS KODU ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
# -----------------------------------------------------

st.sidebar.title("⚽ Sinyor Futbol")
st.sidebar.caption("AI futbol içerik Ar-Ge paneli")

# Ayarlar ve diğer ekstra sekmeler menüden kaldırıldı
section = st.sidebar.radio(
    "Panel",
    [
        "Ana Panel",
        "Gündem",
        "İçerik Üret",
    ],
)

# İlk açılışta canlı RSS gündemi çekmeyi dener.
# Başarısız olursa demo/mock gündeme döner.
if "news" not in st.session_state:
    try:
        st.session_state.news = collect_rss_news()
    except Exception:
        st.session_state.news = collect_mock_news()

if "packages" not in st.session_state:
    st.session_state.packages = []


if section == "Ana Panel":
    st.title("Sinyor Futbol")
    st.subheader("Futbol gündemini içeriğe çeviren AI Ar-Ge paneli")

    # Metrikleri çerçeve içine alıyoruz
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Taranan Haber", len(st.session_state.news))
        col2.metric("Üretilen Paket", len(st.session_state.packages))
        col3.metric("Aktif Format", "Post / Carousel")
        col4.metric("Paylaşım Modu", "Manuel Export")

    st.info(
        "Bu MVP otomatik paylaşım yapmaz. İçerik, görsel, caption ve analiz üretir; paylaşımı sen manuel yaparsın."
    )

    # Özeti çerçeve içine alıyoruz
    with st.container(border=True):
        st.markdown("### 📋 Bugünün kısa özeti")
        st.write(build_daily_briefing(st.session_state.news, st.session_state.packages))


elif section == "Gündem":
    st.title("Gündem Takip")
    st.caption("Kulüp, lig, milli takım ve Dünya Kupası haberlerini canlı RSS veya demo veriyle listeler.")

    with st.container(border=True):
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("Canlı Gündemi Çek", use_container_width=True):
                try:
                    st.session_state.news = collect_rss_news()
                    st.success("Canlı gündem çekildi.")
                except Exception as e:
                    st.error(f"Canlı gündem çekilemedi: {e}")

        with col_b:
            if st.button("Demo Gündem Yükle", use_container_width=True):
                st.session_state.news = collect_mock_news()
                st.success("Demo gündem yüklendi.")

    if not st.session_state.news:
        st.warning("Henüz haber bulunamadı. Canlı gündem çekmeyi veya demo gündem yüklemeyi dene.")
    else:
        df = pd.DataFrame(st.session_state.news)

        preferred_columns = [
            "title",
            "entity",
            "type",
            "category",
            "source",
            "published_at",
            "reliability_score",
            "summary",
            "url",
        ]

        existing_columns = [c for c in preferred_columns if c in df.columns]
        df = df[existing_columns]

        st.dataframe(df, use_container_width=True)


elif section == "İçerik Üret":
    st.title("İçerik Üret")
    st.caption("Seçilen futbol gündeminden post ve carousel içerik paketi üret.")

    if not st.session_state.news:
        st.warning("İçerik üretmek için önce Gündem sekmesinden haber çek.")
    else:
        news_titles = [n["title"] for n in st.session_state.news]
        selected_title = st.selectbox("İçerik üretilecek gündem", news_titles)
        selected_news = next(n for n in st.session_state.news if n["title"] == selected_title)

        with st.container(border=True):
            st.markdown("### 📰 Seçilen Gündem")

            col_info_1, col_info_2, col_info_3 = st.columns(3)
            col_info_1.metric("Kategori", selected_news.get("category", "Bilinmiyor"))
            col_info_2.metric("Varlık", selected_news.get("entity", "Genel Futbol"))
            col_info_3.metric("Güvenilirlik", selected_news.get("reliability_score", 60))

            st.write(selected_news.get("summary", selected_news.get("title", "")))

            if selected_news.get("url"):
                st.link_button("Haberi Aç", selected_news["url"])

        st.divider()

        with st.container(border=True):
            col_a, col_b = st.columns(2)

            with col_a:
                tone = st.selectbox(
                    "Ton",
                    [
                        "Analitik ama taraftar dili",
                        "Sakin ve net",
                        "Heyecanlı ama temkinli",
                        "Ciddi editoryal",
                        "Mizahi ama kontrollü",
                    ],
                )

            with col_b:
                content_format = st.selectbox(
                    "Format",
                    ["Tek Görsel Post", "Carousel"],
                )

            if st.button("İçerik Paketi Üret", type="primary", use_container_width=True):
                selected_news_for_content = dict(selected_news)
                with st.spinner("Haber sayfasindan kisa ozet cikariliyor..."):
                    article_summary = extract_article_summary(
                        selected_news.get("url", ""),
                        f"{selected_news.get('title', '')}. {selected_news.get('summary', '')}",
                    )
                    selected_news_for_content["article_summary"] = article_summary["summary"]
                    selected_news_for_content["article_summary_source"] = article_summary["source"]

                package = generate_content_package(selected_news_for_content, tone, content_format)
                package["article_summary"] = article_summary
                package["style"] = choose_style(selected_news_for_content, content_format)
                with st.spinner("Haberle ilgili web gorseli araniyor..."):
                    package["web_image"] = fetch_relevant_image(selected_news_for_content)
                package["analysis"] = analyze_content(package, selected_news_for_content)

                image_path = create_post_image(package)
                package["image_path"] = image_path

                st.session_state.packages.append(package)
                st.success("İçerik paketi üretildi.")

        if st.session_state.packages:
            st.divider()
            st.markdown("## ✨ Son Üretilen İçerik Paketi")

            package = st.session_state.packages[-1]

            tab_overview, tab_caption, tab_carousel, tab_export = st.tabs(
                [
                    "Özet",
                    "Caption",
                    "Carousel",
                    "Export",
                ]
            )

            with tab_overview:
                with st.container(border=True):
                    web_image = package.get("web_image", {})
                    if web_image.get("image_path"):
                        st.image(
                            web_image["image_path"],
                            caption=f"{web_image.get('query', '')} / {web_image.get('source', '')}",
                            width=420,
                        )
                    else:
                        st.warning("Bu haber icin ilgili web fotografi bulunamadi.")
                        attempts = web_image.get("attempts", [])
                        if attempts:
                            st.caption("Gorsel arama denemeleri: " + " | ".join(attempts[:2]))

            with tab_caption:
                with st.container(border=True):
                    st.markdown("### Instagram Caption")
                    article_summary = package.get("article_summary", {})
                    if article_summary.get("summary"):
                        st.caption(f"Ozet kaynagi: {article_summary.get('source', 'bilinmiyor')}")
                    st.write(package["caption"])

                    st.markdown("### Hashtag")
                    st.code(package["hashtags"])

            with tab_carousel:
                if "carousel_slides" in package and package["carousel_slides"]:
                    for slide in package["carousel_slides"]:
                        with st.container(border=True):
                            st.markdown(f"**Slide {slide['slide']}: {slide['title']}**")
                            st.write(slide["body"])
                else:
                    st.info("Bu içerik Tek Görsel Post formatında üretildiği için Carousel akışı bulunmuyor.")

            with tab_export:
                st.markdown("### Paylaşmaya Hazır İçerik Paketi")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    st.download_button(
                        label="📄 TXT Olarak İndir",
                        data=package["export_text"],
                        file_name="sinyor_futbol_icerik_paketi.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with col_btn2:
                    try:
                        with open(package["image_path"], "rb") as img_file:
                            st.download_button(
                                label="🖼️ PNG Olarak İndir",
                                data=img_file,
                                file_name="sinyor_futbol_post.png",
                                mime="image/png",
                                use_container_width=True
                            )
                    except Exception:
                        st.warning("Görsel dosyası okunamadı.")

                # Ham paket akordeon içine gizlendi ve yazım hatası düzeltildi
                with st.expander("Ham Paketi Görüntüle / Kopyala"):
                    st.text_area(
                        "Kopyalanabilir paket",
                        package["export_text"],
                        height=420,
                        label_visibility="collapsed"
                    )