import git
import pandas as pd
import time

# --- Yapılandırma ---
repo_path = "scikit-learn_repo" 
# Repo URL'sini kaldırabiliriz, zaten klonladık.
# --------------------

# Klonlama kısmı (Önceki başarılı kod)
try:
    # 1. Depoyu yükle
    repo = git.Repo(repo_path)
    print("Depo yüklendi.")
    
    # 2. Commit'leri çekme - Sadece bilinen 'main' dalını kullan
    branch_name = 'main'
    
    # Commit'leri sadece HEAD (aktif en son dal) üzerinden çekmeyi deneriz.
    # Veya spesifik olarak 'main' dalını kullanırız.
    try:
        # Commit'leri 'main' dalı referansıyla çek
        commits = list(repo.iter_commits(branch_name))
        print(f"'{branch_name}' dalından toplam {len(commits)} adet commit yüklendi.")
    except git.GitCommandError as git_err:
        # Eğer Git, 'main' referansını bulamıyorsa (bare repo'larda bazen olur)
        print(f"KRİTİK UYARI: '{branch_name}' referansı bulunamadı. Tüm commit'leri SHA sırasına göre çekmeyi deniyor...")
        # Alternatif: Tüm commit'leri SHA sırasına göre çek (HEAD yerine)
        commits = list(repo.iter_commits())
        print(f"Tüm commit'ler referanssız çekildi. Toplam {len(commits)} adet commit.")
    
    
except Exception as e:
    # Depo yüklenirken (git.Repo(repo_path)) oluşan herhangi bir hatayı yakala.
    print(f"HATA: Depo yüklenirken bir sorun oluştu. Lütfen klonlama adımını tekrar kontrol edin: {e}")
    exit(1)


print("\n### 3. COMMIT ÖZELLİKLERİ ÇIKARIMI BAŞLIYOR ###")
# ... (Kodun geri kalanı aynı kalır: data listesi, for döngüsü, DataFrame oluşturma vb.)

data = []
start_time = time.time()
commit_count = len(commits)

# Her commit'i gezerek özellikleri çıkar
for i, commit in enumerate(commits):
    
    # Commit'in SHA, yazar, tarih ve mesajı
    commit_sha = commit.hexsha
    commit_date = commit.committed_datetime
    commit_author = commit.author.name
    commit_message = commit.message.strip()
    
    # 1. Commit mesajı uzunluğu
    message_length = len(commit_message)
    
    # 2. ve 3. Değişen dosya/satır sayıları (diff kullanarak)
    lines_added = 0
    lines_deleted = 0
    files_changed = 0
    
    # İlk commit'in diff'ini alamayız, bu yüzden None kontrolü yapmalıyız
    if len(commit.parents) > 0:
        # Commit'in ana ebeveyni ile arasındaki farkı al
        diff_index = commit.diff(commit.parents[0])
        
        files_changed = len(diff_index)
        
        for diff in diff_index:
            # diff.diff, diff komutunun ham çıktısıdır.
            # Burada 'stat' metodunu kullanarak özet bilgiyi alıyoruz.
            # GitPython, 'stats' objesi ile satır sayılarını kolayca sunar.
            try:
                stats = commit.stats.files[diff.a_path if diff.a_path else diff.b_path]
                lines_added += stats.get('insertions', 0)
                lines_deleted += stats.get('deletions', 0)
            except:
                # Nadiren dosya adı bulunamazsa atla
                pass
    
    lines_changed_total = lines_added + lines_deleted
    
    # Veri setine ekle
    data.append({
        'sha': commit_sha,
        'date': commit_date,
        'author': commit_author,
        'message': commit_message,
        'message_length': message_length,
        'lines_added': lines_added,
        'lines_deleted': lines_deleted,
        'lines_changed_total': lines_changed_total,
        'files_changed': files_changed,
    })

    # İlerleme raporu (her 1000 commit'te bir)
    if (i + 1) % 1000 == 0 or i + 1 == commit_count:
        elapsed = time.time() - start_time
        remaining = (commit_count - (i + 1)) * (elapsed / (i + 1)) if i > 0 else 0
        print(f"İşlenen: {i + 1}/{commit_count} commit. Süre: {elapsed:.2f} s. Kalan Tahmin: {remaining:.2f} s.")


# DataFrame oluştur ve kaydet
df = pd.DataFrame(data)
output_file = 'scikit_learn_commit_features.csv'
df.to_csv(output_file, index=False)

end_time_total = time.time()
print("\n### 4. ÖZELLİK ÇIKARIMI BAŞARILI ###")
print(f"Toplam özellik çıkarma süresi: {end_time_total - start_time:.2f} saniye.")
print(f"Veri seti '{output_file}' olarak kaydedildi.")
print(f"Oluşturulan DataFrame'in ilk 5 satırı:\n{df.head()}")