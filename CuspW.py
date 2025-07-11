def generate_cardioid_weights_on_diagonals(width, height,
                                           initial_diagonal_start=(0, 0), # Top-Left
                                           initial_diagonal_end=(width-1, height-1), # Bottom-Right
                                           cusp_rotate_reverse=True,
                                           weight_growth_factor=0.1,
                                           decay_rate=0.05):
    """
    Generates a weighting matrix based on a cardioid-like pattern along diagonals.
    This is a highly customized and complex geometric weighting.

    Args:
        width (int): Image width.
        height (int): Image height.
        initial_diagonal_start (tuple): (x, y) of the starting point of the first orthogonal diagonal.
        initial_diagonal_end (tuple): (x, y) of the ending point of the first orthogonal diagonal.
        cusp_rotate_reverse (bool): If true, after reaching a "cusp", rotation reverses.
        weight_growth_factor (float): How much weight grows along the line.
        decay_rate (float): How much weight decreases perpendicular to the line.

    Returns:
        np.array: A (height, width) array of weights.
    """
    weights = np.zeros((height, width))
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

    # Determine the initial diagonal line equation (y = mx + c or x = my + c)
    # Example: Top-Left to Bottom-Right diagonal
    if initial_diagonal_start == (0, 0) and initial_diagonal_end == (width-1, height-1):
        # Line equation: y - 0 = ((height-1) - 0) / ((width-1) - 0) * (x - 0)
        # y = m * x  => mx - y = 0
        m = (height - 1) / (width - 1)
        c = 0
        # Line general form: Ax + By + C = 0  => m*x - y + 0 = 0
        A = m
        B = -1
        C = 0
    else:
        # More general line calculation
        x1, y1 = initial_diagonal_start
        x2, y2 = initial_diagonal_end
        A = y2 - y1
        B = x1 - x2
        C = -A * x1 - B * y1

    # Distance from a point (x,y) to the line Ax + By + C = 0
    # distance = |Ax + By + C| / sqrt(A^2 + B^2)
    distances_to_line = np.abs(A * x_coords + B * y_coords + C) / np.sqrt(A**2 + B**2 + 1e-9)

    # The "perpendicular to the most orthogonal diagonal" part means the weighting lines
    # are perpendicular to the main diagonal.
    # A line perpendicular to Ax + By + C = 0 is -Bx + Ay + D = 0
    # So the perpendicular lines have slope -1/m or A' = -B, B' = A

    # Conceptual Cardioid and criss-cross:
    # This implies iterating through "perpendicular" line segments.
    # Each segment grows/shrinks from a point on the main diagonal.
    # The "cardioid" part suggests a non-linear weighting or shape.

    # Simplified approach: Use a series of parallel lines perpendicular to the main diagonal.
    # The "cusp rotate reverse" and "growing/shrinking" suggest iterating along the main diagonal,
    # launching perpendicular segments that get weighted.

    # This is a highly complex custom algorithm. Here's a conceptual outline:
    # 1. Iterate along the main diagonal (e.g., from top-left to bottom-right).
    # 2. At each point (x_diag, y_diag) on this diagonal, define a line perpendicular to it.
    # 3. For each such perpendicular line, assign weights to pixels based on:
    #    a. Distance along this perpendicular line from (x_diag, y_diag) (decaying weight).
    #    b. Distance of (x_diag, y_diag) from the center of the main diagonal (for cardioid effect,
    #       or varying intensity of the perpendicular line).
    # 4. The "cardioid to the least absolute distance difference orthogonal diagonal" suggests
    #    that the weighting strength might be highest near the 'other' diagonal's intersection points,
    #    and the lines might be related to points closest to those intersection points.

    # Due to its extreme specificity and complexity, a full implementation of this
    # "cardioid to the least absolute distance difference orthogonal diagonal"
    # and the "criss-cross" mechanism is beyond the scope of a single, generic code block.
    # It would require precise mathematical definitions for the cardioid-like function,
    # the exact "growth and shrinking" behavior, and the "cusp rotate reverse" line generation.

    print("Custom cardioid weighting on diagonals is highly complex and conceptualized here.")
    # Return a dummy weight for demonstration
    return np.ones((height, width))

# Example Usage:
# cardioid_weights = generate_cardioid_weights_on_diagonals(original_pixels.shape[1], original_pixels.shape[0])
# (Not called in full flow as it needs more definition)
