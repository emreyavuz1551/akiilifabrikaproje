import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Veriyi yükle
tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

# Zaman verisini datetime formatına çevir
tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

# Hedef değişkeni oluştur: 1 saat sonrasının 'Pressure' değeri
tpot_data['Pressure_Future'] = tpot_data['Pressure'].shift(-60)  # Dakikada bir veri olduğu için 1 saat = 60 adım

# Gelecekteki verisi olmayan satırları çıkar
tpot_data = tpot_data.dropna()

# Özellikler (features) ve hedef (target) değişkenlerini ayır
features = tpot_data.drop(['Pressure_Future', 'Time'], axis=1)
target = tpot_data['Pressure_Future']

# Veriyi eğitim ve test setlerine ayır
training_features, testing_features, training_target, testing_target = \
            train_test_split(features, target, test_size=0.2, random_state=42)

# GradientBoostingRegressor modelini oluştur ve eğit
model = GradientBoostingRegressor(alpha=0.95, learning_rate=0.1, loss="huber", max_depth=7, max_features=0.95, 
                                  min_samples_leaf=8, min_samples_split=17, n_estimators=100, subsample=0.4, random_state=42)

model.fit(training_features, training_target)

# Tahmin yap
results = model.predict(testing_features)

# Performans metriklerini hesapla
mae = mean_absolute_error(testing_target, results)
mse = mean_squared_error(testing_target, results)
rmse = np.sqrt(mse)
r2 = r2_score(testing_target, results)

# MAPE'yi hesapla
def mean_absolute_percentage_error(y_true, y_pred):
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

mape = mean_absolute_percentage_error(testing_target, results)

# Metrikleri yazdır
print(f'Mean Absolute Error (MAE): {mae}')
print(f'Mean Squared Error (MSE): {mse}')
print(f'Root Mean Squared Error (RMSE): {rmse}')
print(f'R-squared (R²): {r2}')
print(f'Mean Absolute Percentage Error (MAPE): {mape:.2f}%')

# 6:00'dan 7:00'ye kadar olan veriler için tahmin yap
future_times = pd.date_range(start="2024-08-13 06:00:00", end="2024-08-13 07:00:00", freq='1T')
future_features = tpot_data[tpot_data['Time'].isin(future_times)].drop(['Pressure_Future', 'Time'], axis=1)
future_predictions = model.predict(future_features)

# Tahmin sonuçlarını ve gerçek değerleri grafik olarak çiz
plt.figure(figsize=(10, 6))
plt.plot(future_times, future_predictions, label='Tahmin Edilen Basınç Değerleri', color='red')
plt.title('6:00 ile 7:00 Arasındaki Tahmin Edilen Basınç Değerleri')
plt.xlabel('Zaman')
plt.ylabel('Basınç (Pressure)')
plt.xticks(rotation=45)
plt.legend()
plt.show()
