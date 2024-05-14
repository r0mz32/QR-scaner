import cv2
import numpy as np
import pytesseract
import requests
import json


def originality(img, tipe):
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade_db.detectMultiScale(img, 1.1, 19)
    for (x, y, w, h) in faces:
        if tipe == 0:
            ORIGINALITY_top_left_X = int(w * 2.2)
            ORIGINALITY_top_left_Y = int(h * 0.7)
            ORIGINALITY_lower_right_X = int(w * 5)
            ORIGINALITY_lower_right_Y = int(h * 1.8)
        if tipe == 1:
            ORIGINALITY_top_left_X = int(w * 2)
            ORIGINALITY_top_left_Y = int(h * 0.5)
            ORIGINALITY_lower_right_X = int(w * 4)
            ORIGINALITY_lower_right_Y = int(h * 1.5)
        orig = img[(y - ORIGINALITY_top_left_Y):(y + ORIGINALITY_lower_right_Y),
               (x - ORIGINALITY_top_left_X):(x + ORIGINALITY_lower_right_X)]
        invert_uf = cv2.bitwise_not(orig)
        _, binary_invert_uf = cv2.threshold(invert_uf, 70, 255, cv2.THRESH_BINARY)
        height, width = orig.shape
        if height > 0:
            b_u = 0
            for i in range(height):
                for j in range(width):
                    if binary_invert_uf[i, j] == 0:
                        b_u += 1
                        if b_u > 500:
                            break
            print(b_u)
            if b_u >= 10:
                return True
            else:
                return False


def birthday(img, tipe):
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade_db.detectMultiScale(img, 1.1, 19)
    for (x, y, w, h) in faces:
        if tipe == 0:
            BIRTHSDAY_top_left_X = int(w * 3.1)
            BIRTHSDAY_top_left_Y = int(h * 0.3)
            BIRTHSDAY_lower_right_X = int(w * 5)
            BIRTHSDAY_lower_right_Y = int(h * 0.9)
        if tipe == 1:
            BIRTHSDAY_top_left_X = int(w * 3)
            BIRTHSDAY_top_left_Y = int(h * 0.2)
            BIRTHSDAY_lower_right_X = int(w * 4.8)
            BIRTHSDAY_lower_right_Y = int(h * 0.8)
        part_of_birthday = img[(y + BIRTHSDAY_top_left_Y):(y + BIRTHSDAY_lower_right_Y),
                           (x + BIRTHSDAY_top_left_X):(x + BIRTHSDAY_lower_right_X)]
        if np.shape(part_of_birthday) != ():
            kernel = np.ones((1, 1), 'uint8')
            erode_birthday_from_img = cv2.erode(part_of_birthday, kernel, cv2.BORDER_REFLECT, iterations=1)
            ret, thresh = cv2.threshold(erode_birthday_from_img, 130, 255, cv2.THRESH_BINARY)
            pre_data = pytesseract.image_to_string(thresh, config="outputbase digits")
            # Удаляю все символы кроме цифр, для удобства работы
            birthday_str = (''.join(x for x in pre_data if x.isdigit()))
            if len(birthday_str) == 8:
                return birthday_str
        else:
            return 0

def series(img, tipe):
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade_db.detectMultiScale(img, 1.1, 19)
    height, width = img.shape
    for (x, y, w, h) in faces:
        if tipe == 0:
            SERIES_top_left_X = int(w * 5.2)
            SERIES_top_left_Y = int(h * 0.9)
            SERIES_lower_right_X = int(w * 6.4)
            SERIES_lower_right_Y = int(h * 2.3)
            if (x + SERIES_lower_right_X) > width:
                SERIES_lower_right_X = width - x
            part_of_number = img[(y - SERIES_top_left_Y):(y + SERIES_lower_right_Y),
                             (x + SERIES_top_left_X):(x + SERIES_lower_right_X)]
            series = cv2.transpose(part_of_number)
            series_t = cv2.flip(series, 0)
            # Перевожу фото в бинарный формат, пиксели светлее 150 станут белыми
        if tipe == 1:
            SERIES_top_left_X = int(w * 4.5)
            SERIES_top_left_Y = int(h * 0.8)
            SERIES_lower_right_X = int(w * 5.5)
            SERIES_lower_right_Y = int(h * 1.9)
            if (x + SERIES_lower_right_X) > width:
                SERIES_lower_right_X = width - x
            part_of_number = img[(y - SERIES_top_left_Y):(y + SERIES_lower_right_Y),
                             (x + SERIES_top_left_X):(x + SERIES_lower_right_X)]
            series = cv2.transpose(part_of_number)
            series_t = cv2.flip(series, 0)
            # Перевожу фото в бинарный формат, пиксели светлее 150 станут белыми
            if np.shape(series_t) != ():
                kernel = np.ones((1, 1), 'uint8')
                series_er = cv2.erode(series_t, kernel, cv2.BORDER_REFLECT, iterations=1)
                ret, thresh = cv2.threshold(series_er, 135, 255, cv2.THRESH_BINARY)
                # Распознавание только цифр
                pre_data = pytesseract.image_to_string(thresh, config="outputbase digits")
                # Удаляю все символы кроме цифр, для удобства работы
                series_str = (''.join(x for x in pre_data if x.isdigit()))
                if len(series_str) == 10:
                    return series_str
        return 0

def exist(series, number):
    url = "https://rtdataport.rt.ru/tech/check-passport?series=%s&number=%s&issuedate" % (series, number)
    response = requests.get(url, timeout=3, verify=False)
    info = json.loads(response.text)
    if info["responseCode"] == '300':
        return True
    else:
        return False

def type_of_passport(img):
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade_db.detectMultiScale(img, 1.1, 19)
    for (x, y, w, h) in faces:
        TIPE_top_left_X = int(w * 0)
        TIPE_top_left_Y = int(h * 1.9)
        TIPE_lower_right_X = int(w * 2)
        TIPE_lower_right_Y = int(h * 2.3)
        height1, width1 = img.shape
        if TIPE_lower_right_Y!=0 and TIPE_top_left_Y!=0:
            if (y + TIPE_lower_right_Y) > height1:
                TIPE_lower_right_Y = height1 - x
            tipe_rec = img[(y + TIPE_top_left_Y):(y + TIPE_lower_right_Y),
                       (x + TIPE_top_left_X):(x + TIPE_lower_right_X)]
            if np.shape(tipe_rec) != ():
                ret, thresh = cv2.threshold(tipe_rec, 140, 255, cv2.THRESH_BINARY)
                height, width = thresh.shape
                if height > 0:
                    b_u = 0
                    for i in range(height):
                        for j in range(width):
                            if thresh[i, j] == 0:
                                b_u += 1
                    if b_u > 500:
                        return 1
                    else:
                        return 0
def re_type_of_passport(img, iter_of_h):
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade_db.detectMultiScale(img, 1.1, 19)
    hip = 0
    tipe = 2
    for (x, y, w, h) in faces:
        if x != 0:
            hip = 2 * (h * h)
    if hip > 0 and hip < 20500:
        tipe = 0
        iter_of_h += 1
    if hip > 20500:
        tipe = 1
        iter_of_h += 1
    if iter_of_h > 5:
        return tipe, iter_of_h
    return tipe,iter_of_h