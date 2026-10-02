# Verifikasi Korpus Final (15 Studi Primer) terhadap Teks Lengkap & Metadata Resmi

> **Tanggal verifikasi**: 2 Oktober 2026  
> **Cakupan**: 15 studi primer final (FP-01 s/d FP-15) + FP-16 (dieksklusi pada tahap teks lengkap)  
> **Sumber kebenaran (urutan prioritas bila terjadi konflik)**: PDF teks lengkap > catatan resmi penerbit (CrossRef / TMLR) > rekaman mentah basis data (`Raw_Articles`) > kolom ekstraksi workbook (`Final_Papers`)  
> **Alat**: `download_final_papers.py` (unduh legal), `pdftotext` (poppler) untuk ekstraksi teks, CrossRef REST API untuk metadata. `opendataloader-pdf` tidak terpasang pada mesin ini, sehingga `pdftotext` dipakai sebagai rute ekstraksi.  
> **Dokumen ini tidak mengubah workbook Excel** (berkas sedang terbuka di LibreOffice). Seluruh koreksi dicatat di sini sebagai usulan (Bagian 7).

---

## 1. Ringkasan Temuan

| Aspek | Hasil |
|:---|:---|
| Teks lengkap terverifikasi dari PDF | **11 dari 15** (FP-01, 02, 03, 05, 07, 09, 11, 12, 13, 14, 15). Judul cocok 100% pada halaman 1-2 |
| Belum ada PDF (verifikasi hanya dari abstrak + CrossRef) | **4 dari 15**: FP-04 (OA gratis, unduhan skrip diblokir Cloudflare), FP-06, FP-08, FP-10 (IEEE, tanpa salinan legal; perlu akses ITS) |
| Metadata bibliografi | Seluruh DOI jurnal (14) resolve di CrossRef. **11 dari 15** entri `Final_Papers` memiliki penulis, tahun, atau URL yang salah/placeholder (FP-01, 05, 06, 08-15); dua selisih lain (FP-03, FP-06) hanya salah ketik nama pada brief tugas, bukan pada workbook (Bagian 2) |
| Kolom ekstraksi workbook (Methodology, Dataset, Key_Findings, Limitations, Future_Work) | **Banyak tidak sesuai dengan isi paper** (Bagian 3). Angka-angka seperti "42 FPS di NVIDIA Orin", "FVD 142.6", "+21.5%" tidak ditemukan di teks lengkap |
| Skor QA | Tercatat 22-24 dari 24 (rerata 23,67 = 98,6%); 11 dari 15 studi bernilai sempurna. Beberapa `QA_Notes` merujuk hal yang tidak ada di paper (Bagian 5) |
| Kelayakan (IC1/IC2) | 4 dari 5 paper JEPA yang teksnya tersedia **tidak pernah memakai istilah "world model"**; 2 paper (FP-04, FP-07) murni citra (Bagian 4) |
| FP-16 (Friston dkk., 2021) | Artikel review/perspektif, mendahului JEPA (2022). **Dieksklusi** (keputusan tim): 16 dinilai, 1 dieksklusi (EC5), **15 diikutsertakan** |

**Angka PRISMA 2020 (Template A)** yang dipakai manuskrip: 2.812 teridentifikasi, 115 duplikat dihapus, 2.697 diskrining, 2.681 dieksklusi (EC3 = 2.196; EC5 = 485, terdiri dari 332 studi sekunder dan 153 preprint non-peer-reviewed), 16 laporan dicari, 0 tidak ditemukan, 16 dinilai kelayakan, 1 dieksklusi (EC5, FP-16), **15 diikutsertakan**.

---

## 2. Koreksi Metadata Bibliografi (hasil CrossRef / TMLR, 2 Okt 2026)

