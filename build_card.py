"""실물 크기 카드 3D 모델(.glb) 생성기.
사용법: python3 build_card.py front.png back.png out.glb [--portrait]
--portrait: 세로형 카드 (이미지 1080x1712 권장). 기본은 가로형(1712x1080).
이미지를 주지 않으면 샘플 디자인을 그려서 사용한다.
"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import trimesh
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial

PORTRAIT = "--portrait" in sys.argv
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
W, H, T, R = 0.0856, 0.05398, 0.0008, 0.00318   # ISO/IEC 7810 ID-1 (m)
PX = 1712, 1080
if PORTRAIT:
    W, H, PX = H, W, (1080, 1712)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def font(size):
    return ImageFont.truetype(FONT, size, index=1)  # KR


def sample_front():
    w, h = PX
    img = Image.new("RGB", PX)
    a = np.linspace(0, 1, w)[None, :, None]
    b = np.linspace(0, 1, h)[:, None, None]
    c1, c2, c3 = np.array([18, 24, 38]), np.array([30, 60, 90]), np.array([120, 200, 190])
    t = np.clip(a * 0.7 + b * 0.3, 0, 1)
    arr = c1 * (1 - t) + c2 * t
    glow = np.exp(-(((a - 0.85) ** 2) / 0.05 + ((b - 0.15) ** 2) / 0.08))
    arr = arr * (1 - glow * 0.6) + c3 * glow * 0.6
    img = Image.fromarray(arr.astype("uint8"))
    d = ImageDraw.Draw(img)
    # 칩
    cx, cy = 150, 400
    d.rounded_rectangle([cx, cy, cx + 200, cy + 150], 24, fill=(212, 182, 110), outline=(160, 130, 70), width=4)
    for yy in (cy + 50, cy + 100):
        d.line([cx, yy, cx + 200, yy], fill=(160, 130, 70), width=4)
    d.line([cx + 100, cy, cx + 100, cy + 150], fill=(160, 130, 70), width=4)
    # 비접촉 아이콘
    for i, r in enumerate((30, 55, 80)):
        d.arc([400 - r, 475 - r, 400 + r, 475 + r], -45, 45, fill=(230, 235, 240), width=8)
    d.text((150, 120), "SAMPLE BANK", font=font(84), fill=(240, 244, 248))
    d.text((150, 760), "1234  5678  9012  3456", font=font(76), fill=(240, 244, 248))
    d.text((150, 890), "JUNG JINYOUNG", font=font(52), fill=(200, 210, 220))
    d.text((1360, 890), "12/30", font=font(52), fill=(200, 210, 220))
    # 브랜드 원
    d.rounded_rectangle([1400, 120, 1560, 240], 30, outline=(240, 244, 248), width=10)
    d.ellipse([1455, 155, 1505, 205], fill=(120, 220, 200))
    return img


def sample_back():
    img = Image.new("RGB", PX, (26, 34, 50))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 110, PX[0], 300], fill=(10, 10, 12))          # 마그네틱 띠
    d.rectangle([150, 400, 1200, 520], fill=(235, 235, 230))       # 서명란
    d.text((1240, 425), "123", font=font(64), fill=(240, 244, 248))
    d.text((150, 620), "이 카드는 AR 시연용 샘플입니다.", font=font(48), fill=(190, 200, 212))
    d.text((150, 700), "SAMPLE BANK  ·  1588-0000", font=font(40), fill=(150, 162, 178))
    return img


def outline(n=12):
    """둥근 모서리 사각형 외곽선 (반시계)."""
    pts = []
    corners = [(W/2 - R, R, -90), (W/2 - R, H - R, 0), (-W/2 + R, H - R, 90), (-W/2 + R, R, 180)]
    for cx, cy, start in corners:
        for i in range(n + 1):
            ang = math.radians(start + 90 * i / n)
            pts.append((cx + R * math.cos(ang), cy + R * math.sin(ang)))
    return np.array(pts)


def face(pts, z, img, back=False):
    n = len(pts)
    center = np.array([[0, H / 2]])
    xy = np.vstack([center, pts])
    v = np.column_stack([xy, np.full(n + 1, z)])
    f = [[0, i + 1, (i + 1) % n + 1] for i in range(n)]
    f = np.array(f)
    if back:
        f = f[:, ::-1]
    u = (xy[:, 0] + W / 2) / W
    if back:
        u = 1 - u
    uv = np.column_stack([u, xy[:, 1] / H])
    mat = PBRMaterial(baseColorTexture=img, metallicFactor=0.15, roughnessFactor=0.35)
    return trimesh.Trimesh(v, f, visual=TextureVisuals(uv=uv, material=mat), process=False)


def edge(pts):
    n = len(pts)
    v = np.vstack([np.column_stack([pts, np.full(n, T / 2)]), np.column_stack([pts, np.full(n, -T / 2)])])
    f = []
    for i in range(n):
        j = (i + 1) % n
        f += [[i, n + i, j], [j, n + i, n + j]]
    m = trimesh.Trimesh(v, np.array(f), process=False)
    m.visual = TextureVisuals(material=PBRMaterial(baseColorFactor=[200, 205, 215, 255], metallicFactor=0.6, roughnessFactor=0.3))
    return m


def main():
    front = Image.open(ARGS[0]).convert("RGB").resize(PX) if len(ARGS) > 0 else sample_front()
    back = Image.open(ARGS[1]).convert("RGB").resize(PX) if len(ARGS) > 1 else sample_back()
    out = ARGS[2] if len(ARGS) > 2 else "card.glb"
    pts = outline()
    scene = trimesh.Scene()
    scene.add_geometry(face(pts, T / 2, front), node_name="front")
    scene.add_geometry(face(pts, -T / 2, back, back=True), node_name="back")
    scene.add_geometry(edge(pts), node_name="edge")
    scene.export(out)
    print(out, "written")


if __name__ == "__main__":
    main()
