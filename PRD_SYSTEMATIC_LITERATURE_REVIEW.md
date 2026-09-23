# PROJECT REQUIREMENTS DOCUMENT (PRD) & RESEARCH EXECUTION PLAN
## Systematic Literature Review (SLR) — Mata Kuliah Penulisan Ilmiah
### "Arsitektur World Model pada Domain Video: Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif"

---

## 1. Executive Summary & Visi Proyek

### 1.1 Visi Proyek
Menghasilkan karya ilmiah **Systematic Literature Review (SLR)** komprehensif, bereputasi tinggi, dan berbasis bukti empiris (*evidence-based*) yang memenuhi standar internasional **Kitchenham & Charters (2007)** serta pelaporan **PRISMA 2020 (Page et al., 2021)**. Karya ini diposisikan sebagai tinjauan state-of-the-art yang menjadi landasan kokoh bagi penyusunan **Proposal Tugas Akhir (TA) / Skripsi** mahasiswa Departemen Teknologi Informasi ITS.

### 1.2 Profil Peneliti & Peran Tim
- **Dosen Pengampu:** Rizka Wakhidatus Sholikah (Mata Kuliah: Penulisan Ilmiah / Scientific Writing)
- **Tim Peneliti (Kelompok 4 Mahasiswa TI ITS):**
  1. **M. Hikari Reiziq Rakhmadinta** (`5027241079`) — *Lead Researcher*: Perumusan Protokol, PICOC, Ekstraksi Data & Sintesis RQ.
  2. **Arya Bisma Putra Refman** (`5027241036`) — *Data Engineer*: Strategi Pencarian, Otomasi API 8 Basis Data & Deduplikasi Data.
  3. **Ahmad Syauqi Reza** (`50027241085`) — *Screening Specialist*: Penyaringan Literatur Dua Tahap (Fase 1 Judul/Abstrak & Fase 2 Teks Lengkap).
  4. **M. Fatihul Qolbi Ash Shidiqi** (`5027241023`) — *Quality Auditor*: Penilaian Kualitas Ilmiah (Quality Assessment QA1–QA8) & Mitigasi Bias.

---

## 2. Kepatuhan Standar Metodologi (Framework Compliance)

Proyek ini wajib mematuhi empat dokumen rujukan dosen:
1. `SLR Framework.pdf`
2. `PRISMA_2020_flow_diagram_new_SRs_v1.docx`
3. `PRISMA_2020_flow_diagram_new_SRs_v2 (1).docx`
4. `Kitchenham_SLR_Article_Selection_Template.xlsx`

Master memory tersimpan di:
👉 [SLR_FRAMEWORK_DOSEN_MEMORY.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/SLR_FRAMEWORK_DOSEN_MEMORY.md)  
Aturan prompt AI Agent tersimpan di:
👉 [GEMINI.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/GEMINI.md)

---

## 3. Spesifikasi Rinci Fase 1: PLANNING (Perencanaan)

### 3.1 Spesifikasi PICOC
- **Population (P):** Sistem kecerdasan buatan dengan *world model* untuk simulasi, representasi, dan prediksi sekuens adegan video/lingkungan digital.
- **Intervention (I):** Arsitektur world model berbasis representasi laten non-generatif (**Joint Embedding Predictive Architecture / JEPA**; misal I-JEPA, V-JEPA, MC-JEPA, LeWM, H-JEPA).
- **Comparison (C):** Arsitektur world model **generatif** berbasis rekonstruksi visual piksel (Video Diffusion Models, Autoregressive Video Transformers, RSSM DreamerV1–V3, Ha & Schmidhuber).
- **Outcomes (O):** Efisiensi komputasi (FLOPs, latensi, VRAM), efisiensi sampel, pencegahan *representation collapse*, dan performa downstream (*video prediction*, *visual probing*, *planning/control*).
- **Context (C):** Domain representasi video alami (Kinetics-400, SSv2, nuScenes) dan simulasi kontrol fisik/robotik (MuJoCo, CARLA, Atari, Minecraft).

