from PyQt6.QtCore import QThread, pyqtSignal
from models.clahe import CLAHEVideoProcessor


class CLAHEWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(str)   # output path
    failed = pyqtSignal(str)

    def __init__(self, in_path: str, out_path: str, clip_limit: float, tile_w: int, tile_h: int, codec: str = "mp4v"):
        super().__init__()
        self.in_path = in_path
        self.out_path = out_path
        self.clip_limit = float(clip_limit)
        self.tile_grid = (int(tile_w), int(tile_h))
        self.codec = codec
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            processor = CLAHEVideoProcessor(
                clip_limit=self.clip_limit,
                tile_grid_size=self.tile_grid,
                codec=self.codec
            )

            def progress_cb(pct: int, msg: str):
                self.progress.emit(pct)
                self.status.emit(msg)

            def cancel_cb() -> bool:
                return self._cancel

            out = processor.process(
                self.in_path,
                self.out_path,
                progress_cb=progress_cb,
                cancel_cb=cancel_cb
            )

            if not self._cancel:
                self.finished_ok.emit(out)

        except Exception as e:
            self.failed.emit(str(e))
