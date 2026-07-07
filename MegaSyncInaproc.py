import os
import time
import random
import math
import re
import json
import glob
import shutil
import threading
import tempfile
from queue import Queue
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Pengunci Thread-Safe global untuk sinkronisasi data antar Agen Robot
counter_lock = threading.Lock()
instansi_sukses_set = set()       # Menyimpan tuple (klpd_id, kode_instansi) yang lolos audit download 100%
target_per_instansi_live = {}     # Menyimpan target baris live per instansi untuk kalkulasi granular

def extract_mapping_from_js(js_file_path):
    """Membaca data array instansi secara lokal dari berkas JavaScript Mapping"""
    try:
        if not os.path.exists(js_file_path):
            print(f"   ⚠️ Berkas mapping tidak ditemukan di jalur: {js_file_path}")
            return []
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'=\s*(\[[\s\S]*?\]);?', content)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        print(f"   ❌ Gagal mengekstrak JSON dari file {os.path.basename(js_file_path)}: {e}")
    return []

def scan_live_jumlah_paket(driver, timeout=3.0):
    """Membaca text UI pada browser secara dinamis (Smart Wait) untuk acuan validasi resmi"""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
            match = re.search(r"Jumlah Paket\s*\n*\s*([\d\.]+)", body_text)
            if match:
                return int(match.group(1).replace(".", ""))
        except:
            pass
        time.sleep(0.2)
    return 0

def wait_and_rename_download(download_dir, new_filename, timeout=60):
    """Deteksi Pintar Real-Time Berkas Masuk Dengan Batas Tunggu Aman 60 Detik"""
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        crdownloads = glob.glob(os.path.join(download_dir, "*.crdownload"))
        csv_files = glob.glob(os.path.join(download_dir, "data_realisasi_*.csv"))
        
        if csv_files and not crdownloads:
            latest_file = max(csv_files, key=os.path.getctime)
            try:
                size_1 = os.path.getsize(latest_file)
                time.sleep(0.6)
                size_2 = os.path.getsize(latest_file)
                
                if size_1 == size_2 and size_2 > 0:
                    new_file_path = os.path.join(download_dir, new_filename)
                    if os.path.exists(new_file_path):
                        os.remove(new_file_path)
                    os.rename(latest_file, new_file_path)
                    return True
            except:
                pass
        time.sleep(0.5)
    return False

def sweep_remaining_files(download_dir, correct_filename):
    """Sweeper penyelamat berkas tersisa di folder isolasi agen"""
    time.sleep(0.5)
    remnants = glob.glob(os.path.join(download_dir, "data_realisasi_*.csv"))
    if remnants:
        try:
            new_file_path = os.path.join(download_dir, correct_filename)
            if os.path.exists(new_file_path):
                os.remove(new_file_path)
            os.rename(remnants[0], new_file_path)
        except:
            pass

