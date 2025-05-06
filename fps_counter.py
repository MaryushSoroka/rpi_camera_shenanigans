from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QTimer

class FPSCounter:
    def __init__(self, parent=None, update_interval=1000):
        """
        FPSCounter tracks and displays frames per second using Qt functionality.

        :param parent: The parent widget for the FPS label.
        :param update_interval: Interval (ms) to update the FPS display.
        """
        self.frame_count = 0
        self.label = QLabel(parent)
        self.label.setStyleSheet("""
            color: white;
            background-color: black;
            font-size: 16px;
            padding: 5px;
        """)
        self.label.setFixedSize(100, 30)
        self.label.setText("FPS: 0")
        # self.label.move(10, 10)  # Position the label on the screen
        # self.label.show()

        # QTimer to update FPS every `update_interval` milliseconds
        self.timer = QTimer(parent)
        self.timer.timeout.connect(self.update_fps)
        self.timer.start(update_interval)

    def frame_processed(self):
        """Increment the frame count for each processed frame."""
        self.frame_count += 1

    def update_fps(self):
        """Update the FPS display using the frame count."""
        self.label.setText(f"FPS: {self.frame_count}")
        self.frame_count = 0  # Reset the frame count
