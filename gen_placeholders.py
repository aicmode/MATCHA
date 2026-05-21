"""
KISSA MATCHA — プレースホルダー画像生成スクリプト
Pure Python (stdlib only) — 外部ライブラリ不要
"""
import math, struct, zlib, os

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

# ── PNG ライター ──────────────────────────────────────────────
def write_png(path, w, h, pixel_fn):
    def chunk(tag, data):
        crc_input = tag + data
        return (struct.pack(">I", len(data)) + crc_input +
                struct.pack(">I", zlib.crc32(crc_input) & 0xFFFFFFFF))

    rows = []
    for y in range(h):
        row = bytearray(b'\x00')
        for x in range(w):
            r, g, b = pixel_fn(x, y, w, h)
            row += bytearray([
                max(0, min(255, int(r))),
                max(0, min(255, int(g))),
                max(0, min(255, int(b))),
            ])
        rows.append(bytes(row))

    idat = zlib.compress(b"".join(rows), 6)
    png  = (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", idat) +
            chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    kb = len(png) // 1024
    print(f"  ✓ {os.path.basename(path)}  ({w}×{h}  {kb}KB)")

def lerp(a, b, t):
    return a + (b - a) * t

def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, v))

def noise(x, y, seed=0):
    v = math.sin(x * 127.1 + y * 311.7 + seed * 74.3) * 43758.5453
    return v - math.floor(v)

def smooth_noise(x, y, w, h, scale=0.008, seed=0):
    fx, fy = x * scale, y * scale
    return noise(fx, fy, seed)

# ── ヒーロー画像（1920×1080）────────────────────────────────
# 抹茶の深い緑と暗い背景 — 高級感のあるグラデーション
def hero_pixel(x, y, w, h):
    # 暗い森の緑 ベースグラデーション
    t = y / h
    # 上: とても暗い黒緑 → 下: 少し明るい抹茶緑
    base_r = lerp(5,  12, t)
    base_g = lerp(12, 28, t)
    base_b = lerp(8,  15, t)

    # 中央に光のグロー（ゴールド × 抹茶）
    cx, cy = w * 0.5, h * 0.45
    dist = math.sqrt((x - cx)**2 + (y - cy)**2)
    glow_r = max(0.0, 1.0 - dist / (w * 0.38))
    glow_strength = glow_r ** 2.5

    # 抹茶グリーングロー
    base_r += glow_strength * 18
    base_g += glow_strength * 55
    base_b += glow_strength * 20

    # ゴールドアクセント（中央下寄り）
    cy2 = h * 0.6
    dist2 = math.sqrt((x - cx)**2 + (y - cy2)**2)
    gold_r = max(0.0, 1.0 - dist2 / (w * 0.25))
    gold_strength = gold_r ** 3.0
    base_r += gold_strength * 40
    base_g += gold_strength * 30
    base_b += gold_strength * 5

    # テクスチャノイズ（超微細）
    n = smooth_noise(x, y, w, h, scale=0.006, seed=3) * 6
    base_r += n
    base_g += n + 2
    base_b += n

    return clamp(base_r), clamp(base_g), clamp(base_b)

# ── About: 茶畑（800×600）────────────────────────────────
def about_farm_pixel(x, y, w, h):
    t = y / h
    # 茶畑の緑のうね — 水平のラインパターン
    row_wave = math.sin(y * 0.18) * 0.5 + 0.5
    col_wave = math.sin(x * 0.05 + y * 0.03) * 0.3 + 0.7

    # 緑のグラデーション（空 → 茶畑の緑）
    if t < 0.28:  # 空
        base_r = lerp(180, 140, t / 0.28)
        base_g = lerp(195, 175, t / 0.28)
        base_b = lerp(170, 140, t / 0.28)
    else:  # 茶畑
        ft = (t - 0.28) / 0.72
        base_r = lerp(40, 20, ft) * col_wave
        base_g = lerp(95, 50, ft) * col_wave + row_wave * 15
        base_b = lerp(38, 18, ft) * col_wave

    n = smooth_noise(x, y, w, h, scale=0.012, seed=7) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n * 0.5)

