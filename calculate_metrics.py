"""
Metrics Calculation Script - Phase 4
Calculates PSNR, SSIM, and RMSE between original and normalized images
"""

import numpy as np
import cv2
from pathlib import Path
import pandas as pd
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from datetime import datetime
from tqdm import tqdm
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config.pipeline_config import DATASETS, RANDOM_SEED


def calculate_image_metrics(original_path, normalized_path, channel_mode='rgb'):
    """
    Calculate PSNR, SSIM, and RMSE between two images.

    Parameters:
    -----------
    original_path : Path
        Path to original image
    normalized_path : Path
        Path to normalized image
    channel_mode : str
        'rgb' for 3-channel or 'gray' for single channel

    Returns:
    --------
    dict : Dictionary with PSNR, SSIM, RMSE values
    """
    # Read images
    orig = cv2.imread(str(original_path))
    norm = cv2.imread(str(normalized_path))

    if orig is None or norm is None:
        return None

    # Convert BGR to RGB
    orig_rgb = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
    norm_rgb = cv2.cvtColor(norm, cv2.COLOR_BGR2RGB)

    if channel_mode == 'gray':
        # Convert to grayscale
        orig_gray = cv2.cvtColor(orig_rgb, cv2.COLOR_RGB2GRAY)
        norm_gray = cv2.cvtColor(norm_rgb, cv2.COLOR_RGB2GRAY)

        # Calculate metrics
        psnr_val = psnr(orig_gray, norm_gray, data_range=255)
        ssim_val = ssim(orig_gray, norm_gray, data_range=255)
        rmse_val = np.sqrt(((orig_gray.astype(float) - norm_gray.astype(float)) ** 2).mean())
    else:
        # RGB mode - calculate on all channels
        psnr_val = psnr(orig_rgb, norm_rgb, data_range=255)
        ssim_val = ssim(orig_rgb, norm_rgb, channel_axis=2, data_range=255)
        rmse_val = np.sqrt(((orig_rgb.astype(float) - norm_rgb.astype(float)) ** 2).mean())

    # Cap PSNR at 60 dB to handle identical images (RMSE=0 → PSNR=inf)
    if np.isinf(psnr_val):
        psnr_val = 60.0

    return {
        'psnr': psnr_val,
        'ssim': ssim_val,
        'rmse': rmse_val
    }


def process_dataset(dataset_name, original_dir, normalized_dir, channel_mode='rgb'):
    """
    Process a dataset and calculate metrics for all image pairs.

    Parameters:
    -----------
    dataset_name : str
        Name of the dataset
    original_dir : Path
        Directory with original images
    normalized_dir : Path
        Directory with normalized images
    channel_mode : str
        'rgb' or 'gray'

    Returns:
    --------
    pd.DataFrame : DataFrame with metrics for each image
    """
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name}")
    print(f"{'='*60}")

    original_dir = Path(original_dir)
    normalized_dir = Path(normalized_dir)

    # Find all normalized images
    norm_images = list(normalized_dir.rglob('*.jpeg')) + \
                  list(normalized_dir.rglob('*.jpg')) + \
                  list(normalized_dir.rglob('*.png')) + \
                  list(normalized_dir.rglob('*.tif'))

    print(f"Found {len(norm_images)} normalized images")

    results = []
    skipped = 0

    for norm_path in tqdm(norm_images, desc=f"Calculating metrics for {dataset_name}"):
        # Find corresponding original image
        relative_path = norm_path.relative_to(normalized_dir)
        orig_path = original_dir / relative_path

        if not orig_path.exists():
            # Try alternative locations (original structure might differ)
            orig_path = original_dir / norm_path.name

        if not orig_path.exists():
            skipped += 1
            continue

        # Calculate metrics
        metrics = calculate_image_metrics(orig_path, norm_path, channel_mode)

        if metrics is not None:
            results.append({
                'dataset': dataset_name,
                'image': norm_path.name,
                'psnr_db': metrics['psnr'],
                'ssim': metrics['ssim'],
                'rmse': metrics['rmse']
            })

    print(f"Processed: {len(results)} images")
    print(f"Skipped: {skipped} images (original not found)")

    return pd.DataFrame(results)


