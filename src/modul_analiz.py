import git
import pandas as pd
import os

# --- Yapılandırma ---
repo_path = "scikit-learn_repo" 
input_file = 'scikit_learn_labeled_commits.csv'
output_file = 'scikit_learn_commit_module_data.csv'
# --------------------

print("### 1. MODÜL ANALİZİ BAŞLIYOR ###")

try:
    # 1. Depo ve Veriyi Yükle
    repo = git.Repo(repo_path)
    df_commits = pd.read_csv(input_file)
    commits_dict = {commit.hexsha: commit for commit in repo.iter_commits('main')}
    print(f"Toplam {len(df_commits)} commit ve depo yüklendi.")
except Exception as e:
    print(f"HATA: Veri veya depo yüklenirken sorun oluştu: {e}")
    exit(1)

# 2. Modül Çıkarma Fonksiyonu
def extract_module(file_path):
    """Dosya yolundan ana modül adını çıkarır (örneğin, sklearn/linear_model)."""
    # Dosya yolu 'sklearn/linear_model/base.py' ise, sadece 'sklearn/linear_model' alınır.
    parts = file_path.split(os.sep)
    
    # scikit-learn projelerinde genellikle en anlamlı modül, ana kütüphane adı (sklearn) 
    # ve hemen altındaki dizin kombinasyonudur.
    if parts and parts[0] == 'sklearn' and len(parts) >= 2:
        return '/'.join(parts[:2])
    
    # Testler veya dökümantasyon gibi yardımcı dizinler için sadece ilk seviyeyi kullan
    if len(parts) >= 1 and (parts[0] == 'doc' or parts[0] == 'examples'):
        return parts[0]
        
    # Diğer kök dizinler için
    if len(parts) >= 1:
        return parts[0]
    
    return 'UNKNOWN'

# 3. Commit'ler Üzerinde Döngü (Zaman alıcı bir adımdır)
module_data = []

# Her bir satır için (bu döngü, commit sayısı kadar çalışır)
for index, row in df_commits.iterrows():
    sha = row['sha']
    commit = commits_dict.get(sha)
    
    if commit is None:
        continue # Commit objesi bulunamazsa atla

    # Değişen modülleri depolamak için set kullan (tekrarı engeller)
    changed_modules = set()
    
    # Commit'in ana ebeveyni ile arasındaki farkı al
    if len(commit.parents) > 0:
        diff_index = commit.diff(commit.parents[0])
        
        for diff in diff_index:
            # Hem eski hem yeni dosya yollarını kontrol et (silme/ekleme durumları için)
            path = diff.a_path if diff.a_path else diff.b_path
            
            if path:
                module = extract_module(path)
                changed_modules.add(module)

    # 4. Modül-Commit Satırlarını Oluşturma
    # Her commit, değiştirdiği her modül için bir satır oluşturacak.
    # Bu, Ay 2'deki risk skorunu hesaplamamız için önemlidir.
    
    for module in changed_modules:
        module_data.append({
            'sha': sha,
            'module_name': module,
            'is_bugfix': row['is_bugfix'],
            'lines_changed_total': row['lines_changed_total'],
            'files_changed': row['files_changed'],
            'date': row['date']
            # Diğer özellikleri (author, message_length vb.) Ay 2'de birleştireceğiz.
        })
    
    # İlerleme raporu
    if (index + 1) % 5000 == 0:
        print(f"İşlenen: {index + 1}/{len(df_commits)} commit.")

# 5. DataFrame oluştur ve kaydet
df_modules = pd.DataFrame(module_data)

print(f"\n### 4. MODÜL ANALİZİ BAŞARILI ###")
print(f"Toplam Commit-Modül Etkileşimi: {len(df_modules)}")
print(f"Benzersiz Modül Sayısı: {df_modules['module_name'].nunique()}")
print(f"İlk 5 Modül Etkileşimi:\n{df_modules.head()}")

df_modules.to_csv(output_file, index=False)
print(f"\nCommit-Modül verisi '{output_file}' olarak kaydedildi.")