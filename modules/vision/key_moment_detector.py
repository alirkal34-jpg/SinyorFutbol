from pathlib import Path
import uuid

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


OUTPUT_DIR = Path("output/vision")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_demo_football_frame():
    """Creates a simple football-like frame for the integrated prototype demo."""
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), "#2f7d32")
    draw = ImageDraw.Draw(image)

    draw.rectangle([40, 40, width - 40, height - 40], outline="#f4f4f4", width=5)
    draw.line([width // 2, 40, width // 2, height - 40], fill="#f4f4f4", width=4)
    draw.ellipse([width // 2 - 80, height // 2 - 80, width // 2 + 80, height // 2 + 80], outline="#f4f4f4", width=4)

    players = [
        (360, 310, "#e30a17"),
        (425, 350, "#e30a17"),
        (785, 325, "#f2f2f2"),
        (850, 360, "#f2f2f2"),
        (675, 340, "#111111"),
    ]
    for x, y, color in players:
        draw.ellipse([x - 18, y - 18, x + 18, y + 18], fill=color)
        draw.rectangle([x - 13, y + 18, x + 13, y + 72], fill=color)

    draw.ellipse([625, 365, 645, 385], fill="#f8f8f8")
    path = OUTPUT_DIR / "demo_football_frame.png"
    image.save(path)
    return str(path)


def _load_cv2():
    try:
        import cv2

        return cv2
    except Exception:
        return None


def _clamp_crop(x, y, w, h, image_w, image_h):
    pad = 90
    left = max(0, x - pad)
    top = max(0, y - pad)
    right = min(image_w, x + w + pad)
    bottom = min(image_h, y + h + pad)
    return left, top, right, bottom


def _fallback_center_crop(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    crop_w = int(width * 0.62)
    crop_h = int(height * 0.72)
    left = (width - crop_w) // 2
    top = (height - crop_h) // 2
    crop = image.crop((left, top, left + crop_w, top + crop_h))
    crop = crop.filter(ImageFilter.SHARPEN)

    output_path = OUTPUT_DIR / f"key_moment_{uuid.uuid4().hex[:8]}.png"
    crop.save(output_path)

    return {
        "processed_image_path": str(output_path),
        "method": "Pillow fallback center crop",
        "confidence": 0.55,
        "detected_elements": ["center field region"],
        "crop_box": [left, top, left + crop_w, top + crop_h],
    }


def process_key_visual_moment(image_path):
    """
    Detects a visually important football region and exports a cropped key moment.
    Uses OpenCV when available, then falls back to a deterministic center crop.
    """
    cv2 = _load_cv2()
    if cv2 is None:
        return _fallback_center_crop(image_path)

    image = cv2.imread(str(image_path))
    if image is None:
        return _fallback_center_crop(image_path)

    height, width = image.shape[:2]
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Football pitch mask: isolate green areas, then look for strong foreground edges.
    lower_green = np.array([35, 35, 35])
    upper_green = np.array([90, 255, 255])
    pitch_mask = cv2.inRange(hsv, lower_green, upper_green)
    pitch_mask = cv2.medianBlur(pitch_mask, 7)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 70, 160)
    foreground = cv2.bitwise_and(edges, cv2.bitwise_not(pitch_mask))
    foreground = cv2.dilate(foreground, np.ones((9, 9), np.uint8), iterations=2)

    contours, _ = cv2.findContours(foreground, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if 250 < area < width * height * 0.90:
            candidates.append((area, x, y, w, h))

    if not candidates:
        object_mask = cv2.bitwise_not(pitch_mask)
        object_mask = cv2.morphologyEx(object_mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        contours, _ = cv2.findContours(object_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            if 250 < area < width * height * 0.90:
                candidates.append((area, x, y, w, h))

    if not candidates:
        return _fallback_center_crop(image_path)

    candidates.sort(reverse=True)
    _, x, y, w, h = candidates[0]
    left, top, right, bottom = _clamp_crop(x, y, w, h, width, height)

    crop = image[top:bottom, left:right]
    crop = cv2.detailEnhance(crop, sigma_s=8, sigma_r=0.12)

    output_path = OUTPUT_DIR / f"key_moment_{uuid.uuid4().hex[:8]}.png"
    cv2.imwrite(str(output_path), crop)

    confidence = min(0.95, 0.62 + (len(candidates) * 0.03))
    return {
        "processed_image_path": str(output_path),
        "method": "OpenCV pitch mask + foreground contour crop",
        "confidence": round(confidence, 2),
        "detected_elements": ["pitch region", "foreground edges", "key visual crop"],
        "crop_box": [int(left), int(top), int(right), int(bottom)],
    }
