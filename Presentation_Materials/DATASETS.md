# Documentation: Multimodal Dataset Specifications

This document outlines the standard datasets chosen for the **Adaptive Gradient Harmonization** benchmarking suite. 

We utilize a rigorous "High-Imbalance" protocol, pairing a high-signal visual dataset (CIFAR-10) with a complex, noisy audio dataset (CREMA-D) to simulate the "Modality Laziness" phenomenon.

---

## 1. Visual Modality: CIFAR-10

- **Source**: [The CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)
- **Description**: A collection of 60,000 32x32 color images in 10 classes.
- **Classes**: Airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck.
- **Role in Benchmark**: Represents the **Dominant Modality**. 
    - The features are spatially correlated and relatively easy for CNNs to learn (High Signal-to-Noise Ratio).
    - Models typically reach >90% accuracy quickly, causing them to ignore the audio stream.
- **Preprocessing via `src/datasets.py`**:
    - **Resolution**: Resized to 32x32.
    - **Normalization**: Standard `(0.5, 0.5, 0.5)` mean/std.
    - **Input Shape**: Flattened to `(3072,)` for the MLP encoder or `(3, 32, 32)` for CNNs.

---

## 2. Audio Modality: CREMA-D

- **Source**: [Crowd-sourced Emotional Multimodal Actors Dataset (CREMA-D)](https://github.com/CheyneyComputerScience/CREMA-D)
- **Description**: A dataset of 7,442 original clips from 91 actors. These clips were from 48 male and 43 female actors between the ages of 20 and 74 coming from a variety of races and ethnicities.
- **Task**: Emotion Recognition (Anger, Disgust, Fear, Happiness, Neutral, Sadness).
- **Role in Benchmark**: Represents the **Weak/Lazy Modality**.
    - Audio signals are temporally complex and contain significant stochastic noise.
    - Learning requires extracting subtle frequency patterns over time, which is slower than visual pattern matching.
- **Preprocessing via `src/datasets.py`**:
    - **Loading**: Loaded via `torchaudio`.
    - **Feature Extraction**: Raw waveform is padded/truncated or processed into Log-Mel Spectrograms.
    - **Input Shape**: Variable length waveforms or fixed-size spectrograms (projected to 128-dim embeddings).
    - **Fallback**: If dataset files are missing, the loader generates simulated tensors with matching statistical variance (`std=2.0`) to mimick high noise.

---

## 3. The "Imbalance" Protocol

By pairing these two datasets, we create a **Synthetic Multimodal Task** where:
1.  **Objective**: Minimize Joint Cross-Entropy Loss.
2.  **Challenge**: The optimizer naturally gravitates towards the CIFAR-10 gradients because they offer the "path of least resistance" (steepest descent).
3.  **Success Metric**: A successful algorithm (like our Fairness Controller) must force the model to learn the CREMA-D targets despite the "distraction" of the easy CIFAR-10 task.
