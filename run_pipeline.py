"""
Main Pipeline Script for Color Normalization
Processes both LC25000 and CRC5000 datasets
"""

import numpy as np
import cv2
from pathlib import Path
import sys
from datetime import datetime
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent))
from config.pipeline_config import DATASETS, MACENKO_PARAMS, PROCESSING, RANDOM_SEED
from src.macenko_normalization import normalize_image_file


def get_all_images(dataset_path, extensions=('*.jpeg', '*.jpg', '*.png', '*.tif', '*.tiff')):
    """Recursively find all images in a directory."""
    dataset_path = Path(dataset_path)
    images = []
    for ext in extensions:
        images.extend(dataset_path.rglob(ext))
    return sorted(images)


def process_dataset(dataset_name, config):
    """
    Process a single dataset with Macenko normalization.

    Parameters:
    -----------
    dataset_name : str
        Name of the dataset (e.g., 'LC25000', 'CRC5000')
    config : dict
        Dataset configuration from pipeline_config.py

    Returns:
    --------
    dict : Processing statistics
    """
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name}")
    print(f"{'='*60}")

    input_dir = Path(config['input_dir'])
    output_dir = Path(config['output_dir'])

    # Get all images
    images = get_all_images(input_dir)
    print(f"Found {len(images)} images")

    if len(images) == 0:
        print(f"Warning: No images found in {input_dir}")
        return {'total': 0, 'success': 0, 'failed': 0}

    # Set random seed
    np.random.seed(RANDOM_SEED)

    # Process images
    success_count = 0
    failed_count = 0

    for img_path in tqdm(images, desc=f"Normalizing {dataset_name}"):
        # Preserve directory structure
        relative_path = img_path.relative_to(input_dir)

        if PROCESSING['preserve_structure']:
            output_path = output_dir / relative_path
        else:
            output_path = output_dir / img_path.name

        # Skip if exists and skip_existing is True
        if PROCESSING['skip_existing'] and output_path.exists():
            success_count += 1
            continue

        # Process image
        success = normalize_image_file(
            img_path,
            output_path,
            Io=MACENKO_PARAMS['Io'],
            alpha=MACENKO_PARAMS['alpha'],
            beta=MACENKO_PARAMS['beta'],
            HERef=np.array(MACENKO_PARAMS['HERef']),
            maxCRef=np.array(MACENKO_PARAMS['maxCRef'])
        )

        if success:
            success_count += 1
        else:
            failed_count += 1

    stats = {
        'total': len(images),
        'success': success_count,
        'failed': failed_count
    }

    print(f"\n{dataset_name} Results:")
    print(f"  Total:   {stats['total']}")
    print(f"  Success: {stats['success']}")
    print(f"  Failed:  {stats['failed']}")

    return stats


def main():
    """Run the full pipeline on all datasets."""
    print("="*60)
    print("COLOR NORMALIZATION PIPELINE - Phase 2")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Method: Macenko normalization")
    print()

    all_stats = {}

    # Process each dataset
    for dataset_name, config in DATASETS.items():
        stats = process_dataset(dataset_name, config)
        all_stats[dataset_name] = stats

    # Summary
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    total_all = sum(s['total'] for s in all_stats.values())
    success_all = sum(s['success'] for s in all_stats.values())
    failed_all = sum(s['failed'] for s in all_stats.values())

    print(f"Total images processed: {total_all}")
    print(f"Successfully normalized: {success_all}")
    print(f"Failed: {failed_all}")
    print(f"Success rate: {100 * success_all / total_all:.2f}%")
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save log
    log_dir = Path("results/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_path = log_dir / "pipeline.log"
    with open(log_path, 'a') as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Phase 2 - Pipeline Execution\n")
        f.write(f"Method: Macenko normalization (Io={MACENKO_PARAMS['Io']}, alpha={MACENKO_PARAMS['alpha']}, beta={MACENKO_PARAMS['beta']})\n")
        for dataset_name, stats in all_stats.items():
            f.write(f"  {dataset_name}: {stats['success']}/{stats['total']} images normalized\n")
        f.write(f"Total: {success_all}/{total_all} images (Success rate: {100 * success_all / total_all:.2f}%)\n")

    print(f"\nLog saved to: {log_path}")


if __name__ == "__main__":
    main()
