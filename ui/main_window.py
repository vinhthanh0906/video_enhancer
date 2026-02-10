import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QPushButton, QFileDialog, QProgressBar, QMessageBox, QDoubleSpinBox
)
from ui.widgets import path_picker_row
from thread.extract_worker import ExtractWorker

#Histogram of euqualization
from thread.histeq_worker import HistEqWorker
from thread.clahe_worker import CLAHEWorker
from thread.power_law_worker import PowerLawWorker

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Enhancer - Step 1: Extract Frames")
        self.worker = None

        root = QVBoxLayout(self)

        # Video path
        row, self.video_edit, btn_video = path_picker_row("Video:", "Choose Video…")
        btn_video.clicked.connect(self.choose_video)
        root.addLayout(row)

        # Output folder
        row, self.out_edit, btn_out = path_picker_row("Output:", "Choose Folder…")
        btn_out.clicked.connect(self.choose_out)
        root.addLayout(row)

        # Mode + N
        mode_row = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Extract at N fps (frames/sec)", userData="fps")
        self.mode_combo.addItem("Extract every N frames", userData="every_n")
        self.n_spin = QSpinBox()
        self.n_spin.setRange(1, 9999)
        self.n_spin.setValue(1)
        mode_row.addWidget(QLabel("Mode:"))
        mode_row.addWidget(self.mode_combo, 2)
        mode_row.addWidget(QLabel("N:"))
        mode_row.addWidget(self.n_spin, 1)
        root.addLayout(mode_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_extract)
        self.cancel_btn.clicked.connect(self.cancel_extract)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.cancel_btn)
        root.addLayout(btn_row)

        # Progress + status
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.status = QLabel("Ready.")
        self.status.setWordWrap(True)
        root.addWidget(self.progress)
        root.addWidget(self.status)

        self.setMinimumWidth(820)
        
        #histogram qualization
        # --- Histogram equalization section ---
        h2 = QHBoxLayout()
        self.histeq_btn = QPushButton("Histogram Equalization → Video")
        self.histeq_btn.clicked.connect(self.run_histeq)
        h2.addWidget(self.histeq_btn)
        root.addLayout(h2)


        #CLAHE
        clahe_row = QHBoxLayout()

        self.clahe_clip = QDoubleSpinBox()
        self.clahe_clip.setRange(0.1, 20.0)
        self.clahe_clip.setSingleStep(0.1)
        self.clahe_clip.setValue(2.5)

        self.clahe_tw = QSpinBox()
        self.clahe_tw.setRange(1, 64)
        self.clahe_tw.setValue(8)

        self.clahe_th = QSpinBox()
        self.clahe_th.setRange(1, 64)
        self.clahe_th.setValue(8)

        self.btn_clahe = QPushButton("CLAHE Enhance → Video")
        self.btn_clahe.clicked.connect(self.run_clahe)

        clahe_row.addWidget(QLabel("CLAHE clip:"))
        clahe_row.addWidget(self.clahe_clip)
        clahe_row.addWidget(QLabel("Tile:"))
        clahe_row.addWidget(self.clahe_tw)
        clahe_row.addWidget(QLabel("x"))
        clahe_row.addWidget(self.clahe_th)
        clahe_row.addStretch(1)
        clahe_row.addWidget(self.btn_clahe)

        root.addLayout(clahe_row)
        
        
        #Power_law
        power_row = QHBoxLayout()

        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.10, 5.00)
        self.gamma_spin.setSingleStep(0.05)
        self.gamma_spin.setValue(0.60)   # good start for low-light

        self.btn_power = QPushButton("Power-law (Gamma) → Video")
        self.btn_power.clicked.connect(self.run_powerlaw)

        power_row.addWidget(QLabel("Gamma:"))
        power_row.addWidget(self.gamma_spin)
        power_row.addStretch(1)
        power_row.addWidget(self.btn_power)

        root.addLayout(power_row)

        
    def run_powerlaw(self):
        in_path = self.video_edit.text().strip()
        out_dir = self.out_edit.text().strip()

        if not in_path:
            QMessageBox.warning(self, "Missing", "Please choose a video file.")
            return
        if not out_dir:
            QMessageBox.warning(self, "Missing", "Please choose an output folder.")
            return

        gamma = float(self.gamma_spin.value())
        out_path = os.path.join(out_dir, f"powerlaw_gamma_{gamma:.2f}.mp4")

        self.worker = PowerLawWorker(in_path, out_path, gamma=gamma, codec="mp4v")
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.finished_ok.connect(self.on_powerlaw_done)
        self.worker.failed.connect(self.on_powerlaw_fail)

        self.progress.setValue(0)
        self.status.setText("Starting power-law enhancement…")
        self.set_running(True)
        self.worker.finished.connect(lambda: self.set_running(False))
        self.worker.start()

        
    def run_powerlaw(self):
        in_path = self.video_edit.text().strip()
        out_dir = self.out_edit.text().strip()

        if not in_path:
            QMessageBox.warning(self, "Missing", "Please choose a video file.")
            return
        if not out_dir:
            QMessageBox.warning(self, "Missing", "Please choose an output folder.")
            return

        gamma = float(self.gamma_spin.value())
        out_path = os.path.join(out_dir, f"powerlaw_gamma_{gamma:.2f}.mp4")

        self.worker = PowerLawWorker(in_path, out_path, gamma=gamma, codec="mp4v")
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.finished_ok.connect(self.on_powerlaw_done)
        self.worker.failed.connect(self.on_powerlaw_fail)

        self.progress.setValue(0)
        self.status.setText("Starting power-law enhancement…")
        self.set_running(True)
        self.worker.finished.connect(lambda: self.set_running(False))
        self.worker.start()

    def on_powerlaw_done(self, out_path: str):
        QMessageBox.information(self, "Done", f"Saved: {out_path}")
        self.worker = None

    def on_powerlaw_fail(self, msg: str):
        QMessageBox.critical(self, "Error", msg)
        self.worker = None

        
        
        
        
        

    def choose_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )
        if path:
            self.video_edit.setText(path)

    def choose_out(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_edit.setText(folder)

    def set_running(self, running: bool):
        self.start_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.mode_combo.setEnabled(not running)
        self.n_spin.setEnabled(not running)

    def start_extract(self):
        video_path = self.video_edit.text().strip()
        out_dir = self.out_edit.text().strip()

        if not video_path or not os.path.isfile(video_path):
            QMessageBox.warning(self, "Missing", "Please choose a valid video file.")
            return
        if not out_dir:
            QMessageBox.warning(self, "Missing", "Please choose an output folder.")
            return

        mode = self.mode_combo.currentData()
        n = int(self.n_spin.value())

        self.worker = ExtractWorker(video_path, out_dir, mode, n, ext="png")
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.finished_ok.connect(self.on_done)
        self.worker.failed.connect(self.on_fail)

        self.progress.setValue(0)
        self.status.setText("Starting…")
        self.set_running(True)
        self.worker.start()

    def cancel_extract(self):
        if self.worker:
            self.worker.cancel()
            self.set_running(False)

    def on_done(self, saved: int):
        self.set_running(False)
        QMessageBox.information(self, "Done", f"Saved {saved} frames.")
        self.worker = None

    def on_fail(self, msg: str):
        self.set_running(False)
        QMessageBox.critical(self, "Error", msg)
        self.worker = None

    
    #Run histogram of equalization
    def run_histeq(self):
        video_path = self.video_edit.text().strip()
        out_dir = self.out_edit.text().strip()

        if not video_path:
            QMessageBox.warning(self, "Missing", "Choose a video first.")
            return
        if not out_dir:
            QMessageBox.warning(self, "Missing", "Choose an output folder.")
            return

        out_path = os.path.join(out_dir, "histeq_enhanced.mp4")

        self.worker = HistEqWorker(video_path, out_path)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.finished_ok.connect(lambda p: QMessageBox.information(self, "Done", f"Saved: {p}"))
        self.worker.failed.connect(lambda m: QMessageBox.critical(self, "Error", m))

        self.progress.setValue(0)
        self.status.setText("Starting histogram equalization…")
        self.set_running(True)
        self.worker.finished.connect(lambda: self.set_running(False))
        self.worker.start()

        
    #Run CLAHE
    def run_clahe(self):
        in_path = self.video_edit.text().strip()
        out_dir = self.out_edit.text().strip()

        if not in_path:
            QMessageBox.warning(self, "Missing", "Please choose a video file.")
            return
        if not out_dir:
            QMessageBox.warning(self, "Missing", "Please choose an output folder.")
            return

        clip = float(self.clahe_clip.value())
        tw = int(self.clahe_tw.value())
        th = int(self.clahe_th.value())

        out_path = os.path.join(out_dir, "clahe_enhanced.mp4")

        # Create worker
        self.worker = CLAHEWorker(in_path, out_path, clip, tw, th, codec="mp4v")
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(self.status.setText)
        self.worker.finished_ok.connect(self.on_clahe_done)
        self.worker.failed.connect(self.on_clahe_fail)

        self.progress.setValue(0)
        self.status.setText("Starting CLAHE…")
        self.set_running(True)     # reuse your existing function (start/cancel disable)
        self.worker.finished.connect(lambda: self.set_running(False))
        self.worker.start()
    def on_clahe_done(self, out_path: str):
        QMessageBox.information(self, "Done", f"Saved: {out_path}")
        self.worker = None

    def on_clahe_fail(self, msg: str):
        QMessageBox.critical(self, "Error", msg)
        self.worker = None
