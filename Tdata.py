def analyze_time_series_data(image_sequence_paths, value_extractor_func,
                             num_values_per_point=4):
    """
    Collects time-series data, calculates Z-scores, normalizes, and centers.

    Args:
        image_sequence_paths (list): List of paths to images in sequence.
        value_extractor_func (callable): A function that takes an image path
                                        and returns a (H, W, C) numpy array
                                        where C is num_values_per_point.
                                        Example: HSL values + color_diff.
        num_values_per_point (int): The number of values extracted per pixel per image.

    Returns:
        tuple: (original_time_series_data, normalized_centered_data, z_scores)
    """
    if not image_sequence_paths:
        return None, None, None

    # Load and extract data for all images
    # This will be a list of (H, W, C) arrays
    time_series_frames = []
    for path in image_sequence_paths:
        # Example extractor: HSL + color diff from previous steps
        # This is highly simplified for demonstration. In reality, you'd define
        # what your 4 values are from each image consistently.
        img_rgb = Image.open(path).convert("RGB")
        width, height = img_rgb.size
        pixels_rgb = np.array(img_rgb) / 255.0
        # Re-using simplified HSL conversion from Step 1
        pixels_hsl = np.zeros_like(pixels_rgb)
        for y in range(height):
            for x in range(width):
                pixels_hsl[y, x] = (apply_circular_gradient_hsl_curves.rgb_to_hsl(*pixels_rgb[y, x]) + (0,))[:3] # Only HSL, add dummy 0 for 4th value if needed

        # For this demo, let's just use R, G, B, and the magnitude of the pixel (sqrt(R^2+G^2+B^2))
        current_frame_data = np.zeros((height, width, num_values_per_point))
        current_frame_data[:, :, :3] = pixels_rgb # R, G, B
        current_frame_data[:, :, 3] = np.linalg.norm(pixels_rgb, axis=-1) # Magnitude
        time_series_frames.append(current_frame_data)

    # Convert to a single (N_frames, H, W, C) array
    time_series_data = np.array(time_series_frames)
    print(f"Time series data shape: {time_series_data.shape}") # (frames, height, width, values_per_pixel)

    # Flatten for easier statistical calculation across time for each pixel
    # Reshape to (num_pixels, num_frames, num_values_per_pixel)
    num_pixels = height * width
    flattened_data = time_series_data.transpose(1, 2, 0, 3).reshape(num_pixels, len(image_sequence_paths), num_values_per_point)

    # Calculate mean and standard deviation across TIME for EACH pixel's values
    # Mean and Std Dev will be (num_pixels, num_values_per_pixel)
    means = np.mean(flattened_data, axis=1)
    stds = np.std(flattened_data, axis=1)

    # Avoid division by zero for std=0 (e.g., if a value is constant over time)
    stds[stds == 0] = 1e-9 # Small epsilon

    # Calculate Z-scores: (X - mu) / sigma
    # Reshape `means` and `stds` to allow broadcasting correctly
    z_scores = (flattened_data - means[:, np.newaxis, :]) / stds[:, np.newaxis, :]

    # Normalization (Min-Max scaling after Z-score, typically not done together unless specified)
    # The request says "normalize and center", Z-score *is* centering (mean 0, std 1).
    # If "normalize" means 0-1 scaling, that's a separate step.
    # Let's assume normalize means min-max scaling across the *entire* dataset for a given value type
    # (e.g., all R values across all pixels/frames)

    # For simple Min-Max normalization of Z-scores (optional, often Z-score is enough)
    min_val_z = z_scores.min(axis=(0,1)) # Min across all pixels and frames for each value type
    max_val_z = z_scores.max(axis=(0,1))
    normalized_centered_data = (z_scores - min_val_z) / (max_val_z - min_val_z + 1e-9)

    print(f"Z-scores shape: {z_scores.shape}")
    print(f"Normalized & Centered data shape: {normalized_centered_data.shape}")

    # You might want to reshape back to (N_frames, H, W, C) for further image-like processing
    original_time_series_data_reshaped = time_series_data
    z_scores_reshaped = z_scores.reshape(height, width, len(image_sequence_paths), num_values_per_point).transpose(2,0,1,3)
    normalized_centered_data_reshaped = normalized_centered_data.reshape(height, width, len(image_sequence_paths), num_values_per_point).transpose(2,0,1,3)


    return original_time_series_data_reshaped, normalized_centered_data_reshaped, z_scores_reshaped

# Example Usage: Create dummy image sequence
num_frames = 5
image_sequence_paths = [f"input_image_{i}.jpg" for i in range(num_frames)]
for i in range(num_frames):
    dummy_img = Image.new('RGB', (100, 100), color = (i*50, 0, 255 - i*50)) # Simple color change over time
    dummy_img.save(image_sequence_paths[i])

original_ts_data, normalized_ts_data, z_scores_ts = analyze_time_series_data(
    image_sequence_paths,
    value_extractor_func=None # Not used directly in this simplified demo
)
