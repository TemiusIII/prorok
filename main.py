import os

import cv2
import json
import requests
import threading
from time import sleep

from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings

# global settings -------------------------

temp_h = 0
cam_w = 1280
cam_h = 560
speed = 10
align = 100
res_koef = 0.5


# -----------------------------------------

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


def get_link():
    file_path = "test_image.png"
    search_url = 'https://yandex.ru/images/search'
    files = {'upfile': ('blob', open(file_path, 'rb'), 'image/jpeg')}
    params = {'rpt': 'imageview', 'format': 'json',
              'request': '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'}
    response = requests.post(search_url, params=params, files=files)
    query_string = json.loads(response.content)['blocks'][0]['params']['url']
    img_search_url = search_url + '?' + query_string

    return str(img_search_url)


def take_screenshot(link):
    global ready

    link = link.replace('&', '\"&\"')

    os.system(f'python get_screenshot.py --link {link}')
    print("Screenshot was successfully taken!")
    ready = 2


def process_image():
    global ready

    while True:
        if ready == -1:
            break
        if ready == 1:
            link = get_link()
            print(link)
            take_screenshot(link)
        sleep(0.5)


def video_stream():
    global ready
    global temp_h
    # Load the cascade
    # face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # To capture video from webcam.
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 10)
    # To use a video file as input
    # cap = cv2.VideoCapture('filename.mp4')
    f_pressed = False
    analysis_started = False

    start_temp = 0
    start_temp_limit = 5

    stop_temp = 0
    stop_temp_limit = 10

    while True:
        # Read the frame
        _, img = cap.read()
        # # Convert to grayscale
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Detect the faces
        # faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        # Draw the rectangle around each face
        search = cv2.waitKey(5) & 0xff
        if search == ord('f'):
            f_pressed = True
        else:
            f_pressed = False

            # for (x, y, w, h) in faces:
            #     cv2.imwrite("test_face.png", img[y - 30: y + h + 30, x - 30: x + w + 30])

        if not f_pressed and not analysis_started and stop_temp == stop_temp_limit:
            print("Start searching")
            height, width, channels = img.shape
            cv2.imwrite('test_image.png',
                        img[height // 2 - align:height // 2 + align, width // 2 - align:width // 2 + align])

            ready = 1
            analysis_started = False
            f_pressed = False
            start_temp = 0
            stop_temp = 0

        if analysis_started:
            height, width, channels = img.shape
            cv2.rectangle(img, (width // 2 - align, height // 2 - align), (width // 2 + align, height // 2 + align),
                          (255, 0, 0), 2)

        if f_pressed:
            if start_temp == start_temp_limit:
                analysis_started = True
            else:
                analysis_started = False

            if analysis_started:
                stop_temp = 0
            else:
                start_temp += 1

        else:
            if analysis_started:
                stop_temp += 1
            else:
                stop_temp = 0
                start_temp = 0

        if stop_temp == stop_temp_limit:
            analysis_started = False
            print("Analysis is over")

        if ready == 2:
            if 'webpage.png' in os.listdir():
                screen = cv2.imread('webpage.png')
                height, width, channels = screen.shape
                new_w = int(res_koef * cam_w)

                screen = cv2.resize(screen, (new_w, height))
                imS = cv2.resize(img, (cam_w, cam_h))

                if temp_h + cam_h < height - 1:
                    imS[0: cam_h, cam_w - new_w: cam_w] = screen[temp_h: temp_h + cam_h]
                    temp_h += speed
                else:
                    temp_h = 0
                    ready = 0
                    os.remove('webpage.png')
            else:
                temp_h = 0

        # Display
        if ready != 2 or 'webpage.png' not in os.listdir():
            imS = cv2.resize(img, (cam_w, cam_h))
        cv2.imshow('img', imS)


        # Stop if escape key is pressed
        k = cv2.waitKey(1) & 0xff
        if k == 27:
            ready = -1
            break
    # Release the VideoCapture object
    cap.release()


if __name__ == "__main__":
    global ready

    ready = 0
    counts = 1

    if 'webpage.png' in os.listdir():
        os.remove('webpage.png')

    main_f = threading.Thread(target=video_stream)
    process_f = threading.Thread(target=process_image, name=str(counts))
    main_f.start()
    process_f.start()

    # while main_f.is_alive():
    #     if help == 1:
    #         help = 0
    #         counts += 1
    #         threading.Thread(target=process_image, name=str(counts)).start()
    #
    #     sleep(0.5)
