"""Generate Urdu overlay PNGs (title, chapters, badge, end card) with Pillow.
Naskh + arabic_reshaper (Nastaliq needs HarfBuzz/raqm, unavailable -> tofu)."""
import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

NB = "work/fonts/NaskhBold.ttf"
NR = "work/fonts/Naskh.ttf"
EN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ENR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W, H = 1280, 720
OUT = "work/overlays"
GOLD = (255, 200, 60)

def ur(draw, xy, text, font, fill, anchor="ra"):
    draw.text(xy, get_display(arabic_reshaper.reshape(text)), font=font, fill=fill, anchor=anchor)

def f(path, size):
    return ImageFont.truetype(path, size)

# ---------- Title card ----------
img = Image.new("RGB", (W, H), (12, 10, 18))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 10], fill=GOLD); d.rectangle([0, H - 10, W, H], fill=GOLD)
ur(d, (W - 90, 140), "مٹی دے باوے", f(NB, 96), GOLD)
ur(d, (W - 90, 280), "قسط نمبر 10 : مکمل خلاصہ و تبصرہ", f(NB, 54), (255, 255, 255))
ur(d, (W - 90, 395), "بلو بڑی سرکار بنے گی؟ بالا کا نیا عشق؟", f(NR, 42), (225, 225, 225))
d.text((90, 560), "MITTI DE BAWAY Ep 10 | Urdu Summary & Review", font=f(EN, 28), fill=(190, 190, 190))
img.save(f"{OUT}/title.png")

# ---------- Badge (persistent review framing, top-center in render) ----------
badge = Image.new("RGBA", (520, 56), (0, 0, 0, 165))
d = ImageDraw.Draw(badge)
d.rectangle([0, 50, 520, 56], fill=GOLD + (255,))
ur(d, (505, 6), "خلاصہ و تبصرہ", f(NB, 34), GOLD, anchor="ra")
d.text((14, 13), "SUMMARY & REVIEW", font=f(EN, 22), fill=(255, 255, 255))
badge.save(f"{OUT}/badge.png")

# ---------- Chapter lower-thirds ----------
chapters = [
    "بلو کی چونکا دینے والی پیشکش", "بلو یہاں تک کیسے پہنچی؟", "پناہ کی تلاش",
    "شاطر یا مجبور؟", "زرینہ کا شک", "اپنے گھر میں مہمان", "بالا کی تاریک دنیا",
    "غلام رسول کی موت", "ٹرک کا راز", "غربت میں خودداری", "ٹوٹتا گھر، بنتا مقام",
    "اگلی جنگ: گدی بمقابلہ بندوق",
]
for i, ch in enumerate(chapters, 1):
    bar = Image.new("RGBA", (W, 100), (0, 0, 0, 0))
    d = ImageDraw.Draw(bar)
    d.rectangle([0, 14, W, 100], fill=(0, 0, 0, 175))
    d.rectangle([W - 14, 14, W, 100], fill=GOLD + (255,))
    ur(d, (W - 42, 57), ch, f(NB, 46), (255, 255, 255), anchor="rm")
    d.text((24, 38), f"PART {i}/12", font=f(EN, 26), fill=GOLD)
    bar.save(f"{OUT}/chapter_{i:02d}.png")

# ---------- End card ----------
img = Image.new("RGB", (W, H), (12, 10, 18))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, W, 10], fill=GOLD); d.rectangle([0, H - 10, W, H], fill=GOLD)
ur(d, (W - 90, 110), "مکمل قسط ضرور دیکھیں", f(NB, 66), GOLD)
ur(d, (W - 90, 230), "گرین ٹی وی کے آفیشل یوٹیوب چینل پر", f(NR, 42), (255, 255, 255))
ur(d, (W - 90, 330), "بلو شاطر ہے یا مجبور؟ کمنٹ میں بتائیں", f(NR, 40), (225, 225, 225))
lines = [
    "Fair Use (17 U.S.C. Section 107): This video is an original transformative",
    "summary, criticism & review. All drama footage belongs to Green Entertainment",
    "/ respective copyright owners. No copyright infringement intended.",
]
y = 500
for ln in lines:
    d.text((90, y), ln, font=f(ENR, 24), fill=(175, 175, 175)); y += 36
img.save(f"{OUT}/end.png")

# ---------- YouTube thumbnail (1280x720) ----------
try:
    base = Image.open("work/frames/hook1_peer_proposal_0630.jpg").convert("RGB").resize((W, H))
except Exception:
    base = Image.new("RGB", (W, H), (20, 16, 24))
d = ImageDraw.Draw(base, "RGBA")
d.rectangle([0, H - 300, W, H], fill=(0, 0, 0, 185))
d.rectangle([0, H - 300, W, H - 288], fill=GOLD + (255,))
ur(d, (W - 40, H - 265), "بلو بڑی سرکار بن گئی؟", f(NB, 74), (255, 255, 255))
ur(d, (W - 40, H - 160), "مٹی دے باوے قسط 10 : مکمل خلاصہ", f(NB, 50), GOLD)
d.rectangle([28, 26, 330, 96], fill=(190, 0, 0, 235))
d.text((48, 42), "EP 10 TWIST!", font=f(EN, 36), fill=(255, 255, 255))
base.save("output/thumbnail.jpg", quality=92)
print("overlays + thumbnail done")
