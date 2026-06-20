import os
import json
import re
import time
import requests
from pathlib import Path

# Setup lokasi penyimpanan data hasil sedotan
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_LOKAL_DIR = BASE_DIR / "Data_Lokal"
DATA_LOKAL_DIR.mkdir(exist_ok=True)

# Peta Induk 50 Kementerian
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

def ekstrak_rows_dari_html(html_text):
    """Tokenize pintar untuk memotong array tableRows secara presisi dan kebal badai teks"""
    # Cari semua posisi kemunculan kata tableRows di dalam HTML
    matches = [m.start() for m in re.finditer(r'\\?"tableRows\\?"', html_text)]
    
    for idx in matches:
        start_idx = html_text.find('[', idx)
        if start_idx == -1:
            continue
            
        bracket_count = 0
        in_quotes = False
        escape_char = False
        
        # Menyisir karakter demi karakter untuk menemukan penutup array asli
        for i in range(start_idx, len(html_text)):
            char = html_text[i]
            
            if escape_char:
                escape_char = False
                continue
            if char == '\\':
                escape_char = True
                continue
            if char == '"':
                in_quotes = not in_quotes
                continue
                
            if not in_quotes:
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        raw_json = html_text[start_idx:i+1]
                        try:
                            # Konversi format string eskaping Next.js ke JSON standar
                            if '\\"' in raw_json:
                                raw_json = raw_json.replace('\\"', '"').replace('\\\\', '\\')
                            data = json.loads(raw_json)
                            if data:  # Jika array berhasil di-parse dan ada isinya
                                return data
                        except:
                            pass
                        break  # Keluar dari loop internal jika gagal parse, coba posisi berikutnya
    return []

def sedot_per_kementerian(kode, nama):
    print(f"\n🚀 Mulai menyedot: {nama} ({kode})")
    all_rows = []
    offset = 0
    halaman = 1
    
    # User-Agent bersih layaknya browser publik biasa
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    while True:
        # Menembak URL publik tanpa menggunakan header gerbang RSC
        url = f"https://data.inaproc.id/realisasi?tahun=2026&jenis_klpd=1&instansi={kode}&offset={offset}"
        print(f"   -> Menarik Halaman {halaman} (Offset: {offset})...", end="", flush=True)
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f" ERROR [Status {response.status_code}]")
                break
                
            rows = ekstrak_rows_dari_html(response.text)
            
            if not rows:
                print(" KOSONG / SELESAI (Data habis atau mencapai ujung halaman)")
                break
                
            all_rows.extend(rows)
            print(f" Berhasil mendapat {len(rows)} baris.")
            
            # Geser offset kelipatan 20 baris
            offset += 20
            halaman += 1
            
            # Jeda napas aman 1 detik demi stabilitas koneksi Cloudflare Anda
            time.sleep(1.0)
            
        except Exception as e:
            print(f" GAGAL Jaringan: {e}")
            break

    # Kunci hasil ke Data_Lokal
    if all_rows:
        output_file = DATA_LOKAL_DIR / f"{kode}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_rows, f, indent=2, ensure_ascii=False)
        print(f"💾 SUKSES! {len(all_rows)} data disimpan di Data_Lokal/{kode}.json")
    else:
        print(f"⚠️ Tidak ada data yang berhasil diamankan untuk {nama}")

def main():
    print("=== MESIN API REVOLUSI V2 INAPROC_DATA DIMULAI ===")
    start_time = time.time()
    
    for kode, nama in KEMENTERIAN_MAP.items():
        sedot_per_kementerian(kode, nama)
        time.sleep(2.0)  # Jeda aman antar instansi
        
    duration = time.time() - start_time
    print(f"\n=== PROSES SELESAI TOTAL DALAM {duration:.2f} DETIK ===")

if __name__ == "__main__":
    main()