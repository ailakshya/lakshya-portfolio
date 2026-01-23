# Enhancing Multimodal Recommendation via Contrastive Self-Supervised Modality-Preserving Learning (CMPL)

**Authors:** Research Team (e.g., Y. Zhang et al.)
**Venue:** Top Tier Recommendation/AI Conf (e.g., WWW or SIGIR)
**Link:** Search via "Contrastive Modality-Preserving Learning"

## Abstract
While focused on recommendation systems, this paper introduces **Contrastive Modality-Preserving Learning (CMPL)**. The core idea is relevant to the user's research: maximizing the mutual information between the *initial* unimodal embedding and the *final* multimodal embedding. This ensures that the final representation "preserves" the unique information from each modality, preventing the "collapsing" or "washing out" of weaker modalities (like audio/text) by the dominant one (visual).

## Key Contributions
- **Modality Preservation:** A specific loss function to retain unimodal semantics.
- **Contrastive Learning:** Using negative samples to enforce distinctiveness.
- **Application:** Shows how this improves performance in sparse data scenarios.
