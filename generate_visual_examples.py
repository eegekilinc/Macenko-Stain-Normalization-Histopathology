"""
Visual Examples Generation Script - Phase 5
Creates side-by-side comparisons of original vs normalized images
"""

import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import sys
import random

sys.path.append(str(Path(__file__).parent.parent))
from config.pipeline_config import RANDOM_SEED


def create_comparison_figure(orig_path, norm_path, title, save_path, add_zoom=False):
    """
    Create side-by-side comparison of original and normalized images.

    Parameters:
    -----------
    orig_path : Path
        Path to original image
    norm_path : Path
        Path to normalized image
    title : str
        Figure title
    save_path : Path
        Path to save the figure
    add_zoom : bool
        Whether to add zoomed inset
    """
    # Read images
    orig = cv2.imread(str(orig_path))
    norm = cv2.imread(str(norm_path))

    if orig is None or norm is None:
        print(f"Error reading images: {orig_path.name}")
        return False

    # Convert BGR to RGB
    orig_rgb = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
    norm_rgb = cv2.cvtColor(norm, cv2.COLOR_BGR2RGB)

    # Create figure
    if add_zoom:
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        # Full images
        axes[0, 0].imshow(orig_rgb)
        axes[0, 0].set_title('Original', fontsize=12)
        axes[0, 0].axis('off')

        axes[0, 1].imshow(norm_rgb)
        axes[0, 1].set_title('Macenko Normalized', fontsize=12)
        axes[0, 1].axis('off')

        # Zoomed regions (center crop)
        h, w = orig_rgb.shape[:2]
        crop_size = min(h, w) // 3
        y1 = h // 2 - crop_size // 2
        x1 = w // 2 - crop_size // 2

        orig_crop = orig_rgb[y1:y1+crop_size, x1:x1+crop_size]
        norm_crop = norm_rgb[y1:y1+crop_size, x1:x1+crop_size]

        axes[1, 0].imshow(orig_crop)
        axes[1, 0].set_title('Original (Zoom)', fontsize=12)
        axes[1, 0].axis('off')

        axes[1, 1].imshow(norm_crop)
        axes[1, 1].set_title('Normalized (Zoom)', fontsize=12)
        axes[1, 1].axis('off')

        # Add rectangle to show zoom region on full images
        rect_orig = patches.Rectangle((x1, y1), crop_size, crop_size,
                                      linewidth=2, edgecolor='red', facecolor='none')
        rect_norm = patches.Rectangle((x1, y1), crop_size, crop_size,
                                      linewidth=2, edgecolor='red', facecolor='none')
        axes[0, 0].add_patch(rect_orig)
        axes[0, 1].add_patch(rect_norm)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle(title, fontsize=16, fontweight='bold')

        axes[0].imshow(orig_rgb)
        axes[0].set_title('Original', fontsize=12)
        axes[0].axis('off')

        axes[1].imshow(norm_rgb)
        axes[1].set_title('Macenko Normalized', fontsize=12)
        axes[1].axis('off')

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"✓ Saved: {save_path.name}")
    return True


def select_representative_images(dataset_dir, n_samples=3):
    """
    Select representative images from a dataset.

    Parameters:
    -----------
    dataset_dir : Path
        Directory containing images
    n_samples : int
        Number of samples to select

    Returns:
    --------
    list : List of selected image paths
    """
    # Find all images
    image_extensions = ['*.jpeg', '*.jpg', '*.png', '*.tif']
    all_images = []
    for ext in image_extensions:
        all_images.extend(list(dataset_dir.rglob(ext)))

    if len(all_images) == 0:
        return []

    # Randomly select n_samples
    random.seed(RANDOM_SEED)
    selected = random.sample(all_images, min(n_samples, len(all_images)))

    return selected


def process_lc25000():
    """Generate visual examples for LC25000 dataset."""
    print("\n" + "="*60)
    print("Processing LC25000 Visual Examples")
    print("="*60)

    original_dir = Path("data/processed/LC25000/LC25000")
    normalized_dir = Path("data/processed/LC25000/macenko_norm")
    output_dir = Path("results/figures/visual_examples")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select 3 representative images
    norm_images = select_representative_images(normalized_dir, n_samples=3)

    success_count = 0
    for i, norm_path in enumerate(norm_images, 1):
        # Find corresponding original
        relative_path = norm_path.relative_to(normalized_dir)
        orig_path = original_dir / relative_path

        if not orig_path.exists():
            continue

        # Create comparison (with zoom for first example)
        title = f"LC25000 Example {i} - {norm_path.parent.name}/{norm_path.name}"
        save_path = output_dir / f"lc25000_example_{i}.png"
        add_zoom = (i == 1)  # Add zoom only for first example

        if create_comparison_figure(orig_path, norm_path, title, save_path, add_zoom):
            success_count += 1

    print(f"LC25000: {success_count} visual examples created")
    return success_count


def process_crc5000():
    """Generate visual examples for CRC5000 dataset."""
    print("\n" + "="*60)
    print("Processing CRC5000 Visual Examples")
    print("="*60)

    original_dir = Path("data/processed/CRC5000/Kather_texture_2016_image_tiles_5000")
    normalized_dir = Path("data/processed/CRC5000/macenko_norm")
    output_dir = Path("results/figures/visual_examples")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Select 3 representative images
    norm_images = select_representative_images(normalized_dir, n_samples=3)

    success_count = 0
    for i, norm_path in enumerate(norm_images, 1):
        # Find corresponding original
        relative_path = norm_path.relative_to(normalized_dir)
        orig_path = original_dir / relative_path

        if not orig_path.exists():
            # Try alternative location
            orig_path = original_dir / norm_path.name

        if not orig_path.exists():
            continue

        # Create comparison (with zoom for first example)
        title = f"CRC5000 Example {i} - {norm_path.parent.name}/{norm_path.name}"
        save_path = output_dir / f"crc5000_example_{i}.png"
        add_zoom = (i == 1)  # Add zoom only for first example

        if create_comparison_figure(orig_path, norm_path, title, save_path, add_zoom):
            success_count += 1

    print(f"CRC5000: {success_count} visual examples created")
    return success_count


def main():
    """Main function to generate all visual examples."""
    print("="*60)
    print("VISUAL EXAMPLES GENERATION - Phase 5")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Random seed: {RANDOM_SEED}")
    print()

    # Set random seed
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # Process both datasets
    lc_count = process_lc25000()
    crc_count = process_crc5000()

    total = lc_count + crc_count

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total visual examples created: {total}")
    print(f"  LC25000: {lc_count} examples")
    print(f"  CRC5000: {crc_count} examples")
    print(f"\nOutput directory: results/figures/visual_examples/")

    # Update log
    log_dir = Path("results/logs")
    log_path = log_dir / "pipeline.log"

    with open(log_path, 'a') as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Phase 5 - Visual Examples COMPLETED\n")
        f.write(f"Generated {total} side-by-side comparisons (original vs normalized)\n")
        f.write(f"  LC25000: {lc_count} examples\n")
        f.write(f"  CRC5000: {crc_count} examples\n")
        f.write(f"Output: results/figures/visual_examples/\n")

    print(f"\nLog updated: {log_path}")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