# ── About: 職人（800×600）────────────────────────────────
def about_artisan_pixel(x, y, w, h):
    t = y / h
    tx = x / w
    # 暗い和室の雰囲気 — 竹・木の温かみ
    base_r = lerp(35, 20, t)
    base_g = lerp(28, 15, t)
    base_b = lerp(18, 10, t)

    # 光の差し込み（左上から）
    dist = math.sqrt((x - w*0.1)**2 + (y - h*0.0)**2)
    light = max(0.0, 1.0 - dist / (w * 0.7)) ** 1.8
    base_r += light * 60
    base_g += light * 50
    base_b += light * 30

    # 茶碗のシルエット（中央）
    cx, cy = w * 0.5, h * 0.55
    bowl_r = w * 0.22
    bd = math.sqrt((x - cx)**2 + ((y - cy) * 0.7)**2)
    if bd < bowl_r:
        rim = (1.0 - bd / bowl_r) ** 0.5
        base_r = lerp(base_r, 55, rim * 0.6)
        base_g = lerp(base_g, 75, rim * 0.6)
        base_b = lerp(base_b, 45, rim * 0.5)

    n = smooth_noise(x, y, w, h, scale=0.015, seed=2) * 10
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n * 0.6)

# ── Products（600×700）────────────────────────────────
def product_ceremonial_pixel(x, y, w, h):
    # 抹茶パウダー — 深い緑、石の質感
    t = y / h
    tx = x / w
    base_r = lerp(18, 10, t)
    base_g = lerp(45, 28, t)
    base_b = lerp(22, 12, t)

    # ゴールドリム
    cx, cy = w * 0.5, h * 0.48
    dist = math.sqrt((x - cx)**2 + ((y - cy) * 0.85)**2)
    if abs(dist - w * 0.28) < 3:
        frac = 1.0 - abs(dist - w * 0.28) / 3.0
        base_r = lerp(base_r, 201, frac)
        base_g = lerp(base_g, 169, frac)
        base_b = lerp(base_b, 110, frac)
    if dist < w * 0.28:
        inner = (1.0 - dist / (w * 0.28)) ** 0.4
        base_r = lerp(base_r, 60, inner * 0.5)
        base_g = lerp(base_g, 105, inner * 0.5)
        base_b = lerp(base_b, 55, inner * 0.4)

    n = smooth_noise(x, y, w, h, scale=0.02, seed=1) * 12
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n * 0.7)

def product_latte_pixel(x, y, w, h):
    # ラテブレンド — クリーミーな温かみ
    t = y / h
    base_r = lerp(240, 200, t)
    base_g = lerp(228, 185, t)
    base_b = lerp(200, 155, t)

    # ラテの泡のサークル
    cx, cy = w * 0.5, h * 0.45
    dist = math.sqrt((x - cx)**2 + ((y - cy) * 0.9)**2)
    foam_r = w * 0.30
    if dist < foam_r:
        inner = (1.0 - dist / foam_r) ** 0.6
        base_r = lerp(base_r, 90, inner * 0.55)
        base_g = lerp(base_g, 120, inner * 0.55)
        base_b = lerp(base_b, 65, inner * 0.45)

    # マイクロフォームのテクスチャ
    n1 = smooth_noise(x, y, w, h, scale=0.025, seed=5) * 15
    n2 = smooth_noise(x, y, w, h, scale=0.008, seed=9) * 8
    return clamp(base_r + n1 - 7), clamp(base_g + n1 - 5), clamp(base_b + n1 - 3)

def product_tea_set_pixel(x, y, w, h):
    # プレミアム茶器セット — 墨黒の高級感
    t = y / h
    base_r = lerp(22, 10, t)
    base_g = lerp(22, 10, t)
    base_b = lerp(22, 10, t)

    # 光沢（上方向から）
    light_y = y / h
    light_x = abs(x / w - 0.5)
    light = (1.0 - light_y) * (1.0 - light_x * 1.5)
    light = max(0, light) ** 1.5
    base_r += light * 45
    base_g += light * 50
    base_b += light * 42

    # ゴールドアクセントライン（横）
    for gy in [h * 0.35, h * 0.65]:
        if abs(y - gy) < 2:
            frac = 1.0 - abs(y - gy) / 2.0
            base_r = lerp(base_r, 201, frac * 0.8)
            base_g = lerp(base_g, 169, frac * 0.8)
            base_b = lerp(base_b, 110, frac * 0.6)

    n = smooth_noise(x, y, w, h, scale=0.01, seed=4) * 6
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

