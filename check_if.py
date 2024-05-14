def usl(NO_INFO_ABOUT_QR, NO_DATA_FROM_QR, TYPE_OF_PASSPORT, NO_INFO_FROM_PASSPORT, BLINKS,
        BIRTHDAY_RECOGNIZED, SERIES_RECOGNIZED, PASSPORT_EXISTS):
    if NO_INFO_ABOUT_QR:
        return 1
    elif NO_DATA_FROM_QR:
        return 2
    elif TYPE_OF_PASSPORT:
        return 3
    elif NO_INFO_FROM_PASSPORT:
        if BLINKS:
            return 5
        elif BIRTHDAY_RECOGNIZED:
            return 6
        elif SERIES_RECOGNIZED:
            return 7
        elif PASSPORT_EXISTS:
            return 8