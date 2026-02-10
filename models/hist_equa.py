import cv2 
import numpy as np

class HistogramEqualizer:

    def apply(self, frame_bgr: np.ndarray) -> np.ndarray:
        if frame_bgr is None:
            return frame_bgr

        if len(frame_bgr.shape) == 2 or frame_bgr.shape[2] == 1:
            return cv2.equalizeHist(frame_bgr)

        ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        y_eq = cv2.equalizeHist(y)
        ycrcb_eq = cv2.merge((y_eq, cr, cb))
        out = cv2.cvtColor(ycrcb_eq, cv2.COLOR_YCrCb2BGR)
        return out