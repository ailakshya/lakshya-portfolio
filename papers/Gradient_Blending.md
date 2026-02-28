# What Makes Training Multi-Modal Classification Networks Hard? (Gradient Blending)

**Authors:** Weiyao Wang, Du Tran, Matt Feiszli
**Venue:** CVPR 2020
**Link:** https://arxiv.org/abs/1905.12681
**Citations:** High impact (~400+)

## Abstract
This paper is a seminal work in understanding why multimodal networks often underperform their unimodal counterparts. The authors identify "overfitting to the dominant modality" (often the one with the strongest signal) as a key issue. They propose **Gradient Blending**, a technique that computes an optimal blend of modalities based on their overfitting behavior during training. This method balances the learning rates of different modalities to prevent one from dominating the optimization landscape.

## Key Contributions
- **Analysis of Optimization:** Detailed study of how different modalities overfit at different rates.
- **Gradient Blending:** A method to re-weight gradients based on generalization performance.
- **Robustness:** Demonstrated improvements in Audio-Visual and Video-Audio tasks.
