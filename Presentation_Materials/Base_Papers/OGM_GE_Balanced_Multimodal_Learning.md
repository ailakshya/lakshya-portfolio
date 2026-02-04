# Balanced Multimodal Learning via On-the-fly Gradient Modulation

**Authors:** Xiaokang Peng, Yake Wei, Andong Deng, Dong Wang, Di Hu
**Venue:** CVPR 2022 (Oral)
**Link:** https://arxiv.org/abs/2203.15332
**Citations:** ~100+

## Abstract
This paper proposes a method to alleviate optimization imbalance in multimodal discriminative models by adaptively controlling the optimization of each modality. The approach, named On-the-fly Gradient Modulation (OGM-GE), introduces an extra dynamically changing Gaussian noise to prevent potential generalization drops. It addresses the issue where the dominant modality suppresses the training of other modalities.

## Key Contributions
- **OGM-GE:** On-the-fly Gradient Modulation with Generalization Enhancement.
- **Dynamic Noise:** injecting noise to the dominant modality's gradient to slow it down.
- **Optimization Imbalance:** Formal analysis of how different modalities converge at different rates.
