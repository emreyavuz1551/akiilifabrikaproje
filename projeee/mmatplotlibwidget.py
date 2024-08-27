import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
import matplotlib.dates as mdates
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import xgboost as xgb
import socket
import json
import time
import matplotlib.animation as animation
import datetime


RASPBERRY_PI_IP = '192.168.1.111'  # Raspberry Pi'nin IP adresi
PORT = 65432

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        # Fare olayını bağlayan satırı kaldırdık
        # self.canvas.mpl_connect('motion_notify_event', self.onMouseMove)

    # onMouseMove metodunu kaldırdık
    # def onMouseMove(self, event):
    #     if event.inaxes is not None:  # Grafiğin içinde mi kontrol et
    #         x_value = mdates.num2date(event.xdata).strftime('%H:%M:%S')
    #         y_value = event.ydata
    #         self.show_tooltip(x_value, y_value)

    # show_tooltip metodunu kaldırdık
    # def show_tooltip(self, x_value, y_value):
    #     # Tooltip gösterme işlemi
    #     print(f"X: {x_value}, Y: {y_value}")

    def predict_and_plot(self):
        # Excel dosyasından veriyi yükle
        tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

        # Zaman verisini datetime formatına çevir
        tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

        # Hedef değişkeni oluştur: 1 saat sonrasının 'Temperature' değeri
        tpot_data['Temperature_Future'] = tpot_data['Temperature'].shift(-60)

        # Gelecekteki verisi olmayan satırları çıkar
        tpot_data = tpot_data.dropna()

        # Time sütununun son değerini al
        # last_time = tpot_data['Time'].max()

        # Son kaydedilen zamandan itibaren 1 saat ileriye kadar olan zaman dilimlerini oluştur
        future_times = pd.date_range(start="2024-08-13 06:00:00", end="2024-08-13 07:00:00", freq='1T')

        # Bu zaman dilimlerine göre veriyi filtrele ve gelecekteki sıcaklık değerlerini çıkar
        future_features = tpot_data[tpot_data['Time'].isin(future_times)].drop(['Temperature_Future', 'Time'], axis=1)

        # Özellikler (features) ve hedef (target) değişkenlerini ayır
        features = tpot_data.drop(['Temperature_Future', 'Time'], axis=1)
        target = tpot_data['Temperature_Future']

        # Veriyi eğitim ve test setlerine ayır
        training_features, testing_features, training_target, testing_target = train_test_split(features, target, random_state=42)

        # Modeli oluştur ve eğit
        model = GradientBoostingRegressor(random_state=42)
        model.fit(training_features, training_target)

        # Test seti üzerinde tahmin yap
        predictions = model.predict(testing_features)

        # Performans metriklerini hesapla
        mae = mean_absolute_error(testing_target, predictions)
        mse = mean_squared_error(testing_target, predictions)
        rmse = mean_squared_error(testing_target, predictions, squared=False)
        r2 = r2_score(testing_target, predictions)

        print(f"Mean Absolute Error (MAE): {mae}")
        print(f"Mean Squared Error (MSE): {mse}")
        print(f"Root Mean Squared Error (RMSE): {rmse}")
        print(f"R-squared (R²): {r2}")

        # Gelecekteki zamanlar için tahmin yap
        future_predictions = model.predict(future_features)

        # Sonuçları görselleştir
        self.ax.clear()
        self.ax.plot(future_times[:len(future_predictions)], future_predictions, label='Tahmin Edilen Sıcaklık')
        self.ax.set_xlabel('Zaman')
        self.ax.set_ylabel('Sıcaklık')
        self.ax.set_title('Gelecekteki Sıcaklık Tahminleri')
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
        self.figure.autofmt_xdate()
        self.ax.legend()
        # self.figure.autofmt_xdate()
        self.canvas.draw()

    def predict_and_plot2(self):
        # Veriyi yükle
        tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

        # Zaman verisini datetime formatına çevir
        tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

        # Hedef değişkeni oluştur: 1 saat sonrasının 'Humidity' değeri
        tpot_data['Humidity_Future'] = tpot_data['Humidity'].shift(-60)
        tpot_data = tpot_data.dropna()

        # Veriyi eğitim ve test setlerine ayır
        features = tpot_data.drop(['Humidity_Future', 'Time'], axis=1)
        target = tpot_data['Humidity_Future']
        training_features, testing_features, training_target, testing_target = \
            train_test_split(features, target, test_size=0.2, random_state=42)

        # Modeli oluştur ve eğit
        model = RandomForestRegressor(bootstrap=True, max_features=0.5, min_samples_leaf=3, 
                                    min_samples_split=2, n_estimators=100, random_state=42)
        model.fit(training_features, training_target)

        # Zaman dilimini 5 dakikalık aralıklarla belirleyin
        future_times = pd.date_range(start="2024-08-13 06:00:00", end="2024-08-13 07:00:00", freq='5min')

        # Bu zaman dilimlerine karşılık gelen verileri filtreleyin
        future_features = tpot_data[tpot_data['Time'].isin(future_times)].drop(['Humidity_Future', 'Time'], axis=1)

        # Eğer future_features boş değilse ve future_times ile boyutları uyumluysa devam edin
        if not future_features.empty and len(future_features) == len(future_times):
            # Gelecekteki tahminleri yap
            future_predictions = model.predict(future_features)

            # Grafiği çiz
            self.ax.clear()
            self.ax.plot(future_times, future_predictions, label='Tahmin Edilen Nem Değerleri', color='red')
            self.ax.set_xlabel('Zaman')
            self.ax.set_ylabel('Nem (Humidity)')
            self.ax.set_title('6:00 ile 7:00 Arasındaki Tahmin Edilen Nem Değerleri')

            # X eksen formatını ayarlayın
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            self.figure.autofmt_xdate()

            self.ax.legend()
            self.canvas.draw()
        else:
            print("Future features are empty or do not match the time points.")

    def predict_and_plot3(self):
        # Veriyi yükle
        tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

        # Zaman verisini datetime formatına çevir
        tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

        # Hedef değişkeni oluştur: 1 saat sonrasının 'Pressure' değeri
        tpot_data['Pressure_Future'] = tpot_data['Pressure'].shift(-60)
        tpot_data = tpot_data.dropna()

        # Veriyi eğitim ve test setlerine ayır
        features = tpot_data.drop(['Pressure_Future', 'Time'], axis=1)
        target = tpot_data['Pressure_Future']
        training_features, testing_features, training_target, testing_target = \
            train_test_split(features, target, test_size=0.2, random_state=42)

        # Modeli oluştur ve eğit
        model = RandomForestRegressor(bootstrap=True, max_features=0.5, min_samples_leaf=3, 
                                    min_samples_split=2, n_estimators=100, random_state=42)
        model.fit(training_features, training_target)

        # Zaman dilimini 5 dakikalık aralıklarla belirleyin
        future_times = pd.date_range(start="2024-08-13 06:00:00", end="2024-08-13 07:00:00", freq='5min')

        # Bu zaman dilimlerine karşılık gelen verileri filtreleyin
        future_features = tpot_data[tpot_data['Time'].isin(future_times)].drop(['Pressure_Future', 'Time'], axis=1)

        # Eğer future_features boş değilse ve future_times ile boyutları uyumluysa devam edin
        if not future_features.empty and len(future_features) == len(future_times):
            # Gelecekteki tahminleri yap
            future_predictions = model.predict(future_features)

            # Grafiği çiz
            self.ax.clear()
            self.ax.plot(future_times, future_predictions, label='Tahmin Edilen Basınç Değerleri', color='red')
            self.ax.set_xlabel('Zaman')
            self.ax.set_ylabel('Basınç (Pressure)')
            self.ax.set_title('6:00 ile 7:00 Arasındaki Tahmin Edilen Basınç Değerleri')
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            self.figure.autofmt_xdate()

            self.ax.legend()
            self.canvas.draw()

    def predict_and_plot4(self):


        # Veriyi yükle
        tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

        # Zaman verisini datetime formatına çevir
        tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

        # Hedef değişkeni oluştur: 1 saat sonrasının 'MQ2 PPM' değeri
        tpot_data['MQ2_PPM_Future'] = tpot_data['MQ2 PPM'].shift(-60)
        tpot_data = tpot_data.dropna()

        # Logaritmik dönüşüm uygulayın
        tpot_data['MQ2 PPM'] = np.log1p(tpot_data['MQ2 PPM'])
        tpot_data['MQ2_PPM_Future'] = np.log1p(tpot_data['MQ2_PPM_Future'])

        # Zaman serisi özellikleri ekle (lag features)
        for lag in range(1, 61):
            tpot_data[f'MQ2_PPM_Lag_{lag}'] = tpot_data['MQ2 PPM'].shift(lag)

        # Hareketli ortalamalar ekleyin
        tpot_data['MQ2_PPM_MA_10'] = tpot_data['MQ2 PPM'].rolling(window=10).mean()
        tpot_data['MQ2_PPM_MA_20'] = tpot_data['MQ2 PPM'].rolling(window=20).mean()

        # Geçmiş verisi olmayan satırları tekrar çıkar
        tpot_data = tpot_data.dropna().reset_index(drop=True)

        # Özellikler (features) ve hedef (target) değişkenlerini ayır
        features = tpot_data.drop(['MQ2_PPM_Future', 'Time'], axis=1)
        target = tpot_data['MQ2_PPM_Future']

        # Veriyi eğitim ve test setlerine ayır
        training_features, testing_features, training_target, testing_target = \
                    train_test_split(features, target, test_size=0.2, random_state=42)

        # Verileri normalize et
        scaler = MinMaxScaler()
        training_features = scaler.fit_transform(training_features)
        testing_features = scaler.transform(testing_features)

        # XGBoost modelini oluştur ve eğit
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        model.fit(training_features, training_target)

        # Test seti üzerinde tahmin yap
        results = model.predict(testing_features)

        # Performans metriklerini hesapla
        mae = mean_absolute_error(testing_target, results)
        mse = mean_squared_error(testing_target, results)
        rmse = np.sqrt(mse)
        r2 = r2_score(testing_target, results)

        def mean_absolute_percentage_error(y_true, y_pred):
            return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

        mape = mean_absolute_percentage_error(testing_target, results)

        # Metrikleri yazdır
        print(f'Mean Absolute Error (MAE): {mae}')
        print(f'Mean Squared Error (MSE): {mse}')
        print(f'Root Mean Squared Error (RMSE): {rmse}')
        print(f'R-squared (R²): {r2}')
        print(f'Mean Absolute Percentage Error (MAPE): {mape}%')

        # Zaman dilimini 5 dakikalık aralıklarla belirleyin
        future_times = pd.date_range(start="2024-08-13 06:00:00", end="2024-08-13 07:00:00", freq='5min')

        # Bu zaman dilimlerine karşılık gelen verileri filtreleyin
        future_features = tpot_data[tpot_data['Time'].isin(future_times)].drop(['MQ2_PPM_Future', 'Time'], axis=1)

        # Eğer future_features boş değilse ve future_times ile boyutları uyumluysa devam edin
        if not future_features.empty and len(future_features) == len(future_times):
            # Gelecekteki tahminleri yap
            future_features_scaled = scaler.transform(future_features)
            future_predictions = model.predict(future_features_scaled)

            # Grafiği çiz
            self.ax.clear()
            self.ax.plot(future_times, np.expm1(future_predictions), label='Tahmin Edilen MQ2 PPM Değerleri', color='red')
            self.ax.set_xlabel('Zaman')
            self.ax.set_ylabel('MQ2 PPM')
            self.ax.set_title('6:00 ile 7:00 Arasındaki Tahmin Edilen MQ2 PPM Değerleri')
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            self.figure.autofmt_xdate()

            self.ax.legend()
            self.canvas.draw()
        else:
            print("Future features are empty or do not match the time points.")

    # def predict_and_plot5(self):
    #     RASPBERRY_PI_IP = '192.168.1.111'  # Raspberry Pi'nin IP adresi
    #     PORT = 65432

    #     # Socket bağlantısını kur
    #     self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    #     try:
    #         self.client_socket.connect((RASPBERRY_PI_IP, PORT))
    #         print("Bağlantı başarılı!")
    #     except Exception as e:
    #         print(f"Socket bağlantısı başarısız: {e}")
    #         return

    #     # Veri listeleri
    #     self.time_list = []
    #     self.pressure_list = []
    #     self.mq2_ppm_list = []
    #     self.temperature_list = []
    #     self.humidity_list = []

    #     # Zamanlayıcıyı başlat
    #     self.start_time = datetime.datetime.now()

    #     def fetch_data():
    #         try:
    #             data = self.client_socket.recv(1024).decode('utf-8').strip()
    #             return json.loads(data)
    #         except Exception as e:
    #             print(f"Veri alırken hata oluştu: {e}")
    #             return None

    #     def animate(i):
    #         sensor_data = fetch_data()
    #         if sensor_data is None:
    #             return
            
    #         time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #         if "error" in sensor_data:
    #             print(sensor_data["error"])
    #             return

    #         self.pressure_list.append(sensor_data["pressure"])
    #         self.mq2_ppm_list.append(sensor_data["lpg_ppm"])
    #         self.temperature_list.append(sensor_data["temperature"])
    #         self.humidity_list.append(sensor_data["humidity"])
    #         self.time_list.append(time_now)

    #         # Verileri 10 elemanla sınırlı tut
    #         if len(self.time_list) > 10:
    #             self.time_list.pop(0)
    #             self.pressure_list.pop(0)
    #             self.mq2_ppm_list.pop(0)
    #             self.temperature_list.pop(0)
    #             self.humidity_list.pop(0)

    #         # Verileri 1 dakikada bir Excel dosyasına kaydet
    #         if (datetime.datetime.now() - self.start_time).total_seconds() >= 60:
    #             print(f"Kayıt zamanı: {datetime.datetime.now()}")  # Kayıt zamanını kontrol et
    #             try:
    #                 df_existing = pd.read_excel('sensor_data.xlsx')
    #                 df_new = pd.DataFrame({
    #                     'Time': [self.time_list[-1]],  # Sadece en son zamanı ekleyin
    #                     'Pressure': [self.pressure_list[-1]],  # Sadece en son basınç değerini ekleyin
    #                     'MQ2 PPM': [self.mq2_ppm_list[-1]],  # Sadece en son MQ2 değerini ekleyin
    #                     'Temperature': [self.temperature_list[-1]],  # Sadece en son sıcaklık değerini ekleyin
    #                     'Humidity': [self.humidity_list[-1]]  # Sadece en son nem değerini ekleyin
    #                 })
    #                 df_combined = pd.concat([df_existing, df_new])
    #             except FileNotFoundError:
    #                 df_combined = pd.DataFrame({
    #                     'Time': [self.time_list[-1]],  # Sadece en son zamanı ekleyin
    #                     'Pressure': [self.pressure_list[-1]],  # Sadece en son basınç değerini ekleyin
    #                     'MQ2 PPM': [self.mq2_ppm_list[-1]],  # Sadece en son MQ2 değerini ekleyin
    #                     'Temperature': [self.temperature_list[-1]],  # Sadece en son sıcaklık değerini ekleyin
    #                     'Humidity': [self.humidity_list[-1]]  # Sadece en son nem değerini ekleyin
    #                 })
                
    #             df_combined.to_excel('sensor_data.xlsx', index=False)
    #             print(f"Veriler Excel'e kaydedildi: {datetime.datetime.now()}")  # Kayıt işlemi tamamlandı

    #             # Listeleri sıfırla
    #             self.time_list.clear()
    #             self.pressure_list.clear()
    #             self.mq2_ppm_list.clear()
    #             self.temperature_list.clear()
    #             self.humidity_list.clear()

    #             # Zamanlayıcıyı sıfırla
    #             self.start_time = datetime.datetime.now()

    #         # Tek grafik üzerinde tüm verileri güncelle
    #         self.ax.clear()

    #         self.ax.plot(self.time_list, self.pressure_list, label='Pressure (hPa)', marker='o')
    #         self.ax.plot(self.time_list, self.mq2_ppm_list, label='MQ2 PPM', marker='o')
    #         self.ax.plot(self.time_list, self.temperature_list, label='Temperature (°C)', marker='o')
    #         self.ax.plot(self.time_list, self.humidity_list, label='Humidity (%)', marker='o')

    #         self.ax.set_ylabel('Değer')
    #         self.ax.set_xlabel('Time')
    #         self.ax.legend(loc='upper left')

    #         plt.xticks(rotation=45, ha='right')
    #         plt.subplots_adjust(bottom=0.30)

    #         self.canvas.draw()

    #     # Animasyonu başlat
    #     self.ani = animation.FuncAnimation(self.figure, animate, interval=1000, cache_frame_data=False)

    #     # Canvas'ın arayüzde gösterildiğinden emin olun
    #     self.canvas.show()




if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main = MatplotlibWidget()
    main.show()
    main.predict_and_plot()  # Grafiği çizmek için bu satırı ekleyin
    main.predict_and_plot2()  # İkinci grafiği çizmek için bu satırı ekleyin
    main.predict_and_plot3()  # Üçüncü grafiği çizmek için bu satırı ekleyin
    main.predict_and_plot4()  # Dördüncü grafiği çizmek için bu satırı ekleyin
    main.predict_and_plot5()  # Beşinci grafiği çizmek için bu satırı ekleyin
    sys.exit(app.exec_())