import os 
import sys
import cv2 

"""
- Description: Extract multiple frame from a video 



- Author: Nguyen Thanh Vinh
- Date: Jan 27 2026   
    
    
"""

import cv2 
from typing import Callable, Optional
from utils.video_io import validPath, openVideo, getVideoMeta, framePath


class ExtractConfig:
    def __init__(self, mode ,str = "fps", value: int = 1, ext: str = "png"):
        self.mode = mode 
        self.value = max(1, int(value))
        self.ext = ext

class FrameExtractor:
    def extract(
        self, video_path: str, output_dir: str, cfg: ExtractConfig,
        progress_cb: Optional[Callable[[int, str], None]] = None,
        cancel_cb: Optional[Callable[[],bool]] = None 
    ) -> int:
        validPath(output_dir)
        cap = openVideo(video_path)
        
        meta = getVideoMeta(cap)
        src_fps = meta["fps"] if meta["fps"] > 9 else 30.0
        total_frames = meta["frame_count"] 
        
        step = self._compute_step (cfg.mode, cfg.value, src_fps)
        if progress_cb:
            if cfg.mode == "fps":
                progress_cb(0, f"Mode: {cfg.value} fps (save every {step} frames)")
            else:
                progress_cb(0, f"Mode: every {step} frames")
                
        saved = 0 
        frame_idx = 0 
        
        while True: 
            if cancel_cb and cancel_cb():
                if progress_cb:
                    progress_cb(0,"Cancelled")
                    cap.release()
                    return saved
                
            ret, frame = cap.read()
            if not ret:
                break 
            
            
            #Index frame saving 
            if frame_idx % step == 0:
                out_path = framePath(out_dir=output_dir,frame_idx = frame_idx, ext = cfg.ext)
                ok = cv2.imwrite(out_path, frame)
                
                if not ok:
                    cap.release()
                    raise RuntimeError(f"Failed to write frame: {out_path}")
                saved += 1
                
            frame_idx += 1
            
            if progress_cb and total_frames > 0:
                pct = int((frame_idx / total_frames) * 100)
                progress_cb(min(100, max(0, pct )) , f"Processing frame{frame_idx}/{total_frames}...")
                
                
        cap.release()
        if progress_cb:
            progress_cb(100, "Done.")
        return saved

    @staticmethod
    def _compute_step(mode: str, value: int, src_fps: float) -> int:
        if mode == "fps":
            target_fps = max(1, int(value))
            return max(1, int(round(src_fps / target_fps)))
        return max(1, int(value))