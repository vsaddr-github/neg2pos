#!/usr/bin/env python3
import argparse
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import sys
import json
import os


debug=0

def compute_brightness(img_np: np.ndarray) -> np.ndarray:
    """Compute a simple luminance map by averaging R, G, B."""
    return np.dot(img_np[..., :3], [0.3333, 0.3333, 0.3334])


def get_rebate_crop(rgb: np.ndarray, pct: float = 98, ksz: int = 15, min_area_frac: float = 0.8):
    """
    Crop out the bright film rebate by thresholding...
    If no contour found, or if cropped area is < min_area_frac of total area,
    return full image coverage and top-left (0,0).
    """
    bright = compute_brightness(rgb)
    thresh = np.percentile(bright, pct)
    mask = (bright >= thresh).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ksz, ksz))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = rgb.shape[:2]
    total_area = w * h
    if not cnts:
        # fallback: full image
        return rgb, thresh, 0, 0, w, h
    x, y, cw, ch = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    crop_area = cw * ch
    if crop_area < min_area_frac * total_area:
        # Too much would be lost—return full image
        return rgb, thresh, 0, 0, w, h
    return rgb[y:y+ch, x:x+cw], thresh, x, y, cw, ch



def crop_inner_and_find_bright(crop_rgb: np.ndarray,
                               rebate_thresh: float,
                               close1: int = 15,
                               close2: int = 25,
                               top_pct: float = 1):
    """
    Crop inner image and compute avg RGB of brightest pixels...
    If no contour found, return full crop and avg [255,255,255].
    """
    bright = compute_brightness(crop_rgb)
    mask = (bright >= rebate_thresh).astype(np.uint8) * 255
    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (close1, close1))
    closed1 = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k1)
    inv = cv2.bitwise_not(closed1)
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (close2, close2))
    clean = cv2.morphologyEx(inv, cv2.MORPH_CLOSE, k2)
    clean = cv2.morphologyEx(clean, cv2.MORPH_OPEN, k2)
    cnts, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        # fallback: full crop
        h, w = crop_rgb.shape[:2]
        avg = [255.0, 255.0, 255.0]
        mask_bright = np.zeros((h, w), dtype=bool)
        return crop_rgb, mask_bright, avg, 0.0, (0, 0, w, h)
    c = max(cnts, key=cv2.contourArea)
    rect = cv2.minAreaRect(c)
    angle = rect[2]
    print(f"Detected skew angle: {angle:.2f} degrees", file=sys.stderr)
    x, y, w, h = cv2.boundingRect(c)
    inner_crop = crop_rgb[y:y+h, x:x+w]
    inner_bright = compute_brightness(inner_crop)
    bright_thresh = np.percentile(inner_bright, 100 - top_pct)
    mask_bright = inner_bright >= bright_thresh
    pixels = inner_crop[mask_bright]
    avg = pixels.mean(axis=0).tolist()
    return inner_crop, mask_bright, avg, angle, (x, y, w, h)

def apply_crop_and_deskew(orig_rgb, crop_rect, angle):
    """
    Crops and deskews the original (non-normalized) image using the
    provided crop rectangle (x, y, w, h) and rotation angle (degrees).
    Returns the final cropped image.
    """
    x, y, w, h = crop_rect
    # 1. Rotate image by -angle (deskew)
    h_img, w_img = orig_rgb.shape[:2]
    center = (w_img / 2.0, h_img / 2.0)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(orig_rgb, M, (w_img, h_img), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
    # 2. Crop the rotated image
    cropped = rotated[y:y+h, x:x+w]
    return cropped


def rotate_image(rgb: np.ndarray, angle: float) -> np.ndarray:
    h, w = rgb.shape[:2]
    center = (w / 2.0, h / 2.0)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(rgb, M, (w, h), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))

    # --- Normalize image using mean RGB of brightest 3% of non-black pixels ---
