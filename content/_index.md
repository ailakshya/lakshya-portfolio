---
# Leave the homepage title empty to use the site title
title: ''
summary: ''
date: 2022-10-24
type: landing

design:
  # Default section spacing
  spacing: '6rem'

sections:
  - block: resume-biography-3
    content:
      # Choose a user profile to display (a folder name within `content/authors/`)
      username: me
      text: ''
      # Show a call-to-action button under your biography? (optional)
      # Show a call-to-action button under your biography? (optional)
      button:
        text: "Download CV"
        url: "uploads/resume.pdf"
      headings:
        about: 'About Me'
        education: 'Education'
        interests: 'Focus Areas'
    design:
      # Use the new Gradient Mesh which automatically adapts to the selected theme colors
      background:
        gradient_mesh:
          enable: true

      # Name heading sizing to accommodate long or short names
      name:
        size: md # Options: xs, sm, md, lg (default), xl

      # Avatar customization
      avatar:
        size: medium # Options: small (150px), medium (200px, default), large (320px), xl (400px), xxl (500px)
        shape: circle # Options: circle (default), square, rounded
  - block: markdown
    content:
      title: '🔬 Research Highlights'
      subtitle: ''
      text: |-
        My research focuses on **Multimodal Representation Learning**, specifically addressing challenges like **Modality Laziness** and **Gradient Harmonization**.

        **Key Works:**
        *   **Adaptive Gradient Harmonization**: Mitigating Modality Dominance in Unified Representation Learning. (Under Review)
        *   **DFU Image Classification Cost Reduction**: Knowledge Distillation & Network Pruning for efficient edge deployment.

        I am also a strong proponent of **High-Performance Engineering**, building custom AI infrastructure and optimizing low-level GPU operations.
    design:
      columns: '1'
  - block: collection
    id: papers
    content:
      title: Featured Publications
      filters:
        folders:
          - publications
        featured_only: true
    design:
      view: article-grid
      columns: 2
  - block: collection
    content:
      title: Recent Publications
      text: ''
      filters:
        folders:
          - publications
        exclude_featured: false
    design:
      view: citation
  - block: collection
    id: projects
    content:
      title: Technical Projects
      subtitle: ''
      text: ''
      filters:
        folders:
          - projects
    design:
      view: card
      columns: 2
---