| ID | Isi workbook / brief | Terverifikasi (dipakai pada `main.tex`) |
|:---:|:---|:---|
| FP-01 | 7 penulis; DOI = DOI arXiv; URL `...id=V-JEPA-TMLR-2024` (tidak ada) | 8 penulis (A. Bardes, Q. Garrido, J. Ponce, X. Chen, M. Rabbat, Y. LeCun, **M. (Mido) Assran, N. Ballas**); *Trans. Mach. Learn. Res.*, Agu. 2024; URL resmi `https://openreview.net/forum?id=QaCCuDfBk2`. **TMLR tidak menerbitkan DOI**; DOI arXiv dihilangkan dari sitasi (kebijakan non-arXiv dosen) |
| FP-02 | OK | A. Vujinović, A. Kovačević; *IEEE Access*, vol. 14, pp. 78895-78906, 2026 (terbit 22 Mei 2026) |
| FP-03 | brief: "Shih-**E**ang Chen" | Shih-**F**ang Chen, Jun-Cheng Chen, I-Hong Jhuo, Yen-Yu Lin; *IEEE TCSVT*, vol. 36, no. 7, pp. 10836-10851, Jul. 2026 |
| FP-04 | OK | L. Gogos, D. Katsikas, N. Passalis, A. Tefas; *Pattern Recognit. Lett.*, vol. 207, pp. 234-240, Sep. 2026 |
| FP-05 | "MDPI Sensors Authors Team" | **Abhishek Gupta, Ajmery Sultana**; *Sensors*, vol. 26, no. 15, art. 4894, 3 Agu. 2026 |
| FP-06 | tahun 2023; brief: "Zhi**bao** Cai; Ningjun **Lu**" | J. Zhao, Y. Wang, **Zhihao** Cai, Ningjun **Liu**, K. Wu, Y. Wang; *IEEE TAI*, vol. 5, no. 3, pp. 1263-1276, **Mar. 2024** (early access 2023) |
| FP-07 | OK | C. Vélez-García, M. Cazorla, J. Pomares; *Comput. Vis. Image Underst.*, vol. 266, art. 104698, Mar. 2026 |
| FP-08 | "IEEE Robotics Authors Team" | **Jihun Moon, Seong-Woo Kim**; *IEEE RA-L*, vol. 11, no. 6, pp. 7460-7467, Jun. 2026 |
| FP-09 | "Ziyuan Jiang ... Yuxin Qin" | **Zhennan** Jiang, Kai Liu, **Yuxing** Qin, S. Tian, Y. Zheng, M. Zhou, Z. Zhang, C. Yu, H. Li, D. Zhao (10 penulis); *IEEE RA-L*, vol. 11, no. 10, pp. 12240-12247, Okt. 2026 |
| FP-10 | "TPAMI Research Group" | **Sen Wang, Sanping Zhou, Huaiyi Dong, Kun Xia, Gang Hua, Le Wang**; *IEEE TPAMI*, early access, 2026 (model: SAMPO++) |
| FP-11 | "IEEE TIP Research Group" | **Lening Wang, Wenzhao Zheng, Yilong Ren, Han Jiang, Zhiyong Cui, Haiyang Yu, Jiwen Lu**; *IEEE TIP*, vol. 35, pp. 4947-4960, 2026 |
| FP-12 | "IEEE TIP Authors Team" | **Siyu Li, Fei Teng, Yihong Cao, Kailun Yang, Zhiyong Li, Yaonan Wang**; *IEEE TIP*, vol. 35, pp. 3038-3052, 2026 |
| FP-13 | "IEEE RA-L Authors Team" | **Jun Guo, Xiaojian Ma, Yikai Wang, Min Yang, Huaping Liu, Qing Li**; *IEEE RA-L*, vol. 11, no. 3, pp. 2466-2473, Mar. 2026 |
| FP-14 | "Nature Communications Engineering Research Team" | **Yanchen Guan, Haicheng Liao, Chengyue Wang, Xingcheng Liu, Jiaxun Zhang, Zhenning Li**; *Commun. Eng.*, vol. 4, art. 144, 5 Agu. 2025 |
| FP-15 | "IEEE RA-L Authors Team" | **Han Qi, Haocheng Yin, Aris Zhu, Yilun Du, Heng Yang**; *IEEE RA-L*, vol. 11, no. 5, pp. 5534-5541, Mei 2026 |

Distribusi korpus terverifikasi: tahun 2024 = 2, 2025 = 1, 2026 = 12. Penerbit/outlet: IEEE = 10 (RA-L x4, TIP x2, TPAMI, TCSVT, TAI, Access), Elsevier = 2 (PRL, CVIU), MDPI = 1, Nature Portfolio = 1, TMLR = 1.

---

## 3. Verifikasi Isi per Paper

Konvensi: **[PDF]** = diverifikasi dari teks lengkap (versi dicatat di `final_paper/download_manifest.json`); **[ABSTRAK]** = hanya dari abstrak/CrossRef (PDF belum ada). Kolom "workbook" merujuk `Final_Papers`.

