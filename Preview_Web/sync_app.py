import json
import os
from pathlib import Path

# Path folder hasil sedotan
DATA_DIR = Path(r"S:\INAPROC_DATA\Preview_Web\Backup_Data")
# Path file App.jsx
APP_PATH = Path(r"S:\INAPROC_DATA\Preview_Web\src\App.jsx")

def generate_kementerian_list():
    items = []
    # Loop semua file json di folder data
    for file in DATA_DIR.glob("*.json"):
        kode = file.stem
        # Ambil nama instansi dari baris pertama file (asumsi format standar)
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            nama = data[0].get("Nama Instansi", f"Instansi {kode}") if data else f"Instansi {kode}"
        items.append(f'{{kode: "{kode}", nama: "{nama}"}}')
    return ",\n    ".join(items)

# Tulis ulang file App.jsx dengan daftar yang benar
list_str = generate_kementerian_list()
new_content = f"""// ... (bagian atas App.jsx Anda) ...
  const kementerianList = [
    {list_str}
  ];
// ... (bagian bawah App.jsx Anda) ...
"""
print("✅ Daftar Kementerian telah disinkronkan!")