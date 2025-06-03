#!/usr/bin/env python3
import argparse
import json
import numpy as np
from PIL import Image
import datetime
import os

debug=0

def divide_blend(image_np: np.ndarray, blend_color: np.ndarray) -> np.ndarray:
    """Divide each channel by the blend color and scale back to 0–255."""
    divided = (image_np.astype(float) / blend_color.astype(float)) * 255.0
    return np.clip(divided, 0, 255).astype(np.uint8)


def invert_image(image_np: np.ndarray) -> np.ndarray:
    """Invert an image: 255 - pixel value."""
    return 255 - image_np


def compute_brightness(image_np: np.ndarray) -> np.ndarray:
    """Compute luminance as weighted sum of R, G, B."""
    return np.dot(image_np[..., :3], [0.3333, 0.3333, 0.3334])


def enhanced_white_balance(image_np: np.ndarray,
                           bright_pct: float,
                           dark_pct: float) -> np.ndarray:
    """
    Apply white balance by stretching based on brightest and darkest percentiles.
    """
    brightness = compute_brightness(image_np)
    bright_th = np.percentile(brightness, bright_pct)
    dark_th = np.percentile(brightness, dark_pct)

    bright_vals = image_np[brightness >= bright_th]
    dark_vals = image_np[brightness <= dark_th]

    max_vals = dark_vals.max(axis=0)
    min_vals = bright_vals.min(axis=0)

    scale = 253.0 / (min_vals - max_vals)
    offset = 2.0 - max_vals * scale

    wb = image_np.astype(float) * scale + offset
    return np.clip(wb, 0, 255).astype(np.uint8)


def auto_contrast(image_np: np.ndarray, clip_pct: float) -> np.ndarray:
    """
    Stretch contrast by clipping a percentage of extreme pixels.
    """
    gray = np.dot(image_np[..., :3], [0.299, 0.587, 0.114])
    hist, _ = np.histogram(gray.flatten(), bins=256, range=(0,256))
    cdf = hist.cumsum()
    total = cdf[-1]
    clip = clip_pct * total

    low = np.searchsorted(cdf, clip)
    high = np.searchsorted(cdf, total - clip)
    if high <= low:
        return image_np.copy()

    scale = 255.0 / (high - low)
    offset = -low * scale
    ac = image_np.astype(float) * scale + offset
    return np.clip(ac, 0, 255).astype(np.uint8)


def save_image(image_np: np.ndarray, base_name: str, suffix: str) -> str:
    """Save array as PNG with timestamped filename."""
    #ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    #filename = f"{base_name}inverted_{ts}.png"
    filename = f"{base_name}inverted.png"
    Image.fromarray(image_np).save(filename, format="PNG")
    return filename


def main():
    """Read JSON config from file, process image, and show/save results."""
    parser = argparse.ArgumentParser(
        description="Process an image using divide blend, invert, white balance, and optional auto-contrast based on JSON config.")
    parser.add_argument("config_path", help="Path to JSON config file")
    args = parser.parse_args()

    # Load JSON config
    try:
        with open(args.config_path, 'r') as cf:
            config = json.load(cf)
    except Exception as e:
        print(f"Error reading config: {e}")
        return

    # Required parameters
    image_path = config.get('image_path')
    if not image_path:
        print("Config missing 'image_path'.")
        return

    # Read blend_color from JSON
    bc = config.get('blend_color')
    corrector=[0,0,0]
    if isinstance(bc, dict):
        blend_color = np.array([bc.get('r')+corrector[0], bc.get('g')+corrector[1], bc.get('b')+corrector[2]], dtype=float)
    elif isinstance(bc, list) and len(bc) == 3:
        blend_color = np.array(bc, dtype=float)
    else:
        print("Config missing or invalid 'blend_color'.")
        return

    # Load image
    img = Image.open(image_path).convert('RGB')
    img_np = np.array(img)
    base, _ = os.path.splitext(image_path)

    # 1) Divide blend
    divided = divide_blend(img_np, blend_color)
    print(f"Divide blend applied with color {blend_color.tolist()}")

    # 2) Invert
    inverted = invert_image(divided)
    print("Image inverted")

    # 3) White balance with fixed percentiles
    wb_np = enhanced_white_balance(inverted, bright_pct=99.99, dark_pct=0.1)
     
    wb_file = save_image(wb_np, base, 'wb')
    if debug:    
        print(f"White balanced image saved as {wb_file}")
        Image.fromarray(wb_np).show()

    # 4) Optional auto-contrast via JSON flag
    if config.get('autocontrast', False) :
        ac_np = auto_contrast(wb_np, clip_pct=0.01)
        ac_file = save_image(ac_np, base, 'ac')
        print(f"Auto contrast image saved as {ac_file}")
        Image.fromarray(ac_np).show()
    else:
        print("Auto contrast not applied")
        
    should_delete = config.get("delete_after_use", False)

    if should_delete:
        print(f"File {image_path} is marked for deletion.")
        if os.path.exists(image_path):
            os.remove(image_path)
        else:
            print("File not found:", image_path)
    else:
        print("File should be kept (or field is missing).")
                    

if __name__ == '__main__':
    main()
