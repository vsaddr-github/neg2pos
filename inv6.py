import numpy as np
from PIL import Image
import argparse
import datetime
import os
import matplotlib.pyplot as plt

def divide_blend(image_np, blend_color):
    blend_color_float = np.array(blend_color, dtype=float)
    divided_image_np = (image_np / blend_color_float) * 255
    divided_image_np = np.clip(divided_image_np, 0, 255).astype(np.uint8)
    return divided_image_np

def invert_image(image_np):
    return 255 - image_np

def compute_brightness(image_np):
    return np.dot(image_np[...,:3], [0.3333, 0.3333, 0.3334])

def enhanced_white_balance(image_np, bright_percentile, dark_percentile):
    brightness = compute_brightness(image_np)
    bright_threshold = np.percentile(brightness, bright_percentile)
    dark_threshold = np.percentile(brightness, dark_percentile)
    
    bright_pixels = image_np[brightness >= bright_threshold]
    dark_pixels = image_np[brightness <= dark_threshold]

    max_values = dark_pixels.max(axis=0)
    min_values = bright_pixels.min(axis=0)

    scale_factors = 253 / (min_values - max_values)
    offsets = 2 - max_values * scale_factors

    white_balanced_image_np = (image_np * scale_factors + offsets).clip(0, 255).astype(np.uint8)
    return white_balanced_image_np

def auto_contrast(image_np, clip_percent):
    grayscale_img = np.dot(image_np[...,:3], [0.299, 0.587, 0.114])
    histogram, bin_edges = np.histogram(grayscale_img.flatten(), bins=256, range=(0,256))
    cdf = histogram.cumsum()
    num_pixels_to_clip = clip_percent * np.prod(image_np.shape)
    
    lower_limit = 0
    while cdf[lower_limit] < num_pixels_to_clip:
        lower_limit += 1

    upper_limit = 255
    while cdf[upper_limit] >= (cdf[-1] - num_pixels_to_clip):
        upper_limit -= 1

    scale_factor = 255.0 / (upper_limit - lower_limit)
    offset = -lower_limit * scale_factor

    auto_contrast_img_np = (image_np * scale_factor + offset).clip(0, 255).astype(np.uint8)
    return auto_contrast_img_np

def save_image(image_np, base_name, suffix):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{base_name}_{suffix}_{timestamp}.jpg"
    Image.fromarray(image_np).save(filename)
    return filename

def show_image_m(image_np, title):
    plt.imshow(image_np)
    plt.title(title)
    plt.show()
    
def show_image(image_np, title):
    Image.fromarray(image_np).show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Processing Script")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("--autocontrast", action="store_true", help="Apply autocontrast if set")
    args = parser.parse_args()

    # Load the image
    img = Image.open(args.image_path)
    img_np = np.array(img)

    # Divide blend mode
    blend_color = np.array([250, 240, 230])
    divided_img_np = divide_blend(img_np, blend_color)
    print(f"Divide blend applied with color {blend_color}")

    # Invert the image
    inverted_img_np = invert_image(divided_img_np)
    print("Image inverted")

    # White balance
    white_balanced_img_np = enhanced_white_balance(inverted_img_np, bright_percentile=99.99, dark_percentile=0.1)
    print("White balance applied with bright percentile 99.99 and dark percentile 0.1")
    base_name, _ = os.path.splitext(args.image_path)
    wb_filename = save_image(white_balanced_img_np, base_name, "wb")
    print(f"White balanced image saved as {wb_filename}")
    show_image(white_balanced_img_np, "White Balanced Image")

    # Conditionally apply auto contrast
    if args.autocontrast:
        auto_contrast_img_np = auto_contrast(white_balanced_img_np, clip_percent=0.01)
        print("Auto contrast applied with clip percent 0.01")
        ac_filename = save_image(auto_contrast_img_np, base_name, "ac")
        print(f"Auto contrast image saved as {ac_filename}")
        show_image(auto_contrast_img_np, "Auto Contrast Image")
    else:
        print("Auto contrast not applied")
