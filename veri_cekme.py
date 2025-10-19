import git
import os
import time

# --- Yapılandırma ---
repo_path = "scikit-learn_repo" 
repo_url = "https://github.com/scikit-learn/scikit-learn"
# --------------------

print("### 1. DEPO KLONLAMA İŞLEMİ ###")

# Klonlama klasörü zaten varsa silinsin (manuel silmeyi teyit ederiz)
if os.path.isdir(repo_path):
    print(f"UYARI: '{repo_path}' klasörü mevcut. Kodu sadece çekim için kullanacağız.")
    
try:
    # 1.1. Eğer klasör yoksa, Klonlama işlemi (bare=True ile sadece git nesneleri)
    print(f"Depo klonlanıyor: {repo_url}")
    print("Lütfen bekleyin, bu işlem büyük bir proje olduğu için ZAMAN ALACAKTIR.")
    start_time = time.time()
    
    # Hata alma ihtimaline karşı: Eğer klasör varsa ve boşsa, git.Repo.clone_from hata verebilir.
    # Ancak "no such file or directory" çıktısı aldığımız için burayı denemeliyiz.
    repo = git.Repo.clone_from(repo_url, repo_path, bare=True)
    
    end_time = time.time()
    print(f"Klonlama tamamlandı. Süre: {end_time - start_time:.2f} saniye.")

except git.GitCommandError as git_err:
    # Klonlama sırasında Git komut hatası olursa (AĞ, YETKİLENDİRME, VEYA KLASÖR İZİNLERİ)
    print("\n--- KRİTİK HATA: KLONLAMA SIRASINDA GIT COMMAND HATASI ---")
    print(f"Hata Kodu: {git_err.status}")
    print(f"Çıktı (stderr): \n{git_err.stderr.strip()}")
    print("Lütfen internet bağlantınızı ve dizin yazma izinlerinizi kontrol edin.")
    exit(1)
except Exception as e:
    # Diğer genel hatalar
    print(f"\n--- KRİTİK HATA: KLONLAMA SIRASINDA GENEL HATA ---\n{e}")
    exit(1)


print("\n### 2. COMMIT'LERİ ÇEKME VE SAYMA ###")

# Klonlama başarılıysa, repo objesini tekrar yüklemeyi deneriz (klonlama başarılıysa bu sorunsuz olmalı)
try:
    repo = git.Repo(repo_path)
    
    # Deponun ana dalını (main veya master) belirleme
    branch_name = 'main'
    commits = list(repo.iter_commits(branch_name))
except git.GitCommandError:
    branch_name = 'master'
    commits = list(repo.iter_commits(branch_name))
except Exception as e:
    print(f"HATA: Commit'ler çekilirken bir sorun oluştu: {e}")
    exit(1)

print(f"'{branch_name}' dalından **TOPLAM {len(commits)} adet commit** bulundu.")
print("Veri toplama adımının ilk aşaması BAŞARILI.")