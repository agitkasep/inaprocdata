import os
import json
import time
import requests
import re
from pathlib import Path

# SETUP LOKASI
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data_Lembaga"
DATA_DIR.mkdir(exist_ok=True)

LEMBAGA_MAP = {
    "L112": "BADAN GIZI NASIONAL", "L1": "ARSIP NASIONAL REPUBLIK INDONESIA",
    "L6": "BADAN INFORMASI GEOSPASIAL", "L2": "BADAN INTELIJEN NEGARA",
    "L106": "BADAN KARANTINA INDONESIA", "L58": "BADAN KEAMANAN LAUT",
    "L3": "BADAN KEPEGAWAIAN NEGARA", "L7": "BADAN METEOROLOGI, KLIMATOLOGI DAN GEOFISIKA",
    "L8": "BADAN NARKOTIKA NASIONAL", "L9": "BADAN NASIONAL PENANGGULANGAN BENCANA",
    "L10": "BADAN NASIONAL PENANGGULANGAN TERORISME", "L100": "BADAN NASIONAL PENCARIAN DAN PERTOLONGAN",
    "L12": "BADAN NASIONAL PENGELOLA PERBATASAN", "L114": "BADAN OTORITA PENGELOLA PANTAI UTARA JAWA",
    "L104": "BADAN PANGAN NASIONAL", "L101": "BADAN PEMBINAAN IDEOLOGI PANCASILA",
    "L13": "BADAN PEMERIKSA KEUANGAN", "L17": "BADAN PENGAWASAN KEUANGAN DAN PEMBANGUNAN",
    "L15": "BADAN PENGAWAS OBAT DAN MAKANAN", "L57": "BADAN PENGAWAS PEMILIHAN UMUM",
    "L16": "BADAN PENGAWAS TENAGA NUKLIR", "I81": "BADAN PENGUSAHAAN KAWASAN BATAM",
    "I100": "BADAN PENGUSAHAAN KAWASAN BATAM 984423", "I82": "BADAN PENGUSAHAAN KAWASAN SABANG",
    "L110": "BADAN PENYELENGGARA JAMINAN PRODUK HALAL", "L21": "BADAN PUSAT STATISTIK",
    "L103": "BADAN RISET DAN INOVASI NASIONAL", "L39": "BADAN SIBER DAN SANDI NEGARA",
    "L23": "BADAN STANDARDISASI NASIONAL", "L27": "DEWAN PERWAKILAN DAERAH",
    "L28": "DEWAN PERWAKILAN RAKYAT", "L46": "KEJAKSAAN REPUBLIK INDONESIA",
    "L47": "KEPOLISIAN NEGARA REPUBLIK INDONESIA", "L29": "KOMISI NASIONAL HAK ASASI MANUSIA",
    "L30": "KOMISI PEMBERANTASAN KORUPSI", "L31": "KOMISI PEMILIHAN UMUM",
    "L32": "KOMISI PENGAWAS PERSAINGAN USAHA", "L33": "KOMISI YUDISIAL RI",
    "L34": "LEMBAGA ADMINISTRASI NEGARA", "L36": "LEMBAGA KEBIJAKAN PENGADAAN BARANG/JASA",
    "L37": "LEMBAGA KETAHANAN NASIONAL", "L51": "LPP TELEVISI REPUBLIK INDONESIA",
    "L52": "LPP RADIO REPUBLIK INDONESIA", "L102": "LEMBAGA PERLINDUNGAN SAKSI DAN KORBAN",
    "L40": "MAHKAMAH AGUNG", "L41": "MAHKAMAH KONSTITUSI RI", "L42": "MAJELIS PERMUSYAWARATAN RAKYAT",
    "L43": "OMBUDSMAN REPUBLIK INDONESIA", "L105": "OTORITA IBU KOTA NUSANTARA (OIKN)",
    "L44": "PERPUSTAKAAN NASIONAL REPUBLIK INDONESIA", "L45": "PPATK", "L56": "SEKRETARIAT KABINET"
}

def ekstrak_rows_dari_html(html_text):
    matches = [m.start() for m in re.finditer(r'\\?"tableRows\\?"', html_text)]
    for idx in matches:
        start_idx = html_text.find('[', idx)
        if start_idx == -1: continue
        bracket_count, in_quotes, escape_char = 0, False, False
        for i in range(start_idx, len(html_text)):
            char = html_text[i]
            if escape_char: escape_char = False; continue
            if char == '\\': escape_char = True; continue
            if char == '"': in_quotes = not in_quotes; continue
            if not in_quotes:
                if char == '[': bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        raw_json = html_text[start_idx:i+1]
                        try:
                            if '\\"' in raw_json: raw_json = raw_json.replace('\\"', '"').replace('\\\\', '\\')
                            return json.loads(raw_json)
                        except: pass
                        break
    return []

def validasi_file(file_path):
    if not file_path.exists(): return False
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return len(data) > 0
    except: return False

def sedot_per_lembaga(kode, nama):
    output_file = DATA_DIR / f"{kode}.json"
    if validasi_file(output_file):
        print(f"⏩ Lewati: {nama} (Data valid)")
        return

    print(f"🚀 Sedang menyedot: {nama} ({kode})")
    all_rows, offset, halaman = [], 0, 1
    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        url = f"https://data.inaproc.id/realisasi?tahun=2026&jenis_klpd=2&instansi={kode}&offset={offset}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            rows = ekstrak_rows_dari_html(response.text)
            if not rows: break
            all_rows.extend(rows)
            print(f"   -> Halaman {halaman}: {len(rows)} baris")
            offset += 20; halaman += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"   -> Error: {e}"); break

    if all_rows:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"💾 Sukses tersimpan.")

def main():
    print("=== MESIN SEDOT LEMBAGA V4 (SELF-HEALING) ===")
    for kode, nama in LEMBAGA_MAP.items():
        sedot_per_lembaga(kode, nama)
    
    print("\n🔍 Final Check & Validasi...")
    for kode, nama in LEMBAGA_MAP.items():
        if not validasi_file(DATA_DIR / f"{kode}.json"):
            print(f"⚠️ Memperbaiki: {nama}...")
            sedot_per_lembaga(kode, nama)
    print("\n=== SELESAI ===")

if __name__ == "__main__":
    main()