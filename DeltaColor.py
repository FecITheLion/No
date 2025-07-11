from scipy.spatial.distance import euclidean

def calculate_color_differences(original_rgb_normalized, processed_rgb_uint8):
    """
    Calculates absolute color differences between original and processed images.

    Args:
        original_rgb_normalized (np.array): Original image pixels (0-1 RGB).
        processed_rgb_uint8 (np.array): Processed image pixels (0-255 RGB).

    Returns:
        np.array: A 2D array of difference magnitudes for each pixel.
    """
    processed_rgb_normalized = processed_rgb_uint8 / 255.0
    height, width, _ = original_rgb_normalized.shape
    differences = np.zeros((height, width))

    # Option 1: Simple Euclidean distance in RGB
    for y in range(height):
        for x in range(width):
            differences[y, x] = euclidean(original_rgb_normalized[y, x], processed_rgb_normalized[y, x])

    # Option 2: Conceptual Delta E (requires conversion to LAB, more complex)
    # from skimage.color import rgb2lab, deltaE_cie2000
    # original_lab = rgb2lab(original_rgb_normalized)
    # processed_lab = rgb2lab(processed_rgb_normalized)
    # differences = deltaE_cie2000(original_lab, processed_lab) # This returns a 2D array directly

    print(f"Calculated {differences.size} color differences. Max: {differences.max():.4f}, Min: {differences.min():.4f}")
    return differences

# Example Usage:
color_diff_map = calculate_color_differences(original_pixels, processed_pixels)

# Optionally save a grayscale difference map
diff_img = Image.fromarray((color_diff_map / color_diff_map.max() * 255).astype(np.uint8), mode='L')
diff_img.save("output_color_difference_map.jpg")
