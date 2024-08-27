import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import matplotlib.pyplot as plt

# Veriyi yükle
tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

# Hedef değişkeni oluştur: 1 saat sonrasının 'MQ2 PPM' değeri
tpot_data['MQ2_PPM_Future'] = tpot_data['MQ2 PPM'].shift(-60)

# Gelecekteki verisi olmayan satırları çıkar
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
            train_test_split(features, target, random_state=42)

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

# Tahmin sonuçlarını ve gerçek değerleri grafik olarak çiz
plt.figure(figsize=(10, 6))
plt.plot(np.expm1(testing_target.values), label='Gerçek Değerler', color='blue')
plt.plot(np.expm1(results), label='Tahmin Değerleri', color='red')
plt.title('Gerçek ve Tahmin Edilen MQ2 PPM Değerleri')
plt.xlabel('Zaman Adımları')
plt.ylabel('MQ2 PPM')
plt.legend()
plt.show()