### FP-01: V-JEPA (Bardes dkk., TMLR 2024) [PDF: arXiv v1; belum dibandingkan dengan versi kamera-siap TMLR]
- **Kategori**: JEPA (video). Tidak memakai istilah "world model" (0 kemunculan).
- **Metode**: encoder + prediktor; regresi ℓ1 ke fitur target dari encoder EMA dengan stop-gradient; pencegahan collapse via EMA + predictor (gaya BYOL); ViT-L/16, ViT-H/16, ViT-H/16₃₈₄; pra-latih hanya pada video (VideoMix2M, sekitar 2 juta video: HowTo100M, Kinetics-400/600/700, SSv2); klip 16 frame, frame-skip 4.
- **Evaluasi**: backbone beku + attentive probing, juga fine-tuning; K400, SSv2, AVA, ImageNet-1K, Places205, iNaturalist.
- **Hasil kunci**: ViT-H/16 (beku) 81,9% K400, **72,2% SSv2**, 77,9% ImageNet-1K; pra-latih sekitar **2x** lebih cepat (wall-clock) daripada model prediksi piksel besar; jumlah sampel jauh lebih sedikit; lebih label-efisien (selisih membesar saat label dikurangi 10x).
- **Visualisasi**: prediksi V-JEPA didekode oleh model difusi terpisah (V-JEPA bukan model generatif).
- **Ketidaksesuaian workbook**: "82,1% di SSv2" (salah, 72,2%); "1,5x-6x lebih cepat" (tidak ada; yang tertulis ~2x); "loss L2" (paper memakai ℓ1); dataset "K400, SSv2, ImageNet-1K" (itu sebagian dataset evaluasi, bukan korpus pra-latih); Limitations ("deterministik murni, tanpa komponen stokastik") dan Future_Work **tidak ditemukan** pada versi ini.

### FP-02: ACT-JEPA (Vujinović & Kovačević, IEEE Access 2026) [PDF: versi penerbit, OA gold]
- **Kategori**: JEPA + imitation learning. 46 kemunculan "world model".
- **Metode**: end-to-end memprediksi (1) urutan aksi (decoder aksi gaya ACT) dan (2) urutan observasi laten (JEPA, target encoder EMA); empat komponen transformer; kedua objektif memakai loss L1. **Target modalitas JEPA = state proprioceptive**; citra RGB (96² / 128²) menjadi masukan encoder.
- **Benchmark**: Push-T (206 demonstrasi), Meta-World (15 tugas, 40 demo/tugas), ManiSkill (50 demo/tugas); seluruhnya simulasi.
- **Baseline**: AR transformer (setara DT/BeT tanpa reward) dan ACT (varian AE). Tidak ada baseline difusi/generatif.
- **Hasil kunci**: probing masa depan: RMSE turun 29-37%, ATE turun 29-40% dibanding ACT ("hingga 40% relatif"); success rate hingga +10 poin atas ACT, +41 / +28 / +53,7 poin atas AR (Push-T / ManiSkill / Meta-World).
- **Keterbatasan (paper)**: hanya simulasi, hanya target proprioceptive, keragaman dan ukuran data terbatas. **Future work**: dataset lebih besar, evaluasi dunia nyata.
- **Ketidaksesuaian workbook**: dataset "DeepMind Control Suite, Franka Kitchen, Gym-MuJoCo" (tidak ada); "mengurangi dimensi komputasi 40%" dan "konvergensi 2,1x" (tidak ada; 40% adalah perbaikan galat probing); Limitations "benda transparan/pantulan" dan Future_Work "invariansi fotometrik" (tidak ada).

### FP-03: GOT-JEPA (Chen dkk., IEEE TCSVT 2026) [PDF: arXiv v5, naskah diterima TCSVT]
- **Kategori**: JEPA (pelacakan objek video); 0 kemunculan "world model".
- **Metode**: pra-latih model-prediktif: teacher menghasilkan pseudo tracking model dari frame bersih, student memprediksinya dari frame terdistorsi; OccuSolver (estimasi visibilitas berbasis point tracker); dibangun di atas ToMP dengan backbone DINOv2 ViT-L beku.
- **Benchmark (7)**: AVisT, NfS, OTB-100, GOT-10k, LaSOT, TrackingNet, VOT2022-STb; metrik SUC, Pr, NPr, AO.
- **Kecepatan**: 24 FPS (resolusi tinggi) / 50 FPS (rendah) pada RTX 4090, sekitar 3 GB.
- **Keterbatasan**: latar berantakan dan gerak cepat; data di luar distribusi (AVisT). **Future work**: isyarat geometri 3D.
- **Ketidaksesuaian workbook**: "UAV123" (tidak ada); "+23% ketahanan oklusi vs model generatif" dan "38 FPS" (tidak ada; pembanding adalah tracker SOTA, bukan model generatif).