def mean_rgb_of_top_percent_full(img, percent=3):
        rgb = img.reshape(-1, 3)
        # Exclude black pixels (from perforation removal)
        mask_nonblack = np.any(rgb > 0, axis=1)
        rgb_nonblack = rgb[mask_nonblack]
        if rgb_nonblack.shape[0] == 0:
            return np.array([254, 254, 254])
        gray = cv2.cvtColor(rgb_nonblack.reshape(-1, 1, 3), cv2.COLOR_RGB2GRAY).flatten()
        n_select = max(1, int(len(gray) * percent / 100.0))
        brightest_idx = np.argpartition(-gray, n_select-1)[:n_select]
        mean_val = rgb_nonblack[brightest_idx].mean(axis=0)
        return mean_val

def remove_perforation(rgb: np.ndarray, dilation_radius: int = 15) -> np.ndarray:
    # 1. Zero out pure white pixels
    mask_white = np.all(rgb == 255, axis=2)
    rgb[mask_white] = [0, 0, 0]
    # 2. Dilate the black (zeroed) regions to cover possible border leaks
    mask_black = np.all(rgb == 0, axis=2).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilation_radius*2+1, dilation_radius*2+1))
    mask_dilated = cv2.dilate(mask_black, kernel, iterations=1)
    rgb[mask_dilated == 255] = [0, 0, 0]
    return rgb



def main():
    p = argparse.ArgumentParser(
        description="Crop scan pipeline with fallbacks.")
    p.add_argument("image_path", help="Path to the scanned frame image")
    args = p.parse_args()

    bgr = cv2.imread(args.image_path)
    if bgr is None:
        print(json.dumps({"error": f"Couldn’t open {args.image_path}"}), file=sys.stderr)
        sys.exit(1)
    rgb_orig = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgb_orig = remove_perforation(rgb_orig)
  
    # --- Highlight-based normalization (insert here) ---
    ref_rgb = mean_rgb_of_top_percent_full(rgb_orig, 3)
    print(f"Reference RGB for normalization (mean of brightest 3%): {ref_rgb}", file=sys.stderr)
    # Normalize channels so this mean becomes 254
    norm = rgb_orig.astype(np.float32)
    for c in range(3):
        val = ref_rgb[c]
        if val > 1:
            norm[:, :, c] = np.clip((norm[:, :, c] / val) * 254.0, 0, 254)
        else:
            norm[:, :, c] = 0
    rgb_norm = norm.astype(np.uint8)
  
    # start processing nor,malized image,
    
    # Returns a crop that covers the rebate and the image inside it (rebate included). 
    # x and y are the coordinates of the rectangle’s top-left corner (in pixels, relative to the image).
    # w and h are the rectangle’s width and height.  
    # x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
    # return rgb[y:y+h, x:x+w], thresh, x, y, w, h
    
    rebate_crop_rgb, rebate_thresh, rx, ry, rw, rh  = get_rebate_crop(rgb_norm, pct=90)
    #_, _, _, angle, _ = crop_inner_and_find_bright(rebate_crop_rgb, rebate_thresh, top_pct=1)
    if debug:
        out_path = os.path.splitext(args.image_path)[0] + "rebate_crop_rgb.jpg"
        Image.fromarray(rebate_crop_rgb).save(out_path)

    #To get the image inside the rebate, use crop_inner_and_find_bright on the rebate crop.
    inner_crop, bright_mask, avg_rgb, angle, (ix, iy, iw, ih) = crop_inner_and_find_bright(rebate_crop_rgb, rebate_thresh, top_pct=1)
    print(f"Crop_inner_and_find_bright(rebate_crop_rgb, rebate_thresh, top_pct=1) angle : {angle}", file=sys.stderr)
    if debug:
        out_path = os.path.splitext(args.image_path)[0] + "_normalized_innercrop_01.jpg"
        Image.fromarray(inner_crop).save(out_path)

    if (angle > 20) : angle=0
   
    final_img = apply_crop_and_deskew(rgb_orig, (ix+rx, iy+ry, iw, ih), angle)
    out_path = os.path.splitext(args.image_path)[0] + "_.png"
    Image.fromarray(final_img).save(out_path, format="PNG")

    # end 
    
    result = {
        "image_path": out_path,
        "blend_color": {"r": ref_rgb[0], "g": ref_rgb[1], "b": ref_rgb[2]},
        "skew_angle": angle,
        "delete_after_use": True
    }
    print(json.dumps(result))

if __name__ == "__main__":
    main()
  
