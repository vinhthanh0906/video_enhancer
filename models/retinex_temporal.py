import cv2
import numpy as np



def single_scale_retinex_L(
    L_8u: np.ndarray,
    sigma: float = 80.0,
    gain: float = 1.08,
    offset: float = 0.0,
    p_low: float = 5.0,
    p_high: float = 95.0
) -> np.ndarray:
    """
    Single-Scale Retinex on LAB L channel (uint8 -> uint8)
    Tuned to be conservative to reduce banding/posterization.
    """
    L = L_8u.astype(np.float32) / 255.0
    L = np.clip(L, 1e-6, 1.0)

    illum = cv2.GaussianBlur(L, (0, 0), sigmaX=sigma, sigmaY=sigma)
    illum = np.clip(illum, 1e-6, 1.0)

    R = np.log(L) - np.log(illum)

    lo, hi = np.percentile(R, (p_low, p_high))
    Rn = (R - lo) / (hi - lo + 1e-6)
    Rn = np.clip(Rn, 0.0, 1.0)

    out = gain * Rn + (offset / 255.0)
    out = np.clip(out, 0.0, 1.0)

    return (out * 255.0).astype(np.uint8)


def exposure_scale_from_mean(
    L_8u: np.ndarray,
    target_L: float = 98.0,      # lower => darker
    min_scale: float = 0.85,
    max_scale: float = 1.05      # clamp to avoid "heaven bright"
) -> float:
    mean = float(np.mean(L_8u))
    if mean < 1e-6:
        return 1.0
    s = target_L / mean
    s = max(min_scale, min(max_scale, s))
    return float(s)


def apply_scale(L_8u: np.ndarray, scale: float) -> np.ndarray:
    Lf = L_8u.astype(np.float32) * float(scale)
    return np.clip(Lf, 0, 255).astype(np.uint8)


def highlight_compress(L_8u: np.ndarray, strength: float = 0.60) -> np.ndarray:
    """
    Soft-knee highlight protection. strength=0 disables.
    Higher strength = more highlight compression (less washout).
    """
    if strength <= 1e-6:
        return L_8u
    x = L_8u.astype(np.float32) / 255.0
    x = np.clip(x, 0.0, 1.0)
    y = x / (x + strength * (1.0 - x) + 1e-6)
    return np.clip(y * 255.0, 0, 255).astype(np.uint8)



def denoise_chroma_lab(A_8u: np.ndarray, B_8u: np.ndarray, k: int = 3):
    """
    Median blur on chroma channels helps with 4:2:0 macroblock / chroma noise.
    Keep k small (3 or 5) to avoid color bleeding.
    """
    if k < 3:
        return A_8u, B_8u
    if k % 2 == 0:
        k += 1
    A2 = cv2.medianBlur(A_8u, k)
    B2 = cv2.medianBlur(B_8u, k)
    return A2, B2



def unsharp_mask_L(
    L_8u: np.ndarray,
    amount: float = 0.55,     # 0.3..0.8
    radius: float = 1.1,      # 0.8..2.0 (Gaussian sigma)
    threshold: float = 6.0    # increase to avoid sharpening blocks/noise
) -> np.ndarray:
    """
    Unsharp mask on luminance with thresholding to avoid amplifying compression blocks.
    """
    L = L_8u.astype(np.float32)
    blur = cv2.GaussianBlur(L, (0, 0), radius)
    detail = L - blur

    mask = (np.abs(detail) > threshold).astype(np.float32)
    sharp = L + amount * detail * mask

    return np.clip(sharp, 0, 255).astype(np.uint8)



def deband_L(L_8u: np.ndarray, sigma: float = 0.4) -> np.ndarray:
    """
    Tiny blur can reduce banding without killing edges (especially before sharpening).
    Set sigma=0 to disable.
    """
    if sigma <= 1e-6:
        return L_8u
    return cv2.GaussianBlur(L_8u, (0, 0), sigmaX=sigma, sigmaY=sigma)


