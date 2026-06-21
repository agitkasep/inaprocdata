import json
import time
import requests
import re
from pathlib import Path

# --- SETUP ---
# Menggunakan path absolut S:/INAPROC_DATA/Data_Lembaga
BASE_DIR = Path("S:/INAPROC_DATA")
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
    """Logika identik dengan script kementerian Anda"""
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
                            data = json.loads(raw_json)
                            if data: return data
                        except: pass
                        break
    return []

def sedot_per_lembaga(kode, nama):
    output_file = DATA_DIR / f"{kode}.json"
    print(f"\n🚀 Mulai menyedot: {nama} ({kode})")
    all_rows, offset, halaman = [], 0, 1
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    while True:
        url = f"https://data.inaproc.id/realisasi?tahun=2026&jenis_klpd=2&instansi={kode}&offset={offset}"
        print(f"   -> Menarik Halaman {halaman} (Offset: {offset})...", end="", flush=True)
        try:
            response = requests.get(url, headers=headers, timeout=15)
            rows = ekstrak_rows_dari_html(response.text)
            if not rows:
                print(" KOSONG / SELESAI")
                break
            all_rows.extend(rows)
            print(f" Berhasil mendapat {len(rows)} baris.")
            offset += 20; halaman += 1
            time.sleep(1.0)
        except Exception as e:
            print(f" GAGAL: {e}")
            break

    if all_rows:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"💾 SUKSES! {len(all_rows)} data disimpan.")

def main():
    print("=== MESIN API REVOLUSI LEMBAGA DIMULAI ===")
    start_time = time.time()
    for kode, nama in LEMBAGA_MAP.items():
        sedot_per_lembaga(kode, nama)
        time.sleep(2.0)
    print(f"\n=== PROSES SELESAI DALAM {time.time() - start_time:.2f} DETIK ===")

if __name__ == "__main__":
    main()