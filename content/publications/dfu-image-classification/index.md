---
title: "DFU Image Classification Cost Reduction"
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
publication: "Pipeline / In Progress"
publication_short: ""

abstract: "This project focuses on **Knowledge Distillation & Network Pruning** for efficient edge deployment of medical imaging models. By implementing a paired reduction strategy using a ResNet-50 Teacher and MobileNetV2 Student, we achieved a **3.47x inference speedup** on CPU and **1.71x** on GPU, optimized for edge deployment without sacrificing diagnostic accuracy."

# Summary. An optional shortened abstract.
summary: Knowledge Distillation & Network Pruning for efficient edge deployment, achieving 3.47x CPU speedup.

tags:
- Computer Vision
- Edge AI
- Model Optimization

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

projects: []
slides: ""
---
## Overview

Diabetic Foot Ulcer (DFU) detection relies on heavyweight models that are often unsuitable for mobile or edge deployment. This project addresses the computational bottleneck by applying **Knowledge Distillation (KD)** and **Network Pruning**.

### Key Achievements
1.  **Architecture**: ResNet-50 (Teacher) → MobileNetV2 (Student).
2.  **Performance**:
    *   **CPU Inference**: 3.47x Speedup.
    *   **GPU Inference**: 1.71x Speedup.
3.  **Deployment**: Optimized for low-latency healthcare devices.
