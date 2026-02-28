# Scaling Multimodal Pre-Training via Cross-Modality Gradient Harmonization

**Authors:** Google Research Team
**Venue:** NeurIPS 2022
**Link:** https://arxiv.org/abs/2211.02077
**Citations:** High Impact

## Abstract
This paper addresses the challenges in self-supervised pre-training with large-scale multimodal data, where semantic misalignment can cause conflicts and biases among modalities, leading to "gradient conflicts". The authors propose Cross-Modality Gradient Realignment and Gradient-based Curriculum Learning. Applying these techniques to VATT pre-training on HowTo100M improved performance and allowed scaling to Youtube8M.

## Key Contributions
- **Cross-Modality Gradient Realignment:** Aligning gradient directions of different tasks.
- **Gradient-based Curriculum Learning:** Using gradient conflict as a noise indicator.
- **Scalability:** Demonstrated on large-scale datasets (HowTo100M, Youtube8M).
