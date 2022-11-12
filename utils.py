import datetime
import sys


def change_language(date):
    month_dict = {"Enero": "January", "Febrero": "February", "Abril": "April", "Marzo": "March",
                  "Mayo": "May", "Junio": "June", "Julio": "July", "Agosto": "August", "Septiembre": "September",
                  "Octubre": "October", "Noviembre": "November", "Diciembre": "December"}
    date_list = date.split("-")
    if date_list[1] in month_dict.values:
        return date
    month = month_dict[date_list[1]]
    return "-".join([date_list[0], month, date_list[2]])