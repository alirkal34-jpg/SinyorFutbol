from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
import uuid

OUTPUT_DIR = Path("output/posts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _font(size):
    # Ortamda font yoksa PIL default font kullanır.
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()

def create_post_image(package):
    """Basit 1080x1350 post görseli üretir."""
    style = package["style"]
    w, h = 1080, 1350
    img = Image.new("RGB", (w, h), style["background"])
    draw = ImageDraw.Draw(img)

    accent = style["accent"]
    text_color = style["text"]

    # Accent bar
    draw.rectangle([0, 0, 28, h], fill=accent)
    draw.rectangle([60, 70, 420, 118], outline=accent, width=3)
    draw.text((85, 82), "SINYOR FUTBOL", fill=text_color, font=_font(28))

    # Category
    category = package["source_news"]["category"].upper()
    draw.text((70, 175), category, fill=accent, font=_font(34))

    # Headline
    headline = package["headline"]
    lines = textwrap.wrap(headline, width=16)
    y = 280
    for line in lines[:4]:
        draw.text((70, y), line, fill=text_color, font=_font(78))
        y += 92

    # Minimal manipulation area: use processed key visual when the prototype provides one.
    visual_asset = package.get("visual_asset", {})
    web_image = package.get("web_image", {})
    visual_path = visual_asset.get("processed_image_path") or web_image.get("image_path")
    if visual_path:
        try:
            visual = Image.open(visual_path).convert("RGB")
            visual = ImageOps.fit(visual, (360, 360))
            img.paste(visual, (670, 560))
            draw.rectangle([670, 560, 1030, 920], outline=accent, width=5)
        except Exception:
            visual_path = None

    if not visual_path:
        draw.ellipse([650, 420, 1180, 960], outline=accent, width=8)
        draw.rectangle([690, 610, 1010, 930], outline="#333333", width=5)
        draw.text((725, 735), "PLAYER\nCUTOUT\nAREA", fill="#666666", font=_font(40), spacing=12)

    # Short comment box
    comment = package["short_comment"]
    comment_lines = textwrap.wrap(comment, width=48)
    box_y = 1030
    draw.rectangle([70, box_y, 1010, 1230], fill="#1B1B1B", outline="#2A2A2A", width=2)
    y = box_y + 34
    for line in comment_lines[:4]:
        draw.text((105, y), line, fill="#DDDDDD", font=_font(30))
        y += 42

    draw.text((70, 1275), "@sinyorfutbol • paylaşmaya hazır içerik paketi", fill="#777777", font=_font(24))

    path = OUTPUT_DIR / f"sinyor_futbol_{uuid.uuid4().hex[:8]}.png"
    img.save(path)
    return str(path)
