# Characterizing and Overcoming the Greedy Nature of Learning in Multi-modal Deep Neural Networks

**Authors:** Nan Wu, Stanislaw Jastrzebski, Kyunghyun Cho, Krzysztof J. Geras
**Venue:** ICML 2022
**Link:** https://arxiv.org/abs/2202.05306
**Citations:** ~181

## Abstract
The paper hypothesizes that multi-modal deep neural networks tend to rely predominantly on one modality while under-fitting others, a behavior termed "greedy learning" that negatively impacts generalization. To address this, the authors propose a method to balance the "conditional learning speeds" between modalities during training. This approach has been shown to improve model generalization on datasets such as Colored MNIST, Princeton ModelNet40, and NVIDIA Dynamic Hand Gesture.

## Key Contributions
- **Greedy Learning:** Identification of the phenomenon where models over-rely on the easier modality.
- **Conditional Learning Speed:** A metric to measure how fast a model learns from a specific modality given others.
- **Balancing Algorithm:** A regularizer or optimization strategy to equalize these speeds.
