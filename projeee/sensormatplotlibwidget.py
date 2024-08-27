import socket
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import datetime
import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3

class MatplotlibbWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.axs = plt.subplots(4, 1, sharex=True, figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.time_list = []
        self.pressure_list = []
        self.mq2_ppm_list = []
        self.temperature_list = []
        self.humidity_list = []
        self.start_time = datetime.datetime.now()

        self.ani = None
        self.client_socket = None  # Socket bağlantısı için bir referans oluşturun

        # Sensör referans aralıkları
        self.pressure_range = (950, 1050)  # hPa
        self.mq2_ppm_range = (0, 1000)  # PPM
        self.temperature_range = (0, 50)  # °C
        self.humidity_range = (20, 80)  # %

    def start_live_plot(self):
        if self.client_socket is not None:
            return
        
        RASPBERRY_PI_IP = '192.168.1.111'
        PORT = 65432

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((RASPBERRY_PI_IP, PORT))
            print("Bağlantı kuruldu")
        except ConnectionRefusedError as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"Raspberry Pi'ye bağlantı kurulamadı: {str(e)}")
            self.client_socket = None
            return

        def fetch_data():
            try:
                data = self.client_socket.recv(1024).decode('utf-8').strip()
                sensor_data = json.loads(data)
                print("Veri alındı:", sensor_data)
                return sensor_data
            except Exception as e:
                print(f"Veri alırken hata oluştu: {e}")
                return None

        def animate(i):
            sensor_data = fetch_data()
            if sensor_data is None:
                return

            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.pressure_list.append(sensor_data["pressure"])
            self.mq2_ppm_list.append(sensor_data["lpg_ppm"])
            self.temperature_list.append(sensor_data["temperature"])
            self.humidity_list.append(sensor_data["humidity"])
            self.time_list.append(time_now)

            if len(self.time_list) > 10:
                self.time_list.pop(0)
                self.pressure_list.pop(0)
                self.mq2_ppm_list.pop(0)
                self.temperature_list.pop(0)
                self.humidity_list.pop(0)

            self.axs[0].clear()
            self.axs[1].clear()
            self.axs[2].clear()
            self.axs[3].clear()

            self.axs[0].plot(self.time_list, self.pressure_list, label='Pressure (hPa)', marker='o')
            self.axs[1].plot(self.time_list, self.mq2_ppm_list, label='MQ2 PPM', marker='o')
            self.axs[2].plot(self.time_list, self.temperature_list, label='Temperature (°C)', marker='o')
            self.axs[3].plot(self.time_list, self.humidity_list, label='Humidity (%)', marker='o')

            self.axs[0].set_ylabel('Pressure (hPa)')
            self.axs[1].set_ylabel('MQ2 PPM')
            self.axs[2].set_ylabel('Temperature (°C)')
            self.axs[3].set_ylabel('Humidity (%)')

            for ax in self.axs:
                ax.legend(loc='upper left')

            self.axs[3].set_xlabel('Time')
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)

            self.canvas.draw()  # Grafiklerin çizimini burada çağırın

            # Sensör verilerini kontrol et ve uyarı ver
            self.check_sensor_data(sensor_data)

        # Animasyonu başlat ve referansını sakla
        self.ani = animation.FuncAnimation(self.figure, animate, interval=2000, cache_frame_data=False)
        self.canvas.draw()  # İlk çizimi hemen burada yapın
        print("Animasyon başlatıldı")

    def check_sensor_data(self, sensor_data):
        warnings = []
        if not (self.pressure_range[0] <= sensor_data["pressure"] <= self.pressure_range[1]):
            warnings.append(f"Pressure out of range: {sensor_data['pressure']} hPa")
        if not (self.mq2_ppm_range[0] <= sensor_data["lpg_ppm"] <= self.mq2_ppm_range[1]):
            warnings.append(f"MQ2 PPM out of range: {sensor_data['lpg_ppm']} PPM")
        if not (self.temperature_range[0] <= sensor_data["temperature"] <= self.temperature_range[1]):
            warnings.append(f"Temperature out of range: {sensor_data['temperature']} °C")
        if not (self.humidity_range[0] <= sensor_data["humidity"] <= self.humidity_range[1]):
            warnings.append(f"Humidity out of range: {sensor_data['humidity']} %")

        if warnings:
            warning_message = "\n".join(warnings)
            QMessageBox.warning(self, "Sensor Warning", warning_message)
            self.send_email(warning_message)

    def send_email(self, message):
        conn = sqlite3.connect("projee.db")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM projee")
        emails = cursor.fetchall()
        conn.close()

        sender_email = "emreyavuz1551@gmail.com"
        sender_password = "lnqy laui pzrz fvjd"

        for email in emails:
            receiver_email = email[0]
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = "Sensor Warning"

            msg.attach(MIMEText(message, 'plain'))

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                text = msg.as_string()
                server.sendmail(sender_email, receiver_email, text)
                server.quit()
                print(f"Email sent to {receiver_email}")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")

    def disconnect_and_stop(self):
        # Socket bağlantısını kapat
        if self.client_socket is not None:
            try:
                self.client_socket.close()
                self.client_socket = None
                print("Bağlantı kesildi")
            except Exception as e:
                print(f"Bağlantıyı keserken hata oluştu: {e}")

        # Animasyonu durdur
        if self.ani is not None:
            self.ani.event_source.stop()
            self.ani = None
            print("Animasyon durduruldu")