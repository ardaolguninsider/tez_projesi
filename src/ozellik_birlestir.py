import pandas as pd
import re

# ... (Yapılandırma kısmı aynı kalır) ...
risk_scored_file = 'data/scikit_learn_risk_scored.csv'
commit_features_file = 'data/scikit_learn_commit_features.csv'
output_final_file = 'data/scikit_learn_final_features.csv'

print("### 2.2. ÖZELLİK BİRLEŞTİRME BAŞLIYOR ###")

try:
    # 1. Verileri Yükle
    df_risk = pd.read_csv(risk_scored_file)
    df_risk['date'] = pd.to_datetime(df_risk['date'], utc=True)
    
    df_features = pd.read_csv(commit_features_file)
    df_features = df_features.drop(columns=['author', 'message', 'date', 'is_bugfix'], errors='ignore')
    
except FileNotFoundError as e:
    print(f"HATA: Gerekli dosya bulunamadı: {e}")
    exit(1)

# 2. Sütun Adlarını Temizleme (Whitespace ve Özel Karakterler)
def clean_cols(df):
    new_cols_map = {}
    for col in df.columns:
        # Boşlukları kaldır ve alt çizgi yerine küçük harf/birleşik isim kullan
        col_clean = col.strip().replace('_', '').lower()
        new_cols_map[col] = col_clean
    df.rename(columns=new_cols_map, inplace=True)
    return df

df_features = clean_cols(df_features.copy())
df_risk = clean_cols(df_risk.copy())


print(f"Risk kaydı sayısı: {len(df_risk)}. Ham özellik kaydı sayısı: {len(df_features)}.")

# 3. Verileri SHA üzerinden birleştirme (Join)
df_final = pd.merge(
    df_risk,
    df_features,
    on='sha',
    how='left' 
)

print(f"Birleştirme tamamlandı. Final DataFrame boyutu: {len(df_final)} satır.")

# 4. Özellik Seçimi ve Kategorik Değişken Dönüşümü

# KRİTİK DÜZELTME: Modül Sütununu Otomatik Bulma
# Temizlik sonrası adı 'modulename' olmalı, onu kullanacağız.
module_col_name = 'modulename' 
if module_col_name not in df_final.columns:
    # Eğer beklenmedik bir durum olursa ve temizlenmiş sütun adı hala hatalıysa,
    # manuel kontrol etmemiz gerekirdi, ancak temizleme fonksiyonu bu sefer düzeltmeli.
    print(f"KRİTİK HATA ÖNLEME: '{module_col_name}' sütunu bulunamadı. Lütfen temizlik fonksiyonunu kontrol edin.")
    print(f"Mevcut Sütunlar: {df_final.columns.tolist()}")
    exit(1)


# One-Hot Encoding
df_final = pd.get_dummies(df_final, columns=[module_col_name], prefix='mod') 

# Gereksiz Sütunları Temizleme
df_final = df_final.drop(columns=['sha'], errors='ignore')


# 5. Final Veri Setini Kaydet
df_final.to_csv(output_final_file, index=False)
print(f"\nFinal özellik seti '{output_final_file}' olarak kaydedildi.")
print(f"Final DataFrame'in sütun sayısı: {len(df_final.columns)}")

# Kontrol için kullanılan sütunları otomatik bulma (Temizlik sonrası isimler)
kontrol_sutunlari = ['date', 'isbugfix', 'historicalbugcount', 'lineschangedtotal'] 

# Eksik sütunları filtrele
available_cols = [col for col in kontrol_sutunlari if col in df_final.columns]

# En az bir modül sütunu bul
mod_col = next((col for col in df_final.columns if col.startswith('mod_')), None)
if mod_col:
    available_cols.append(mod_col)

print("İlk 5 satır (Sütunlar kısaltıldı):")
print(df_final[available_cols].head())