"""
Pipeline Configuration for Color Normalization
Phase 2 - Preprocessing Pipeline Design
"""

# Random seed for reproducibility
RANDOM_SEED = 42

# Dataset paths
DATASETS = {
    'LC25000': {
        'input_dir': 'data/processed/LC25000/LC25000',
        'output_dir': 'data/processed/LC25000/macenko_norm',
        'format': 'jpeg',
        'resolution': (768, 768),
        'use_patches': False,  # Images already appropriately sized
    },
    'CRC5000': {
        'input_dir': 'data/processed/CRC5000/Kather_texture_2016_image_tiles_5000',
        'output_dir': 'data/processed/CRC5000/macenko_norm',
        'format': 'tif',
        'resolution': (150, 150),
        'use_patches': False,  # Images are small tiles already
    }
}

# Macenko normalization parameters
MACENKO_PARAMS = {
    'Io': 240,           # Transmitted light intensity (default 240)
    'alpha': 1,          # Percentile for robust OD computation (1%)
    'beta': 0.15,        # OD threshold for tissue detection
    'HERef': [           # Reference H&E stain matrix
        [0.5626, 0.2159],  # Hematoxylin
        [0.7201, 0.8012],  # Eosin
        [0.4062, 0.5581]   # Residual
    ],
    'maxCRef': [1.9705, 1.0308]  # Reference maximum concentrations
}

# Processing parameters
PROCESSING = {
    'channel_mode': 'rgb',          # Color space: 'rgb' or 'gray'
    'preserve_structure': True,     # Maintain original folder structure
    'skip_existing': False,         # Re-process existing files
    'log_every': 100,              # Log progress every N images
}

# Pipeline steps (in order)
PIPELINE_STEPS = [
    "1. Load image (RGB)",
    "2. Apply Macenko color normalization",
    "3. Save normalized image (preserve format)",
]

# Optional: Denoising (currently disabled)
DENOISE_ENABLED = False
DENOISE_PARAMS = {
    'h': 10,                    # Filter strength
    'templateWindowSize': 7,    # Template patch size
    'searchWindowSize': 21,     # Search area size
}
