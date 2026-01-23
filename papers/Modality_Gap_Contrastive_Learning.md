# The Modality Gap in Multimodal Contrastive Learning

**Authors:** Liang et al.
**Venue:** NeurIPS 2022 / ICLR 2023
**Link:** https://arxiv.org/abs/2203.02053

## Abstract
This paper identifies and analyzes the **"Modality Gap"**: a phenomenon where the embeddings of different modalities (e.g., image and text) cluster globally in two separate regions of the hypersphere, even after "successful" contrastive training (like CLIP).
This gap limits the fine-grained alignment and transferability of the model. The authors propose temperature scaling and specific initialization techniques to close this gap.

## Key Contributions
- **Geometric Analysis:** Visualizing and quantifying the gap on the hypersphere.
- **cone effect:** Explaining why the gap arises (initialization + contrastive dynamics).
- **Gap Closing:** Simple techniques to reduce the gap and improve zero-shot performance.
