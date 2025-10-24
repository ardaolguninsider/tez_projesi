import pandas as pd
import re

# --- Yapılandırma ---
input_file = 'scikit_learn_commit_features.csv'
output_file = 'scikit_learn_labeled_commits.csv'
# --------------------

print("### 1. ETİKETLEME BAŞLIYOR: Hata Düzeltme Tespiti ###")

# Veri setini yükle
try:
    df = pd.read_csv(input_file)
    print(f"Toplam {len(df)} commit yüklendi.")
except FileNotFoundError:
    print(f"HATA: '{input_file}' dosyası bulunamadı. Lütfen dosya adını kontrol edin.")
    exit(1)

# Hata düzeltmesi olarak kabul edilecek anahtar kelimelerin regex deseni
# 'r' ön eki, kelimelerin tam olarak (büyük/küçük harf duyarsız) aranmasını sağlar.
# \b: Kelime sınırı (sadece 'fix' kelimesini arar, 'fixing' içinde aramaz)
bug_keywords = r'\b(fix|bug|error|issue|closes|resolves|bugfix|ci|test)\b'

# Commit mesajı üzerinde desen arama fonksiyonu
def label_commit(message):
    if isinstance(message, str):
        # re.IGNORECASE ile büyük/küçük harf duyarsız arama yaparız.
        if re.search(bug_keywords, message, re.IGNORECASE):
            return 1  # Bugfix (Hata Düzeltmesi)
    return 0  # Non-Bugfix (Normal Geliştirme/Özellik)

# Yeni hedef değişken sütununu oluştur
df['is_bugfix'] = df['message'].apply(label_commit)

# 2. Etiketleme Sonuçlarını Analiz Etme
bugfix_count = df['is_bugfix'].sum()
total_commits = len(df)
bugfix_ratio = (bugfix_count / total_commits) * 100

print("\n### 2. ETİKETLEME SONUÇLARI ###")
print(f"Toplam Commit Sayısı: {total_commits}")
print(f"Hata Düzeltme (is_bugfix=1) Sayısı: {bugfix_count}")
print(f"Hata Düzeltme Oranı: {bugfix_ratio:.2f}%")
print(f"Oluşturulan DataFrame'in ilk 5 satırı (is_bugfix sütunu dahil):\n{df[['sha', 'message', 'is_bugfix']].head()}")


# Etiketlenmiş veriyi yeni CSV dosyasına kaydet
df.to_csv(output_file, index=False)
print(f"\nEtiketlenmiş veri seti '{output_file}' olarak kaydedildi.")