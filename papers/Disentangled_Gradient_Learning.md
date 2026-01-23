# Boosting Multimodal Learning via Disentangled Gradient Learning

**Authors:** Shicai Wei et al.
**Venue:** ICCV 2025 (or ArXiv 2022)
**Link:** https://arxiv.org/abs/2206.02425
**Citations:** High relevance to Gradient Starvation

## Abstract
The paper introduces a novel Disentangled Gradient Learning (DGL) framework designed to address optimization conflicts within multimodal models. Specifically, it tackles the issue where cross-modal interactions can reduce the gradient propagated back to individual modality encoders. DGL achieves this by decoupling the optimization of the modality encoder and the modality fusion module. It truncates the gradient from the multimodal loss to the modality encoder and replaces it with gradients derived from unimodal losses.

## Key Contributions
- **Disentangled Gradient Learning (DGL):** Main proposed framework.
- **Gradient Decoupling:** Separating fusion gradients from encoder gradients.
- **Conflict Resolution:** Eliminating interference between unimodal and multimodal objectives.
