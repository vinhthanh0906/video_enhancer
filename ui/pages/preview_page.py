import os
import glob
import cv2

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QSlider, QPushButton, QFileDialog
)

def cv_bgr_to_qpixmap(bgr):
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg)

class PreviewPage(QWidget):
    """
    Timeline-like frame preview for extracted frames.
    Expects a folder with frame_000001.png ... etc
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.frames = []  # list of filepaths
        self.current_index = 0

        root = QVBoxLayout(self)

        # Top controls
        top = QHBoxLayout()
        self.folder_label = QLabel("Folder: (none)")
        self.btn_load = QPushButton("Load Frames Folder…")
        self.btn_load.clicked.connect(self.pick_folder)
        top.addWidget(self.folder_label, 1)
        top.addWidget(self.btn_load)
        root.addLayout(top)

        # Big preview
        self.preview = QLabel("No frame loaded.")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(360)
        self.preview.setStyleSheet("background:#111; color:#ddd; border-radius:8px;")
        root.addWidget(self.preview)

        # Scrubber
        scrub = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.idx_label = QLabel("0 / 0")
        scrub.addWidget(QLabel("Timeline:"))
        scrub.addWidget(self.slider, 1)
        scrub.addWidget(self.idx_label)
        root.addLayout(scrub)

        # Thumbnail strip
        self.thumbs = QListWidget()
        self.thumbs.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumbs.setFlow(QListWidget.Flow.LeftToRight)
        self.thumbs.setWrapping(False)
        self.thumbs.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumbs.setMovement(QListWidget.Movement.Static)
        self.thumbs.setIconSize(QSize(120, 68))
        self.thumbs.setFixedHeight(110)
        self.thumbs.itemClicked.connect(self.on_thumb_clicked)
        root.addWidget(self.thumbs)

    # ---- Public API: call this after extraction finishes ----
    def load_frames_dir(self, folder: str):
        self.folder_label.setText(f"Folder: {folder}")

        # Get common patterns
        patterns = ["*.png", "*.jpg", "*.jpeg", "*.bmp"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(folder, p)))
        files.sort()

        self.frames = files
        self.thumbs.clear()

        if not self.frames:
            self.preview.setText("No frames found in folder.")
            self.slider.setRange(0, 0)
            self.idx_label.setText("0 / 0")
            return

        # Populate thumbnails (simple and reliable version)
        # For huge frame counts, we can later “sample” every k frames or async load.
        for i, fp in enumerate(self.frames):
            bgr = cv2.imread(fp)
            if bgr is None:
                continue
            thumb = cv2.resize(bgr, (240, 136), interpolation=cv2.INTER_AREA)
            icon = QIcon(cv_bgr_to_qpixmap(thumb))
            item = QListWidgetItem(icon, str(i))
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.thumbs.addItem(item)

        self.slider.setRange(0, len(self.frames) - 1)
        self.set_index(0)

    # ---- Internal handlers ----
    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select frames folder")
        if folder:
            self.load_frames_dir(folder)

    def set_index(self, idx: int):
        if not self.frames:
            return
        idx = max(0, min(idx, len(self.frames) - 1))
        self.current_index = idx

        fp = self.frames[idx]
        bgr = cv2.imread(fp)
        if bgr is None:
            return

        pix = cv_bgr_to_qpixmap(bgr)
        # Fit preview while preserving aspect
        scaled = pix.scaled(self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        self.preview.setPixmap(scaled)

        self.slider.blockSignals(True)
        self.slider.setValue(idx)
        self.slider.blockSignals(False)

        self.idx_label.setText(f"{idx+1} / {len(self.frames)}")

        # keep thumbnails visible
        item = self.thumbs.item(idx)
        if item:
            self.thumbs.setCurrentItem(item)
            self.thumbs.scrollToItem(item)

    def on_thumb_clicked(self, item: QListWidgetItem):
        idx = int(item.data(Qt.ItemDataRole.UserRole))
        self.set_index(idx)

    def on_slider_changed(self, value: int):
        self.set_index(value)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # re-scale current preview on resize
        if self.frames:
            self.set_index(self.current_index)
