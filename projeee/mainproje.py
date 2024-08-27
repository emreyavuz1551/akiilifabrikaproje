import subprocess
import sys
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
import time
import res_rc
from canlisen import Ui_sensorliveform
from degiskenlerbutons import Ui_degiskenler
from gaspre import Ui_gaspreform
from girisekran import Ui_anaekranform
from hesapolustur import Ui_kayitekranfrom
from humiditypre import Ui_humidityform
from pressurepre import Ui_pressurepreform
from temperaturepre import Ui_temperaturepreform
from mmatplotlibwidget import MatplotlibWidget
from sensormatplotlibwidget import MatplotlibbWidget



class GirisEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_anaekranform()
        self.ui.setupUi(self)
        self.ui.loginbutton.clicked.connect(self.handle_button_click)
        self.ui.siginbutton.clicked.connect(self.kayitekranacici)
        self.db_connection = sqlite3.connect("projee.db")

    def kayitekranacici(self):
        self.kayitekran = Kayitekran()
        self.kayitekran.show()
        self.close()
        
    def handle_button_click(self):
        if self.login():
            self.degiskenler = DegiskenlerEkran()
            self.degiskenler.show()
            self.close()

    def login(self):
        username = self.ui.usernamelineEdit.text()
        password = self.ui.passwordlineEdit.text()
        # email = self.ui2.gmailLineEdit_3()

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM projee WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            QMessageBox.information(self, "Giriş Başarılı", "Hoş geldiniz, {}".format(username))
            return True
        else:
            QMessageBox.warning(self, "Giriş Başarısız", "Kullanıcı adı veya şifre hatalı")
            return False



