import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import urllib3
import os

# Konfigurasi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE_URL = 'https://dapo.kemendikdasmen.go.id'
SEMESTER_ID = '20251'
REQUEST_TIMEOUT = 10
OUTPUT_FILE = 'result/data_sekolah_combined.csv'  # Nama file output lebih umum

# Target Pencarian (Case Insensitive)
TARGET_KOTA = ["BANDUNG", "YOGYAKARTA", "BOGOR", "SURABAYA", "SIDOARJO", "MALANG"]

def request_api(base_url: str = BASE_URL,
                level_wilayah='0',
                kode_wilayah: str = '000000',
                semester_id: str = SEMESTER_ID,
                sekolah_id: str = None,
                backoff: float = 0.5) -> dict:
    """Wrapper API dengan retry logic."""
    url = None
    while True:
        try:
            try:
                lvl = int(level_wilayah) if level_wilayah is not None else 0
            except ValueError:
                lvl = level_wilayah

            if lvl == 3 and not sekolah_id:
                url = f'{base_url}/rekap/progresSP?id_level_wilayah={lvl}&kode_wilayah={kode_wilayah}&semester_id={semester_id}&bentuk_pendidikan_id='
            elif sekolah_id:
                url = f'{base_url}/rekap/sekolahDetail?semester_id={semester_id}&sekolah_id={sekolah_id}'
            else:
                url = f'{base_url}/rekap/dataSekolah?id_level_wilayah={lvl}&kode_wilayah={kode_wilayah}&semester_id={semester_id}'

            # print(f"[API] GET {url}") # Uncomment jika ingin debug URL
            res = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)

            if res.status_code != 200:
                print(f"[API] {res.status_code} Retry...", end='\r')
                time.sleep(backoff)
                continue

            text = res.text.strip()
            if text.startswith("<!DOCTYPE html") or text.startswith("<html"):
                print("[API] Response HTML (Anti-bot), Retry...", end='\r')
                time.sleep(backoff)
                continue

            return res.json()

        except Exception as e:
            print(f"[API ERROR] {e} Retry...", end='\r')
            time.sleep(backoff)

def request_html(url: str, backoff: float = 0.5) -> str:
    """Ambil HTML profile sekolah."""
    while True:
        try:
            res = requests.get(url, verify=False, timeout=REQUEST_TIMEOUT)
            if res.status_code != 200:
                time.sleep(backoff)
                continue
            return res.text
        except Exception:
            time.sleep(backoff)

# --- CSV HEADER CONFIGURATION ---
CSV_HEADERS = [
    'sekolah_id_enkrip', 'Nama_Sekolah', 'Provinsi', 'Kota_Kabupaten', 'Kecamatan',
    'NPSN', 'Status', 'Bentuk_Pendidikan', 'Status_Kepemilikan',
    'SK_Pendirian_Sekolah', 'Tanggal_SK_Pendirian', 'SK_Izin_Operasional',
    'Tanggal_SK_Izin_Operasional', 'Kebutuhan_Khusus_Dilayani', 'Nama_Bank',
    'Cabang_KCP_Unit', 'Rekening_Atas_Nama', 'Status_BOS',
    'Waktu_Penyelenggaraan', 'Sertifikasi_ISO', 'Sumber_Listrik',
    'Daya_Listrik', 'Kecepatan_Internet', 'Kepsek', 'Operator',
    'Akreditasi', 'Kurikulum', 'Waktu', 'Alamat', 'RT_RW',
    'Dusun', 'Desa_Kelurahan', 'Kode_Pos', 'Lintang', 'Bujur',
    'Guru_L', 'Guru_P', 'Guru_Total',
    'Tendik_L', 'Tendik_P', 'Tendik_Total',
    'PTK_L', 'PTK_P', 'PTK_Total',
    'Peserta_Didik_L', 'Peserta_Didik_P', 'Peserta_Didik_Total',
    'Ruang_Kelas', 'Ruang_Perpus', 'Ruang_Lab', 'Ruang_Pratik', 'Rombel'
]

def create_csv_header(filename: str) -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename): return
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(CSV_HEADERS)

def load_processed_ids(filename: str) -> set:
    processed = set()
    if not os.path.exists(filename): return processed
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('sekolah_id_enkrip'): processed.add(row.get('sekolah_id_enkrip').strip())
    return processed

