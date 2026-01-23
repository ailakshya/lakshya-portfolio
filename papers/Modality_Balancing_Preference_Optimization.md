# Modality-Balancing Preference Optimization (MBPO) for LMMs

**Authors:** Research Team (e.g., L. Wang et al.)
**Venue:** ICLR / NeurIPS (Recent 2024/2025)
**Link:** https://arxiv.org/abs/2405.xxxxx (Hypothetical, search specific MBPO)

## Abstract
This paper addresses the "hallucination" and "modality laziness" issues in Large Multimodal Models (LMMs). It introduces **Modality-Balancing Preference Optimization (MBPO)** to align the model's preference with a balanced usage of both visual and textual inputs.
The authors construct a dataset of "hard negatives" – examples where the model relies solely on the LLM prior (text) and ignores the image. By optimizing against these negatives, the model is forced to "look" at the image.

## Key Contributions
- **Preference Learning:** Applying DPO (Direct Preference Optimization) to modality balancing.
- **Hard Negative Mining:** Generating counterfactuals where text-only inference fails.
- **Reduction in Hallucinations:** Significant drop in object hallucination rates.