class Kayitekran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui2 = Ui_kayitekranfrom()
        self.ui2.setupUi(self)
        self.db_connection = sqlite3.connect("projee.db")
        self.create_table()
        self.ui2.adduserbutton.clicked.connect(self.add_user)
        self.ui2.loginbutton_2.clicked.connect(self.anaekranacilacak)

    def anaekranacilacak(self):
        self.anaekran = GirisEkran()
        self.anaekran.show()
        self.close()

    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projee (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        self.db_connection.commit()

    def add_user(self):
        username = self.ui2.usernamelineEdit_2.text()
        password = self.ui2.passwordlineEdit_2.text()
        email = self.ui2.gmailLineEdit_3.text()

        if username.isalpha() and password.isdigit():
            cursor = self.db_connection.cursor()
            cursor.execute("INSERT INTO projee (username, password,email) VALUES (?, ?, ?)", (username, password,email))
            self.db_connection.commit()
            QMessageBox.information(self, "Kullanıcı Eklendi", "Kullanıcı bilgileri veritabanına eklendi.")
        else:
            QMessageBox.warning(self, "Geçersiz Bilgi", "Kullanıcı adı harf, şifre sayılardan oluşmalıdır.")

    def login(self):
        username = self.ui2.usernamelineEdit_2.text()
        password = self.ui2.passwordlineEdit_2.text()
        # email = self.ui2.gmailLineEdit_3()

        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM projee WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            QMessageBox.information(self, "Giriş Başarılı", "Hoş geldiniz, {}".format(username))
            return True
        else:
            QMessageBox.warning(self, "Giriş Başarısız", "Kullanıcı adı veya şifre hatalı")
            return False


class DegiskenlerEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui3 = Ui_degiskenler()
        self.ui3.setupUi(self)
        self.ui3.live_sensor_button.clicked.connect(self.scalisensoracici)
        self.ui3.temperaturebutton.clicked.connect(self.temperatureacici)
        self.ui3.pressurebutton.clicked.connect(self.pressureacici)
        self.ui3.humiditybutton.clicked.connect(self.humidityacici)
        self.ui3.gasbutton.clicked.connect(self.gasacici)

    def scalisensoracici(self):
        self.sensorlive = SensorliveEkran()
        self.sensorlive.show()
        self.close()

    def temperatureacici(self):
        self.temperature = TemperatureEkran()
        self.temperature.show()
        self.close()
    
    def pressureacici(self):
        self.pressure = PressureEkran()
        self.pressure.show()
        self.close()

    def humidityacici(self):
        self.humidity = HumidityEkran()
        self.humidity.show()
        self.close()
    def gasacici(self):
        self.gas = GasEkran()
        self.gas.show()
        self.close()
       
class SensorliveEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui4 = Ui_sensorliveform()
        self.ui4.setupUi(self)
        self.widgetsensorlive = MatplotlibbWidget(self)
        self.widgetsensorlive.setGeometry(10, 10, 1041, 681)
        self.ui4.socketbaglantibutton.clicked.connect(self.socketbaglantisi)
        self.ui4.livesensorbackbutton.clicked.connect(self.disconnect_and_go_back)

    def socketbaglantisi(self):

        
        self.widgetsensorlive.start_live_plot()
        # self.widgetsensorlive.setGeometry(10, 10, 1041, 681)

    def disconnect_and_go_back(self):

        self.widgetsensorlive.disconnect_and_stop()

        self.degiskenlererkaninageri()
        
    def degiskenlererkaninageri(self):
        self.degiskenler = DegiskenlerEkran()
        self.degiskenler.show()
        self.close()

class TemperatureEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui5 = Ui_temperaturepreform()
        self.ui5.setupUi(self)
        self.widgettemperaturepre = MatplotlibWidget(self)
        
        self.widgettemperaturepre.setGeometry(50, 70, 941, 541)
        
        self.ui5.temperatureprebackbutton.clicked.connect(self.degiskenlererkaninageri)
        self.ui5.temperaturepreforecastbutton.clicked.connect(self.temperatureforecast)

    def temperatureforecast(self):
        self.widgettemperaturepre.predict_and_plot()

    def degiskenlererkaninageri(self):
        self.degiskenler = DegiskenlerEkran()
        self.degiskenler.show()
        self.close()

class PressureEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui6 = Ui_pressurepreform()
        self.ui6.setupUi(self)
        self.widgetpressurepre = MatplotlibWidget(self)
        self.widgetpressurepre.setGeometry(50, 70, 941, 541)
        self.ui6.pressureprebackbutton.clicked.connect(self.degiskenlererkaninageri)
        self.ui6.pressurepreforecastbutton.clicked.connect(self.pressureforecast)

    def pressureforecast(self):
        self.widgetpressurepre.predict_and_plot3()
        # self.widgettemperaturepre.setGeometry(50, 70, 941, 541)
    def degiskenlererkaninageri(self):
        self.degiskenler = DegiskenlerEkran()
        self.degiskenler.show()
        self.close()

class HumidityEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui7 = Ui_humidityform()
        self.ui7.setupUi(self)
        self.widgethumiditypre = MatplotlibWidget(self)
        self.widgethumiditypre.setGeometry(50, 70, 941, 541)
        self.ui7.humidityprebackbutton.clicked.connect(self.degiskenlererkaninageri)
        self.ui7.humiditypreforecastbutton.clicked.connect(self.humidityforecast)

    def humidityforecast(self):
        self.widgethumiditypre.predict_and_plot2()
        self.widgethumiditypre.setGeometry(50, 70, 941, 541)

    def degiskenlererkaninageri(self):
        self.degiskenler = DegiskenlerEkran()
        self.degiskenler.show()
        self.close()

class GasEkran(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui8 = Ui_gaspreform()
        self.ui8.setupUi(self)
        self.widgetgaspre = MatplotlibWidget(self)
        self.widgetgaspre.setGeometry(50, 70, 941, 541)
        self.ui8.gasprebackbutton.clicked.connect(self.degiskenlererkaninageri)
        self.ui8.gaspreforecastbutton.clicked.connect(self.gasforecast)

    def gasforecast(self):
        self.widgetgaspre.predict_and_plot4()
        self.widgetgaspre.setGeometry(50, 70, 941, 541)

    def degiskenlererkaninageri(self):
        self.degiskenler = DegiskenlerEkran()
        self.degiskenler.show()
        self.close()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GirisEkran()  # Giriş ekranı ile başlıyoruz
    window.show()
    sys.exit(app.exec_())
