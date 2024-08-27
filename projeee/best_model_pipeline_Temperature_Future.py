import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np

# Excel dosyasından veriyi yükle
tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

# Zaman verisini datetime formatına çevir
tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

# Hedef değişkeni oluştur: 1 saat sonrasının 'Temperature' değeri
tpot_data['Temperature_Future'] = tpot_data['Temperature'].shift(-60)

# Gelecekteki verisi olmayan satırları çıkar
tpot_data = tpot_data.dropna()

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

# MAPE'yi hesapla
def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

mape = mean_absolute_percentage_error(testing_target, predictions)

print(f"Mean Absolute Error (MAE): {mae}")
print(f"Mean Squared Error (MSE): {mse}")
print(f"Root Mean Squared Error (RMSE): {rmse}")
print(f"R-squared (R²): {r2}")
print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")

# Gelecekteki zamanlar için tahmin yap
future_predictions = model.predict(future_features)

# Sonuçları görselleştir
plt.figure(figsize=(10, 6))
plt.plot(future_times[:len(future_predictions)], future_predictions, label='Tahmin Edilen Sıcaklık')
plt.xlabel('Zaman')
plt.ylabel('Sıcaklık')
plt.title('Gelecekteki Sıcaklık Tahminleri')
plt.legend()
plt.show()
