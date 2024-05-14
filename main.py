import cv2
import datetime
import time
import RPi.GPIO as gpio

import passport
import qr
import check_if


def QRCR():
    cap = cv2.VideoCapture(0)
    face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # conditions for the execution of functions, to reduce the load on the processor
    USER_VERIFICATION = True
    NO_INFO_ABOUT_QR = True
    NO_DATA_FROM_QR = False
    TYPE_OF_PASSPORT = False
    BLINKS = False
    NO_INFO_FROM_PASSPORT = False
    BIRTHDAY_RECOGNIZED = False
    SERIES_RECOGNIZED = False
    PASSPORT_EXISTS = False
    ANSWR = True
    # Attempts to recognize text from a passport
    iter_of_h = 0
    iter_of_dr = 0
    try_of_date = 7
    try_of_recogn=0
    try_of_orig = 15
    try_of_pasport = 15
    try_of_pasport2 = 20
    NO_COVER=0
    cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
    # Checking if there is activity
    start_of_script = datetime.datetime.now()
    while USER_VERIFICATION:
        ret, img = cap.read()
        # A function that is responsible for the execution of a piece of code and the smoothness of the picture
        check = check_if.usl(NO_INFO_ABOUT_QR, NO_DATA_FROM_QR, TYPE_OF_PASSPORT, NO_INFO_FROM_PASSPORT,
                             BLINKS, BIRTHDAY_RECOGNIZED, SERIES_RECOGNIZED, PASSPORT_EXISTS)
        if check > 2:
            if check == 3:
                gpio.output(16, 1)
            if check == 5 and NO_COVER==1:
                gpio.output(16, 0)
                gpio.output(22, 1)
            if check > 5:
                gpio.output(16, 1)
        cv2.imshow('frame', img)
        if cv2.waitKey(15) & 0xff == ord('q'):
            break
        # Converting an image to gray
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # The first function, receives data from the QRcode
        if check == 1:
            print('Please, show qr code')
            qr_time = datetime.datetime.now()
            raz = qr_time - start_of_script
            if raz.seconds > 20:
                print('no activity')
                ANSWR = False
                break
            url_from_qr = qr.recognition(frame)
            if url_from_qr != None:
                if url_from_qr != 0:
                    NO_INFO_ABOUT_QR = False
                    NO_DATA_FROM_QR = True
                else:
                    print('Sorry, fake qr')
                    ANSWR = False
                    USER_VERIFICATION = False
                    break
        #  The second function, gets the data from the link from the code, formats it and checks if the code is valid
        if check == 2:
            expiration_date, birthday_date, passport_from_gos = qr.check(url_from_qr)
            if expiration_date != 0:
                # убираю все символы кроме чисел
                birthday_date = (''.join(x for x in birthday_date if x.isdigit()))
                passport_from_gos = (''.join(x for x in passport_from_gos if x.isdigit()))
                print(birthday_date)
                # проверяю совпадает ли дата
                date1 = datetime.datetime.strptime(expiration_date, "%d.%m.%Y")
                date2 = datetime.datetime.today()
                if date1 < date2:
                    print('sorry, qr code is no longer valid')
                    ANSWR = False
                    break
                else:
                    print('qr code is valid')
                    NO_DATA_FROM_QR = False
                    TYPE_OF_PASSPORT = True
        # Determining the type of passport, new or old
        if check == 3:
            print('Please, show your passport')
            tipe=passport.type_of_passport(frame)
            print(tipe)
            TYPE_OF_PASSPORT = False
            BLINKS = True
            NO_INFO_FROM_PASSPORT = True
        # Working with data from the passport
        if check == 5 or check == 6 or check == 7 or check == 8:
            faces = face_cascade_db.detectMultiScale(frame, 1.1, 19)
            for (x, y, w, h) in faces:
                if x > 0:
                    # Check for originality, implemented based on the available LEDs
                    if check == 5:
                        if NO_COVER==1:
                            pasp_o = passport.originality(frame, tipe)
                            print('try')
                            if pasp_o == True:
                                gpio.output(22, 0)
                                BIRTHDAY_RECOGNIZED = True
                                BLINKS = False
                                print('orig')
                            if pasp_o == False:
                                try_of_orig -= 1
                                if try_of_orig == 0:
                                    gpio.output(22, 0)
                                    print('Sorry, fake passport')
                                    ANSWR = False
                                    USER_VERIFICATION = False
                                    break
                            print('try2')
                        else:
                            BIRTHDAY_RECOGNIZED = True
                            BLINKS = False
                    # Birthday Recognition
                    if check == 6:
                        birthday_recognized = passport.birthday(frame, tipe)
                        if birthday_recognized != 0:
                            print(birthday_recognized)
                            if birthday_recognized == birthday_date:
                                print(passport_from_gos)
                                BIRTHDAY_RECOGNIZED = False
                                SERIES_RECOGNIZED = True
                            else:
                                try_of_date -= 1
                                if try_of_date == 0:
                                    gpio.output(16, 0)
                                    print('Sorry, the date of birth in the passport and on the website do not match')
                                    ANSWR = False
                                    USER_VERIFICATION = False
                                    break
                        if birthday_recognized==None:
                            try_of_recogn+=1
                        if try_of_recogn > 20:
                            print('re_tipe')
                            tipe_re,iter_of_h=passport.re_type_of_passport(frame,iter_of_h)
                            if iter_of_h>5:
                                tipe=tipe_re
                    if check == 7:
                        passport_recognized = passport.series(frame, tipe)
                        if passport_recognized != 0:
                            print(passport_recognized)
                            if passport_recognized[0:2] == passport_from_gos[0:2] and passport_recognized[
                                                                                      7:10] == passport_from_gos[2:5]:
                                SERIES_RECOGNIZED = False
                                # PASSPORT_EXISTS = True
                                gpio.output(16, 0)
                                USER_VERIFICATION = False
                                break
                            else:
                                try_of_pasport -= 1
                                passport_recognized = 0
                                frame = 0
                                if try_of_pasport == 0:
                                    gpio.output(16, 0)
                                    print(
                                        'Sorry, the series and number in the passport and on the website do not match')
                                    ANSWR = False
                                    USER_VERIFICATION = False
                                    break
                    if check==8:
                        if passport.exist(passport_recognized[0:4], passport_recognized[4:10]):
                            USER_VERIFICATION = False
                        else:
                            passport_recognized = passport.series(frame, tipe)
                            try_of_pasport2 -= 1
                            if try_of_pasport2 == 0:
                                USER_VERIFICATION = False
                                ANSWR = False
                                break
            check = 0
    cap.release()
    cv2.destroyAllWindows()
    return ANSWR


def QRstart(RCpin):
    gpio.setup(RCpin, gpio.IN)
    gpio.wait_for_edge(RCpin, gpio.RISING)
    signal = gpio.input(RCpin)
    print('catch')
    if QRCR():
        print('nice, u r wellcome')
    else:
        print('go away')


def main():
    gpio.setmode(gpio.BOARD)
    gpio.setup(16, gpio.OUT)  # GPIO 16 - к нему подключен лампу дневного света
    gpio.setup(22, gpio.OUT)  # GPIO 22 - к нему подключен лампу ультрафиолетовую
    gpio.setup(7, gpio.IN)  # GPIO 7 - к нему подключен инфракрасный датчик
    gpio.output(16, 0)
    gpio.output(22, 0)
    while True:
        #         QRstart(7)
        #         time.sleep(2)
        n = input()
        if n == '1':
            if QRCR():
                print('nice, u r wellcome')
            else:
                print('go away')

                # time.sleep(5)


if __name__ == "__main__":
    main()