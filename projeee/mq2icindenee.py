import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

# Veriyi yükle
tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

# Hedef değişkeni oluştur: 1 saat sonrasının 'MQ2 PPM' değeri
tpot_data['MQ2_PPM_Future'] = tpot_data['MQ2 PPM'].shift(-60)

# Gelecekteki verisi olmayan satırları çıkar
tpot_data = tpot_data.dropna()

# Özellikler (features) ve hedef (target) değişkenlerini ayır
features = tpot_data.drop(['MQ2_PPM_Future', 'Time'], axis=1)
target = tpot_data['MQ2_PPM_Future']

# Veriyi eğitim ve test setlerine ayır
training_features, testing_features, training_target, testing_target = \
            train_test_split(features, target, random_state=42)

# Verileri normalize et
scaler = MinMaxScaler()
training_features = scaler.fit_transform(training_features)
testing_features = scaler.transform(testing_features)

# KNeighborsRegressor modelini oluştur ve eğit
exported_pipeline = KNeighborsRegressor(n_neighbors=10, p=2, weights="distance")
exported_pipeline.fit(training_features, training_target)

# Test seti üzerinde tahmin yap
results = exported_pipeline.predict(testing_features)

# Performans metriklerini hesapla
mae = mean_absolute_error(testing_target, results)
mse = mean_squared_error(testing_target, results)
rmse = np.sqrt(mse)
r2 = r2_score(testing_target, results)
mape = np.mean(np.abs((testing_target - results) / testing_target)) * 100

# Metrikleri yazdır
print(f'Mean Absolute Error (MAE): {mae:.2f}')
print(f'Mean Squared Error (MSE): {mse:.2f}')
print(f'Root Mean Squared Error (RMSE): {rmse:.2f}')
print(f'R-squared (R²): {r2:.2f}')
print(f'Mean Absolute Percentage Error (MAPE): {mape:.2f}%')

# Tahmin sonuçlarını ve gerçek değerleri grafik olarak çiz
plt.figure(figsize=(10, 6))
plt.plot(testing_target.values, label='Gerçek Değerler', color='blue')
plt.plot(results, label='Tahmin Değerleri', color='red')
plt.title('Gerçek ve Tahmin Edilen MQ2 PPM Değerleri')
plt.xlabel('Zaman Adımları')
plt.ylabel('MQ2 PPM')
plt.legend()
plt.show()
