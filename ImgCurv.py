import numpy as np
from PIL import Image, ImageOps, ImageFilter
import math

def apply_circular_gradient_hsl_curves(image_path, output_path,
                                       red_center_percent=(0.1, 0.9),  # (x_percent, y_percent) for red gradient center
                                       blue_center_percent=(0.9, 0.1), # (x_percent, y_percent) for blue gradient center
                                       gradient_radius_px=200,         # Radius for full intensity, decreases outwards
                                       max_hue_shift_deg=30,           # Max H shift at center
                                       max_saturation_adjust=0.2,      # Max S adjustment (-0.2 to +0.2)
                                       max_lightness_adjust=0.1,       # Max L adjustment (-0.1 to +0.1)
                                       red_mix_hue_deg=0,              # Target hue for red (0 deg is red)
                                       blue_mix_hue_deg=240,           # Target hue for blue (240 deg is blue)
                                       secondary_mix_factor=0.5):      # How much secondary colors influence
    """
    Applies HSL and curve adjustments using circular gradients for red and blue,
    mixing with secondary colors.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the processed image.
        red_center_percent (tuple): (x_norm, y_norm) for the red gradient center.
        blue_center_percent (tuple): (x_norm, y_norm) for the blue gradient center.
        gradient_radius_px (int): Radius (in pixels) within which gradient influence is strong.
        max_hue_shift_deg (int): Maximum degrees to shift Hue at gradient center.
        max_saturation_adjust (float): Max +/- adjustment for Saturation.
        max_lightness_adjust (float): Max +/- adjustment for Lightness.
        red_mix_hue_deg (int): Hue value (0-360) associated with the "red" gradient.
        blue_mix_hue_deg (int): Hue value (0-360) associated with the "blue" gradient.
        secondary_mix_factor (float): Factor (0-1) influencing secondary color blends.
                                      e.g., 0.5 means 50% blend with secondary.
    """
    img_rgb = Image.open(image_path).convert("RGB")
    width, height = img_rgb.size
    pixels_rgb = np.array(img_rgb) / 255.0 # Normalize to 0-1

    # Convert RGB to HSL (using a common conversion function, not built-in PIL)
    # A simplified RGB to HSL conversion (not exact for all cases, but illustrative)
    def rgb_to_hsl(r, g, b):
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        h, s, l = 0, 0, (max_val + min_val) / 2

        if max_val == min_val:
            h = 0 # achromatic
        else:
            d = max_val - min_val
            s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
            if max_val == r:
                h = (g - b) / d + (0 if g < b else 6)
            elif max_val == g:
                h = (b - r) / d + 2
            elif max_val == b:
                h = (r - g) / d + 4
            h /= 6
        return h * 360, s, l # H in degrees, S/L in 0-1

    # Apply HSL conversion to all pixels
    pixels_hsl = np.zeros_like(pixels_rgb)
    for y in range(height):
        for x in range(width):
            pixels_hsl[y, x] = rgb_to_hsl(*pixels_rgb[y, x])

    red_center_px = (int(red_center_percent[0] * width), int(red_center_percent[1] * height))
    blue_center_px = (int(blue_center_percent[0] * width), int(blue_center_percent[1] * height))

    # Define secondary colors (conceptual HSL points)
    # Yellow: ~60 deg Hue
    # Cyan: ~180 deg Hue
    # Magenta: ~300 deg Hue

    # Pre-calculate distances and weights
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

    dist_to_red_center = np.sqrt((x_coords - red_center_px[0])**2 + (y_coords - red_center_px[1])**2)
    weight_red = np.clip(1 - (dist_to_red_center / gradient_radius_px), 0, 1)

    dist_to_blue_center = np.sqrt((x_coords - blue_center_px[0])**2 + (y_coords - blue_center_px[1])**2)
    weight_blue = np.clip(1 - (dist_to_blue_center / gradient_radius_px), 0, 1)

    # Combined influence (simple sum, could be more complex blend)
    total_weight_influence = np.clip(weight_red + weight_blue, 0, 1)

    processed_hsl = np.copy(pixels_hsl)

    # Apply adjustments based on gradient weights and color mixes
    for y in range(height):
        for x in range(width):
            h, s, l = pixels_hsl[y, x]

            # Influence based on red gradient
            red_influence = weight_red[y, x]
            # Influence based on blue gradient
            blue_influence = weight_blue[y, x]

            # Calculate secondary color influence
            # Example: If a pixel is near red, shift its hue towards yellow/magenta depending on its original hue
            # This is a highly conceptual interpretation of "secondary color mixes"
            hue_mix_factor = (red_influence * secondary_mix_factor) + (blue_influence * secondary_mix_factor)
            
            # Simplified hue shift towards red or blue target hues
            target_hue = red_mix_hue_deg if red_influence > blue_influence else blue_mix_hue_deg
            # Shift towards target hue based on influence
            h_adjusted = (h + (target_hue - h) * total_weight_influence[y, x] * (max_hue_shift_deg / 360.0)) % 360

            # Apply saturation and lightness adjustments
            s_adjusted = np.clip(s + total_weight_influence[y, x] * max_saturation_adjust * (1 if red_influence > blue_influence else -1), 0, 1)
            l_adjusted = np.clip(l + total_weight_influence[y, x] * max_lightness_adjust * (1 if red_influence > blue_influence else -1), 0, 1)

            processed_hsl[y, x] = [h_adjusted, s_adjusted, l_adjusted]

    # Convert HSL back to RGB (simplified)
    def hsl_to_rgb(h, s, l):
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        r, g, b = 0, 0, 0

        h %= 360 # Ensure hue is within 0-360

        if 0 <= h < 60: r, g, b = c, x, 0
        elif 60 <= h < 120: r, g, b = x, c, 0
        elif 120 <= h < 180: r, g, b = 0, c, x
        elif 180 <= h < 240: r, g, b = 0, x, c
        elif 240 <= h < 300: r, g, b = x, 0, c
        elif 300 <= h < 360: r, g, b = c, 0, x
        return ((r + m) * 255, (g + m) * 255, (b + m) * 255)

    processed_rgb_uint8 = np.zeros_like(pixels_rgb, dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            processed_rgb_uint8[y, x] = hsl_to_rgb(*processed_hsl[y, x])

    processed_img = Image.fromarray(processed_rgb_uint8)
    processed_img.save(output_path)
    print(f"Processed image saved to {output_path}")

    return pixels_rgb, processed_rgb_uint8 # Return original and processed for difference analysis

# Example Usage:
# Create a dummy image for testing if you don't have one
try:
    Image.open("input_image.jpg")
except FileNotFoundError:
    print("Creating a dummy input_image.jpg...")
    dummy_img = Image.new('RGB', (800, 600), color = 'gray')
    dummy_img.save("input_image.jpg")

original_pixels, processed_pixels = apply_circular_gradient_hsl_curves(
    "input_image.jpg",
    "output_hsl_gradient.jpg"
)
