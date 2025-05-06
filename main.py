import sys
# import cv2

from picamera2 import Picamera2
from picamera2.previews.qt import QGlPicamera2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QDialog, QSlider, QHBoxLayout, QWidget, QTextEdit, QSplitter

from gpio_controller import GPIO_CONTROLLER, PINS
from fps_counter import FPSCounter

# from laser_gaze_process import GazeProcessor
# gp = GazeProcessor()

class EyeTrackingUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eye Tracking and Gaze Estimation")
        self.setGeometry(0, 0, 800, 600)  # Full screen resolution

        # logger
        self.log_widget = LogWidget(name="Logger", parent=self)
        self.gaze_data_log_widget = LogWidget(name="Gaze data", parent=self, buffer_size=100)

        # # Initialize OpenCV video capture
        # self.cap = cv2.VideoCapture(0)
        # if not self.cap.isOpened():
        #     raise RuntimeError("Unable to access webcam.")
        # width  = self.cap.get(3)
        # height = self.cap.get(4)
        # self.log_widget.log(f"{width=} {height=}")
        # # Webcam feed label
        # self.webcam_label = QLabel(self)
        # self.webcam_label.setStyleSheet("background-color: black;")
        # self.webcam_label.setAlignment(Qt.AlignCenter)
        # self.webcam_label.setMaximumHeight(height)

        # Initialize RaspberryPI camera capture
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"size": (800, 600)}))
        #Picamera QT widget
        self.qpicamera2 = QGlPicamera2(self.picam2, width=800, height=600, keep_ar=False)
        self.picam2.start()

        # self.fps_counter = FPSCounter(parent=self)

        # Hollow circular gaze point
        # self.gaze_label = QLabel(self)
        # self.gaze_label.setFixedSize(50, 50)  # Diameter of the circle
        # self.gaze_label.setStyleSheet("""
        #     background-color: transparent;
        #     border: 3px solid red;
        #     border-radius: 25px;  /* Half of fixed size to make it a circle */
        # """)
        # self.gaze_label.raise_()
        # self.gaze_label.hide()  # Initially hidden

        logger_container = QSplitter(Qt.Orientation.Horizontal)
        logger_container.addWidget(self.log_widget)
        logger_container.addWidget(self.gaze_data_log_widget)

        # Layout
        main_layout = QVBoxLayout()
        # main_layout.addWidget(self.webcam_label)
        main_layout.addWidget(self.qpicamera2)
        # main_layout.addWidget(self.fps_counter.label)
        main_layout.addWidget(logger_container)
        main_layout.addStretch()

        # GPIO control buttons
        self.gpio_controller = GPIO_CONTROLLER()
        
        self.left_button = QPushButton("Left", self)
        self.left_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.left_button.clicked.connect(lambda: self.gpio_controller.toggle_pin(PINS.LEFT))

        self.right_button = QPushButton("Right", self)
        self.right_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.right_button.clicked.connect(lambda: self.gpio_controller.toggle_pin(PINS.RIGHT))
        
        self.top_button = QPushButton("Top", self)
        self.top_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.top_button.clicked.connect(lambda: self.gpio_controller.toggle_pin(PINS.TOP))
        
        self.bottom_button = QPushButton("Bottom", self)
        self.bottom_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.bottom_button.clicked.connect(lambda: self.gpio_controller.toggle_pin(PINS.BOTTOM))
        
        self.camera_button = QPushButton("Camera", self)
        self.camera_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.camera_button.clicked.connect(lambda: self.gpio_controller.toggle_pin(PINS.CAMERA))

        gpio_buttons_layout = QHBoxLayout()
        gpio_buttons_layout.addWidget(self.left_button)
        gpio_buttons_layout.addWidget(self.bottom_button)
        gpio_buttons_layout.addWidget(self.top_button)
        gpio_buttons_layout.addWidget(self.right_button)
        gpio_buttons_layout.addWidget(self.camera_button)
        main_layout.addLayout(gpio_buttons_layout)


        # Control Buttons
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.settings_button.clicked.connect(self.open_settings_dialog)

        self.toggle_frame_button = QPushButton("Toggle Fullscreen", self)
        self.toggle_frame_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.toggle_frame_button.clicked.connect(self.toggle_window_mode)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.setStyleSheet("background-color: #444; color: white; font-size: 14px;")
        self.exit_button.clicked.connect(self.close)

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.toggle_frame_button)
        button_layout.addWidget(self.exit_button)

        main_layout.addLayout(button_layout)

        # Central widget
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Timer for webcam capture
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_frame)

        # Start webcam feed (Dont need when using PI)
        # self.timer.start(30)

        self.setWindowState(Qt.WindowFullScreen)
        self.is_full_screen = True  # Track current window mode

    def resizeEvent(self, event):
        self.log_widget.log(f"{self.centralWidget().size()=}")
        return super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keypress events."""
        if event.key() == Qt.Key_F11:
            self.toggle_window_mode()
        elif event.key() == Qt.Key_Escape:
            self.cap.release()
            self.close()

    # def update_frame(self):
    #     """Capture frame from webcam and update UI."""
    #     ret, frame = self.cap.read()
    #     frame = cv2.flip(frame, flipCode=1)
    #     if ret:
    #         # frame, gaze_data = gp.analize_frame(frame)
    #         gaze_data = ""
    #         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         h, w, ch = frame.shape
    #         bytes_per_line = ch * w
    #         qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #         self.webcam_label.setPixmap(QPixmap.fromImage(qimg))
    #         self.gaze_data_log_widget.log(gaze_data, append=False)
    #         self.fps_counter.frame_processed()

    def update_gaze_point(self, x, y):
        """Move the gaze point to specified screen coordinates."""
        self.gaze_label.move(x - self.gaze_label.width() // 2, y - self.gaze_label.height() // 2)
        self.gaze_label.raise_()
        self.gaze_label.show()

    def open_settings_dialog(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def toggle_window_mode(self):
        """Toggle between framed and frameless window."""
        if self.is_full_screen:
            # self.setWindowFlags(Qt.Window)
            self.showNormal()
        else:
            # self.setWindowFlags(Qt.FramelessWindowHint)
            self.showFullScreen()
        self.is_full_screen = not self.is_full_screen

    def closeEvent(self, event):
        """Handle application close event to release webcam."""
        self.cap.release()
        event.accept()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        # Example sliders for settings
        self.brightness_slider = QSlider(Qt.Horizontal, self)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)

        self.contrast_slider = QSlider(Qt.Horizontal, self)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(50)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Brightness"))
        layout.addWidget(self.brightness_slider)
        layout.addWidget(QLabel("Contrast"))
        layout.addWidget(self.contrast_slider)

        # Close button
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


class LogWidget(QWidget):
    def __init__(self, name="Logger", parent=None, buffer_size=100):
        super().__init__(parent)

        # Layout for the logger widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove unnecessary padding

        # Label to display the widget name
        self.label = QLabel(name, self)
        self.label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.label)

        # Text edit for displaying logs
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Make the text edit read-only
        self.text_edit.setStyleSheet("""
            background-color: black; 
            color: white; 
            font-family: Consolas, monospace;
            font-size: 12px;
        """)
        layout.addWidget(self.text_edit)

        # Limit the number of lines stored in the QTextEdit
        self.text_edit.document().setMaximumBlockCount(buffer_size)

    def log(self, message: str, append=True):
        """Append a message to the logger."""
        if append:
            self.text_edit.append(message)  # Add the message to the text edit
        else:
            self.text_edit.setText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EyeTrackingUI()
    window.show()
    # window.update_gaze_point(100, 100)  # Example: Center of a 1920x1080 screen
    sys.exit(app.exec())
