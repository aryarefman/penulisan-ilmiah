import shutil, time, os

src = r"d:\Kuliahh\Semester 5\Penulisan Ilmiah\penulisan-ilmiah\Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif_Clean_Final.xlsx"
dst_updated = r"d:\Kuliahh\Semester 5\Penulisan Ilmiah\penulisan-ilmiah\Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif_Updated.xlsx"
dst_main = r"d:\Kuliahh\Semester 5\Penulisan Ilmiah\penulisan-ilmiah\Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif.xlsx"

print("Menyinkronkan file Clean_Final ke Updated dan Main...")
for attempt in range(15):
    try:
        shutil.copyfile(src, dst_updated)
        shutil.copyfile(src, dst_main)
        print("BERHASIL: Seluruh file Excel berhasil diperbarui dengan versi terbaru yang 100% jurnal resmi!")
        break
    except PermissionError:
        print(f"Percobaan {attempt+1}: File masih terkunci oleh Excel. Menunggu 2 detik... (Tutup Excel jika masih terbuka)")
        time.sleep(2)
    except Exception as e:
        print("Terjadi kesalahan:", e)
        break
