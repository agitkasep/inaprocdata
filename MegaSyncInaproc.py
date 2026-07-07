import os
import time
import random
import re
import json
import glob
import shutil
import threading
import tempfile
import sys
from queue import Queue
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Pengunci Thread-Safe global
counter_lock = threading.Lock()
instansi_sukses_set = set()
target_per_instansi_live = {}

# ===== LOGGING UTILITY =====
def log_info(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] ℹ️  {message}")

def log_success(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] ✅ {message}")

def log_warning(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] ⚠️  {message}")

def log_error(message):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] ❌ {message}")

# ===== CHROME DRIVER SETUP =====
def setup_chrome_driver():
    try:
        service = Service(ChromeDriverManager().install())
        
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        return driver
    except Exception as e:
        log_error(f"Failed to setup Chrome driver: {e}")
        raise

def extract_mapping_from_js(js_file_path):
    try:
        if not os.path.exists(js_file_path):
            log_warning(f"Mapping file not found: {js_file_path}")
            return []
        with open(js_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        match = re.search(r'=\s*(\[[\s\S]*?\]);?', content)
        if match:
            return json.loads(match.group(1))
    except Exception as e:
        log_error(f"Failed to extract JSON: {e}")
    return []

def scan_live_jumlah_paket(driver, timeout=3.0):
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
    log_info(f"[{worker_name}] Starting...")
    
    download_dir_worker = tempfile.mkdtemp(prefix=f"inaproc_{worker_name.split('/')[0].lower()}_")
    driver = setup_chrome_driver()
    
    try:
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "allow", 
            "downloadPath": download_dir_worker
        })

        while not task_queue.empty():
            try:
                task = task_queue.get_nowait()
            except:
                break
                
            klpd_id = task["klpd_id"]
            kode_instansi = task["kode"]
            nama_daerah = task["nama"]
            
            format_nama_baru = f"klpd{klpd_id}instansi{kode_instansi}.csv"
            url_target = f"https://data.inaproc.id/realisasi?tahun={tahun}&jenis_klpd={klpd_id}&instansi={kode_instansi}"
            
            log_info(f"[{worker_name}] Processing: {nama_daerah}")
            
            navigasi_instansi_sukses = False
            target_instansi = 0
            
            for nav_attempt in range(1, 5):
                try:
                    driver.get(url_target)
                    time.sleep(random.uniform(2.5, 3.5))
                    target_instansi = scan_live_jumlah_paket(driver, timeout=5.0)
                    navigasi_instansi_sukses = True
                    break
                except:
                    time.sleep(nav_attempt * 4)
            
            if not navigasi_instansi_sukses:
                log_error(f"[{worker_name}] Network error for {nama_daerah}")
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
                    log_success(f"[{worker_name}] {nama_daerah} - 0 packets")
                    with counter_lock:
                        instansi_sukses_set.add((klpd_id, kode_instansi))
                        target_per_instansi_live[(klpd_id, kode_instansi)] = 0
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
                except:
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
                    
                    if baris_lokal == target_instansi or (target_instansi == 0 and baris_lokal > 0):
                        log_success(f"[{worker_name}] Downloaded {baris_lokal:,} rows for {nama_daerah}")
                        with counter_lock:
                            instansi_sukses_set.add((klpd_id, kode_instansi))
                            target_per_instansi_live[(klpd_id, kode_instansi)] = baris_lokal
                    else:
                        log_error(f"[{worker_name}] Mismatch: expected {target_instansi}, got {baris_lokal}")
                        if os.path.exists(path_tujuan_final):
                            os.remove(path_tujuan_final)
                except Exception as e:
                    log_warning(f"[{worker_name}] Error: {e}")
                    if os.path.exists(path_tujuan_final):
                        os.remove(path_tujuan_final)
            else:
                log_error(f"[{worker_name}] Failed to download {nama_daerah}")
                    
            task_queue.task_done()
            time.sleep(random.uniform(0.1, 0.2))
            
    finally:
        driver.quit()
        if os.path.exists(download_dir_worker):
            shutil.rmtree(download_dir_worker)