### FP-04: Probabilistic I-JEPA (Gogos dkk., PRL 2026) [ABSTRAK, sumber OpenAlex]
- **Kategori**: JEPA (citra). Abstrak: formulasi probabilistik I-JEPA yang mencocokkan distribusi representasi patch target dengan prediksi dari blok konteks; perbaikan konsisten atas I-JEPA pada klasifikasi hilir dan transfer learning.
- **Tidak terverifikasi**: dataset, metrik, angka. Workbook ("varians Gaussian, estimasi ketidakpastian, CIFAR-100/STL-10/Mini-ImageNet, NLL, <12 ms") **tidak didukung abstrak**: tujuan abstrak adalah representasi yang lebih kaya secara semantik, bukan estimasi ketidakpastian.
- **Tindakan**: unduh PDF (OA CC-BY) dan jalankan ulang verifikasi.

### FP-05: LM-JEPA (Gupta & Sultana, Sensors 2026) [PDF: versi penerbit MDPI, OA]
- **Kategori**: JEPA multimodal + VLM ringan; **0 kemunculan "world model"**; tidak ada pembandingan dengan world model difusi.
- **Metode**: encoder ViT ringan (d = 512) untuk kamera/LiDAR/radar/peta HD, fusi adaptif konteks, transmisi laten selektif, VLM ringan untuk penalaran.
- **Data/evaluasi**: BDD100K, nuScenes-QA; evaluasi loop-tertutup di CARLA (Coll, SpdVar, Jerk, Route Completion). **Baseline**: GPT-4o, LLaMA-3.1 (LLM); Qwen2.5-VL, InternVL2.5 (VLM); JEPA konvensional.
- **Hasil kunci (abstrak/tabel)**: akurasi persepsi +5%, latensi -7% (sekitar) vs baseline LLM/VLM; pemahaman adegan hingga +25%; keberhasilan persimpangan +20%; parameter yang ditransmisikan -15%.
- **Ketidaksesuaian workbook**: "nuScenes, Waymo, KITTI; mAP, NDS" (hanya nuScenes-QA dan BDD100K); "42 FPS di NVIDIA Orin, 3,8 GB vs 16,4 GB pada world model difusi" (tidak ada: tidak ada FPS, Waymo, KITTI, maupun difusi).

### FP-06: Contrastive world model STC (Zhao dkk., IEEE TAI 2024) [ABSTRAK]
- **Kategori**: world model laten kontrastif (**bukan JEPA**). Abstrak: model transisi dinamika berbasis RNN membangun ruang laten bersama (spasial + temporal) dengan loss kontrastif multi-objektif; encoder pra-latih dipakai untuk policy; evaluasi pada lingkungan navigasi drone simulasi dan dataset di luar domain; efisiensi data meningkat lebih dari separuh dibanding baseline task-specific dan kontrastif; kode tersedia.
- **Ketidaksesuaian workbook** (tidak didukung abstrak): AirSim, "penerbangan indoor dunia nyata", "efisiensi sampel 2,8x", "galat lintasan -31,4% vs world model VAE generatif". `QA_Notes` ("eksperimen penerbangan fisik dunia nyata") bertentangan dengan abstrak.

### FP-07: SCOTT + MIM-JEPA (Vélez-García dkk., CVIU 2026) [PDF: arXiv v2, memuat journal-ref CVIU 2026]
- **Kategori**: JEPA (**citra saja**; "video" muncul 1 kali, "world model" 0 kali).
- **Metode**: SCOTT (tokenizer konvolusi jarang untuk ViT) + MIM-JEPA (encoder konteks, target EMA, prediktor).
- **Data**: Oxford Flowers-102, Oxford-IIIT Pets-37, ImageNet-100; 1 GPU RTX 3090.
- **Hasil kunci (probe beku)**: Pets-37 90,7% top-1 (7.349 citra tak berlabel) vs 48,3% latih dari awal; Flowers-102 96,9% (SCOTT-7/16*, 8.189 citra); ImageNet-100 84,8% (vs SparseSwin ImageNet-1K 86,9%).
- **Ketidaksesuaian workbook**: "Small-Scale Video Action benchmarks", perbandingan dengan MAE/difusi, "90% akurasi dengan 40% data" (tidak ada).

