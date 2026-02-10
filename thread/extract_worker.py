'''
- Description: 
    Assign process to thread 

- Author: Vinh Thanh Nguyen
- Date: Jan 27 2026

'''



from PyQt6.QtCore import QThread, pyqtSignal
from utils.frame_extraction import FrameExtractor, ExtractConfig


class ExtractWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(int)
    failed = pyqtSignal(str)
    
    #Assign 
    def __init__(self, video_path: str, 
                 output_dir: str, 
                 mode: str, 
                 value: int,
                 ext: str = "png"):
        super().__init__()
        
        self.video_path = video_path 
        self.out_dir = output_dir
        self.cfg = ExtractConfig(mode=mode, value=value, ext= ext)
        self._cancel = False
        
    def cancel(self):
        self._cancel = True
    
    def run(self):
        try:
            extractor = FrameExtractor()

            def progress_cb(pct: int, msg: str):
                self.progress.emit(pct)
                self.status.emit(msg)

            def cancel_cb() -> bool:
                return self._cancel

            saved = extractor.extract(
                self.video_path,
                self.out_dir,
                self.cfg,
                progress_cb=progress_cb,
                cancel_cb=cancel_cb,
            )
            # If cancelled, we still emit finished with saved count (up to you)
            if self._cancel:
                self.status.emit("Cancelled.")
            self.finished_ok.emit(saved)

        except Exception as e:
            self.failed.emit(str(e))
        