# ── Experience（1200×600）────────────────────────────────
def experience_pixel(x, y, w, h):
    t = y / h
    tx = x / w
    # 抹茶パウダーがふわっと舞うイメージ
    base_r = lerp(8, 15, t)
    base_g = lerp(20, 38, t)
    base_b = lerp(10, 18, t)

    for i, (bx, by, strength) in enumerate([
        (0.2, 0.4, 0.7), (0.5, 0.3, 0.9), (0.75, 0.6, 0.6), (0.88, 0.35, 0.5)
    ]):
        dist = math.sqrt((tx - bx)**2 + (t - by)**2)
        g = max(0.0, 1.0 - dist / 0.35) ** 2.0 * strength
        base_g += g * 50
        base_r += g * 15

    n = smooth_noise(x, y, w, h, scale=0.007, seed=6) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

# ── Story（1200×700）────────────────────────────────
def story_pixel(x, y, w, h):
    t = y / h
    tx = x / w
    # 茶室の窓から差し込む光 — 畳の質感
    base_r = lerp(38, 18, t)
    base_g = lerp(32, 15, t)
    base_b = lerp(20, 10, t)

    # 光の帯（右上から）
    lx = (x - w * 0.7) / (w * 0.5)
    ly = y / (h * 0.6)
    if 0 <= lx <= 1 and ly < 1:
        beam = max(0.0, 1.0 - abs(lx - 0.5) * 3.0) * max(0.0, 1.0 - ly)
        base_r += beam * 60
        base_g += beam * 55
        base_b += beam * 35

    # 畳のテクスチャ（下半分）
    if t > 0.55:
        stripe = (math.sin(x * 0.12) * 0.5 + 0.5) * 0.15
        weave  = (math.sin(y * 0.18) * 0.5 + 0.5) * 0.1
        base_r += (stripe + weave) * 20
        base_g += (stripe + weave) * 18
        base_b += (stripe + weave) * 10

    n = smooth_noise(x, y, w, h, scale=0.009, seed=8) * 10
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

# ── Gallery（800×600 × 6枚）────────────────────────────────
def gallery_matcha_bowl_pixel(x, y, w, h):
    # 真上から見た抹茶碗
    t = y / h; tx = x / w
    cx, cy = 0.5, 0.5
    dist = math.sqrt((tx - cx)**2 + (t - cy)**2)
    base_r = lerp(10, 6, t)
    base_g = lerp(28, 15, t)
    base_b = lerp(14, 8, t)
    if dist < 0.42:
        inner = (1.0 - dist / 0.42) ** 0.5
        # 抹茶の泡
        froth = smooth_noise(x, y, w, h, scale=0.02, seed=11) * 0.5 + 0.5
        base_g = lerp(base_g, 80 + froth * 30, inner * 0.8)
        base_r = lerp(base_r, 40 + froth * 10, inner * 0.5)
        base_b = lerp(base_b, 35 + froth * 8, inner * 0.4)
    # 陶器のリム
    if 0.40 < dist < 0.46:
        rim = 1.0 - abs(dist - 0.43) / 0.03
        base_r = lerp(base_r, 180, rim * 0.4)
        base_g = lerp(base_g, 160, rim * 0.3)
        base_b = lerp(base_b, 130, rim * 0.25)
    n = smooth_noise(x, y, w, h, scale=0.018, seed=11) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

def gallery_chasen_pixel(x, y, w, h):
    # 茶筅のシルエット — 竹・ゴールドトーン
    t = y / h; tx = x / w
    base_r = lerp(25, 12, t)
    base_g = lerp(22, 10, t)
    base_b = lerp(15, 7, t)
    # 竹の光沢
    for i in range(5):
        bx = 0.3 + i * 0.1
        dist_x = abs(tx - bx)
        if dist_x < 0.012:
            sheen = (1.0 - dist_x / 0.012) ** 1.5 * (1.0 - t) * 0.8
            base_r += sheen * 120
            base_g += sheen * 110
            base_b += sheen * 70
    n = smooth_noise(x, y, w, h, scale=0.01, seed=12) * 10
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

def gallery_tearoom_pixel(x, y, w, h):
    # 茶室の静寂 — 暗く静かな空間
    t = y / h; tx = x / w
    base_r = lerp(20, 8, t)
    base_g = lerp(17, 7, t)
    base_b = lerp(12, 5, t)
    # 障子からの光
    if tx > 0.65:
        light = ((tx - 0.65) / 0.35) ** 1.2 * (1.0 - abs(t - 0.45) * 1.8)
        light = max(0, light)
        base_r += light * 80
        base_g += light * 75
        base_b += light * 55
    n = smooth_noise(x, y, w, h, scale=0.008, seed=13) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

