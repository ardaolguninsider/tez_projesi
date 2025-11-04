import pandas as pd
import numpy as np

# --- Yapılandırma ---
input_file = 'data/scikit_learn_commit_module_data.csv'
output_file_risk = 'data/scikit_learn_risk_scored.csv'
# --------------------

print("### 2.1. RİSK SKORU HESAPLAMA BAŞLIYOR ###")

try:
    df = pd.read_csv(input_file)
    # Tarih sütununu datetime formatına çevir
    df['date'] = pd.to_datetime(df['date'])
    print(f"Toplam {len(df)} commit-modül kaydı yüklendi.")
except FileNotFoundError:
    print(f"HATA: '{input_file}' dosyası bulunamadı. Lütfen Ay 1 çıktısının 'data/' klasöründe olduğundan emin olun.")
    exit(1)

# 1. Veriyi Tarih ve Modüle Göre Sıralama (Kritik Adım: Zaman serisi analizi için)
df = df.sort_values(by=['date', 'module_name']).reset_index(drop=True)

# 2. Risk Skoru Hesaplama
# Bu işlem, modül bazında kümülatif toplamı hesaplar.
# shift(1) kullanarak, ilgili commit'i sayıma dahil etmeyiz;
# sadece o commit'ten önceki geçmiş hataları sayarız.
df['historical_bug_count'] = df.groupby('module_name')['is_bugfix'].transform(
    lambda x: x.shift(1).fillna(0).cumsum()
)

print("\nRisk Skoru Hesaplama Tamamlandı.")

# Kontrol: En riskli modülleri kontrol edelim
risk_kontrol = df.groupby('module_name')['historical_bug_count'].max().sort_values(ascending=False).head(5)
print("En Yüksek Kümülatif Riski Olan İlk 5 Modül (Kontrol Amaçlı):\n", risk_kontrol)

# Kaydet
df.to_csv(output_file_risk, index=False)
print(f"\nRisk skorları eklenmiş veri seti '{output_file_risk}' olarak kaydedildi.")