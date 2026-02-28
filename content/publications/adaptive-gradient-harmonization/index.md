---
title: "Adaptive Gradient Harmonization: Mitigating Modality Dominance in Unified Representation Learning"
authors:
- me
date: "2025-01-23T00:00:00Z"
doi: ""

# Schedule page publish date (NOT publication's date).
publishDate: "2025-01-23T00:00:00Z"

# Publication type.
# Legend: 0 = Uncategorized; 1 = Conference paper; 2 = Journal article;
# 3 = Preprint / Working Paper; 4 = Report; 5 = Book; 6 = Book section;
# 7 = Thesis; 8 = Patent
publication_types: ["3"]

# Publication name and optional abbreviation
publication: "Under Review"
publication_short: ""

abstract: "In unified representation learning, distinct modalities often compete for optimization bandwidth, leading to a phenomenon known as 'Modality Laziness' or dominance. This paper introduces **Adaptive Gradient Harmonization**, a novel approach to mitigate this issue. We innovate the **Modality Fairness Controller (MFC)** to dynamically balance learning rates across Vision and Audio based on their real-time training dynamics. Furthermore, we propose the **Overfitting-to-Generalization Ratio (OGR)** as a new metric for evaluating multimodal model health. Our experiments on CIFAR-10 and CREMA-D benchmarks demonstrate a **2.3% accuracy boost** and a **40% reduction in modality imbalance**."

# Summary. An optional shortened abstract.
summary: Innovated the Modality Fairness Controller (MFC) to dynamically balance learning rates across Vision and Audio.

tags:
- Multimodal Learning
- Deep Learning
- Optimization

featured: true

links:
# - name: Custom Link
#   url: http://example.org
url_pdf: ''
url_code: ''
url_dataset: ''
url_poster: ''
url_project: ''
url_slides: ''
url_source: ''
url_video: ''

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder. 
image:
  caption: ''
  focal_point: ""
  preview_only: false

# Associated Projects (optional).
#   Associate this publication with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `internal-project` references `content/project/internal-project/index.md`.
#   Otherwise, set `projects: []`.
projects: []

# Slides (optional).
#   Associate this publication with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides: "example"` references `content/slides/example/index.md`.
#   Otherwise, set `slides: ""`.
slides: ""
---

## Overview

This research addresses the critical challenge of **Modality Dominance** in multimodal neural networks. When training on diverse data types (e.g., Audio and Vision), models often prioritize the modality that is "easier" to learn, neglecting the other.

### Key Contributions
1.  **Modality Fairness Controller (MFC)**: A dynamic mechanism that adjusts learning rates in real-time.
2.  **Overfitting-to-Generalization Ratio (OGR)**: A robustness metric for unified models.
3.  **Benchmark Success**: Verified improvements on CIFAR-10 and CREMA-D.