def enhance_video(
    in_path: str,
    out_path: str,
    codec: str = "mp4v",

    # Retinex
    sigma_retinex: float = 80.0,
    gain_retinex: float = 1.08,
    offset_retinex: float = 0.0,
    p_low: float = 5.0,
    p_high: float = 95.0,

    target_L: float = 98.0,
    min_scale: float = 0.85,
    max_scale: float = 1.05,
    alpha_scale: float = 0.92,     # higher => steadier exposure

    # Highlight protection
    hl_strength: float = 0.60,

    # Chroma cleanup
    chroma_median_k: int = 3,

    # Deband + Sharpen (L only)
    deband_sigma: float = 0.4,
    sharp_amount: float = 0.55,
    sharp_radius: float = 1.1,
    sharp_threshold: float = 6.0,

    # Optional global denoise (slow)
    denoise: bool = False
):
    cap = cv2.VideoCapture(in_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {in_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*codec), fps, (w, h))
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"Cannot open writer: {out_path}")

    ema_scale = None  # smooth only a scalar scale => NO tracer

    while True:
        ok, frame_bgr = cap.read()
        if not ok:
            break

        if denoise:
            frame_bgr = cv2.fastNlMeansDenoisingColored(frame_bgr, None, 3, 3, 7, 21)

        lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
        L, A, B = cv2.split(lab)

        # Retinex on luminance 
        Lr = single_scale_retinex_L(
            L,
            sigma=sigma_retinex,
            gain=gain_retinex,
            offset=offset_retinex,
            p_low=p_low,
            p_high=p_high
        )

        #  Exposure guard: compute scale and smooth scale over time (NO ghosting) 
        s = exposure_scale_from_mean(Lr, target_L=target_L, min_scale=min_scale, max_scale=max_scale)
        if ema_scale is None:
            ema_scale = s
        else:
            ema_scale = alpha_scale * ema_scale + (1.0 - alpha_scale) * s

        Lx = apply_scale(Lr, ema_scale)

        Lx = highlight_compress(Lx, strength=hl_strength)

        Lx = deband_L(Lx, sigma=deband_sigma)

        A2, B2 = denoise_chroma_lab(A, B, k=chroma_median_k)

        Lx = unsharp_mask_L(Lx, amount=sharp_amount, radius=sharp_radius, threshold=sharp_threshold)

        out_lab = cv2.merge([Lx, A2, B2])
        out_bgr = cv2.cvtColor(out_lab, cv2.COLOR_LAB2BGR)

        writer.write(out_bgr)

    cap.release()
    writer.release()


#DARK VIDEO
# if __name__ == "__main__":
#     enhance_video(
#         in_path=r"D:\WORK\Python\CV\video_enhancer\data\bright.mp4",
#         out_path="debright.mp4",

#         # Exposure target (slightly darker = safer)
#         target_L=92.0,
#         min_scale=0.90,
#         max_scale=1.02,
#         alpha_scale=0.95,      # more temporal stability

#         # Retinex (very conservative)
#         sigma_retinex=120.0,   # larger = smoother illumination
#         gain_retinex=1.02,     # keep low to avoid banding
#         offset_retinex=0.0,
#         p_low=10.0,
#         p_high=90.0,

#         # Highlight protection
#         hl_strength=0.70,

#         # Chroma cleanup
#         chroma_median_k=3,

#         # Anti-banding FIRST
#         deband_sigma=0.7,

#         # Gentle sharpening
#         sharp_amount=0.35,
#         sharp_radius=1.3,
#         sharp_threshold=10.0,

#         # Optional global denoise (use only if very noisy)
#         denoise=False
#     )




#BRIGHT VIDEO 

if __name__ == "__main__":
    enhance_video(
        in_path=r"D:\WORK\Python\CV\video_enhancer\data\bright.mp4",
        out_path="debright.mp4",

        target_L=60.0,          # darker target → real debright
        min_scale=0.82,         # allow stronger exposure reduction
        max_scale=1.00,         # NEVER brighten
        alpha_scale=0.96,       # strong temporal stability

        sigma_retinex=140.0,    # large → remove lighting, not texture
        gain_retinex=1.015,    # ultra-safe (prevents halos/banding)
        offset_retinex=0.0,
        p_low=8.0,              # avoid gray blacks
        p_high=86.0,            # compress highlights

        hl_strength=0.78,       # strong highlight roll-off

        chroma_median_k=3,      # suppress Retinex chroma noise

        deband_sigma=0.8,       # important for skies & walls

        sharp_amount=0.25,      # reduce ringing
        sharp_radius=1.2,
        sharp_threshold=12.0,

        denoise=False           # enable only if source is very noisy
    )
