import sys
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


CHUNK = 1000  # Veri bloğu boyutu
FORMAT = pyaudio.paInt16  # Veri formatı (16-bit PCM)
CHANNELS = 1  # Tek kanallı (mono)
RATE = 50000  # Örnekleme hızı (Hz)

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1)  # Grafiği güncelleme süresi (ms)

    def initUI(self):
        self.setWindowTitle('EEG Monitoring by Neurazum')
        self.setWindowIcon(QIcon('C:/Users/eyupi/PycharmProjects/Neurazum/NeurAI/Assets/neurazumicon.ico'))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [9, 1]})
        self.fig.tight_layout()
        self.canvas = FigureCanvas(self.fig)

        self.layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)

        self.x = np.arange(0, 2 * CHUNK, 2)
        self.line1, = self.ax1.plot(self.x, np.random.rand(CHUNK))
        self.line2, = self.ax2.plot(self.x, np.random.rand(CHUNK))

        self.legend_elements = [
            Line2D([0, 4], [0], color='yellow', lw=4, label='DELTA (0hz-4hz)'),
            Line2D([4, 7], [0], color='blue', lw=4, label='THETA (4hz-7hz)'),
            Line2D([8, 12], [0], color='green', lw=4, label='ALPHA (8hz-12hz)'),
            Line2D([12, 30], [0], color='red', lw=4, label='BETA (12hz-30hz)'),
            Line2D([30, 100], [0], color='purple', lw=4, label='GAMMA (30hz-100hz)')
        ]

    def update_plot(self):
        data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
        data = np.abs(data)
        voltage_data = data * (3.3 / 1024)  # Voltajı "mV" cinsine dönüştürme

        self.line1.set_ydata(data)
        self.line2.set_ydata(voltage_data)

        for coll in self.ax1.collections:
            coll.remove()

        self.ax1.fill_between(self.x, data, where=((self.x >= 0) & (self.x <= 4)), color='yellow', alpha=1)
        self.ax1.fill_between(self.x, data, where=((self.x >= 4) & (self.x <= 7)), color='blue', alpha=1)
        self.ax1.fill_between(self.x, data, where=((self.x >= 8) & (self.x <= 12)), color='green', alpha=1)
        self.ax1.fill_between(self.x, data, where=((self.x >= 12) & (self.x <= 30)), color='red', alpha=1)
        self.ax1.fill_between(self.x, data, where=((self.x >= 30) & (self.x <= 100)), color='purple', alpha=1)

        self.ax1.legend(handles=self.legend_elements, loc='upper right')
        self.ax1.set_ylabel('Şiddet (dB)')
        self.ax1.set_xlabel('Frekans (Hz)')
        self.ax1.set_title('Gerçek Zamanlı Frekans ve mV Değerleri')

        self.ax2.set_ylabel('Voltaj (mV)')
        self.ax2.set_xlabel('Zaman')

        self.canvas.draw()

    def close_application(self):
        self.timer.stop()
        stream.stop_stream()
        stream.close()
        p.terminate()
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