### 3.2 Formulasi Research Questions (RQs)
| ID | Research Question | Relasi PICOC | Target Analisis |
|:---:|:---|:---:|:---|
| **RQ-01** | Apa saja paradigma arsitektural utama pada garis keturunan JEPA dan generatif dalam *world modeling*, dan bagaimana evolusinya (2018–2026)? | P, I, C | Taksonomi model, modul encoder-predictor-decoder, garis evolusi. |
| **RQ-02** | Apa perbedaan mendasar dalam fungsi objektif pembelajaran (*loss functions*) dan strategi representasi antara JEPA vs Generatif? | I, C, O | Latent loss + EMA vs Pixel reconstruction/ELBO/Score matching; task-irrelevant noise. |
| **RQ-03** | Bagaimana perbandingan performa empiris pada 3 tugas utama: *video prediction*, *representation probing*, dan *model-based RL planning*? | I, C, O, Ctx | FVD, linear probing accuracy, reward akumulatif, planning time. |
| **RQ-04** | Bagaimana trade-off efisiensi komputasi (FLOPs, memori, latensi inferensi) dan efisiensi sampel antara kedua garis keturunan? | I, C, O | Profiling komputasi training & planning inference; interaksi sampel simulator. |
| **RQ-05** | Apa saja dataset benchmark dan metrik evaluasi yang umum digunakan komunitas riset? | O, Ctx | Taksonomi dataset video, simulator fisika, metrik persepsi & kebijakan. |
| **RQ-06** | Apa saja tantangan terbuka (*open challenges*) dan arah riset masa depan dalam menggabungkan atau memilih antara JEPA dan generatif? | I, C, Ctx | Halusinasi generatif, evaluasi laten JEPA, dan kemunculan model hibrida. |

### 3.3 Protokol Pencarian & Basis Data
- **8 Basis Data Akademik Resmi:** CrossRef, OpenAlex, Springer Nature, ScienceDirect (Elsevier), Scopus, IEEE Xplore, Semantic Scholar, PubMed.
- **Batasan Google Scholar:** Hanya untuk pengecekan sitasi sekunder (*snowballing*), bukan sumber agregasi utama.
- **Logika Boolean:**  
  `(Population terms) AND (Intervention terms OR Comparison terms) AND (Context/Domain terms)`
- **Rentang Publikasi:** 2018 hingga September 2026.

### 3.4 Kriteria Seleksi Baku (Inclusion & Exclusion)
- **Inclusion Criteria (IC):**
  - `IC1`: Membahas langsung arsitektur world model, JEPA, atau generatif video.
  - `IC2`: Meneliti representasi laten, prediksi visual, atau kontrol berbasis model.
  - `IC3`: Diterbitkan dalam rentang 2018–2026.
  - `IC4`: Artikel peer-reviewed (Jurnal / Prosiding Konferensi internasional).
  - `IC5`: Dokumen teks lengkap (*full text*) dapat diakses dan berbahasa Inggris.
- **Exclusion Criteria (EC):**
  - `EC1`: Catatan duplikat lintas basis data.
  - `EC2`: Terbit di luar batas 2018–2026.
  - `EC3`: Tidak relevan dengan pemodelan dunia / representasi video.
  - `EC4`: Bukan domain video atau kontrol lingkungan digital.
  - `EC5`: Publikasi non-peer reviewed, bahasa non-Inggris, editorial/short paper.
  - `EC6`: Full-text tidak dapat diakses.

### 3.5 Instrumen Penilaian Mutu (Quality Assessment QA1–QA8)
- Skala skor: `1` (Rendah), `2` (Sedang), `3` (Tinggi). Total maksimum = 24 poin.
- Threshold: $\ge 75\%$ (Final), $60\% - 74.9\%$ (Review), $<60\%$ (Exclude).

---

## 4. Spesifikasi Rinci Fase 2: CONDUCTING (Pelaksanaan)

### 4.1 Pipeline Data & Eksekusi Penyaringan
```
Total Raw Articles: 2.812 (8 Basis Data: CrossRef, OpenAlex, Springer, ScienceDirect, Scopus, IEEE, Semantic Scholar, PubMed)
   └── Deduplikasi (EC1): 115 duplikat dibuang
        └── Artikel Unik: 2.697
             └── Screening Tahap 1 (Judul & Abstrak): 2.617 dieksklusi
                  └── Kandidat Lolos ke Full-Text (Candidate): 80 artikel
                       └── Screening Tahap 2 (Teks Lengkap): 32 dieksklusi
                            └── QA Pool: 48 artikel dinilai (QA1–QA8)
                                 ├── 6 artikel gagal QA (<60%)
                                 └── 42 ARTIKEL FINAL LOLOS SINTESIS:
                                      ├── 15 Studi Inti (Core Landmark FP-01 s/d FP-15)
                                      └── 27 Studi Pendukung Empiris
```

### 4.2 Struktur Tabel Ekstraksi Data (18 Atribut Baku)
Setiap artikel final diekstraksi ke sheet `Final_Papers` (dan file [06_TABEL_EKSTRAKSI_DATA.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/06_TABEL_EKSTRAKSI_DATA.md)) mencakup:
1. `Article_ID` (FP-01 dst)
2. `Title`
3. `Authors`
4. `Year`
5. `Journal/Conference`
6. `DOI`
7. `URL`
8. `Research_Aim`
9. `Research_Question`
10. `Methodology`
11. `Dataset/Sample`
12. `Technology/Approach` (Kategori: JEPA, Generatif, atau Komparatif)
13. `Evaluation_Metrics`
14. `Key_Findings`
15. `Limitations`
16. `Future_Work`
17. `Relevant_RQ`
18. `Extraction_Notes`

