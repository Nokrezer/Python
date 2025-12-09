import get_check
import imaplib, email
from bs4 import BeautifulSoup

import datetime

import calendar

from gui import MainGui
from data import Data
from variables import ru_months

import openpyxl
class Main:
    def main(self):
        data = Data()
        
        data.load()#загружаем сохранённые данные, если такие имеются
        gui = MainGui(data)

if __name__ == "__main__":
    Main().main()