from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton

def path_picker_row(label: str, button_text: str):
    layout = QHBoxLayout()
    edit = QLineEdit()
    btn = QPushButton(button_text)
    layout.addWidget(QLabel(label))
    layout.addWidget(edit)
    layout.addWidget(btn)
    return layout, edit, btn
