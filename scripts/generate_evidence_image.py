"""Assemble the preserved screenshots from the historical AWS demonstration."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
OUTPUT = ROOT / "diagrams" / "live_verification_evidence.png"

W, H = 2200, 680
canvas = Image.new("RGB", (W, H), "#0B1522")
draw = ImageDraw.Draw(canvas)

font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 20)
font_badge = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
font_panel = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 17)
font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)
font_code_lg = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 20)

# Top banner
draw.rectangle([0, 0, W, 38], fill="#123B56")
draw.text((20, 9), "AWS DEMONSTRATION EVIDENCE (14 OCTOBER 2026)", fill="#FFFFFF", font=font_title)
draw.text((W - 740, 10), "Historical app: 52.66.212.52  |  Jenkins: 13.127.44.70:8080  |  Commit: c87389e", fill="#5CE1E6", font=font_badge)

pad = 10
header_h = 38
grid_top = header_h + pad
grid_w = (W - 3 * pad) // 2
grid_h = (H - grid_top - 2 * pad) // 2

def draw_card_frame(x, y, w, h, title_text, badge_text, badge_color="#2ECC71"):
    draw.rectangle([x, y, x + w, y + h], fill="#111B27", outline="#253D58", width=2)
    bar_h = 28
    draw.rectangle([x, y, x + w, y + bar_h], fill="#182E46")
    draw.text((x + 10, y + 5), title_text, fill="#FFFFFF", font=font_panel)
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 14
    bx = x + w - bw - 8
    by = y + 4
    draw.rounded_rectangle([bx, by, bx + bw, by + 20], radius=4, fill="#0F1E2E", outline=badge_color, width=1)
    draw.text((bx + 7, by + 2), badge_text, fill=badge_color, font=font_badge)
    return x + 2, y + bar_h + 2, w - 4, h - bar_h - 4

# Load screenshots
im_home = Image.open(SCREENSHOTS / "screenshot_app_home.png")
im_note = Image.open(SCREENSHOTS / "screenshot_app_created_note.png")
im_jenkins = Image.open(SCREENSHOTS / "screenshot_jenkins.png")

# --- PANEL A: Home UI ---
x_a, y_a = pad, grid_top
cx, cy, cw, ch = draw_card_frame(x_a, y_a, grid_w, grid_h, "Panel A: CloudNotes Frontend Screenshot", "UI capture")
crop_a = im_home.crop((180, 60, 1100, 460))
scaled_a = crop_a.resize((cw, ch), Image.Resampling.LANCZOS)
canvas.paste(scaled_a, (cx, cy))

# --- PANEL B: Note Creation & Dynamic DOM Toast ---
x_b, y_b = 2 * pad + grid_w, grid_top
cx, cy, cw, ch = draw_card_frame(x_b, y_b, grid_w, grid_h, "Panel B: Note Creation Screenshot", "Toast shown")
crop_b_cards = im_note.crop((180, 470, 1100, 780))
crop_b_toast = im_note.crop((950, 30, 1260, 95))
scaled_b = crop_b_cards.resize((cw, ch), Image.Resampling.LANCZOS)
canvas.paste(scaled_b, (cx, cy))
tw, th = int(crop_b_toast.width * 1.05), int(crop_b_toast.height * 1.05)
scaled_toast = crop_b_toast.resize((tw, th), Image.Resampling.LANCZOS)
canvas.paste(scaled_toast, (cx + cw - tw - 10, cy + 10))

# --- PANEL C: Clearly labeled transcription of the captured API response ---
x_c, y_c = pad, grid_top + grid_h + pad
cx, cy, cw, ch = draw_card_frame(x_c, y_c, grid_w, grid_h, "Panel C: API Body (Transcribed from Screenshot)", "Transcription")
draw.rectangle([cx, cy, cx + cw, cy + ch], fill="#0A111A")
draw.rounded_rectangle([cx + 25, cy + 45, cx + cw - 25, cy + ch - 45], radius=6, fill="#05090F", outline="#1F364E")
draw.text((cx + 50, cy + 65), '{"status":"ok"}', fill="#2ECC71", font=font_code_lg)

# --- PANEL D: Jenkins Portal ---
x_d, y_d = 2 * pad + grid_w, grid_top + grid_h + pad
cx, cy, cw, ch = draw_card_frame(x_d, y_d, grid_w, grid_h, "Panel D: Jenkins Pipeline Dashboard", "Dashboard")
draw.rectangle([cx, cy, cx + cw, cy + 30], fill="#ECEFF1")
draw.rounded_rectangle([cx + 10, cy + 4, cx + cw - 110, cy + 26], radius=4, fill="#FFFFFF", outline="#CFD8DC")
draw.text((cx + 18, cy + 6), "GET  http://13.127.44.70:8080/", fill="#263238", font=font_code)
scaled_d = im_jenkins.resize((cw, ch - 30), Image.Resampling.LANCZOS)
canvas.paste(scaled_d, (cx, cy + 30))

canvas.save(OUTPUT, "PNG")
print(f"Saved {OUTPUT} with size {canvas.size}")