def gallery_latte_pixel(x, y, w, h):
    # 抹茶ラテ（横から）
    t = y / h; tx = x / w
    base_r = lerp(245, 210, t)
    base_g = lerp(235, 195, t)
    base_b = lerp(215, 170, t)
    # ラテの抹茶層
    if t > 0.35:
        ft = (t - 0.35) / 0.65
        base_r = lerp(base_r, 70, ft * 0.7)
        base_g = lerp(base_g, 110, ft * 0.7)
        base_b = lerp(base_b, 60, ft * 0.65)
    # グラスの反射
    for gx in [0.08, 0.92]:
        if abs(tx - gx) < 0.03:
            refl = (1.0 - abs(tx - gx) / 0.03) * 0.4
            base_r = lerp(base_r, 250, refl)
            base_g = lerp(base_g, 250, refl)
            base_b = lerp(base_b, 250, refl)
    n = smooth_noise(x, y, w, h, scale=0.014, seed=14) * 10
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

def gallery_teafield_pixel(x, y, w, h):
    # 茶畑の空撮 — 美しい緑の畝
    t = y / h; tx = x / w
    if t < 0.22:
        base_r = lerp(160, 130, t / 0.22)
        base_g = lerp(185, 155, t / 0.22)
        base_b = lerp(175, 140, t / 0.22)
    else:
        ft = (t - 0.22) / 0.78
        row = math.sin((y * 0.14 + x * 0.03)) * 0.5 + 0.5
        base_r = (lerp(38, 15, ft) + row * 8)
        base_g = (lerp(88, 40, ft) + row * 20)
        base_b = (lerp(35, 12, ft) + row * 6)
    n = smooth_noise(x, y, w, h, scale=0.012, seed=15) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

def gallery_ceramics_pixel(x, y, w, h):
    # 茶器のクローズアップ — 黒の和陶器
    t = y / h; tx = x / w
    base_r = lerp(28, 10, t)
    base_g = lerp(25, 9, t)
    base_b = lerp(20, 7, t)
    # 釉薬の光沢
    cx, cy = 0.45, 0.38
    dist = math.sqrt((tx - cx)**2 + (t - cy)**2)
    glaze = max(0.0, 1.0 - dist / 0.45) ** 2.0
    base_r += glaze * 55
    base_g += glaze * 60
    base_b += glaze * 50
    # ゴールドの金継ぎライン
    kintsugi_y = h * 0.52
    kintsugi_x = lambda yy: w * (0.3 + 0.4 * (yy / h))
    kx = kintsugi_x(y)
    if abs(x - kx) < 2:
        frac = 1.0 - abs(x - kx) / 2.0
        base_r = lerp(base_r, 210, frac * 0.9)
        base_g = lerp(base_g, 170, frac * 0.75)
        base_b = lerp(base_b, 90,  frac * 0.6)
    n = smooth_noise(x, y, w, h, scale=0.01, seed=16) * 8
    return clamp(base_r + n), clamp(base_g + n), clamp(base_b + n)

# ── 生成 ──────────────────────────────────────────────────
print("KISSA MATCHA — 画像生成中...")

write_png(f"{OUT}/hero-matcha.png",       1200, 720, hero_pixel)
write_png(f"{OUT}/about-farm.png",         800, 600, about_farm_pixel)
write_png(f"{OUT}/about-artisan.png",      800, 600, about_artisan_pixel)
write_png(f"{OUT}/product-ceremonial.png", 600, 700, product_ceremonial_pixel)
write_png(f"{OUT}/product-latte-blend.png",600, 700, product_latte_pixel)
write_png(f"{OUT}/product-tea-set.png",    600, 700, product_tea_set_pixel)
write_png(f"{OUT}/experience-bg.png",     1200, 600, experience_pixel)
write_png(f"{OUT}/story-bg.png",          1200, 700, story_pixel)
write_png(f"{OUT}/gallery-01-bowl.png",    800, 600, gallery_matcha_bowl_pixel)
write_png(f"{OUT}/gallery-02-chasen.png",  800, 600, gallery_chasen_pixel)
write_png(f"{OUT}/gallery-03-tearoom.png", 800, 600, gallery_tearoom_pixel)
write_png(f"{OUT}/gallery-04-latte.png",   800, 600, gallery_latte_pixel)
write_png(f"{OUT}/gallery-05-field.png",   800, 600, gallery_teafield_pixel)
write_png(f"{OUT}/gallery-06-ceramics.png",800, 600, gallery_ceramics_pixel)

print("\n完了！14枚の画像を images/ フォルダに生成しました。")
