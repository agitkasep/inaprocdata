import os
import json
from pathlib import Path

# Setup lokasi folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_LOKAL_DIR = BASE_DIR / "Data_Lokal"

# Peta Induk 50 Kementerian untuk cross-check
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

def audit_data():
    print("\n========================================================")
    print("        📊 LAPORAN AUDIT HASIL SEDOT KEMENTERIAN        ")
    print("========================================================")
    
    belum_kesedot = []
    sudah_kesedot = 0
    total_baris_keseluruhan = 0
    
    for kode, nama in KEMENTERIAN_MAP.items():
        file_path = DATA_LOKAL_DIR / f"{kode}.json"
        
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    jumlah_baris = len(data)
                    total_baris_keseluruhan += jumlah_baris
                    sudah_kesedot += 1
                    print(f"✅ [{kode}] {nama:<65} -> Terisi ({jumlah_baris} Paket)")
            except Exception:
                print(f"❌ [{kode}] {nama:<65} -> File Rusak/Gagal Dibaca")
                belum_kesedot.append((kode, nama))
        else:
            print(f"🚨 [{kode}] {nama:<65} -> BELUM KESEDOT (KOSONG)")
            belum_kesedot.append((kode, nama))
            
    print("\n=================== KESIMPULAN AUDIT ===================")
    print(f"🔹 Total Instansi Terdaftar  : {len(KEMENTERIAN_MAP)} Kementerian")
    print(f"🔹 Berhasil Disedot          : {sudah_kesedot} Instansi")
    print(f"🔹 Gagal / Belum Disedot     : {len(belum_kesedot)} Instansi")
    print(f"🔹 Total Data Paket Tersimpan: {total_baris_keseluruhan:,} Baris Paket RUP")
    print("========================================================")
    
    if belum_kesedot:
        print("\n📌 DAFTAR KEMENTERIAN YANG HARUS DISEDOT ULANG:")
        for idx, (k, n) in enumerate(belum_kesedot, 1):
            print(f"  {idx}. Kode: {k} -> {n}")
    else:
        print("\n🎉 MANTAP! Semua kementerian sudah 100% tersedot sempurna tanpa ada yang tertinggal!")
    print("========================================================\n")

if __name__ == "__main__":
    audit_data()