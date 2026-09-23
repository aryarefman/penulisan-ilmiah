#!/usr/bin/env python3
"""
Update Excel Workbook Terbaru dengan Penambahan 73 Artikel IEEE Xplore
Menggabungkan data dari penulisan-ilmiah/csv/ieee.csv ke dalam sheet Raw_Articles
dan memperbarui statistik pencarian di sheet Search_Strategy.
"""

import zipfile
import xml.etree.ElementTree as ET
import csv
import os
import shutil
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

EXCEL_PATH = os.path.join(PROJECT_ROOT, "Terbaru_Arsitektur World Model pada Domain Video_ Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif.xlsx")
IEEE_CSV_PATH = os.path.join(BASE_DIR, "csv", "ieee.csv")

def update_workbook():
    print(f"Membuka file Excel: {EXCEL_PATH}")
    if not os.path.exists(EXCEL_PATH):
        raise FileNotFoundError(f"File tidak ditemukan: {EXCEL_PATH}")

    # 1. Baca data IEEE CSV
    with open(IEEE_CSV_PATH, "r", encoding="utf-8-sig") as f:
        ieee_records = list(csv.DictReader(f))
    print(f"Total data IEEE yang akan ditambahkan: {len(ieee_records)} artikel")

    # 2. Buka zip xlsx dan ekstrak file yang akan dimodifikasi
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(EXCEL_PATH, "r") as z:
        z.extractall(temp_dir)

    # 3. Modifikasi xl/sharedStrings.xml
    ss_path = os.path.join(temp_dir, "xl", "sharedStrings.xml")
    ss_root = ET.fromstring(open(ss_path, "r", encoding="utf-8").read())

    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ET.register_namespace("", ns)

    string_to_idx = {}
    current_idx = 0
    for si in ss_root.findall(f"{{{ns}}}si"):
        t_elem = si.find(f"{{{ns}}}t")
        txt = t_elem.text if t_elem is not None and t_elem.text else ""
        if txt not in string_to_idx:
            string_to_idx[txt] = current_idx
        current_idx += 1

    def get_or_add_str(txt):
        nonlocal current_idx
        txt = str(txt or "")
        if txt in string_to_idx:
            return string_to_idx[txt]
        new_idx = current_idx
        string_to_idx[txt] = new_idx
        si = ET.SubElement(ss_root, f"{{{ns}}}si")
        t = ET.SubElement(si, f"{{{ns}}}t")
        t.text = txt
        current_idx += 1
        return new_idx

    # 4. Modifikasi xl/worksheets/sheet5.xml (Raw_Articles)
    s5_path = os.path.join(temp_dir, "xl", "worksheets", "sheet5.xml")
    s5_root = ET.fromstring(open(s5_path, "r", encoding="utf-8").read())
    sheet_data = s5_root.find(f"{{{ns}}}sheetData")

    existing_rows = sheet_data.findall(f"{{{ns}}}row")
    start_row_num = len(existing_rows) + 1  # Baris 2741

    print(f"Menambahkan baris {start_row_num} s/d {start_row_num + len(ieee_records) - 1} ke Raw_Articles...")

    for i, rec in enumerate(ieee_records):
        row_num = start_row_num + i
        row_elem = ET.SubElement(sheet_data, f"{{{ns}}}row", {"r": str(row_num)})

        cols = [
            ("A", rec.get("Article_ID", f"IEEE-{i+1:04d}"), True),
            ("B", rec.get("Source_Type", "API"), True),
            ("C", rec.get("Database/Source", "IEEE Xplore"), True),
            ("D", "46288.0", False, "42"),  # Tanggal numeric Excel serial format
            ("E", rec.get("Search_Query", ""), True),
            ("F", rec.get("Title", ""), True),
            ("G", rec.get("Authors", ""), True),
            ("H", f"{float(rec.get('Year', 2026)):.1f}" if rec.get("Year") else "2026.0", False, "15"),
            ("I", rec.get("Journal/Conference", ""), True),
            ("J", rec.get("DOI", ""), True),
            ("K", rec.get("URL", ""), True, "44"),
            ("L", rec.get("Abstract", ""), True),
            ("M", rec.get("Document_Type", "journal-article"), True),
            ("N", rec.get("Language", "en"), True),
            ("O", rec.get("Duplicate_Key", ""), True),
            ("P", rec.get("Duplicate?", ""), True),
            ("Q", rec.get("Notes", ""), True)
        ]

        for col_def in cols:
            col_letter = col_def[0]
            val = col_def[1]
            is_str = col_def[2]
            style = col_def[3] if len(col_def) > 3 else "15"
            cell_ref = f"{col_letter}{row_num}"

            if is_str:
                str_idx = get_or_add_str(val)
                c_elem = ET.SubElement(row_elem, f"{{{ns}}}c", {"r": cell_ref, "s": style, "t": "s"})
                v_elem = ET.SubElement(c_elem, f"{{{ns}}}v")
                v_elem.text = str(str_idx)
            else:
                c_elem = ET.SubElement(row_elem, f"{{{ns}}}c", {"r": cell_ref, "s": style})
                v_elem = ET.SubElement(c_elem, f"{{{ns}}}v")
                v_elem.text = str(val)

    # Update dimension sheet5
    dim = s5_root.find(f"{{{ns}}}dimension")
    if dim is not None:
        dim.set("ref", f"A1:Q{start_row_num + len(ieee_records) - 1}")

    # Simpan kembali sheet5
    with open(s5_path, "wb") as f:
        f.write(ET.tostring(s5_root, encoding="utf-8", xml_declaration=True))

    # 5. Modifikasi xl/worksheets/sheet3.xml (Search_Strategy)
    s3_path = os.path.join(temp_dir, "xl", "worksheets", "sheet3.xml")
    s3_root = ET.fromstring(open(s3_path, "r", encoding="utf-8").read())
    s3_sheet_data = s3_root.find(f"{{{ns}}}sheetData")

    # Update baris 24 (IEEE Xplore) & baris 25 (TOTAL)
    for r in s3_sheet_data.findall(f"{{{ns}}}row"):
        r_num = r.get("r")
        if r_num == "24":  # IEEE Xplore
            for c in r.findall(f"{{{ns}}}c"):
                ref = c.get("r")
                if ref == "D24":  # Date
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = "46288.0"
                elif ref == "E24":  # Query string
                    idx = get_or_add_str("7 Kueri Terarah (Q01-Q07) via IEEE Xplore REST API (content_type: Journals)")
                    c.set("t", "s")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = str(idx)
                elif ref == "F24":  # Filters
                    idx = get_or_add_str("Tahun 2018-2026; content_type: Journals; Page-size: 25/batch")
                    c.set("t", "s")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = str(idx)
                elif ref == "G24":  # Results count
                    c.attrib.pop("t", None)
                    v = c.find(f"{{{ns}}}v")
                    if v is None: v = ET.SubElement(c, f"{{{ns}}}v")
                    v.text = "73.0"
                elif ref == "H24":  # Notes
                    idx = get_or_add_str("Dieksekusi penuh via IEEE REST API (key resmi) setelah aktivasi aktif: 73 artikel jurnal unik.")
                    c.set("t", "s")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = str(idx)
        elif r_num == "25":  # Total row
            for c in r.findall(f"{{{ns}}}c"):
                ref = c.get("r")
                if ref == "B25":
                    idx = get_or_add_str("TOTAL KESELURUHAN (8 basis data tereksekusi penuh; IEEE Xplore telah aktif & dimasukkan)")
                    c.set("t", "s")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = str(idx)
                elif ref == "G25":
                    c.attrib.pop("t", None)
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = "2812.0"
                elif ref == "H25":
                    idx = get_or_add_str("Total unik setelah deduplikasi lintas basis data (EC1): 2.697 artikel (115 duplikat dieliminasi).")
                    c.set("t", "s")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None: v.text = str(idx)

    with open(s3_path, "wb") as f:
        f.write(ET.tostring(s3_root, encoding="utf-8", xml_declaration=True))

    # Update sharedStrings root counts
    ss_root.set("count", str(current_idx))
    ss_root.set("uniqueCount", str(len(string_to_idx)))
    with open(ss_path, "wb") as f:
        f.write(ET.tostring(ss_root, encoding="utf-8", xml_declaration=True))

    # 6. Repack zip
    backup_path = EXCEL_PATH + ".bak"
    shutil.copy2(EXCEL_PATH, backup_path)
    print(f"Backup dibuat: {backup_path}")

    # Buat file xlsx baru
    new_zip_path = os.path.join(temp_dir, "updated.zip")
    with zipfile.ZipFile(new_zip_path, "w", zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == "updated.zip":
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                z_out.write(full_path, rel_path)

    shutil.move(new_zip_path, EXCEL_PATH)
    shutil.rmtree(temp_dir)
    print(f"[SUKSES] File Excel berhasil diperbarui: {EXCEL_PATH}")
    print(f"Total baris Raw_Articles sekarang: {start_row_num + len(ieee_records) - 1} baris!")

if __name__ == "__main__":
    update_workbook()
