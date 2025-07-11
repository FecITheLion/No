def apply_simulated_polarization(image_path, output_path, filter_angle_deg=45,
                                 perpendicular_reduction_factor=0.25,
                                 parallel_reduction_factor=0.15):
    """
    Simulates a linear polarization filter effect.
    This is an artistic simulation, not physically accurate without polarized light data.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the filtered image.
        filter_angle_deg (float): The angle of the linear polarizer in degrees.
        perpendicular_reduction_factor (float): Factor to reduce light perpendicular to filter.
        parallel_reduction_factor (float): Factor to reduce light parallel to filter.
                                           (A polarizer primarily reduces perpendicular light)
    """
    img_rgb = Image.open(image_path).convert("RGB")
    pixels = np.array(img_rgb) / 255.0

    # Conceptual: Use image gradients as a proxy for local "light orientation"
    # This is a very rough artistic approximation.
    img_gray = ImageOps.grayscale(img_rgb)
    img_gray_np = np.array(img_gray)

    # Calculate image gradients (Sobel filter for edge detection)
    from scipy.ndimage import sobel
    gradient_x = sobel(img_gray_np, axis=1)
    gradient_y = sobel(img_gray_np, axis=0)

    # Calculate local "orientation" (angle of brightest gradient)
    orientation_rad = np.arctan2(gradient_y, gradient_x)
    orientation_deg = np.degrees(orientation_rad) % 180 # Angle from 0 to 180

    filter_angle_rad = np.radians(filter_angle_deg)

    # Calculate "perpendicularity" to filter angle for each pixel
    # If local orientation is parallel to filter, little reduction. If perpendicular, strong reduction.
    angle_diff_rad = np.abs(orientation_rad - filter_angle_rad) % np.pi # Angle difference from 0 to pi
    perpendicularity_score = np.abs(np.sin(angle_diff_rad)) # 1 when perpendicular, 0 when parallel

    # Apply reduction based on perpendicularity
    # For a simple linear polarizer, intensity reduction is cos^2(theta)
    # Here we use more explicit factors for "25% 15% perpendicular quantum light filter"
    # This means (1 - reduction_factor) is the transmittance.
    # Let's interpret 25% perpendicular reduction as 75% transmission, and 15% parallel as 85% transmission.
    # Total reduction is a weighted sum: (1-0.15) + (1-0.25)*perpendicularity_score
    # A simpler model:
    transmittance_factor = (1 - parallel_reduction_factor) - (perpendicular_reduction_factor - parallel_reduction_factor) * perpendicularity_score
    transmittance_factor = np.clip(transmittance_factor, 0, 1) # Ensure valid range

    processed_pixels = pixels * transmittance_factor[:, :, np.newaxis] # Apply to all RGB channels

    processed_img = Image.fromarray((processed_pixels * 255).astype(np.uint8))
    processed_img.save(output_path)
    print(f"Simulated polarization filter applied and saved to {output_path}")

# Example Usage:
apply_simulated_polarization("input_image.jpg", "output_polarized.jpg")
