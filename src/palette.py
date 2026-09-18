"""
Palette conversion and image processing utilities for Game Boy 4-Color aesthetics.
"""
from PIL import Image
import os

# Game Boy DMG-01 Classic 4-Shade Palette
# From darkest to lightest
GB_PALETTE = [
    (15, 56, 15),     # #0f380f - Darkest green / black
    (48, 98, 48),     # #306230 - Dark green
    (139, 172, 15),   # #8bac0f - Light green
    (155, 188, 15),   # #9bbc0f - Lightest green / phosphor highlight
]

def create_gb_palette_image() -> Image.Image:
    """Create a 1-pixel palette reference image for PIL quantize."""
    palette_data = []
    for r, g, b in GB_PALETTE:
        palette_data.extend([r, g, b])
    # Pad to 256 colors as required by PIL palette
    palette_data.extend([0, 0, 0] * (256 - len(GB_PALETTE)))
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette(palette_data)
    return pal_img

def convert_to_gameboy_palette(
    src_path: str,
    dest_path: str,
    crop_top_pct: float = 0.08,
    target_size: tuple[int, int] = (320, 200),
    dither: bool = True
) -> str:
    """
    Load an image, optionally crop top header text, resize to retro resolution,
    and quantize to the authentic 4-color Game Boy palette.
    """
    img = Image.open(src_path).convert("RGB")
    width, height = img.size

    # Crop unwanted header text if requested
    if crop_top_pct > 0:
        top_y = int(height * crop_top_pct)
        img = img.crop((0, top_y, width, height))

    # Resize to retro target size with high quality downsampling
    img_resized = img.resize(target_size, Image.Resampling.LANCZOS)

    # Quantize to Game Boy palette
    pal_ref = create_gb_palette_image()
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    quantized = img_resized.quantize(palette=pal_ref, dither=dither_mode)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    quantized.save(dest_path, "PNG")
    return dest_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        convert_to_gameboy_palette(sys.argv[1], sys.argv[2])
