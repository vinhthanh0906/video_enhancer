import os
import cv2
from typing import Optional, Callable
from utils.video_io import openVideo, getVideoMeta, validPath

class VideoProcessConfig:
    def __init__(self, out_fps: Optional[float] = None, codec: str = "mp4v"):
        self.out_fps = out_fps
        self.codec = codec

class VideoProcessor:
    """
    Apply a frame_transform(frame)->frame to every frame and write to output video.
    progress_cb(percent:int, msg:str)
    cancel_cb()->bool
    """
    def process(
        self,
        in_path: str,
        out_path: str,
        frame_transform,
        cfg: VideoProcessConfig,
        progress_cb: Optional[Callable[[int, str], None]] = None,
        cancel_cb: Optional[Callable[[], bool]] = None,
    ) -> None:
        cap = openVideo(in_path)
        meta = getVideoMeta(cap)

        fps_in = meta["fps"] if meta["fps"] > 0 else 30.0
        fps_out = cfg.out_fps if (cfg.out_fps and cfg.out_fps > 0) else fps_in
        w, h = meta["width"], meta["height"]
        total = meta["frame_count"]  # might be 0

        validPath(os.path.dirname(out_path) or ".")

        fourcc = cv2.VideoWriter_fourcc(*cfg.codec)
        writer = cv2.VideoWriter(out_path, fourcc, fps_out, (w, h))
        if not writer.isOpened():
            cap.release()
            raise RuntimeError("Could not open VideoWriter. Try codec='XVID' or output .avi")

        if progress_cb:
            progress_cb(0, f"Processing… {w}x{h} @ {fps_out:.2f} fps")

        idx = 0
        while True:
            if cancel_cb and cancel_cb():
                if progress_cb:
                    progress_cb(0, "Cancelled.")
                break

            ret, frame = cap.read()
            if not ret:
                break

            out_frame = frame_transform(frame)

            # Safety: ensure correct size for writer
            if out_frame.shape[1] != w or out_frame.shape[0] != h:
                out_frame = cv2.resize(out_frame, (w, h), interpolation=cv2.INTER_LINEAR)

            writer.write(out_frame)
            idx += 1

            if progress_cb and total > 0:
                pct = int((idx / total) * 100)
                progress_cb(min(100, max(0, pct)), f"Frame {idx}/{total}")

        cap.release()
        writer.release()

        if progress_cb:
            progress_cb(100, "Done.")
