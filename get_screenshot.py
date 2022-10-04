from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import argparse
import sys


class Screenshot(QWebEngineView):

    def capture(self, url, output_file):
        self.output_file = output_file
        self.load(QUrl(url))
        self.loadFinished.connect(self.on_loaded)
        # Create hidden view without scrollbars
        self.setAttribute(Qt.WA_DontShowOnScreen)
        self.page().settings().setAttribute(
            QWebEngineSettings.ShowScrollBars, False)
        self.show()

    def on_loaded(self):
        size = self.page().contentsSize().toSize()
        self.resize(size)
        # Wait for resize
        QTimer.singleShot(1000, self.take_screenshot)

    def take_screenshot(self):
        self.grab().save(self.output_file, b'PNG')
        self.close()


def take_screenshot(link):
    global help
    global ready
    app = QApplication(sys.argv)
    s = Screenshot()
    s.app = app
    s.capture(link,
              'webpage.png')

    sys.exit(app.exec_())

parser = argparse.ArgumentParser()

parser.add_argument('--link', required=True)
args = parser.parse_args()

take_screenshot(args.link)
print("Done")

