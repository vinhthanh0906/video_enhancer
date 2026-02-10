'''
Description:
    - Docstring for utils.video_io
Components:
    - Ensure video path--> String and exist
    - Read the system path and upload the video 
    - Open the video and frame 

Author: Vinh Thanh Nguyen 
Date: Jan 27 2026

'''


import os 
import cv2 

def validPath(path: str)-> None:
    os.makedirs(path, exist_ok=True)
    
def openVideo(path: str)-> cv2.VideoCapture:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError("Could not open video (codec/path issue).")
    return cap 

def getVideoMeta(cap:  cv2.VideoCapture)-> dict:
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0 
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0 
    width = int (cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 0 
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 0 
    return {"fps": fps, "frame_count": frame_count, "width": width, "height": height}
    
def framePath(out_dir: str, frame_idx: int, ext: str = "png") -> str:
    return os.path.join(out_dir, f"frame_{frame_idx:06d}.{ext}")



