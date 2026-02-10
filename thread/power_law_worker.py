from PyQt6.QtCore import QThread, pyqtSignal
from models.power_transformation import PowerLawVideoProcessor


class PowerLawWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished_ok = pyqtSignal(str)   # output path
    failed = pyqtSignal(str)

    def __init__(self, in_path: str, out_path: str, gamma: float, codec: str = "mp4v"):
        super().__init__()
        self.in_path = in_path
        self.out_path = out_path
        self.gamma = float(gamma)
        self.codec = codec
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        try:
            processor = PowerLawVideoProcessor(gamma=self.gamma, codec=self.codec)

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
