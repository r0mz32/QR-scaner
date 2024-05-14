from pyzbar import pyzbar
import re
import requests as req
import json

def recognition(image):
    barcode = pyzbar.decode(image)
    for obj in barcode:
        url_from_qr = obj.data.decode("utf-8")
        barcodeType = obj.type
        if barcodeType == 'QRCODE':
            match = re.search('https://www.gosuslugi.ru/covid-cert/status/\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\S\Slang=\w\w', url_from_qr)
            if match:
                return url_from_qr
            else:
                return 0
def check(url):
    gos_id = url[url.rfind('/') + 1:url.find('?')]
    json_url = "https://www.gosuslugi.ru/api/covid-cert-checker/v3/cert/status/" + gos_id
    response = req.get(json_url)
    if response.status_code == 400:
        print("error")
        return 0, 0, 0
    else:
        json_text = response.text
        doc = json.loads(json_text)
        expiration_date = doc["expiredAt"]
        birthday_date = doc["attrs"][1]['value']
        passport = doc["attrs"][2]['value']
        return expiration_date, birthday_date, passport