# Reproducible Benchmark for Adaptive Gradient Harmonization

This directory contains the standardized benchmarking suite for the paper "Adaptive Gradient Harmonization". It is designed to work with standard datasets (CIFAR-10, CREMA-D) but includes robust fallbacks if data is missing.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install torch torchvision torchaudio matplotlib seaborn pandas numpy
   ```

2. **Run Benchmark**
   ```bash
   python3 benchmarking/run_reproducible.py
   ```
   *This command will automatically download CIFAR-10 (~170MB). If CREMA-D is not found, it will print a warning and use mock tensors for the audio stream to ensure the code runs successfully.*

## Data Setup (Optional)

To reproduce the *exact* results from the paper, you need the real CREMA-D dataset:

1. Download the CREMA-D `AudioWAV` zip file from [GitHub/Kaggle](https://github.com/CheyneyComputerScience/CREMA-D).
2. Unzip the wav files into `data/CREMA-D/`.
   * The folder structure should look like `data/CREMA-D/1001_DFA_ANG_XX.wav`.

## Code Structure

- `src/datasets.py`: Implementation of `CIFAR10Loader` and `CREMADLoader`. Contains the logic to check for file existence and generate compatible mock data if needed.
- `benchmarking/run_reproducible.py`: The main execution script. Redefines the `ModalityFairnessController` and runs the comparative study against Gradient Blending and OGM-GE.
