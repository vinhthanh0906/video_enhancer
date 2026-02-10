import os
import cv2
from typing import Optional, Callable


class CLAHEVideoProcessor:
    def __init__(
        self,
        clip_limit: float = 2.0,
        tile_grid_size: tuple[int, int] = (8, 8),
        codec: str = "mp4v",
    ):
        self.clip_limit = float(clip_limit)
        self.tile_grid_size = tile_grid_size
        self.codec = codec

        self._clahe = cv2.createCLAHE(
            clipLimit=self.clip_limit,
            tileGridSize=self.tile_grid_size
        )

    def _apply_clahe(self, frame_bgr):
        lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l2 = self._clahe.apply(l)
        lab2 = cv2.merge((l2, a, b))
        return cv2.cvtColor(lab2, cv2.COLOR_LAB2BGR)

    def process(
        self,
        input_video: str,
        output_video: str,
        progress_cb: Optional[Callable[[int, str], None]] = None,
        cancel_cb: Optional[Callable[[], bool]] = None,
    ) -> str:
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open input video: {input_video}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0

        os.makedirs(os.path.dirname(output_video) or ".", exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        writer = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
        if not writer.isOpened():
            cap.release()
            raise RuntimeError("Cannot open VideoWriter. Try codec='XVID' and output '.avi'")

        if progress_cb:
            progress_cb(0, f"CLAHE running… {w}x{h} @ {fps:.2f} fps")

        idx = 0
        while True:
            if cancel_cb and cancel_cb():
                if progress_cb:
                    progress_cb(0, "Cancelled.")
                break

            ret, frame = cap.read()
            if not ret:
                break

            out_frame = self._apply_clahe(frame)
            writer.write(out_frame)

            idx += 1
            if progress_cb and total > 0 and (idx % 5 == 0):
                pct = int((idx / total) * 100)
                progress_cb(min(100, max(0, pct)), f"Frame {idx}/{total}")

        cap.release()
        writer.release()

        if progress_cb and not (cancel_cb and cancel_cb()):
            progress_cb(100, "Done.")
        return output_video