def run_mega_pipeline_staging_paralel():
    target_klpd = [
        {"id": 1, "nama": "Kementerian (KLPD 1)"},
        {"id": 2, "nama": "Lembaga (KLPD 2)"},
        {"id": 3, "nama": "Provinsi (KLPD 3)"},
        {"id": 4, "nama": "Kabupaten (KLPD 4)"},
        {"id": 5, "nama": "Kota (KLPD 5)"}
    ]
    
    tahun = "2026"
    MAX_RETRIES = 3
    FOLDER_UTAMA = "filecsv"
    FOLDER_TEMPORARY = "filecsv_temp"

    if os.path.exists(FOLDER_TEMPORARY):
        shutil.rmtree(FOLDER_TEMPORARY)
    os.makedirs(FOLDER_TEMPORARY, exist_ok=True)

    log_info("🔄 Starting Inaproc Data Sync Pipeline...")
    
    driver_main = setup_chrome_driver()

    try:
        # TAHAP 1
        log_info("="*70)
        log_info("PHASE 1: Reading Master Checksum")
        log_info("="*70)
        url_master = f"https://data.inaproc.id/realisasi?tahun={tahun}"
        
        angka_validasi_web_sumber = 0
        for master_attempt in range(1, 6):
            try:
                log_info(f"Connecting to main gateway (attempt {master_attempt}/5)...")
                driver_main.get(url_master)
                angka_validasi_web_sumber = scan_live_jumlah_paket(driver_main, timeout=6.0)
                if angka_validasi_web_sumber > 0:
                    break
            except Exception as conn_err:
                log_warning(f"Connection error: {conn_err}")
            time.sleep(master_attempt * 5)

        if angka_validasi_web_sumber == 0:
            log_error("[FATAL] Failed to read national checksum")
            driver_main.quit()
            return False
            
        log_success(f"🎯 National anchor: {angka_validasi_web_sumber:,} packets\n")

        # TAHAP 2
        log_info("="*70)
        log_info("PHASE 2: Reading KLPD Subtargets")
        log_info("="*70)
        
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
            log_info(f"🎯 {nama_rumpun}: {target_rumpun:,} packets")
            
        driver_main.quit()

        # TAHAP 3
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
            log_info(f"\n" + "="*70)
            log_info(f"🔄 DOWNLOAD PHASE: Round #{putaran_makro}")
            log_info("="*70)
            
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
                            "nama": item.get("nama", "Unknown"),
                            "index": index,
                            "total_in_klpd": len(daftar_instansi)
                        }
                        antrean_global.put(task_data)
                        tugas_terkumpul += 1
            
            if tugas_terkumpul == 0:
                log_success("🎯 All CSV files downloaded accurately!")
                download_fase_valid = True
                break
            else:
                log_info(f"📊 {tugas_terkumpul} files need update. Starting robot crew...")
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

            log_info("\n📊 Accuracy Check Report:")
            for k_id in [1, 2, 3, 4, 5]:
                target_web = target_klpd_terekam.get(k_id, 0)
                terkumpul_lokal = total_baris_csv_lokal.get(k_id, 0)
                status = "✅ MATCH" if target_web == terkumpul_lokal else f"❌ MISMATCH (diff: {abs(target_web - terkumpul_lokal):,})"
                log_info(f"   KLPD {k_id}: Web={target_web:,} | Local={terkumpul_lokal:,} | {status}")
            
            total_lokal_global = sum(total_baris_csv_lokal.values())
            log_info(f"📈 Total local rows: {total_lokal_global:,}")
            log_info(f"📉 Target web rows: {angka_validasi_web_sumber:,}")
            
            if total_lokal_global == angka_validasi_web_sumber:
                download_fase_valid = True
                log_success("🚀 Download phase successful - 100% accurate!")
                break
            else:
                log_warning(f"Round #{putaran_makro} incomplete. Retrying...")
                time.sleep(3)

        if not download_fase_valid:
            log_error("[FATAL] Download phase failed to reach 100% accuracy")
            return False

        # TAHAP 4
        log_info("\n" + "="*70)
        log_info("PHASE 4: Activating Official Folder")
        log_info("="*70)
        log_info("Replacing official folder with validated temporary data...")
        if os.path.exists(FOLDER_UTAMA):
            shutil.rmtree(FOLDER_UTAMA)
        os.rename(FOLDER_TEMPORARY, FOLDER_UTAMA)
        
        log_success("\n🎉 Pipeline Complete! All CSV files are validated and ready for GitHub.")
        return True

    except Exception as e:
        log_error(f"Fatal error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = run_mega_pipeline_staging_paralel()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log_warning("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        sys.exit(1)