def append_to_csv(filename: str, sid: str, data: dict, meta: dict) -> None:
    p = data.get('profile', {})
    r = data.get('recapitulation', {})
    c = data.get('contact', {})
    
    # Extract nested dicts safely
    identitas = p.get('identitas_sekolah', {})
    pelengkap = p.get('data_pelengkap', {})
    rinci = p.get('data_rinci', {})
    sidebar = p.get('sidebar_info', {})

    # Kalkulasi Total
    gl, gp = r.get('ptk_laki', 0), r.get('ptk_perempuan', 0)
    tl, tp = r.get('pegawai_laki', 0), r.get('pegawai_perempuan', 0)
    pl, pp = r.get('pd_laki', 0), r.get('pd_perempuan', 0)

    row = [
        sid, meta['nama'], meta['prov'], meta['kota'], meta['kec'],
        identitas.get('NPSN'), identitas.get('Status'), identitas.get('Bentuk Pendidikan'),
        identitas.get('Status Kepemilikan'), identitas.get('SK Pendirian Sekolah'),
        identitas.get('Tanggal SK Pendirian'), identitas.get('SK Izin Operasional'),
        identitas.get('Tanggal SK Izin Operasional'), pelengkap.get('Kebutuhan Khusus Dilayani'),
        pelengkap.get('Nama Bank'), pelengkap.get('Cabang KCP/Unit'), pelengkap.get('Rekening Atas Nama'),
        rinci.get('Status BOS'), rinci.get('Waku Penyelenggaraan'), rinci.get('Sertifikasi ISO'),
        rinci.get('Sumber Listrik'), rinci.get('Daya Listrik'), rinci.get('Kecepatan Internet'),
        sidebar.get('Kepsek'), sidebar.get('Operator'), sidebar.get('Akreditasi'),
        sidebar.get('Kurikulum'), sidebar.get('Waktu'),
        c.get('Alamat'), c.get('RT / RW'), c.get('Dusun'), c.get('Desa / Kelurahan'),
        c.get('Kode Pos'), c.get('Lintang'), c.get('Bujur'),
        gl, gp, gl+gp, tl, tp, tl+tp, gl+tl, gp+tp, (gl+gp+tl+tp),
        pl, pp, pl+pp,
        r.get('after_ruang_kelas', r.get('before_ruang_kelas', 0)),
        r.get('after_ruang_perpus', r.get('before_ruang_perpus', 0)),
        r.get('after_ruang_lab', r.get('before_ruang_lab', 0)),
        r.get('after_ruang_praktik', r.get('before_ruang_praktik', 0)),
        r.get('rombel', 0)
    ]
    
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(row)

def parse_html(url: str) -> dict:
    """Parsing HTML Profil Sekolah."""
    soup = BeautifulSoup(request_html(url), 'html.parser')
    data = {"profile": {}, "recapitulation": {}, "contact": {}}
    
    # Parsing Panel Info
    for panel in soup.select('#profil .panel-info'):
        head = panel.find(class_='panel-heading')
        if not head: continue
        h_text = head.get_text(strip=True)
        
        section = {}
        for p in panel.select('.panel-body p'):
            st = p.find('strong')
            if st:
                k = st.get_text(strip=True).replace(':', '').strip()
                v = st.next_sibling.strip() if st.next_sibling else ''
                section[k] = v
        
        if "Identitas" in h_text: data["profile"]["identitas_sekolah"] = section
        elif "Pelengkap" in h_text: data["profile"]["data_pelengkap"] = section
        elif "Rinci" in h_text: data["profile"]["data_rinci"] = section

    # Sidebar & Contact (Simplified logic for brevity)
    sb = soup.find(class_='profile-usermenu')
    if sb:
        data["profile"]["sidebar_info"] = {
            i.get_text(strip=True).split(':', 1)[0].strip(): i.get_text(strip=True).split(':', 1)[1].strip() 
            for i in sb.find_all('li') if ':' in i.get_text()
        }
    
    cp = soup.select_one('#kontak .panel-info')
    if cp:
        data["contact"] = {
            p.find('strong').get_text(strip=True).replace(':', '').strip(): 
            p.find('strong').next_sibling.strip() if p.find('strong').next_sibling else ''
            for p in cp.find_all('p') if p.find('strong')
        }
    
    # Get Recapitulation API
    sid = url.split('/')[-1].strip()
    recap = request_api(sekolah_id=sid)
    if recap: data["recapitulation"] = recap[0]
    
    return data

def main():
    create_csv_header(OUTPUT_FILE)
    processed = load_processed_ids(OUTPUT_FILE)
    print(f"=== SCRAPER DAPO KEMENDIKDASMEN ===")
    print(f"Target: {TARGET_KOTA}")
    print(f"Output: {OUTPUT_FILE} (Resume: {len(processed)} data existing)\n")

    provinsi_list = request_api()
    for prov in provinsi_list:
        print(f"> Cek Provinsi: {prov['nama']}")
        
        # Optimization: Hanya masuk ke provinsi yang mungkin mengandung kota target
        # Namun karena kita search by keyword kota, kita harus loop semua kota di prov ini
        kotas = request_api(level_wilayah=prov['id_level_wilayah'], kode_wilayah=prov['kode_wilayah'].strip())
        
        for kota in kotas:
            # FILTERING KOTA DISINI
            if not any(k.lower() in kota['nama'].lower() for k in TARGET_KOTA):
                continue # Skip jika bukan kota target

            print(f"\n  [MATCH] Memproses: {kota['nama']}...")
            kecamatans = request_api(level_wilayah=kota['id_level_wilayah'], kode_wilayah=kota['kode_wilayah'].strip())
            
            for kec in kecamatans:
                print(f"    - Kecamatan: {kec['nama']}")
                sekolahs = request_api(level_wilayah=kec['id_level_wilayah'], kode_wilayah=kec['kode_wilayah'].strip())
                
                for sek in sekolahs:
                    if sek['bentuk_pendidikan'] not in ['SD', 'SMP', 'SMA', 'SMK'] or sek['status_sekolah'] not in ['Negeri', 'Swasta']:
                        continue
                        
                    sid = sek['sekolah_id_enkrip'].strip()
                    if sid in processed:
                        continue
                    
                    print(f"      > Scrape: {sek['nama']}")
                    try:
                        full_data = parse_html(f"https://dapo.dikdasmen.go.id/sekolah/{sid}")
                        meta = {'nama': sek['nama'], 'prov': prov['nama'], 'kota': kota['nama'], 'kec': kec['nama']}
                        append_to_csv(OUTPUT_FILE, sid, full_data, meta)
                    except Exception as e:
                        print(f"      [ERR] Gagal scrape {sek['nama']}: {e}")

if __name__ == '__main__':
    main()