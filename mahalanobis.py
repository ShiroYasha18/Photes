import numpy as np


def align_coefficients(p1: list, p2: list) -> tuple:
    """Pad coefficient lists with zeros to ensure equal length."""
    max_length = max(len(p1), len(p2))
    return (
        p1 + [0] * (max_length - len(p1)),
        p2 + [0] * (max_length - len(p2))
    )


def mahalanobis_distance(poly1: list, poly2: list, inv_cov_matrix: np.ndarray) -> float:

    p1, p2 = align_coefficients(poly1, poly2)

    # Convert to numpy arrays
    vec1 = np.array(p1)
    vec2 = np.array(p2)

    # Calculate difference vector
    delta = vec1 - vec2

    # Compute Mahalanobis distance
    temp = delta.T @ inv_cov_matrix
    distance = np.sqrt(temp @ delta)

    return distance


# Example usage
if __name__ == "__main__":
    poly1 = [1, 2, 3]  # 3x² + 2x + 1
    poly2 = [4, 0, 0, 2]  # 2x³ + 4

    # Sample inverse covariance matrix (4x4 for aligned coefficients)
    inv_cov = np.array([
        [1.2, 0.3, 0.1, 0.0],
        [0.3, 0.8, 0.2, 0.1],
        [0.1, 0.2, 1.0, 0.2],
        [0.0, 0.1, 0.2, 0.9]
    ])

    distance = mahalanobis_distance(poly1, poly2, inv_cov)
    print(f"Mahalanobis distance between the polynomials: {distance:.4f}")