# Asymmetric Representation Learning for Multimodal optimization

**Authors:** (e.g., Z. Huang et al.)
**Venue:** CVPR / ICCV
**Link:** Recent arXiv

## Abstract
This paper challenges the assumption that "perfectly balanced" learning is always optimal. It introduces **Asymmetric Representation Learning (ARL)**, suggesting that optimization should adhere to the *modality variance ratio*.
Instead of forcing equal learning speeds, ARL modulates gradients to align with the *information content* (variance) of each modality. This prevents "noise" in weaker modalities from corrupting the shared embedding, while still allowing the stronger modality to drive the primary structure.

## Key Contributions
- **Variance-based scaling:** Learning rates are adjusted dynamically based on data variance.
- **No extra parameters:** Efficient implementation without complex controllers.
- **Theory:** Provides a theoretical justification for why asymmetry is beneficial in high-noise regimes.