### FP-08: SPREAD (Moon & Kim, IEEE RA-L 2026) [ABSTRAK]
- **Kategori**: world model terlatih + adaptasi online kontinu: model beku, hanya adapter LoRA yang diperbarui; galat prediksi turun 40% dalam 100 langkah di bawah perubahan visual dan dinamika; berdampak pada success rate; diuji pada continual learning. **Jenis model dasar (laten non-rekonstruktif vs rekonstruktif) tidak dapat dipastikan dari abstrak**, sehingga kategori "JEPA/laten prediktif" pada workbook **belum terverifikasi**.
- **Ketidaksesuaian workbook**: "Meta-World ML10/ML45", "meta-learning", "hemat memori GPU 72% vs difusi" (tidak didukung abstrak; mekanisme adalah LoRA, bukan meta-learning).

### FP-09: World4RL (Jiang dkk., IEEE RA-L 2026) [PDF: arXiv v2]
- **Kategori**: generatif (difusi); 57 kemunculan "world model".
- **Metode**: world model difusi gaya EDM (U-Net 2D) sebagai simulator; two-hot action encoding; refinement policy sepenuhnya di rollout imajinasi (model beku); kondisi 4 frame riwayat + aksi.
- **Evaluasi**: Meta-World (6 tugas, 3 seed) + 6 tugas dunia nyata (Franka Emika Panda, 20 rollout/tugas); metrik FVD, FID, LPIPS dan success rate. **Baseline**: NWM (DiT), iVideoGPT, DiWA (RSSM) untuk prediksi video; BC, DP, TD3+BC, IQL, IRASim, DiWA, TD-MPC2, serta Uni-O4/RLPD (butuh +300 ribu langkah online).
- **Hasil kunci**: success rate rerata terbaik **67,5%** pada Meta-World.
- **Keterbatasan (paper)**: resolusi visual dan kapasitas model moderat karena keterbatasan komputasi.
- **Ketidaksesuaian workbook**: RoboMimic/RLBench, "FVD 142,6", "120-250 ms per langkah", "A100/H100" (tidak ada; paper tidak melaporkan latensi atau perangkat keras).

### FP-10: SAMPO++ (Wang dkk., IEEE TPAMI 2026) [ABSTRAK]
- **Kategori**: generatif (autoregresi temporal + scale-wise flow matching pada piramida laten kontinu; Action-Controlled Velocity Field, PC-RoPE, rollout-aware training). Metrik: FVD, PSNR, SSIM, LPIPS + action alignment, counterfactual accuracy, no-op residual, rollout drift; diuji pada manipulasi robot, perencanaan visual, MBRL, dan prediksi video mengemudi tanpa aksi.
- **Tidak terverifikasi**: nama dataset (abstrak tidak menyebutnya). Workbook ("Ego4D, BridgeData V2, DVD", "3,4x lebih cepat dari difusi", "galat akumulatif setelah 16 frame") tidak didukung abstrak. **Catatan**: arXiv 2509.15536 ("SAMPO") adalah makalah pendahulu yang berbeda; tidak dipakai sebagai pengganti.

### FP-11: OccSora (Wang dkk., IEEE TIP 2026) [PDF: arXiv v1, Mei 2024; versi TIP 2026 dapat berbeda]
- **Kategori**: generatif (difusi); 41 kemunculan "world model".
- **Metode**: tokenizer adegan okupansi 4D (kompresi temporal 32x relatif OccWorld, sekitar 50% mIoU rekonstruksi OccWorld dipertahankan) + diffusion transformer berkondisi trajektori; 32 frame, 16 detik.
- **Data/metrik**: nuScenes + anotasi Occ3D; mIoU/IoU rekonstruksi; FID untuk generasi. Pelatihan pada A100: tokenizer ~42 GB/GPU (150 epoch, 50,6 jam), model difusi ~47 GB/GPU.
- **Keterbatasan (paper)**: granularitas voxel; detail objek bergerak tidak konsisten (data latih kecil).
- **Ketidaksesuaian workbook**: "Waymo 3D Occupancy", "Ray-IoU", "FVD", "310 ms per frame" (tidak ada; FVD tidak dilaporkan, latensi inferensi tidak dilaporkan).

