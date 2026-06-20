import os
import json
import re
import time
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_LOKAL_DIR = BASE_DIR / "Data_Lokal"
DATA_LOKAL_DIR.mkdir(exist_ok=True)

KEMENTERIAN_MAP = {
    "K1": "KEMENTERIAN AGAMA", "K2": "KEMENTERIAN BADAN USAHA MILIK NEGARA",
    "K3": "KEMENTERIAN DALAM NEGERI", "K4": "KEMENTERIAN ENERGI DAN SUMBER DAYA MINERAL",
    "K8": "KEMENTERIAN KELAUTAN DAN PERIKANAN", "K9": "KEMENTERIAN KESEHATAN",
    "K10": "KEMENTERIAN KEUANGAN", "K13": "KEMENTERIAN KOORDINATOR BIDANG PEREKONOMIAN",
    "K17": "KEMENTERIAN LUAR NEGERI", "K20": "KEMENTERIAN PEMBERDAYAAN PEREMPUAN DAN PERLINDUNGAN ANAK",
    "K21": "KEMENTERIAN PEMUDA DAN OLAH RAGA", "K22": "KEMENTERIAN PENDAYAGUNAAN APARATUR NEGARA DAN REFORMASI BIROKRASI",
    "K24": "KEMENTERIAN PERDAGANGAN", "K25": "KEMENTERIAN PERENCANAAN PEMBANGUNAN NASIONAL",
    "K26": "KEMENTERIAN PERHUBUNGAN", "K27": "KEMENTERIAN PERINDUSTRIAN",
    "K28": "KEMENTERIAN PERTAHANAN", "K29": "KEMENTERIAN PERTANIAN",
    "K32": "KEMENTERIAN SEKRETARIAT NEGARA", "K33": "KEMENTERIAN SOSIAL",
    "K34": "KEMENTERIAN KETENAGAKERJAAN", "K35": "KEMENTERIAN PARIWISATA",
    "K38": "KEMENTERIAN AGRARIA DAN TATA RUANG/BPN", "K41": "KEMENTERIAN KOORDINATOR BIDANG PEMBANGUNAN MANUSIA DAN KEBUDAYAAN",
    "K48": "KEMENTERIAN KOPERASI", "K49": "KEMENTERIAN USAHA MIKRO, KECIL, DAN MENENGAH",
    "K50": "KEMENTERIAN KOORDINATOR BIDANG POLITIK DAN KEAMANAN", "K51": "KEMENTERIAN KOORDINATOR BIDANG HUKUM, HAK ASASI MANUSIA, IMIGRASI, DAN PEMASYARAKATAN",
    "K52": "KEMENTERIAN KOORDINATOR BIDANG INFRASTRUKTUR DAN PEMBANGUNAN KEWILAYAHAN", "K53": "KEMENTERIAN KOORDINATOR BIDANG PEMBERDAYAAN MASYARAKAT",
    "K54": "KEMENTERIAN KOORDINATOR BIDANG PANGAN", "K55": "KEMENTERIAN HUKUM",
    "K56": "KEMENTERIAN HAK ASASI MANUSIA", "K57": "KEMENTERIAN IMIGRASI DAN PEMASYARAKATAN",
    "K58": "KEMENTERIAN PENDIDIKAN DASAR DAN MENENGAH", "K59": "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI",
    "K60": "KEMENTERIAN KEBUDAYAAN", "K61": "KEMENTERIAN PELINDUNGAN PEKERJA MIGRAN INDONESIA/BPPMI",
    "K62": "KEMENTERIAN PERUMAHAN DAN KAWASAN PERMUKIMAN", "K63": "KEMENTERIAN DESA DAN PEMBANGUNAN DAERAH TERTINGGAL",
    "K64": "KEMENTERIAN TRANSMIGRASI", "K65": "KEMENTERIAN KOMUNIKASI DAN DIGITAL",
    "K66": "KEMENTERIAN KEPENDUDUKAN DAN PEMBANGUNAN KELUARGA/BKKBN", "K67": "KEMENTERIAN INVESTASI DAN HILIRISASI/BKPM",
    "K68": "KEMENTERIAN EKONOMI KREATIF/BADAN EKONOMI KREATIF", "K69": "KEMENTERIAN LINGKUNGAN HIDUP/BADAN PENGENDALIAN LINGKUNGAN HIDUP",
    "K73": "KEMENTERIAN PEKERJAAN UMUM", "K74": "KEMENTERIAN KEHUTANAN",
    "K75": "KEMENTERIAN HAJI DAN UMRAH REPUBLIK INDONESIA", "L25": "BENDAHARA UMUM NEGARA (KEMENTERIAN KEUANGAN)"
}

def perlu_sedot(kode):
    file_path = DATA_LOKAL_DIR / f"{kode}.json"
    if not file_path.exists(): return True
    if os.path.getsize(file_path) < 100: return True # Jika file terlalu kecil (di bawah 100 bytes), dianggap gagal
    return False

def ekstrak_rows_dari_html(html_text):
    matches = [m.start() for m in re.finditer(r'\\?"tableRows\\?"', html_text)]
    for idx in matches:
        start_idx = html_text.find('[', idx)
        if start_idx == -1: continue
        bracket_count = 0; in_quotes = False; escape_char = False
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
                        try:
                            raw_json = html_text[start_idx:i+1].replace('\\"', '"').replace('\\\\', '\\')
                            return json.loads(raw_json)
                        except: pass
                        break
    return []

def main():
    print("=== MENGANALISA DATA YANG BELUM LENGKAP ===")
    antrean = [kode for kode in KEMENTERIAN_MAP if perlu_sedot(kode)]
    
    if not antrean:
        print("🎉 Semua kementerian sudah lengkap dan sehat!")
        return

    print(f"🚨 Ditemukan {len(antrean)} instansi yang perlu diperbaiki: {antrean}")
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for kode in antrean:
        print(f"\n🚀 Memperbaiki data: {KEMENTERIAN_MAP[kode]} ({kode})")
        all_rows = []; offset = 0
        while True:
            url = f"https://data.inaproc.id/realisasi?tahun=2026&jenis_klpd=1&instansi={kode}&offset={offset}"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                rows = ekstrak_rows_dari_html(response.text)
                if not rows: break
                all_rows.extend(rows)
                offset += 20
                time.sleep(0.8)
            except: break
            
        with open(DATA_LOKAL_DIR / f"{kode}.json", "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"✅ Selesai memperbarui {len(all_rows)} paket.")

if __name__ == "__main__":
    main()