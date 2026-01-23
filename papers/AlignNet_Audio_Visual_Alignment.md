# AlignNet: A Unifying Approach to Audio-Visual Alignment

**Authors:** (e.g., J. Smith et al.)
**Venue:** WACV / CVPR
**Link:** https://openaccess.thecvf.com/content/...

## Abstract
AlignNet addresses the problem of **non-uniform and irregular misalignment** between audio and video. Unlike global shift corrections (like SyncNet), AlignNet proposes an end-to-end trainable solution that can handle *arbitrary* temporal distortions (warping).
This is crucial for "Robustness" research, as it deals with the *temporal* aspect of modality dominance—if one modality is slightly delayed, the model might ignore it.

## Key Contributions
- **Dense Alignment:** Frame-by-frame alignment rather than global shift.
- **Warping correction:** Can fix speed variations between audio and video.
- **Self-supervised:** Learns from naturally synchronized videos by synthetically de-syncing them.
