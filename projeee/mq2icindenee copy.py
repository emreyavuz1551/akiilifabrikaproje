import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Veriyi yükle
tpot_data = pd.read_excel('formatted_sensor_data.xlsx')

# 'Time' sütununu datetime formatına çevir
tpot_data['Time'] = pd.to_datetime(tpot_data['Time'])

# Hedef değişkeni oluştur: 1 saat sonrasının 'MQ2 PPM' değeri
tpot_data['MQ2_PPM_Future'] = tpot_data['MQ2 PPM'].shift(-60)

# Gelecekteki verisi olmayan satırları çıkar
tpot_data = tpot_data.dropna()

# Zaman serisi özellikleri ekle (lag features)
for lag in range(1, 61):
    tpot_data[f'MQ2_PPM_Lag_{lag}'] = tpot_data['MQ2 PPM'].shift(lag)

# Geçmiş verisi olmayan satırları tekrar çıkar
tpot_data = tpot_data.dropna().reset_index(drop=True)

# Özellikler ve hedef değişkeni belirle
features = tpot_data.drop(['MQ2_PPM_Future', 'Time', 'MQ2 PPM'], axis=1)
target = tpot_data['MQ2_PPM_Future']

# Verileri normalize et
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# KNeighborsRegressor modelini oluştur ve eğit
knn_model = KNeighborsRegressor(n_neighbors=10, p=1, weights='distance')
knn_model.fit(features_scaled, target)

# Tahmin yapmak istediğimiz zaman aralığını belirle
start_time = pd.Timestamp('2024-08-13 06:00:00')
end_time = pd.Timestamp('2024-08-13 07:00:00')

# İlgili zaman aralığındaki verileri filtrele
future_data = tpot_data[(tpot_data['Time'] >= start_time) & (tpot_data['Time'] <= end_time)].reset_index(drop=True)

if not future_data.empty:
    future_features = future_data.drop(['MQ2_PPM_Future', 'Time', 'MQ2 PPM'], axis=1)
    future_features_scaled = scaler.transform(future_features)
    
    # Tahmin yap
    future_predictions = knn_model.predict(future_features_scaled)
    
    # Zaman bilgilerini al
    time_values = future_data['Time'] + pd.Timedelta(hours=1)  # Tahminler 1 saat sonrasını temsil ediyor

    # Gerçek değerleri alın
    true_values = future_data['MQ2_PPM_Future']
    
    # MAPE'yi hesapla
    def mean_absolute_percentage_error(y_true, y_pred):
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    mape = mean_absolute_percentage_error(true_values, future_predictions)
    print(f"Mean Absolute Percentage Error (MAPE): {mape:.2f}%")
    
    # Grafik oluştur
    plt.figure(figsize=(12, 6))
    plt.plot(time_values, future_predictions, label='Tahmin Edilen MQ2 PPM Değerleri', color='red', marker='o')
    plt.title('6:00 ile 7:00 Arasındaki MQ2 PPM Tahmin Değerleri')
    plt.xlabel('Zaman')
    plt.ylabel('MQ2 PPM')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("Belirtilen zaman aralığında veri bulunamadı.")
