"""
Macenko Color Normalization for H&E Stained Histopathology Images
Reference: Macenko et al. "A method for normalizing histology slides for quantitative analysis"
IEEE ISBI 2009
"""

import numpy as np
import cv2
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.pipeline_config import MACENKO_PARAMS


def macenko_normalize(img, Io=240, alpha=1, beta=0.15, HERef=None, maxCRef=None):
    """
    Apply Macenko color normalization to an H&E stained image.

    Parameters:
    -----------
    img : np.ndarray
        Input RGB image (H x W x 3)
    Io : int
        Transmitted light intensity (default 240)
    alpha : float
        Percentile for robust OD computation (default 1%)
    beta : float
        OD threshold for tissue detection (default 0.15)
    HERef : np.ndarray
        Reference H&E stain matrix (3 x 2)
    maxCRef : np.ndarray
        Reference maximum concentrations (2,)

    Returns:
    --------
    np.ndarray : Normalized RGB image
    """
    # Set default reference values if not provided
    if HERef is None:
        HERef = np.array(MACENKO_PARAMS['HERef'])
    if maxCRef is None:
        maxCRef = np.array(MACENKO_PARAMS['maxCRef'])

    # Reshape image to (N_pixels, 3)
    h, w, c = img.shape
    img_flat = img.reshape((-1, 3)).astype(np.float64)

    # Convert RGB to optical density (OD)
    OD = -np.log((img_flat + 1) / Io)

    # Remove transparent pixels (background)
    ODhat = OD[~np.any(OD < beta, axis=1)]

    if ODhat.shape[0] == 0:
        # If no tissue detected, return original image
        return img

    # Compute eigenvectors (stain vectors)
    eigvals, eigvecs = np.linalg.eigh(np.cov(ODhat.T))

    # Project on the plane spanned by the two largest eigenvectors
    That = ODhat.dot(eigvecs[:, 1:3])

    # Find the min and max angles
    phi = np.arctan2(That[:, 1], That[:, 0])

    minPhi = np.percentile(phi, alpha)
    maxPhi = np.percentile(phi, 100 - alpha)

    # Compute stain vectors
    vMin = eigvecs[:, 1:3].dot(np.array([(np.cos(minPhi), np.sin(minPhi))]).T)
    vMax = eigvecs[:, 1:3].dot(np.array([(np.cos(maxPhi), np.sin(maxPhi))]).T)

    # Stain matrix (H&E)
    if vMin[0] > vMax[0]:
        HE = np.array((vMin[:, 0], vMax[:, 0])).T
    else:
        HE = np.array((vMax[:, 0], vMin[:, 0])).T

    # Rows of HE must be normalized
    HE = HE / np.linalg.norm(HE, axis=0)

    # Compute source concentrations
    C = np.linalg.lstsq(HE, OD.T, rcond=None)[0]

    # Normalize stain concentrations
    maxC = np.array([np.percentile(C[0, :], 99), np.percentile(C[1, :], 99)])

    # Avoid division by zero
    maxC[maxC == 0] = 1.0

    C = C * (maxCRef / maxC)[:, np.newaxis]

    # Recreate the image using reference stain vectors
    Inorm = np.exp(-HERef.dot(C)) * Io
    Inorm[Inorm > 255] = 255
    Inorm = np.reshape(Inorm.T, (h, w, 3)).astype(np.uint8)

    return Inorm


def normalize_image_file(input_path, output_path, **kwargs):
    """
    Load, normalize, and save a single image.

    Parameters:
    -----------
    input_path : str or Path
        Path to input image
    output_path : str or Path
        Path to save normalized image
    **kwargs : dict
        Additional parameters for macenko_normalize

    Returns:
    --------
    bool : True if successful, False otherwise
    """
    try:
        # Read image
        img = cv2.imread(str(input_path))
        if img is None:
            print(f"Warning: Could not read {input_path}")
            return False

        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Apply normalization
        normalized = macenko_normalize(img_rgb, **kwargs)

        # Convert back to BGR for saving
        normalized_bgr = cv2.cvtColor(normalized, cv2.COLOR_RGB2BGR)

        # Save
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), normalized_bgr)

        return True

    except Exception as e:
        print(f"Error processing {input_path}: {str(e)}")
        return False


if __name__ == "__main__":
    # Test on a single image
    import sys

    if len(sys.argv) < 3:
        print("Usage: python macenko_normalization.py <input_image> <output_image>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    success = normalize_image_file(input_path, output_path)

    if success:
        print(f"Successfully normalized: {input_path} -> {output_path}")
    else:
        print(f"Failed to normalize: {input_path}")
