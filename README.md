# ⚽ Sinyor Futbol

<div align="center">

**AI-powered football content R&D panel**  
Transform breaking football news into publication-ready social media content

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-MVP-yellow)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Demo](#-demo)

</div>

---

## 📌 What is Sinyor Futbol?

**Sinyor Futbol** is a desktop content creation and R&D platform designed for football content creators and editorial teams. It bridges the gap between **breaking football news** and **social media-ready content**.

The platform:
- **Tracks** football headlines across clubs, leagues, national teams, and tournaments
- **Analyzes** content for audience fit, engagement potential, and reliability
- **Generates** publication-ready posts, carousels, and short-form scripts
- **Scores** content by virality, brand alignment, and audience engagement potential
- **Exports** content packages with visuals, captions, and editorial notes

Perfect for:
- 🎬 Content creators managing multi-platform presence
- 📊 Editorial teams conducting content research
- 🤖 AI integration experiments
- 🧪 MVP development and prototyping

---

## ✨ Features

### Core Capabilities
- **📰 Headline Collection** - Mock news simulation (ready for real API integration)
- **🎯 Smart Categorization** - Auto-tags content by: transfers, matches, tournaments, club news, national teams
- **✍️ Multi-Format Generation**
  - Instagram captions & carousels
  - TikTok/Reels scripts with voiceover hooks
  - Hashtag packages
  - Content angle briefings
- **🎨 Visual Style Engine** - Simple, editorial-focused image composition
- **📊 Content Analytics Dashboard**
  - Engagement score prediction
  - Virality potential estimation
  - Audience fit analysis
  - Brand alignment verification
- **🤖 AI Assistant** - Daily briefing and content value analysis
- **💾 Smart Export** - One-click content package export with all assets

### Design Philosophy
- **Clean & Editorial** - Minimal manipulation, maximum clarity
- **Decisive** - Bold headlines, confident tone
- **On-brand** - Consistent visual and editorial identity
- **Accessible** - Distraction-free interface focused on output

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip / virtualenv

### Installation

```bash
# Clone the repository
git clone https://github.com/alirkal34-jpg/SinyorFutbol.git
cd SinyorFutbol

# Navigate to app directory
cd sinyor_futbol_project/app

# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run app.py
```

The panel will open at `http://localhost:8501`

---

## 📖 Usage Guide

### 1. **Load Headlines**
   - Click "Gündem" (Headlines) tab
   - Choose between:
     - **Demo Mode**: Load mock football news
     - **Live Feed**: Connect to RSS sources (coming soon)

### 2. **Browse & Analyze**
   - View categorized headlines with reliability scores
   - Filter by team, league, or content type
   - See engagement predictions and audience fit analysis

### 3. **Generate Content**
   - Select a headline
   - Choose content format (Post / Carousel / Reels)
   - Select tone (Analytical / Enthusiastic / Breaking News)
   - AI generates captions, scripts, and hashtags in seconds

### 4. **Review & Export**
   - Preview generated content with proposed visuals
   - Adjust copy or formatting as needed
   - Export complete content package (all formats, metadata, analysis)

### 5. **Multi-Platform Publishing** *(Coming Soon)*
   - Direct integration with Instagram/TikTok APIs
   - Scheduled posting
   - Performance tracking

---

## 🏗️ Architecture

```
sinyor_futbol_project/
├── app.py                          # Main Streamlit app
├── modules/
│   ├── collectors/                 # News collection engines
│   │   ├── mock_collector.py       # Demo data generation
│   │   ├── rss_collector.py        # RSS feed parser
│   │   └── match_stats_collector.py# Football match data
│   ├── content/                    # Content generation
│   │   └── ai_writer.py            # Copy + format logic
│   ├── design/                     # Visual layer
│   │   ├── style_engine.py         # Design system
│   │   └── image_composer.py       # Image generation
│   ├── research_center/            # Analytics & scoring
│   │   └── content_analyzer.py     # Content valuation
│   ├── assistant/                  # AI features
│   │   └── daily_briefing.py       # Briefing generation
│   ├── media/                      # Media handling
│   │   ├── web_image_fetcher.py    # Image download
│   │   └── article_summarizer.py   # Text extraction
│   └── vision/                     # Visual intelligence
│       └── key_moment_detector.py  # Key frame detection
└── requirements.txt                # Dependencies
```

### Module Breakdown

| Module | Purpose | Status |
|--------|---------|--------|
| **Collectors** | Fetch football news | MVP (mock data) |
| **Content Generator** | Create captions/scripts | MVP (rule-based) |
| **Style Engine** | Visual design & composition | MVP (template-based) |
| **Research Center** | Score & analyze content | MVP (formula-based) |
| **Vision** | Extract key moments | Prototype |
| **Assistant** | Daily briefing & insights | MVP |

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in `sinyor_futbol_project/app/` to configure API keys:

```bash
# OpenAI Integration (Optional)
OPENAI_API_KEY=your_api_key_here

# News Sources (Optional)
RSS_FEEDS=https://example.com/feed1,https://example.com/feed2

# Image Search (Optional)
UNSPLASH_API_KEY=your_key_here
```

**Default behavior**: All features work with mock data. Real API integration is optional.

---

## 🚀 Roadmap

### Phase 1 (Current - MVP)
- ✅ Mock news generation
- ✅ Rule-based content creation
- ✅ Template-based visual design
- ✅ Content scoring system
- 🔄 Streamlit UI

### Phase 2 (Q3 2024)
- 🎯 Real news API integration (ESPN, Football-Data.org, etc.)
- 🎯 OpenAI GPT integration for dynamic copy
- 🎯 Advanced image manipulation
- 🎯 Direct platform publishing (Instagram, TikTok)

### Phase 3 (Q4 2024+)
- 📋 Performance tracking & learning
- 📋 User preference learning
- 📋 Multi-account management
- 📋 Team collaboration features

---

## 💡 Use Cases

### 📱 Content Creators
Create 5-10 pieces of publication-ready content per day without manual writing.

### 🏢 Editorial Teams  
Generate content at scale while maintaining brand voice and editorial standards.

### 🧪 AI Researchers
Prototype content generation pipelines with modular, extensible architecture.

### 🎓 Students  
Learn Streamlit, NLP, image processing, and Python in a real-world context.

---

## 🛠️ Development

### Install Dev Dependencies

```bash
pip install -r requirements-dev.txt  # (Testing, linting, etc.)
```

### Run Tests

```bash
pytest tests/
```

### Code Style

```bash
black modules/ app.py
flake8 modules/ app.py
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Update README for new features
- Test your code before submitting

---

## 🐛 Issues & Support

Found a bug? Have a feature request?  
→ [Open an issue](https://github.com/alirkal34-jpg/SinyorFutbol/issues)

---

## 👥 Team

**Sinyor Futbol** was created by content creators and engineers passionate about football and automation.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Football data from mock generators (ready for real API integration)
- Design inspired by modern editorial platforms

---

<div align="center">

**Transform football news into engaging content.**  
Made with ⚽ by [Your Team]

[⬆ back to top](#-sinyor-futbol)

</div>