### FP-12: NRSeg (Li dkk., IEEE TIP 2026) [PDF: arXiv v2, "Accepted to TIP"]
- **Kategori**: pemanfaatan data sintetis dari world model mengemudi generatif (mis. MagicDrive, BEVControl) untuk segmentasi BEV; **bukan** arsitektur world model baru. 44 kemunculan "world model".
- **Metode**: PGCM (metrik konsistensi perspektif-geometri), BiDPP (prediksi paralel multinomial + Dirichlet, evidential learning), HLSE.
- **Data**: nuScenes (tugas UDA dan semi-supervised); adaptasi lintas dataset Argoverse ke nuScenes. **Hasil**: mIoU +13,8% (unsupervised) dan +11,4% (semi-supervised).
- **Keterbatasan (paper)**: perlu ko-training pada data domain sumber. **Future work**: meta-learning bila hanya ada model pra-latih.
- **Ketidaksesuaian workbook**: nuScenes-C, SemanticKITTI, "+4,7% mIoU cuaca buruk", "halusinasi batas jalan" (tidak ada; "hallucination" 0 kemunculan).

### FP-13: FlowDreamer (Guo dkk., IEEE RA-L 2026) [PDF: arXiv v1, Mei 2025; versi RA-L 2026 dapat berbeda]
- **Kategori**: generatif: U-Net memprediksi scene flow 3D, lalu Stable Diffusion (latent diffusion) yang di-fine-tune merender frame RGB berikutnya (kondisi RGB-D, aksi, flow); dilatih end-to-end.
- **Benchmark (4)**: SimplerEnv RT-1, Language Table (prediksi video); VP2 dengan tugas RoboDesk dan Robosuite (perencanaan visual/MPC). **Metrik**: DINOv2 L2 dan CLIP score, PSNR/SSIM/LPIPS, FID/FVD, success rate.
- **Hasil kunci**: +7% kemiripan semantik, +11% kualitas piksel, +6% success rate vs world model RGB-D baseline (Vanilla, MinkNet, SepTrain, dll.).
- **Keterbatasan (paper)**: flow kurang presisi pada tugas push Robosuite; reward visual tidak selalu menunjuk lintasan benar.
- **Ketidaksesuaian workbook**: "arsitektur Dreamer rekursif laten dengan kepala flow generatif", RLBench/Franka, EPE, "-18,2% galat perencanaan", "+45% waktu latih" (tidak ada).

### FP-14: Pembangkitan adegan untuk antisipasi kecelakaan (Guan dkk., Commun. Eng. 2025) [PDF: versi penerbit, OA]
- **Kategori**: generatif: world model berbasis Stable Diffusion v1.5 (dilatih pada nuScenes) dipandu prompt (peta HD, BEV, cuaca) menghasilkan video berkendara sintetis (FVD 36,38 terhadap DAD); ditambah GCN dinamis + konvolusi dilasi temporal untuk antisipasi kecelakaan; dataset baru AoTA (4.000 klip) dan AoTA+.
- **Data/metrik**: DAD, A3D, CCD, AoTA/AoTA+; AP dan mTTA; RTX 4090. **Hasil**: pada A3D, +3,9% AP dan +33,2% mTTA atas model terbaik kedua (sesuai klaim paper).
- **Ketidaksesuaian workbook**: "DADA-2000", "+0,82 detik TTA" (tidak ada).

### FP-15: Generative Predictive Control (Qi dkk., IEEE RA-L 2026) [PDF: arXiv v4, "Acceptance to RA-L"]
- **Kategori**: **generatif**: kebijakan difusi beku + world model difusi **ruang citra** berkondisi aksi (GPC-RANK, GPC-OPT). Label "hibrida / world model laten" pada workbook **tidak didukung** (world model-nya generatif ruang citra).
- **Tugas**: Push-T berbasis state, empat tugas simulasi berbasis visi (Push-T, Triangle Drawing, Block Stacking, Cube & Sphere Swapping), dunia nyata: Push-T dan melipat kain (10 percobaan). **Baseline**: Diffusion Policy, LaDi-WM, V-GPS, DreamerV3.
- **Keterbatasan (paper)**: biaya inferensi, rollout difusi mendominasi waktu (sekitar 90-95%; sekitar 3 detik per siklus keputusan nyata).
- **Ketidaksesuaian workbook**: RoboCasa, "+21,5% success rate" (tidak ada), "latensi linier terhadap K" (tidak dinyatakan).

### FP-16 (dieksklusi, EC5): Friston dkk., Neural Networks 2021 [ABSTRAK; PDF opsional, OA gratis]
- Abstrak: "setelah menyurvei secara singkat sejarah ... kami memperkenalkan free energy principle ... kami meninjau kemajuan terkini ... bahasa pemrograman probabilistik" = artikel review/perspektif (studi sekunder).
- Klaim workbook "membuktikan secara matematis bahwa JEPA dan generatif bertemu pada free energy" **tidak mungkin benar** (paper terbit 2021, JEPA diusulkan 2022) dan tidak ada dalam abstrak.

