from PyQt6.QtCore import QThread, pyqtSignal
from utils.video_process import VideoProcessor, VideoProcessConfig
from models.hist_equa import HistogramEqualizer

class HistEqWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(str)   # output path
    failed = pyqtSignal(str)

    def __init__(self, in_path: str, out_path: str):
        super().__init__()
        self.in_path = in_path
        self.out_path = out_path
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            processor = VideoProcessor()
            eq = HistogramEqualizer()
            cfg = VideoProcessConfig(out_fps=None, codec="mp4v")

            def progress_cb(pct: int, msg: str):
                self.progress.emit(pct)
                self.status.emit(msg)

            def cancel_cb() -> bool:
                return self._cancel

            processor.process(
                self.in_path,
                self.out_path,
                frame_transform=eq.apply,
                cfg=cfg,
                progress_cb=progress_cb,
                cancel_cb=cancel_cb,
            )

            if not self._cancel:
                self.finished_ok.emit(self.out_path)

        except Exception as e:
            self.failed.emit(str(e))