def jalankan_worker_pengeroyok(worker_name, task_queue, tahun, FOLDER_TEMPORARY, MAX_RETRIES):
    """
    Sistem Pengeroyokan Multi-Thread Berbasis Agen Cerdas (Dynamic Load Balancing).
    Folder unduhan terisolasi rapi di OS Temp agar workspace Anda bersih total.
    """
    print(f"🚀 [{worker_name}] Resmi Aktif dan Bersiap Menyedot Berkas...")
    
    download_dir_worker = tempfile.mkdtemp(prefix=f"inaproc_{worker_name.split('/')[0].lower()}_")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow", "downloadPath": download_dir_worker
    })

    try:
        while not task_queue.empty():
            try:
                task = task_queue.get_nowait()
            except:
                break
                
            klpd_id = task["klpd_id"]
            kode_instansi = task["kode"]
            nama_daerah = task["nama"]
            index_daerah = task["index"]
            total_daerah = task["total_in_klpd"]
            
            format_nama_baru = f"klpd{klpd_id}instansi{kode_instansi}.csv"
            url_target = f"https://data.inaproc.id/realisasi?tahun={tahun}&jenis_klpd={klpd_id}&instansi={kode_instansi}"
            
            print(f"🔍 [{worker_name}] Memindai Halaman -> KLPD {klpd_id} [{index_daerah}/{total_daerah}] {nama_daerah}...")
            
            navigasi_instansi_sukses = False
            target_instansi = 0
            
            for nav_attempt in range(1, 5):
                try:
                    driver.get(url_target)
                    time.sleep(random.uniform(2.5, 3.5))
                    target_instansi = scan_live_jumlah_paket(driver, timeout=5.0)
                    navigasi_instansi_sukses = True
                    break
                except Exception:
                    time.sleep(nav_attempt * 4)
            
            if not navigasi_instansi_sukses:
                print(f"   ❌ [{worker_name}] Jaringan Terputus Saat Mengakses {nama_daerah}.")
                task_queue.task_done()
                continue

            tombol_eksis = False
            try:
                tombol_check = driver.find_elements(By.XPATH, "//*[contains(text(), 'Download CSV')]")
                if len(tombol_check) > 0:
                    tombol_eksis = True
            except:
                pass

            if not tombol_eksis:
                if target_instansi == 0:
                    print(f"   ⏭️  [{worker_name}] [Kosong Valid] -> {nama_daerah} terkonfirmasi 0 Paket.")
                    with counter_lock:
                        instansi_sukses_set.add((klpd_id, kode_instansi))
                        target_per_instansi_live[(klpd_id, kode_instansi)] = 0
                else:
                    print(f"   ⚠️  [{worker_name}] [Tombol Lag] Halaman {nama_daerah} gagal muat tombol, dilempar ke putaran recovery.")
                task_queue.task_done()
                continue

            download_sukses = False
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    tombol = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Download CSV')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tombol)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", tombol)
                    
                    if wait_and_rename_download(download_dir_worker, format_nama_baru, timeout=60):
                        download_sukses = True
                        break
                except Exception:
                    pass
                
                sweep_remaining_files(download_dir_worker, format_nama_baru)
                time.sleep(random.uniform(1.2, 2.0))
            
            if download_sukses:
                path_sumber_worker = os.path.join(download_dir_worker, format_nama_baru)
                folder_tujuan_rumpun = os.path.join(FOLDER_TEMPORARY, f"klpd{klpd_id}")
                os.makedirs(folder_tujuan_rumpun, exist_ok=True)
                path_tujuan_final = os.path.join(folder_tujuan_rumpun, format_nama_baru)
                
                try:
                    shutil.move(path_sumber_worker, path_tujuan_final)
                    df_temp = pd.read_csv(path_tujuan_final)
                    baris_lokal = len(df_temp)
                    
                    if target_instansi == 0 and baris_lokal > 0:
                        target_instansi = baris_lokal
                        
                    if baris_lokal == target_instansi:
                        print(f"      ✅ [{worker_name}] [Granular Download Match] Berhasil Amankan {baris_lokal:,} Baris Untuk {nama_daerah}.")
                        with counter_lock:
                            instansi_sukses_set.add((klpd_id, kode_instansi))
                            target_per_instansi_live[(klpd_id, kode_instansi)] = target_instansi
                    else:
                        print(f"      ❌ [{worker_name}] [DOWNLOAD TIDAK AKURAT] Target Web: {target_instansi} | File Didapat: {baris_lokal}. Berkas Dihapus!")
                        if os.path.exists(path_tujuan_final):
                            os.remove(path_tujuan_final)
                except Exception as file_err:
                    print(f"      ⚠️ [{worker_name}] Gagal membaca berkas audit download {kode_instansi}: {file_err}")
                    if os.path.exists(path_tujuan_final):
                        os.remove(path_tujuan_final)
            else:
                print(f"   ❌ [{worker_name}] [CRITICAL TIMEOUT] {nama_daerah} gagal diunduh dalam 60 detik.")
                    
            task_queue.task_done()
            time.sleep(random.uniform(0.1, 0.2))
            
    finally:
        driver.quit()
        if os.path.exists(download_dir_worker):
            shutil.rmtree(download_dir_worker)

