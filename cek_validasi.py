import json
from pathlib import Path

DATA_DIR = Path("S:/INAPROC_DATA/Data_Lembaga")

def cek_semua():
    print("=== MONITORING KESEHATAN DATA ===")
    eror_list = []
    
    # Ambil semua file json di folder
    files = list(DATA_DIR.glob("*.json"))
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not data or len(data) == 0:
                    print(f"❌ KOSONG: {file_path.name}")
                    eror_list.append(file_path.name.replace('.json', ''))
                else:
                    # Optional: Print jika ingin melihat detail jumlah data
                    # print(f"✅ OK: {file_path.name} ({len(data)} baris)")
                    pass
        except Exception as e:
            print(f"❌ RUSAK: {file_path.name} -> {e}")
            eror_list.append(file_path.name.replace('.json', ''))
    
    print("\n=== HASIL PEMERIKSAAN ===")
    if eror_list:
        print(f"Ditemukan {len(eror_list)} file bermasalah.")
        print("Kode yang harus disedot ulang:", ", ".join(eror_list))
    else:
        print("Semua data SEHAT!")

if __name__ == "__main__":
    cek_semua()