---

## 4. Audit Kelayakan (IC1-IC5) per Studi

| ID | IC1 (arsitektur world model / garis keturunan JEPA vs generatif) | IC2 (video / dinamika visual berurutan) | Catatan |
|:---:|:---|:---|:---|
| FP-01 | Garis keturunan JEPA; **tidak memakai istilah "world model"** | Ya (video) | Dimasukkan sebagai bukti JEPA (Intervention PICOC) |
| FP-02 | Ya | Sebagian: observasi citra (simulasi), target JEPA proprioceptive | |
| FP-03 | Garis keturunan JEPA; **0 kemunculan "world model"** | Ya (pelacakan video) | |
| FP-04 | Garis keturunan JEPA (abstrak) | **Tidak (citra saja)** | Dipertahankan (keputusan tim), diungkap |
| FP-05 | Garis keturunan JEPA; **0 kemunculan "world model"** | Sebagian (persepsi berkendara, CARLA loop tertutup) | |
| FP-06 | Ya (judul: contrastive world model) | Ya (navigasi visual) | berdasarkan abstrak |
| FP-07 | Garis keturunan JEPA; **0 kemunculan "world model"** | **Tidak (citra saja)** | Dipertahankan (keputusan tim), diungkap |
| FP-08 | Ya | Perubahan visual + dinamika | berdasarkan abstrak |
| FP-09, 10, 11, 13, 15 | Ya (world model generatif eksplisit) | Ya | |
| FP-12 | Sebagian: memakai data dari world model, bukan mengusulkan world model | Ya (BEV dari kamera) | |
| FP-14 | Ya (world model untuk pembangkitan adegan) + model antisipasi hilir | Ya (video dashcam) | |

IC3 (Jan 2018-Sep 2026): seluruhnya terpenuhi (FP-09 terbit pada edisi Okt. 2026 tetapi terjaring pada pencarian 22 Sep 2026). IC4: seluruhnya artikel jurnal (FP-01 = TMLR; FP-10 = early access). IC5: bahasa Inggris; teks lengkap tersedia untuk 11 dari 15.

**Implikasi pelaporan**: manuskrip tidak menyatakan bahwa seluruh studi "menyebut dirinya world model"; tanda † pada Tabel II menandai studi JEPA yang tidak memakai istilah tersebut, dan hal ini dicantumkan sebagai batasan.

---

## 5. Audit Kualitas (QA): hanya laporan, tidak ada penilaian ulang

- Skor tercatat (`Quality_Assessment`): FP-01 24, FP-02 23, FP-03 24, FP-04 22, FP-05 23, FP-06 24, FP-07 23, FP-08 24, FP-09-FP-15 masing-masing 24. **11 dari 15 bernilai 24/24; rerata 23,67 (98,6%)**; semua ≥ 91,7% sehingga seluruhnya berstatus *Final*. Rentang skala 1-3 per kriteria berarti total 8-24 (bukan 0-24).
- Efek langit-langit (*ceiling effect*) ini rawan dipertanyakan reviewer. Skor dicatat sebelum teks lengkap diunduh; **disarankan penilaian ulang independen oleh dua penilai** dengan rubrik `Protocol_Criteria`.
- `QA_Notes` yang bertentangan dengan paper/abstrak: FP-06 ("penerbangan fisik dunia nyata"; abstrak hanya simulasi + dataset di luar domain); FP-02 ("baseline varian RL berbasis model"; baseline sebenarnya AR transformer dan ACT); FP-09 ("metrik FVD, PSNR, serta latensi"; paper tidak melaporkan PSNR maupun latensi).
- Rubrik QA1-QA8 di `04_PENILAIAN_KUALITAS_QA.md` berbeda dari rubrik pada sheet `Protocol_Criteria` workbook; manuskrip memakai rubrik **workbook**.

---

## 6. Pemetaan Pertanyaan Penelitian (workbook 6 RQ menjadi manuskrip 5 RQ)

| RQ manuskrip | Asal di workbook |
|:---|:---|
| RQ1 Paradigma arsitektur & evolusi | RQ-01 |
| RQ2 Objektif pembelajaran & ruang representasi | RQ-02 |
| RQ3 Performa tugas hilir + dataset, benchmark, metrik | RQ-03 + RQ-05 |
| RQ4 Trade-off efisiensi komputasi & sampel | RQ-04 |
| RQ5 Tantangan terbuka & arah hibrida | RQ-06 |