def run_mega_pipeline_staging_paralel():
    target_klpd = [
        {"id": 1, "nama": "Kementerian (KLPD 1)", "target_count": 50},
        {"id": 2, "nama": "Lembaga (KLPD 2)", "target_count": 52},
        {"id": 3, "nama": "Provinsi (KLPD 3)", "target_count": 38},
        {"id": 4, "nama": "Kabupaten (KLPD 4)", "target_count": 416},
        {"id": 5, "nama": "Kota (KLPD 5)", "target_count": 93}
    ]
    
    tahun = "2026"
    MAX_RETRIES = 3
    FOLDER_UTAMA = "filecsv"
    FOLDER_TEMPORARY = "filecsv_temp"

    if os.path.exists(FOLDER_TEMPORARY):
        shutil.rmtree(FOLDER_TEMPORARY)
    os.makedirs(FOLDER_TEMPORARY, exist_ok=True)

    options_main = webdriver.ChromeOptions()
    options_main.add_argument("--headless=new")
    options_main.add_argument("--window-size=1920,1080")
    options_main.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options_main.add_argument("--disable-blink-features=AutomationControlled")
    options_main.experimental_options["excludeSwitches"] = ["enable-automation"]
    options_main.experimental_options['useAutomationExtension'] = False

    driver_main = webdriver.Chrome(options=options_main)
    driver_main.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        # ====================================================================
        # TAHAP 1: MEREKAM JANGKAR ACUAN GLOBAL NASIONAL
        # ====================================================================
        print("============================================================")
        print("TAHAP 1: MEMBACA DAN MEREKAM MASTER CHECKSUM WEB PUSAT")
        print("============================================================")
        url_master = f"https://data.inaproc.id/realisasi?tahun={tahun}"
        
        angka_validasi_web_sumber = 0
        for master_attempt in range(1, 6):
            try:
                print(f"🔗 Menghubungkan ke gerbang utama (Mencoba akses ke-{master_attempt}/5)...")
                driver_main.get(url_master)
                angka_validasi_web_sumber = scan_live_jumlah_paket(driver_main, timeout=6.0)
                if angka_validasi_web_sumber > 0:
                    break
            except Exception as conn_err:
                print(f"   ⚠️ Gangguan sinyal pada gerbang utama: {conn_err}")
            time.sleep(master_attempt * 5)

        if angka_validasi_web_sumber == 0:
            print("❌ [FATAL] Gagal merekam acuan nasional. Sistem dihentikan.")
            driver_main.quit()
            return
            
        print(f"🎯 ANGKA JANGKAR NASIONAL HARI INI: {angka_validasi_web_sumber:,} Paket (Baris)\n")

        # ====================================================================
        # TAHAP 2: MEREKAM PATOKAN SUB-TARGET PER RUMPUN KLPD DI AWAL PROSES
        # ====================================================================
        print("============================================================")
        print("TAHAP 2: MEREKAM PATOKAN TARGET MASING-MASING RUMPUN KLPD")
        print("============================================================")
        
        target_klpd_terekam = {}
        for kat in target_klpd:
            klpd_id = kat["id"]
            nama_rumpun = kat["nama"]
            url_rumpun = f"https://data.inaproc.id/realisasi?tahun={tahun}&jenis_klpd={klpd_id}"
            
            target_rumpun = 0
            for rumpun_attempt in range(1, 5):
                try:
                    driver_main.get(url_rumpun)
                    target_rumpun = scan_live_jumlah_paket(driver_main, timeout=5.0)
                    if target_rumpun > 0:
                        break
                except:
                    pass
                time.sleep(2)
            
            target_klpd_terekam[klpd_id] = target_rumpun
            print(f"🎯 Patokan Web Target Resmi [{nama_rumpun}] -> {target_rumpun:,} Paket.")
            
        driver_main.quit()

        # ====================================================================
        # TAHAP 3: RECOVERY PENGEROYOKAN BERULANG UNTUK FASE DOWNLOAD LOKAL
        # ====================================================================
        nama_robot_crew = [
            "Robot-Alpha/Stealth-01", 
            "Robot-Beta/Stealth-02", 
            "Robot-Gamma/Stealth-03", 
            "Robot-Delta/Stealth-04", 
            "Robot-Epsilon/Stealth-05"
        ]
        
        MAX_MACRO_ATTEMPTS = 5
        download_fase_valid = False

        for putaran_makro in range(1, MAX_MACRO_ATTEMPTS + 1):
            print(f"\n" + "="*70)
            print(f"🔄 FASE DOWNLOAD: PUTARAN KOREKSI LOKAL #{putaran_makro}")
            print("="*70)
            
            antrean_global = Queue()
            tugas_terkumpul = 0
            
            for kat in target_klpd:
                klpd_id = kat["id"]
                path_mapping = os.path.join("maping", f"klpd{klpd_id}.js")
                daftar_instansi = extract_mapping_from_js(path_mapping)
                
                for index, item in enumerate(daftar_instansi, start=1):
                    kode_ins = item.get("kode")
                    if (klpd_id, kode_ins) not in instansi_sukses_set:
                        task_data = {
                            "klpd_id": klpd_id,
                            "kode": kode_ins,
                            "nama": item.get("nama", "Tidak Diketahui"),
                            "index": index,
                            "total_in_klpd": len(daftar_instansi)
                        }
                        antrean_global.put(task_data)
                        tugas_terkumpul += 1
            
            if tugas_terkumpul == 0:
                print("🎯 [Info Audit] Seluruh manifest file CSV telah sukses terunduh Akurat 100%!")
                download_fase_valid = True
                break
            else:
                print(f"📊 Terdeteksi {tugas_terkumpul} file belum akurat/terlewat. Menugaskan Kru Robot...")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for nama_bot in nama_robot_crew:
                        executor.submit(
                            jalankan_worker_pengeroyok, 
                            nama_bot, antrean_global, tahun, FOLDER_TEMPORARY, MAX_RETRIES
                        )
                antrean_global.join()
            
            total_baris_csv_lokal = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for k_id in [1, 2, 3, 4, 5]:
                folder_upload = os.path.join(FOLDER_TEMPORARY, f"klpd{k_id}")
                if os.path.exists(folder_upload):
                    daftar_file_upload = glob.glob(os.path.join(folder_upload, "*.csv"))
                    for path_csv in daftar_file_upload:
                        try:
                            df_audit = pd.read_csv(path_csv)
                            total_baris_csv_lokal[k_id] += len(df_audit)
                        except:
                            pass

            semua_rumpun_match = True
            print("\n📊 LAPORAN CEK AKURASI FILE CSV LOKAL SEMENTARA:")
            for k_id in [1, 2, 3, 4, 5]:
                target_web = target_klpd_terekam.get(k_id, 0)
                terkumpul_lokal = total_baris_csv_lokal.get(k_id, 0)
                
                if target_web == terkumpul_lokal:
                    status_rumpun = "✅ MATCH LOKAL"
                else:
                    status_rumpun = f"❌ MISMATCH LOKAL (Selisih: {abs(target_web - terkumpul_lokal):,} Baris)"
                    semua_rumpun_match = False
                    
                print(f"   - KLPD {k_id} -> Target Web Pusat: {target_web:,} | Terkumpul Lokal: {terkumpul_lokal:,} | {status_rumpun}")
            
            total_lokal_global = sum(total_baris_csv_lokal.values())
            print("-" * 70)
            print(f"📈 TOTAL SELURUH BARIS DATA LOKAL    : {total_lokal_global:,} Baris")
            print(f"📉 ACUAN JANGKAR TARGET WEB PUSAT    : {angka_validasi_web_sumber:,} Paket")
            print("-" * 70)
            
            if total_lokal_global == angka_validasi_web_sumber and semua_rumpun_match:
                download_fase_valid = True
                print("🚀 [DOWNLOAD SUCCESS] File lokal dikonfirmasi telah 100% Akurat Mutlak!")
                break
            else:
                print(f"⚠️  [DOWNLOAD BELUM AKURAT] Target belum terpenuhi pada putaran #{putaran_makro}. Berputar kembali...")
                time.sleep(3)

        if not download_fase_valid:
            print("\n❌ [FATAL ABORT] Proses dihentikan total karena fase download lokal gagal mencapai akurasi 100%.")
            return

        # ====================================================================
        # TAHAP 4 (FINAL): AKTIFKAN PARKIRAN FILE WEB RESMI!
        # ====================================================================
        print("\n" + "="*70)
        print("TAHAP 4: AKTIVASI FOLDER RESMI PARKIRAN WEB ('filecsv')")
        print("="*70)
        print("👉 Mengganti folder resmi dengan data tervalidasi dari temporary...")
        if os.path.exists(FOLDER_UTAMA):
            shutil.rmtree(FOLDER_UTAMA)
        os.rename(FOLDER_TEMPORARY, FOLDER_UTAMA)
        
        print("\n" + "="*70)
        print("🎉 STATUS FINAL: === SELURUH DATA CSV LOKAL VALID & SIAP UPLOAD KE GITHUB ===")
        print("Folder 'filecsv' beserta seluruh isinya kini siap di-push ke repository.")
        print("============================================================\n")

    except Exception as mega_err:
        print(f"\n[Fatal Error Sistem]: {mega_err}")

if __name__ == "__main__":
    run_mega_pipeline_staging_paralel()