def main():
    """Main function to calculate metrics for all datasets."""
    print("="*60)
    print("METRICS CALCULATION - Phase 4")
    print("="*60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Metrics: PSNR (dB), SSIM [0-1], RMSE")
    print(f"Channel mode: RGB (3-channel average)")
    print()

    # Set random seed
    np.random.seed(RANDOM_SEED)

    all_results = []

    # Process LC25000
    lc_original = "data/processed/LC25000/LC25000"
    lc_normalized = "data/processed/LC25000/macenko_norm"
    lc_df = process_dataset("LC25000", lc_original, lc_normalized, channel_mode='rgb')
    all_results.append(lc_df)

    # Process CRC5000
    crc_original = "data/processed/CRC5000/Kather_texture_2016_image_tiles_5000"
    crc_normalized = "data/processed/CRC5000/macenko_norm"
    crc_df = process_dataset("CRC5000", crc_original, crc_normalized, channel_mode='rgb')
    all_results.append(crc_df)

    # Combine all results
    combined_df = pd.concat(all_results, ignore_index=True)

    # Calculate summary statistics per dataset
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)

    summary_rows = []
    for dataset in ['LC25000', 'CRC5000']:
        dataset_metrics = combined_df[combined_df['dataset'] == dataset]

        if len(dataset_metrics) > 0:
            summary = {
                'dataset': dataset,
                'method': 'Macenko Normalization',
                'n_images': len(dataset_metrics),
                'psnr_mean': dataset_metrics['psnr_db'].mean(),
                'psnr_std': dataset_metrics['psnr_db'].std(),
                'ssim_mean': dataset_metrics['ssim'].mean(),
                'ssim_std': dataset_metrics['ssim'].std(),
                'rmse_mean': dataset_metrics['rmse'].mean(),
                'rmse_std': dataset_metrics['rmse'].std()
            }
            summary_rows.append(summary)

            print(f"\n{dataset}:")
            print(f"  Images: {summary['n_images']}")
            print(f"  PSNR: {summary['psnr_mean']:.2f} ± {summary['psnr_std']:.2f} dB")
            print(f"  SSIM: {summary['ssim_mean']:.4f} ± {summary['ssim_std']:.4f}")
            print(f"  RMSE: {summary['rmse_mean']:.2f} ± {summary['rmse_std']:.2f}")

    summary_df = pd.DataFrame(summary_rows)

    # Save results
    output_dir = Path("results/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save detailed metrics
    detailed_path = output_dir / "metrics_detailed.csv"
    combined_df.to_csv(detailed_path, index=False)
    print(f"\nDetailed metrics saved to: {detailed_path}")

    # Save summary metrics
    summary_path = output_dir / "metrics.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Summary metrics saved to: {summary_path}")

    # Save log
    log_dir = Path("results/logs")
    log_path = log_dir / "pipeline.log"

    with open(log_path, 'a') as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Phase 4 - Metrics Calculation COMPLETED\n")
        f.write(f"Method: RGB 3-channel metrics (PSNR, SSIM, RMSE)\n")
        for _, row in summary_df.iterrows():
            f.write(f"  {row['dataset']}: n={row['n_images']}, ")
            f.write(f"PSNR={row['psnr_mean']:.2f}±{row['psnr_std']:.2f} dB, ")
            f.write(f"SSIM={row['ssim_mean']:.4f}±{row['ssim_std']:.4f}, ")
            f.write(f"RMSE={row['rmse_mean']:.2f}±{row['rmse_std']:.2f}\n")

    print(f"\nLog updated: {log_path}")
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)


if __name__ == "__main__":
    main()
