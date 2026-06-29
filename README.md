# Sinyor Futbol

**Sinyor Futbol** is a desktop football content R&D panel that tracks football headlines, generates AI-powered social media content (posts, carousels, and reels) ready for Instagram/TikTok, and analyzes the target audience, format, risk, credibility, and publishing value of that content.

This package is an **MVP project skeleton**. Real news sources, paid APIs, advanced visual manipulation, and LLM integration are designed to be modular and connected later.

## What's Included?

- Streamlit desktop panel
- News/headline collection simulation
- Content structure focused on clubs, leagues, national teams, and World Cup
- Post, carousel, and reels text generation module
- Simple manipulation-based visual style engine
- Content R&D analysis panel
- AI assistant daily report logic
- Export folder structure

## Installation

```bash
cd sinyor_futbol_project/app
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

If the panel doesn't open, navigate to this URL in your browser:

```text
http://localhost:8501
```

## OpenAI / LLM Integration

This MVP generates mock content by default. To use real AI, copy `.env.example` to `.env`, add your API key, and uncomment the relevant section in `modules/content/ai_writer.py`.

## Project Vision

Sinyor Futbol's ultimate goal is to be:

> An AI-powered desktop panel that tracks football headlines, analyzes breaking news, generates brand-aligned social media content, and measures the content's potential reach—all while helping content creators understand the story behind the story.
