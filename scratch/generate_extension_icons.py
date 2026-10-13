import os
from PIL import Image, ImageDraw

def create_shield_icon(size: int) -> Image.Image:
    # High-res rendering scale for anti-aliasing
    scale = 4
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pad = canvas_size * 0.08
    cx = canvas_size / 2.0

    # Shield boundary points
    p_top_left = (pad, pad)
    p_top_right = (canvas_size - pad, pad)
    p_mid_right = (canvas_size - pad, canvas_size * 0.55)
    p_bottom = (cx, canvas_size - pad)
    p_mid_left = (pad, canvas_size * 0.55)

    shield_polygon = [
        p_top_left,
        (canvas_size - pad, pad),
        p_mid_right,
        (canvas_size - pad * 1.5, canvas_size * 0.78),
        p_bottom,
        (pad + pad * 0.5, canvas_size * 0.78),
        p_mid_left,
        p_top_left
    ]

    # Draw dark background shield
    draw.polygon(shield_polygon, fill=(15, 23, 42, 255))

    # Outer neon cyan glow / border
    border_width = max(2, int(canvas_size * 0.045))
    draw.line(shield_polygon, fill=(14, 165, 233, 255), width=border_width, joint="curve")

    # Inner shield accent
    inner_pad = pad + border_width * 1.5
    inner_polygon = [
        (inner_pad, inner_pad),
        (canvas_size - inner_pad, inner_pad),
        (canvas_size - inner_pad, canvas_size * 0.52),
        (cx, canvas_size - inner_pad),
        (inner_pad, canvas_size * 0.52),
        (inner_pad, inner_pad)
    ]
    draw.polygon(inner_polygon, fill=(2, 6, 23, 240))

    # Center stylized AI Radar / Checkmark symbol
    # Left check leg
    c_start = (cx - canvas_size * 0.22, cx + canvas_size * 0.02)
    c_pivot = (cx - canvas_size * 0.04, cx + canvas_size * 0.20)
    c_end   = (cx + canvas_size * 0.25, cx - canvas_size * 0.16)

    check_width = max(2, int(canvas_size * 0.07))
    draw.line([c_start, c_pivot], fill=(56, 189, 248, 255), width=check_width)
    draw.line([c_pivot, c_end], fill=(56, 189, 248, 255), width=check_width)

    # Core glowing dot at pivot
    dot_r = canvas_size * 0.05
    draw.ellipse(
        [c_pivot[0] - dot_r, c_pivot[1] - dot_r, c_pivot[0] + dot_r, c_pivot[1] + dot_r],
        fill=(16, 185, 129, 255)
    )

    # Downsample with Lanczos filter for crisp anti-aliasing
    final_img = img.resize((size, size), Image.Resampling.LANCZOS)
    return final_img

def main():
    icons_dir = os.path.join(r"c:\Docs\Phishing_Detection\extension", "icons")
    os.makedirs(icons_dir, exist_ok=True)

    sizes = [16, 32, 48, 128]
    for s in sizes:
        icon = create_shield_icon(s)
        out_path = os.path.join(icons_dir, f"icon{s}.png")
        icon.save(out_path, "PNG")
        print(f"Generated {out_path} ({s}x{s})")

if __name__ == "__main__":
    main()
