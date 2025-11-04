import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np

# --- Yapılandırma ---
input_final_file = 'data/scikit_learn_final_features.csv'
TRAIN_RATIO = 0.70  # %70 eğitim
VALIDATION_RATIO = 0.15 # %15 validasyon
# Geriye kalan %15 test için (0.70 + 0.15 = 0.85)
# --------------------

print("### 2.3. ZAMANA DAYALI VERİ BÖLME BAŞLIYOR ###")

try:
    df = pd.read_csv(input_final_file)
    # Tarih sütununu tekrar datetime formatına çevir
    df['date'] = pd.to_datetime(df['date'], utc=True)
except FileNotFoundError:
    print(f"HATA: '{input_final_file}' dosyası bulunamadı.")
    exit(1)

# 1. Veriyi Tarihe Göre Sıralama (Zaman serisi bölme için zorunlu)
df = df.sort_values(by='date').reset_index(drop=True)

# 2. X (Özellikler) ve y (Hedef) Ayırma
# 'isbugfix' hedef değişkeni, 'date' ise indeksi bozmamak için çıkarılır.
X = df.drop(columns=['isbugfix', 'date']) 
y = df['isbugfix']

# 3. Veri Seti İndekslerini Belirleme
N = len(df)
train_end_index = int(N * TRAIN_RATIO)
validation_end_index = train_end_index + int(N * VALIDATION_RATIO)

# 4. Zamana Dayalı Bölme
X_train_full = X.iloc[:train_end_index]
y_train_full = y.iloc[:train_end_index]

X_val = X.iloc[train_end_index:validation_end_index]
y_val = y.iloc[train_end_index:validation_end_index]

X_test = X.iloc[validation_end_index:]
y_test = y.iloc[validation_end_index:]


# 5. Özellik Ölçekleme (StandardScaler)
# Sadece sayısal sütunları ölçeklemeliyiz (modül sütunları hariç)
# Tüm X_train_full verisi üzerinden ölçekleme yapılır, test ve val verisine uygulanır.
scaler = StandardScaler()
numeric_cols = X.select_dtypes(include=np.number).columns.tolist()
# One-Hot Encoded modül sütunlarını ölçeklemeden hariç tut
cols_to_scale = [col for col in numeric_cols if not col.startswith('mod_')]


# Sadece eğitim verisine fit et
X_train_full[cols_to_scale] = scaler.fit_transform(X_train_full[cols_to_scale])

# Aynı scaler'ı test ve validasyon verilerine uygula
X_val[cols_to_scale] = scaler.transform(X_val[cols_to_scale])
X_test[cols_to_scale] = scaler.transform(X_test[cols_to_scale])


print("\n### 5. VERİ BÖLME VE ÖLÇEKLEME SONUÇLARI ###")
print(f"Toplam Kayıt Sayısı: {N}")
print(f"Eğitim (Train) Seti Boyutu: {len(X_train_full)} (%{TRAIN_RATIO * 100:.0f})")
print(f"Validasyon (Validation) Seti Boyutu: {len(X_val)} (%{VALIDATION_RATIO * 100:.0f})")
print(f"Test Seti Boyutu: {len(X_test)} (%{(1 - TRAIN_RATIO - VALIDATION_RATIO) * 100:.0f})")

# Model eğitimine hazır çıktılar (X_train, X_val, X_test, y_train, y_val, y_test)
# Bu çıktıları global alanda tutmak yerine, doğrudan Ay 4'teki modelleme kodunda yükleyeceğiz.
print("\nAy 2: Özellik Mühendisliği Başarıyla Tamamlandı!")