#!/usr/bin/env python3
"""
Unduh PDF teks lengkap studi primer final SLR ke final_paper/ (HANYA sumber Open Access legal).

Korpus: 15 studi primer final (FP-01..FP-15) + FP-16 (dinilai pada tahap teks lengkap, lalu
dieksklusi: EC5 - artikel review/perspektif, disimpan di final_paper/excluded_fulltext/).

Urutan sumber per paper: publisher OA / TMLR OpenReview -> repositori (PMC, DSpace) -> arXiv.
Tidak ada penghindaran paywall/CAPTCHA dan tidak memakai shadow library. Paper tanpa salinan yang bisa
diunduh secara terprogram ditandai `manual_required`: FP-06, FP-08, FP-10 (IEEE, perlu akses institusi ITS)
serta FP-04 dan FP-16 (OA gratis, tetapi situs penerbit/repositori memblokir unduhan skrip). Simpan berkas
dengan nama yang dicetak skrip, lalu jalankan `--verify-only`.

Setiap berkas divalidasi: magic bytes %PDF-, ukuran, jumlah halaman (pdfinfo), dan kecocokan judul
terhadap teks halaman 1-2 (pdftotext). Hasil dicatat di final_paper/download_manifest.json
(tanpa API key dan tanpa alamat e-mail).

Pemakaian:
  python3 download_final_papers.py                  # unduh semua yang belum ada
  python3 download_final_papers.py --only FP-02,FP-04
  python3 download_final_papers.py --force          # unduh ulang
  python3 download_final_papers.py --verify-only    # validasi berkas yang ada (mis. unduhan manual), tanpa jaringan
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone

import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "final_paper")
EXCL_DIR = os.path.join(OUT_DIR, "excluded_fulltext")
MANIFEST_PATH = os.path.join(OUT_DIR, "download_manifest.json")

UA = "AcademicSLR/1.0 (+https://github.com/aryarefman/penulisan-ilmiah; academic research use)"
MIN_BYTES = 100_000
MIN_PAGES = 5
MIN_TITLE_MATCH = 0.75
HOST_GAP = {"arxiv.org": 3.5}  # detik minimum antar-permintaan per host (sopan terhadap arXiv)
DEFAULT_GAP = 1.0

POLICY = ("Hanya sumber Open Access legal (publisher OA, TMLR/OpenReview, arXiv, PMC/repositori institusi). "
          "Tidak ada penghindaran paywall. Versi tiap berkas dicatat; salinan arXiv dapat berbeda dari "
          "versi akhir (VoR) jurnal, sitasi tetap merujuk catatan jurnal.")


def arxiv(aid, note):
    return dict(kind="arxiv", url=f"https://arxiv.org/pdf/{aid}", status="ok_preprint", version=note)


# FP-16 dinilai penuh lalu dieksklusi (EC5); file disimpan terpisah sebagai bukti tahap eligibility.
PAPERS = [
    dict(id="FP-01", raw="SCOPUS-0077", role="included",
         title="Revisiting Feature Prediction for Learning Visual Representations from Video",
         doi=None, record="https://openreview.net/forum?id=QaCCuDfBk2",
         venue="Transactions on Machine Learning Research (TMLR), Aug. 2024",
         file="FP-01_SCOPUS-0077_TMLR_V-JEPA.pdf",
         candidates=[
             dict(kind="openreview_tmlr", url="https://openreview.net/pdf?id=QaCCuDfBk2",
                  status="ok_publisher_oa", version="TMLR camera-ready (OpenReview)"),
             arxiv("2404.08471", "arXiv preprint (bukan catatan jurnal)"),
         ],
         note="Tidak ada DOI jurnal; DOI di workbook adalah DOI arXiv. Sitasi memakai catatan TMLR."),
    dict(id="FP-02", raw="OA-0030", role="included",
         title="ACT-JEPA: Novel Joint-Embedding Predictive Architecture for Efficient Policy Representation Learning",
         doi="10.1109/ACCESS.2026.3696039", venue="IEEE Access, vol. 14, 2026",
         file="FP-02_OA-0030_IEEE_Access_ACT-JEPA.pdf",
         candidates=[
             dict(kind="ieee_oa", status="ok_publisher_oa", version="publishedVersion (IEEE Access, gold OA)"),
             arxiv("2501.14622", "arXiv v5, ditandai penulis sebagai 'Published version'"),
         ]),
    dict(id="FP-03", raw="CR-0039", role="included",
         title="GOT-JEPA: Generic Object Tracking With Model Adaptation and Occlusion Handling Using Joint-Embedding Predictive Architecture",
         doi="10.1109/TCSVT.2026.3675005", venue="IEEE Trans. Circuits Syst. Video Technol., vol. 36, no. 7, 2026",
         file="FP-03_CR-0039_IEEE-TCSVT_GOT-JEPA.pdf",
         candidates=[arxiv("2602.14771", "arXiv (accepted manuscript TCSVT; jurnal belum OA)")]),
    dict(id="FP-04", raw="CR-0040", role="included",
         title="Probabilistic image-based joint embedding predictive architecture",
         doi="10.1016/j.patrec.2026.07.005", venue="Pattern Recognition Letters, vol. 207, 2026",
         file="FP-04_CR-0040_PRL_Prob-I-JEPA.pdf",
         candidates=[],
         hint="OA gratis (CC-BY): buka tautan DOI di browser dan unduh PDF (unduhan skrip diblokir Cloudflare)",
         note="Hybrid OA (CC-BY). Elsevier API tidak memberi akses teks lengkap dengan key yang tersedia; unduh manual dari ScienceDirect."),
    dict(id="FP-05", raw="OA-0034", role="included",
         title="Object Detection and Scene Perception for Connected and Autonomous Vehicles Using LM-JEPA",
         doi="10.3390/s26154894", venue="Sensors, vol. 26, no. 15, 2026",
         file="FP-05_OA-0034_Sensors_LM-JEPA.pdf",
         candidates=[
             dict(kind="mdpi_cdn",
                  url="https://mdpi-res.com/d_attachment/sensors/sensors-26-04894/article_deploy/sensors-26-04894.pdf",
                  status="ok_publisher_oa", version="publishedVersion (MDPI CDN, gold OA)"),
             dict(kind="pmc", url="https://pmc.ncbi.nlm.nih.gov/articles/PMC13469734/pdf/sensors-26-04894.pdf",
                  status="ok_repository", version="PMC copy"),
             dict(kind="europepmc", url="https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC13469734&blobtype=pdf",
                  status="ok_repository", version="Europe PMC copy"),
         ]),
    dict(id="FP-06", raw="OA-0820", role="included",
         title="Learning Visual Representation for Autonomous Drone Navigation via a Contrastive World Model",
         doi="10.1109/TAI.2023.3283488", venue="IEEE Trans. Artif. Intell., vol. 5, no. 3, 2024",
         file="FP-06_OA-0820_IEEE-TAI_STC-Contrastive-WM.pdf", candidates=[],
         hint="IEEE Xplore (akses institusi ITS)",
         note="Closed access; tidak ada salinan OA/arXiv. Unduh manual via IEEE Xplore (akses ITS)."),
    dict(id="FP-07", raw="OA-0453", role="included",
         title="Escaping the big data paradigm in self-supervised representation learning",
         doi="10.1016/j.cviu.2026.104698", venue="Computer Vision and Image Understanding, vol. 266, 2026",
         file="FP-07_OA-0453_CVIU_SCOTT-MIM-JEPA.pdf",
         candidates=[arxiv("2502.18056", "arXiv (jurnal Elsevier tertutup; arXiv memuat journal-ref CVIU 2026)")]),
    dict(id="FP-08", raw="IEEE-0006", role="included",
         title="SPREAD: Scalable Pre-Trained World Model for Adaptive Dynamics Model",
         doi="10.1109/LRA.2026.3688061", venue="IEEE Robot. Autom. Lett., vol. 11, no. 6, 2026",
         file="FP-08_IEEE-0006_IEEE-RAL_SPREAD.pdf", candidates=[],
         hint="IEEE Xplore (akses institusi ITS)",
         note="Closed access; tidak ada salinan OA/arXiv. Unduh manual via IEEE Xplore (akses ITS)."),
    dict(id="FP-09", raw="OA-0018", role="included",
         title="World4RL: Diffusion World Models for Policy Refinement With Reinforcement Learning for Robotic Manipulation",
         doi="10.1109/LRA.2026.3728345", venue="IEEE Robot. Autom. Lett., vol. 11, no. 10, 2026",
         file="FP-09_OA-0018_IEEE-RAL_World4RL.pdf",
         candidates=[arxiv("2509.19080", "arXiv (jurnal IEEE tertutup)")]),
    dict(id="FP-10", raw="SCOPUS-0014", role="included",
         title="Action-Controlled Scale-Wise Flow Matching for Embodied World Models",
         doi="10.1109/TPAMI.2026.3727986", venue="IEEE Trans. Pattern Anal. Mach. Intell., early access, 2026",
         file="FP-10_SCOPUS-0014_IEEE-TPAMI_SAMPO-pp.pdf", candidates=[],
         hint="IEEE Xplore (akses institusi ITS)",
         note=("Closed access. arXiv 2509.15536 ('SAMPO') adalah makalah pendahulu yang BERBEDA, bukan SAMPO++; "
               "tidak dipakai. Unduh manual via IEEE Xplore (akses ITS).")),
    dict(id="FP-11", raw="SCOPUS-0015", role="included",
         title="OccSora: 4D Occupancy Generation Models as World Simulators for Autonomous Driving",
         doi="10.1109/TIP.2026.3687468", venue="IEEE Trans. Image Process., vol. 35, 2026",
         file="FP-11_SCOPUS-0015_IEEE-TIP_OccSora.pdf",
         candidates=[arxiv("2405.20337", "arXiv v1 (Mei 2024); dapat berbeda dari versi TIP 2026")]),
    dict(id="FP-12", raw="IEEE-0004", role="included",
         title="NRSeg: Noise-Resilient Learning for BEV Semantic Segmentation via Driving World Models",
         doi="10.1109/TIP.2026.3671686", venue="IEEE Trans. Image Process., vol. 35, 2026",
         file="FP-12_IEEE-0004_IEEE-TIP_NRSeg.pdf",
         candidates=[arxiv("2507.04002", "arXiv (accepted to TIP)")]),
    dict(id="FP-13", raw="SCOPUS-0013", role="included",
         title="FlowDreamer: A RGB-D World Model With Flow-Based Motion Representations for Robot Manipulation",
         doi="10.1109/LRA.2026.3653273", venue="IEEE Robot. Autom. Lett., vol. 11, no. 3, 2026",
         file="FP-13_SCOPUS-0013_IEEE-RAL_FlowDreamer.pdf",
         candidates=[arxiv("2505.10075", "arXiv v1 (Mei 2025); dapat berbeda dari versi RA-L 2026")]),
    dict(id="FP-14", raw="SCOPUS-0027", role="included",
         title="World model-based end-to-end scene generation for accident anticipation in autonomous driving",
         doi="10.1038/s44172-025-00474-7", venue="Communications Engineering, vol. 4, art. 144, 2025",
         file="FP-14_SCOPUS-0027_Commun-Eng_Accident-Anticipation.pdf",
         candidates=[dict(kind="nature", url="https://www.nature.com/articles/s44172-025-00474-7.pdf",
                          status="ok_publisher_oa", version="publishedVersion (Nature Portfolio, gold OA)")]),
    dict(id="FP-15", raw="IEEE-0050", role="included",
         title="Inference-Time Enhancement of Generative Robot Policies via Predictive World Modeling",
         doi="10.1109/LRA.2026.3673995", venue="IEEE Robot. Autom. Lett., vol. 11, no. 5, 2026",
         file="FP-15_IEEE-0050_IEEE-RAL_GPC.pdf",
         candidates=[arxiv("2502.00622", "arXiv v4 (accepted to RA-L)")]),
    dict(id="FP-16", raw="OA-0395", role="excluded_fulltext",
         title="World model learning and inference",
         doi="10.1016/j.neunet.2021.09.011", venue="Neural Networks, vol. 144, 2021",
         file=os.path.join("excluded_fulltext", "FP-16_OA-0395_Neural-Networks_World-Model-Learning-Inference.pdf"),
         candidates=[],
         hint="OA gratis: https://hdl.handle.net/1721.1/150396 (MIT DSpace) atau halaman penerbit; opsional (bukti tahap eligibility)",
         note="Dieksklusi pada tahap teks lengkap (EC5: artikel review/perspektif, bukan studi primer empiris)."),
]

_last_hit = {}


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def polite_wait(url):
    host = re.sub(r"^https?://([^/]+).*$", r"\1", url)
    gap = HOST_GAP.get(host, DEFAULT_GAP)
    wait = gap - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=180)


def pdf_pages(path):
    m = re.search(r"^Pages:\s+(\d+)", run(["pdfinfo", path]).stdout, re.M)
    return int(m.group(1)) if m else 0


def first_pages_text(path):
    return run(["pdftotext", "-f", "1", "-l", "2", "-layout", path, "-"]).stdout


def arxiv_version(path):
    """Versi arXiv dibaca dari cap pada halaman 1 PDF (mis. 'arXiv:2404.08471v1')."""
    m = re.search(r"arXiv:\d{4}\.\d{4,5}(v\d+)", first_pages_text(path))
    return m.group(1) if m else None


def tokens(s):
    s = s.lower().replace("ﬁ", "fi").replace("ﬂ", "fl")
    return {t for t in re.findall(r"[a-z0-9]+", s) if len(t) >= 3}


def title_match(title, text):
    exp = tokens(title)
    return len(exp & tokens(text)) / len(exp) if exp else 0.0


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_pdf(path, title):
    info = {"bytes": os.path.getsize(path)}
    with open(path, "rb") as f:
        if f.read(5) != b"%PDF-":
            return False, {**info, "reason": "bukan PDF (magic bytes)"}
    if info["bytes"] < MIN_BYTES:
        return False, {**info, "reason": f"ukuran < {MIN_BYTES} byte"}
    info["pages"] = pdf_pages(path)
    if info["pages"] < MIN_PAGES:
        return False, {**info, "reason": f"halaman < {MIN_PAGES}"}
    info["title_match"] = round(title_match(title, first_pages_text(path)), 3)
    if info["title_match"] < MIN_TITLE_MATCH:
        return False, {**info, "reason": f"judul tidak cocok (skor {info['title_match']} < {MIN_TITLE_MATCH})"}
    info["sha256"] = sha256(path)
    return True, info


def fetch(session, url, headers=None, timeout=90):
    """Unduh url; kembalikan (response, error)."""
    polite_wait(url)
    try:
        r = session.get(url, headers=headers or {}, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    if r.content[:5] != b"%PDF-":
        return None, f"bukan PDF (content-type={r.headers.get('content-type', '?')[:40]})"
    return r, None


def fetch_ieee_oa(session, doi):
    """IEEE Access (gold OA): resolusi DOI -> arnumber -> getPDF. Gagal -> fallback ke sumber berikutnya."""
    polite_wait("https://doi.org/")
    try:
        r = session.get(f"https://doi.org/{doi}", timeout=45, allow_redirects=True)
    except requests.RequestException as e:
        return None, None, f"{type(e).__name__}"
    m = re.search(r"/document/(\d+)", r.url)
    if not m:
        return None, r.url, f"arnumber tidak ditemukan (HTTP {r.status_code})"
    url = f"https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={m.group(1)}&ref="
    resp, err = fetch(session, url, headers={"Referer": r.url})
    return resp, url, err


def load_manifest():
    try:
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return {p["id"]: p for p in json.load(f).get("papers", [])}
    except (OSError, ValueError):
        return {}


def save_manifest(entries):
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = {
        "generated_at": now(),
        "tool": "download_final_papers.py",
        "policy": POLICY,
        "corpus": {"included": sum(1 for p in PAPERS if p["role"] == "included"),
                   "excluded_fulltext": sum(1 for p in PAPERS if p["role"] == "excluded_fulltext")},
        "papers": [entries[p["id"]] for p in PAPERS if p["id"] in entries],
    }
    tmp = MANIFEST_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    os.replace(tmp, MANIFEST_PATH)


def base_entry(p):
    return {
        "id": p["id"], "raw_id": p["raw"], "role": p["role"], "title": p["title"],
        "doi": p["doi"], "record_url": p.get("record") or (f"https://doi.org/{p['doi']}" if p["doi"] else None),
        "venue": p["venue"], "file": os.path.join("final_paper", p["file"]),
        "status": "pending", "source_kind": None, "source_url": None, "version": None,
        "checked_at": now(), "attempts": [], "note": p.get("note", ""),
        "manual_hint": p.get("hint"),
    }


def process(session, p, force, verify_only, old):
    entry = base_entry(p)
    dest = os.path.join(OUT_DIR, p["file"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    # 1) berkas sudah ada (unduhan sebelumnya atau manual): validasi, pertahankan metadata lama
    if os.path.exists(dest) and not force:
        ok, info = validate_pdf(dest, p["title"])
        prev = old.get(p["id"], {})
        if ok:
            entry.update(info)
            if prev.get("status", "").startswith("ok_"):
                for k in ("status", "source_kind", "source_url", "version", "attempts"):
                    entry[k] = prev.get(k, entry[k])
                if entry["source_kind"] == "arxiv" and "[v" not in (entry["version"] or ""):
                    v = arxiv_version(dest)
                    if v:
                        entry["version"] = f"{entry['version']} [{v}]"
            else:
                entry.update(status="ok_manual", source_kind="existing_file", version="disediakan pengguna (akses institusi)")
            return entry
        entry["attempts"].append({"url": "(berkas lokal)", "result": info.get("reason")})
        os.replace(dest, dest + ".invalid")  # simpan, jangan hapus bukti
        entry["note"] = (entry["note"] + " Berkas lokal gagal validasi: " + str(info.get("reason"))).strip()

    if verify_only:
        entry["status"] = "manual_required"
        return entry

    # 2) coba kandidat sumber legal secara berurutan
    for cand in p["candidates"]:
        kind = cand["kind"]
        if kind == "ieee_oa":
            resp, url, err = fetch_ieee_oa(session, p["doi"])
        else:
            url = cand["url"]
            resp, err = fetch(session, url, headers={"Accept": "application/pdf"})
        if resp is None:
            entry["attempts"].append({"kind": kind, "url": url, "result": err})
            continue
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            f.write(resp.content)
        ok, info = validate_pdf(tmp, p["title"])
        if not ok:
            entry["attempts"].append({"kind": kind, "url": resp.url, "result": f"validasi gagal: {info.get('reason')}"})
            os.remove(tmp)
            continue
        os.replace(tmp, dest)
        version = cand["version"]
        if kind == "arxiv":
            v = arxiv_version(dest)
            if v:
                version += f" [{v}]"
        entry.update(info)
        entry.update(status=cand["status"], source_kind=kind, source_url=resp.url, version=version)
        entry["attempts"].append({"kind": kind, "url": resp.url, "result": "ok"})
        return entry

    entry["status"] = "manual_required"
    return entry


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="daftar ID dipisah koma, mis. FP-02,FP-04")
    ap.add_argument("--force", action="store_true", help="unduh ulang walau berkas sudah valid")
    ap.add_argument("--verify-only", action="store_true", help="hanya validasi berkas lokal (tanpa jaringan)")
    args = ap.parse_args()

    only = {s.strip().upper() for s in args.only.split(",")} if args.only else None
    os.makedirs(EXCL_DIR, exist_ok=True)
    old = load_manifest()
    entries = dict(old)
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    for p in PAPERS:
        if only and p["id"] not in only:
            continue
        entries[p["id"]] = process(session, p, args.force, args.verify_only, old)
        e = entries[p["id"]]
        print(f"[{p['id']}] {e['status']:<16} {e.get('pages', '-'):>3} hlm  judul={e.get('title_match', '-')}  "
              f"{e.get('source_kind') or '-'}", flush=True)
        save_manifest(entries)

    # ringkasan + panduan unduh manual
    missing = [e for e in entries.values() if e["status"] in ("manual_required", "failed")]
    ok_n = sum(1 for e in entries.values() if e["status"].startswith("ok_") and e["role"] == "included")
    print(f"\nTerunduh/valid (included): {ok_n}/15 | perlu unduh manual: {len(missing)}")
    for e in missing:
        tag = "" if e["role"] == "included" else " [opsional, dieksklusi]"
        print(f"  - {e['id']}{tag}: {e.get('manual_hint') or 'unduh manual'} | {e['record_url']} -> simpan sebagai {e['file']}")
    if missing:
        print("Setelah menaruh berkas, jalankan: python3 download_final_papers.py --verify-only")


if __name__ == "__main__":
    sys.exit(main())
