# Video_Enhancer-
GUI for video brightness adjustment and video brighten, using CLAHE + Gamma Transformation, Retinex Theory 


This project is suitable for:
- Overexposed indoor/outdoor videos
- Bright skies, white walls, strong lighting
- Pre-processing for CV / ML pipelines

---

## Features

- Retinex-based illumination removal
- Exposure stabilization with temporal smoothing
- Highlight compression & roll-off
- Anti-banding (gradient smoothing)
- Chroma noise cleanup
- Optional gentle sharpening
- Video-safe (frame-to-frame stable)

---

## Requirements

- Python **3.9+**
- OpenCV
- NumPy
- SciPy

### Install dependencies

```bash
pip install -r requirements.txt
```

## Example usage: Retinex Config for bright video
``` bash
from enhance_video import enhance_video

enhance_video(
    in_path="data/bright.mp4",
    out_path="output/debright.mp4",

    # Exposure control
    target_L=86.0,
    min_scale=0.82,
    max_scale=1.00,
    alpha_scale=0.96,

    # Retinex
    sigma_retinex=140.0,
    gain_retinex=1.015,
    offset_retinex=0.0,
    p_low=8.0,
    p_high=88.0,

    # Highlight protection
    hl_strength=0.78,

    # Artifact control
    deband_sigma=0.8,
    chroma_median_k=3,

    # Sharpen (gentle)
    sharp_amount=0.25,
    sharp_radius=1.2,
    sharp_threshold=12.0,

    denoise=False
)
```


## Contact
Author: Vinh Thanh.  
GitHub: https://github.com/vinhthanh0906