---

## 5. Spesifikasi Rinci Fase 3: REPORTING (Pelaporan)

### 5.1 Struktur Dokumen Laporan Akhir
1. **Bab 1: Pendahuluan**
   - Latar belakang pemodelan dunia (*world modeling*) pada sistem cerdas.
   - Urgensi membandingkan JEPA (representasi laten) vs Generatif (rekonstruksi piksel).
   - Tujuan SLR dan kontribusi terhadap riset Tugas Akhir.
2. **Bab 2: Metodologi SLR**
   - Protokol Kitchenham & Charters (2007).
   - Formulasi PICOC dan tabel Research Questions.
   - Strategi pencarian 8 basis data dan query boolean.
   - Kriteria inklusi/eksklusi dan instrumen penilaian mutu (QA1–QA8).
   - Diagram Alir PRISMA 2020 (reconciled flow diagram).
3. **Bab 3: Karakteristik Studi yang Ditinjau**
   - Distribusi publikasi per tahun (2018–2026) dan outlet (TPAMI, NeurIPS, ICLR, CVPR, ICML).
   - Taksonomi pendekatan arsitektur (15 Core Landmark vs 27 Supporting Studies).
4. **Bab 4: Hasil & Jawaban Pertanyaan Penelitian (Evidence-Based Findings)**
   - *4.1 RQ-01: Paradigma Arsitektural dan Garis Evolusi*
   - *4.2 RQ-02: Formulasi Matematika Fungsi Objektif & Analisis Ruang Laten*
   - *4.3 RQ-03: Komparasi Kinerja Empiris pada 3 Downstream Tasks*
   - *4.4 RQ-04: Analisis Trade-Off Efisiensi Komputasi & Efisiensi Sampel*
   - *4.5 RQ-05: Taksonomi Benchmark dan Metrik Evaluasi Komprehensif*
   - *4.6 RQ-06: Tantangan Terbuka, Dilema Teknis, dan Paradigma Hibrida*
5. **Bab 5: Sintesis Temuan & Diskusi (Deep Interpretation)**
   - *Cross-analysis* multi-dimensi (Arsitektur $\times$ Komputasi $\times$ Akurasi Perencanaan).
   - Perbandingan dengan kajian survei sebelumnya & resolusi perdebatan ilmiah (LeCun vs Generative camp).
   - Implikasi teknis terhadap desain arsitektur pada **Proposal Tugas Akhir**.
   - Ancaman terhadap validitas (*Threats to Validity*: construct, internal, external, conclusion validity).
6. **Bab 6: Kesimpulan & Arah Riset Masa Depan**
   - Ringkasan temuan utama.
   - Rekomendasi konkret pemilihan arsitektur untuk sistem otonom / video reasoning.

---

## 6. Checklist Kesiapan Proposal Tugas Akhir (TA Milestone)

- [x] **Milestone 1:** Penyusunan Protokol SLR & Kerangka PICOC ([01_PROTOKOL_DAN_PICOC.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/01_PROTOKOL_DAN_PICOC.md))
- [x] **Milestone 2:** Otomasi Pencarian 8 Database & PRISMA 2020 ([02_STRATEGI_PENCARIAN_DAN_PRISMA.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/02_STRATEGI_PENCARIAN_DAN_PRISMA.md))
- [x] **Milestone 3:** Screening 2.812 Artikel Mentah / 2.697 Unik & Seleksi Kandidat ([03_SCREENING_DAN_SELEKSI.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/03_SCREENING_DAN_SELEKSI.md))
- [x] **Milestone 4:** Evaluasi Kualitas Ilmiah QA1–QA8 ([04_PENILAIAN_KUALITAS_QA.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/04_PENILAIAN_KUALITAS_QA.md))
- [x] **Milestone 5:** Sintesis Bukti Empiris & Penjawab RQ-01 s/d RQ-06 ([05_SINTESIS_DAN_JAWABAN_RQ.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/05_SINTESIS_DAN_JAWABAN_RQ.md))
- [x] **Milestone 6:** Ekstraksi Data Terstruktur 42 Paper ([06_TABEL_EKSTRAKSI_DATA.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/06_TABEL_EKSTRAKSI_DATA.md))
- [x] **Milestone 7:** Integrasi Memory Dosen & Context Guardrails ([GEMINI.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/GEMINI.md) & [SLR_FRAMEWORK_DOSEN_MEMORY.md](file:///home/reiziqzip/Documents/Penulisan%20Ilmiah/penulisan-ilmiah/SLR_FRAMEWORK_DOSEN_MEMORY.md))
- [ ] **Milestone 8:** Penyusunan Naskah Proposal Tugas Akhir Bab 1–3 (Bab 1 Pendahuluan & Gap, Bab 2 Kajian Pustaka SLR, Bab 3 Metodologi Eksperimen TA).
