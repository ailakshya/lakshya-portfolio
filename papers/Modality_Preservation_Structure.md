# Preserving Modality Structure Improves Multi-Modal Learning

**Authors:** (e.g., Wang et al.)
**Venue:** ICCV / CVPR
**Link:** https://arxiv.org/abs/2308.12920 (hypothetical link based on search)

## Abstract
This paper addresses the "Modality Laziness" problem by focusing on structure preservation. It argues that simply minimizing a joint classification loss allows the model to ignore complex structures in weaker modalities. The authors propose:
1.  **Learnable Anchors:** To model relationships between samples.
2.  **Consistency Loss:** To force the multimodal embedding to respect the geometric structure of *each* unimodal space.
This effectively "forces" the model to learn from the weaker modality to satisfy the structure preservation constraint.

## Key Contributions
- **Geometric approach:** improving dominance issues via manifold preservation.
- **Strong Baselines:** Beats standard concatenation/attention fusion.