Kolom `Relevant_RQ` pada `Final_Papers` masih memakai skema 6-RQ; gunakan tabel ini untuk konversi.

---

## 7. Checklist Sinkronisasi Workbook (usulan, belum dilakukan)

1. **Final_Papers / Quality_Assessment**: hapus baris FP-16 atau tandai "dieksklusi pada teks lengkap (EC5)". Perbaiki penulis, tahun, volume/halaman, URL dan DOI sesuai Bagian 2 (FP-01: URL `QaCCuDfBk2`, tanpa DOI).
2. **Final_Papers**: ganti `Methodology`, `Dataset/Sample`, `Technology/Approach`, `Key_Findings`, `Limitations`, `Future_Work` sesuai Bagian 3 (khususnya FP-01, 02, 03, 05, 07, 09, 11, 12, 13, 14, 15). Kategori FP-15 = generatif (bukan hibrida).
3. **PRISMA_Counts**: `C8` (Records screened) dari 2.812 menjadi **2.697**; formula rentang `A2:A17` menjadi `A2:A16` setelah FP-16 dikeluarkan; tambahkan baris "reports sought = 16", "not retrieved = 0", "assessed = 16", "excluded = 1", "included = 15".
4. **Search_Strategy**: baris IEEE Xplore belum mencatat tanggal pencarian (23 Sep 2026); teks lama ("API 7 basis data", "IEEE menunggu aktivasi") dan "61 kueri" perlu menjadi 8 basis data dan **68 kueri**.
5. **Protocol_Criteria**: EC5 perlu menyebut eksplisit studi sekunder dan preprint; catat interpretasi IC2 (garis keturunan JEPA pada citra).
6. **PICOC_RQs**: pilih skema 5 RQ (atau pertahankan 6 dan pakai Bagian 6).
7. **Berkas lain yang usang**: `csv/screening.csv` (versi lama 65 + 15), `01`-`06`, `README.md`, `PRD_...md`, `GEMINI.md` (korpus 42 studi, 6 RQ, nama penulis yang tidak valid).

---

## 8. Berkas yang Masih Perlu Diunduh Manual

| ID | Sumber | Simpan sebagai |
|:---:|:---|:---|
| FP-04 | OA gratis (CC-BY): `https://doi.org/10.1016/j.patrec.2026.07.005` | `final_paper/FP-04_CR-0040_PRL_Prob-I-JEPA.pdf` |
| FP-06 | IEEE Xplore (akses ITS): `https://doi.org/10.1109/TAI.2023.3283488` | `final_paper/FP-06_OA-0820_IEEE-TAI_STC-Contrastive-WM.pdf` |
| FP-08 | IEEE Xplore (akses ITS): `https://doi.org/10.1109/LRA.2026.3688061` | `final_paper/FP-08_IEEE-0006_IEEE-RAL_SPREAD.pdf` |
| FP-10 | IEEE Xplore (akses ITS): `https://doi.org/10.1109/TPAMI.2026.3727986` | `final_paper/FP-10_SCOPUS-0014_IEEE-TPAMI_SAMPO-pp.pdf` |
| FP-16 (opsional, dieksklusi) | OA gratis: `https://hdl.handle.net/1721.1/150396` | `final_paper/excluded_fulltext/FP-16_OA-0395_Neural-Networks_World-Model-Learning-Inference.pdf` |

Setelah berkas diletakkan: `python3 download_final_papers.py --verify-only`. Verifikasi isi untuk FP-04/06/08/10 lalu diselesaikan dan baris Tabel II terkait dapat difinalisasi.

---

## 9. Catatan Teknis & Batasan Verifikasi

- Versi berkas: FP-02, 05, 14 = versi penerbit; FP-01, 03, 07, 09, 11, 12, 13, 15 = salinan arXiv (versi dicatat di manifest). Salinan arXiv dapat berbeda dari versi akhir jurnal; angka pada manuskrip yang berasal dari salinan arXiv adalah angka pada salinan tersebut. FP-01 dan FP-11/FP-13 paling berisiko (arXiv v1 lebih tua dari terbitan jurnal).
- OpenReview (FP-01), MDPI domain utama, Europe PMC dan MIT DSpace memblokir unduhan skrip (HTTP 403/405/CAPTCHA); tidak ada upaya mengakali pemblokiran. FP-05 diunduh melalui CDN resmi MDPI.
- Seluruh pernyataan "tidak ditemukan di paper" didasarkan pada pencarian teks pada badan makalah (sebelum daftar pustaka) menggunakan `grep` atas hasil `pdftotext`.
