import sys 
from PySide6.QtCore import Qt 
from PySide6.QtWidgets import QPushButton, QMainWindow, QSlider


class ButtonHolder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Button Holder App")
        button = QPushButton("Press me")
        
        #Setup the button as our central widget 
        self.setCentralWidget(button)
        button.clicked.connect(self.signal_process)

    
    def signal_process(self):
        print("Hello world")
        

class Slider(QWidgets):
    
    def __init__(self):
        super().__init__()
        slider = QSlider(Qt.Horizon)
    
        
    