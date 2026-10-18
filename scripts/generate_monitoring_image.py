"""Assemble the Grafana and Prometheus monitoring screenshots into a composite evidence graphic."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "screenshots"
OUTPUT = ROOT / "diagrams" / "monitoring_telemetry_evidence.png"

# Canvas dimensions (2200 x 1200 for crisp 2-tier monitoring layout)
W, H = 2200, 1260
canvas = Image.new("RGB", (W, H), "#0B1522")
draw = ImageDraw.Draw(canvas)

font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 22)
font_badge = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 15)
font_panel = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 17)
font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 16)

# Top banner
draw.rectangle([0, 0, W, 42], fill="#123B56")
draw.text((20, 10), "LOCAL DOCKER COMPOSE MONITORING EVIDENCE (GRAFANA & PROMETHEUS)", fill="#FFFFFF", font=font_title)
draw.text((W - 740, 12), "Dashboard UID: cloudnotes-prod  |  Scrape: 15s  |  Target health captured locally", fill="#5CE1E6", font=font_badge)

pad = 12
header_h = 42

def draw_card_frame(x, y, w, h, title_text, badge_text, badge_color="#2ECC71"):
    draw.rectangle([x, y, x + w, y + h], fill="#111B27", outline="#253D58", width=2)
    bar_h = 30
    draw.rectangle([x, y, x + w, y + bar_h], fill="#182E46")
    draw.text((x + 12, y + 6), title_text, fill="#FFFFFF", font=font_panel)
    bbox = font_badge.getbbox(badge_text)
    bw = bbox[2] - bbox[0] + 16
    bx = x + w - bw - 10
    by = y + 5
    draw.rounded_rectangle([bx, by, bx + bw, by + 20], radius=4, fill="#0F1E2E", outline=badge_color, width=1)
    draw.text((bx + 8, by + 2), badge_text, fill=badge_color, font=font_badge)
    return x + 2, y + bar_h + 2, w - 4, h - bar_h - 4

# Load screenshots
im_grafana = Image.open(SCREENSHOTS / "screenshot_grafana_dashboard.png")
im_alerts = Image.open(SCREENSHOTS / "screenshot_prometheus_alerts.png")
im_targets = Image.open(SCREENSHOTS / "screenshot_prometheus_targets.png")

# --- TOP TIER: Grafana Production Dashboard (Full width, cropped clean) ---
top_w = W - 2 * pad
top_h = 740
x_g, y_g = pad, header_h + pad
cx, cy, cw, ch = draw_card_frame(x_g, y_g, top_w, top_h, "Panel A: Grafana Dashboard ('cloudnotes-prod')", "Captured telemetry", "#2ECC71")

# Crop Grafana: exclude left sidebar (start x=165) to maximize dashboard space
crop_grafana = im_grafana.crop((165, 45, 1910, 800))
scaled_grafana = crop_grafana.resize((cw, ch), Image.Resampling.LANCZOS)
canvas.paste(scaled_grafana, (cx, cy))

# --- BOTTOM TIER: 2 Columns (Prometheus Alerts & Target Health) ---
bot_y = y_g + top_h + pad
bot_w = (W - 3 * pad) // 2
bot_h = H - bot_y - pad

# Panel B: Prometheus Alerts
x_b = pad
cx_b, cy_b, cw_b, ch_b = draw_card_frame(x_b, bot_y, bot_w, bot_h, "Panel B: Prometheus Alert Rules (cloudnotes-alerts)", "4 Rules Listed (Inactive)", "#3498DB")
crop_alerts = im_alerts.crop((10, 125, 1450, 420))
scaled_alerts = crop_alerts.resize((cw_b, ch_b), Image.Resampling.LANCZOS)
canvas.paste(scaled_alerts, (cx_b, cy_b))

# Panel C: Prometheus Target Health
x_c = 2 * pad + bot_w
cx_c, cy_c, cw_c, ch_c = draw_card_frame(x_c, bot_y, bot_w, bot_h, "Panel C: Prometheus Targets (Docker Compose)", "2 of 2 Targets UP", "#2ECC71")
crop_targets = im_targets.crop((10, 120, 1450, 420))
scaled_targets = crop_targets.resize((cw_c, ch_c), Image.Resampling.LANCZOS)
canvas.paste(scaled_targets, (cx_c, cy_c))

canvas.save(OUTPUT, "PNG")
print(f"Successfully generated composite monitoring graphic: {OUTPUT} ({canvas.size})")
