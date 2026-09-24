import shutil, time, os

src = r"d:\Kuliahh\Semester 5\Penulisan Ilmiah\penulisan-ilmiah\Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif_Updated.xlsx"
dst = r"d:\Kuliahh\Semester 5\Penulisan Ilmiah\penulisan-ilmiah\Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif.xlsx"

print("Menyinkronkan file updated ke file utama...")
for attempt in range(10):
    try:
        shutil.copyfile(src, dst)
        print("BERHASIL: File utama berhasil diperbarui dengan versi terbaru!")
        break
    except PermissionError:
        print(f"Percobaan {attempt+1}: File masih terkunci oleh Excel. Menunggu 2 detik... (Pastikan Excel sudah ditutup)")
        time.sleep(2)
    except Exception as e:
        print("Terjadi kesalahan:", e)
        break
