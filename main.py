import os
import subprocess
import tempfile
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QProgressBar,
    QSlider,
    QPushButton,
    QFileDialog,
    QLabel,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class VideoProcessingThread(QThread):
    progress_update = pyqtSignal(int, str)
    processing_complete = pyqtSignal()

    def __init__(self, input_video, output_video, compression_level):
        QThread.__init__(self)
        self.input_video = input_video
        self.output_video = output_video
        self.compression_level = compression_level

    def run(self):
        self.process_video()

    def process_video(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update progress bar to "Processing"
            self.progress_update.emit(0, "Processing")

            # Extract video information
            ffprobe_cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-count_packets",
                "-show_entries",
                "stream=r_frame_rate,nb_read_packets",
                "-of",
                "csv=p=0",
                self.input_video,
            ]
            ffprobe_output = (
                subprocess.check_output(ffprobe_cmd).decode("utf-8").strip().split(",")
            )
            fps = eval(ffprobe_output[0])
            total_frames = int(ffprobe_output[1])

            # Update progress bar to "Extracting frames"
            self.progress_update.emit(0, "Extracting frames")

            # Extract frames and audio
            extract_cmd = [
                "ffmpeg",
                # "-hwaccel cuda", not working for some reason??
                "-i",
                self.input_video,
                "-vf",
                f"fps={fps}",
                f"{temp_dir}/frame%08d.png",
                "-q:v",
                "1",
                f"{temp_dir}/audio.aac",
            ]
            subprocess.run(extract_cmd, check=True)
            
            # Apply JPEG compression
            for i in range(1, total_frames + 1):
                input_frame = f"{temp_dir}/frame{i:08d}.png"
                output_frame = f"{temp_dir}/processed_frame{i:08d}.jpg"

                # Convert PNG to JPG (which applies JPEG compression)
                compress_cmd = [
                    "ffmpeg",
                    # "-hwaccel cuda", not working for some reason??
                    "-i",
                    input_frame,
                    "-q:v",
                    str(self.compression_level),
                    output_frame,
                ]
                subprocess.run(compress_cmd, check=True)

                # Update progress
                self.progress_update.emit(
                    int((i / total_frames) * 100),
                    f"Processing frame {i}/{total_frames}",
                )

            # Update progress bar to "Combining frames"
            self.progress_update.emit(100, "Combining frames")

            # Combine processed frames and audio
            combine_cmd = [
                "ffmpeg",
                # "-hwaccel cuda", not working for some reason??
                "-framerate",
                str(fps),
                "-i",
                f"{temp_dir}/processed_frame%08d.jpg",
                "-i",
                f"{temp_dir}/audio.aac",
                "-c:v",
                "libx264",
                "-crf",
                "23",
                "-preset",
                "medium",
                "-c:a",
                "copy",
                self.output_video,
            ]
            subprocess.run(combine_cmd, check=True)

        self.processing_complete.emit()


class VideoProcessorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.input_button = QPushButton("Select Input Video")
        self.input_button.clicked.connect(self.select_input)
        layout.addWidget(self.input_button)

        self.output_button = QPushButton("Select Output Video")
        self.output_button.clicked.connect(self.select_output)
        layout.addWidget(self.output_button)

        self.compression_label = QLabel("Compression Level: 1")
        layout.addWidget(self.compression_label)

        self.compression_slider = QSlider(Qt.Horizontal)
        self.compression_slider.setMinimum(1)
        self.compression_slider.setMaximum(31)
        self.compression_slider.setValue(1)
        self.compression_slider.valueChanged.connect(self.update_compression_label)
        layout.addWidget(self.compression_slider)

        self.process_button = QPushButton("Process Video")
        self.process_button.clicked.connect(self.process_video)
        layout.addWidget(self.process_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setWindowTitle("Video Processor")
        self.setGeometry(300, 300, 400, 200)

        self.input_video = ""
        self.output_video = ""

    def select_input(self):
        self.input_video, _ = QFileDialog.getOpenFileName(self, "Select Input Video")
        self.input_button.setText(
            os.path.basename(self.input_video) or "Select Input Video"
        )

    def select_output(self):
        self.output_video, _ = QFileDialog.getSaveFileName(self, "Select Output Video")
        self.output_button.setText(
            os.path.basename(self.output_video) or "Select Output Video"
        )

    def update_compression_label(self, value):
        self.compression_label.setText(f"Compression Level: {value}")

    def process_video(self):
        if not self.input_video or not self.output_video:
            return

        self.process_button.setEnabled(False)
        self.thread = VideoProcessingThread(
            self.input_video, self.output_video, self.compression_slider.value()
        )
        self.thread.progress_update.connect(self.update_progress)
        self.thread.processing_complete.connect(self.processing_finished)
        self.thread.start()

    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.progress_bar.setFormat(f"{text} - %p%")

    def processing_finished(self):
        self.progress_bar.setValue(100)
        self.progress_bar.setFormat("Processing Complete - 100%")
        self.process_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VideoProcessorGUI()
    ex.show()
    sys.exit(app.exec_())
