import React, { useState, useEffect } from 'react';
import { supabase } from './supabaseClient';

// IMPORT SEMUA VARIABEL MAPPING JAVASCRIPT (.JS)
import { MINISTRIES } from './mapping/klpd1'; 
import { PROVINCES } from './mapping/klpd2';    
import { REGENCIES } from './mapping/klpd3';    
import { CITIES } from './mapping/klpd4';       
import { INSTITUTIONS } from './mapping/klpd5';  

function App() {
  const [dataRealisasi, setDataRealisasi] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pencarian, setPencarian] = useState('');
  const [errorStatus, setErrorStatus] = useState(null);
  
  // State Filter Bersusun Horizontal (Induk & Anak)
  const [filterIndukKlpd, setFilterIndukKlpd] = useState('1'); 
  const [daftarAnakInstansi, setDaftarAnakInstansi] = useState([]); 
  const [filterAnakInstansi, setFilterAnakInstansi] = useState('SEMUA'); 

  // Paginasi Server-Side (20 Baris/Halaman)
  const [halamanAktif, setHalamanAktif] = useState(1);
  const [totalPaket, setTotalPaket] = useState(0);
  const itemPerHalaman = 20;

  // 1. Sinkronisasi Dropdown Mengikuti Pilihan Induk
  useEffect(() => {
    let mappingTerpilih = [];
    
    try {
      switch (filterIndukKlpd) {
      case '1': mappingTerpilih = typeof MINISTRIES !== 'undefined' ? MINISTRIES : []; break;
      case '2': mappingTerpilih = typeof PROVINCES !== 'undefined' ? PROVINCES : []; break;
      case '3': mappingTerpilih = typeof REGENCIES !== 'undefined' ? REGENCIES : []; break;
      case '4': mappingTerpilih = typeof CITIES !== 'undefined' ? CITIES : []; break;
      case '5': mappingTerpilih = typeof INSTITUTIONS !== 'undefined' ? INSTITUTIONS : []; break;
      default: mappingTerpilih = [];
    }

      if (Array.isArray(mappingTerpilih)) {
        const sortedMapping = [...mappingTerpilih].sort((a, b) => {
          if (!a.nama || !b.nama) return 0;
          return a.nama.localeCompare(b.nama);
        });
        setDaftarAnakInstansi(sortedMapping);
      } else {
        setDaftarAnakInstansi([]);
      }
    } catch (err) {
      console.error("Error membaca file mapping:", err);
      setErrorStatus("Gagal membaca file mapping lokal (.js). Periksa kembali format array Anda.");
    }
    
    setFilterAnakInstansi('SEMUA'); 
    setHalamanAktif(1);
  }, [filterIndukKlpd]);

  // 2. Fetch Data Otomatis saat Parameter Berubah
  useEffect(() => {
    fetchDataTabel();
  }, [filterIndukKlpd, filterAnakInstansi, halamanAktif]);

  // Reset ke halaman awal jika mengetik pencarian paket
  useEffect(() => {
    setHalamanAktif(1);
  }, [pencarian]);

  // 3. Fungsi Utama Komunikasi Supabase Paginasi Range
  const fetchDataTabel = async () => {
    setLoading(true);
    setErrorStatus(null);
    try {
      const indexMulai = (halamanAktif - 1) * itemPerHalaman;
      const indexSelesai = indexMulai + itemPerHalaman - 1;

      // Cek apakah koneksi objek supabase siap digunakan
      if (supabase && typeof supabase.from === 'function') {
        let query = supabase
          .from('realisasi_inaproc')
          .select('*', { count: 'exact' })
          .eq('jenis_klpd', parseInt(filterIndukKlpd))
          .order('id_auto', { ascending: false })
          .range(indexMulai, indexSelesai);

        if (filterAnakInstansi !== 'SEMUA') {
          query = query.eq('id_instansi', filterAnakInstansi);
        }
        
        if (pencarian.trim() !== '') {
          query = query.ilike('nama_paket', `%${pencarian}%`);
        }

        const { data, count, error } = await query;
        if (error) throw error;

        setDataRealisasi(data || []);
        setTotalPaket(count || 0);
      } else {
        throw new Error("Klien Supabase belum terinisialisasi dengan benar.");
      }

    } catch (err) {
      console.warn("Mengaktifkan mode data tiruan (Fallback) karena:", err.message);
      // Data Cadangan Sementara agar browser TIDAK halaman putih polos saat database kosong
      setDataRealisasi([
        { 
          id_auto: 999, 
          nama_instansi: "SISTEM OFFLINE / MEMUAT DATA", 
          nama_satuan_kerja: "Silakan periksa koneksi internet atau kolom database", 
          kode_paket: "TEST-MODE", 
          nama_paket: "Data asli akan muncul otomatis setelah uploader Python Anda selesai dijalankan.", 
          metode_pengadaan: "E-Purchasing", 
          status_paket: "SELESAI" 
        }
      ]);
      setTotalPaket(1);
    } finally {
      setLoading(false);
    }
  };

  const totalHalaman = Math.ceil(totalPaket / itemPerHalaman) || 1;

  return (
    <div style={{ fontFamily: '"Segoe UI", Arial, sans-serif', backgroundColor: '#f8fafc', minHeight: '100vh', paddingBottom: '40px', margin: 0 }}>
      
      {/* Jumbotron Header */}
      <div style={{ backgroundColor: '#0f766e', color: 'white', padding: '45px 40px' }}>
        <h1 style={{ margin: 0, fontSize: '2.2rem', fontWeight: '700' }}>DATA INAPROC 2026</h1>
        <p style={{ opacity: 0.8, margin: '5px 0 20px 0' }}>Sistem Monitoring Realisasi Pengadaan Barang & Jasa</p>
        <input 
          type="text" 
          placeholder="🔍 Cari nama paket proyek di sini..." 
          value={pencarian}
          onChange={(e) => setPencarian(e.target.value)}
          style={{ width: '100%', maxWidth: '450px', padding: '12px 18px', borderRadius: '8px', border: 'none', outline: 'none', fontSize: '0.95rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}
        />
      </div>

      <div style={{ maxWidth: '1400px', margin: '20px auto', padding: '0 20px' }}>
        
        {/* Notifikasi Peringatan */}
        {errorStatus && (
          <div style={{ backgroundColor: '#fee2e2', color: '#991b1b', padding: '15px 20px', borderRadius: '8px', marginBottom: '20px', fontWeight: '600' }}>
            ⚠️ {errorStatus}
          </div>
        )}

        {/* Panel Filter Bersusun Horizontal */}
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', display: 'flex', gap: '25px', marginBottom: '25px', alignItems: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px', letterSpacing: '0.5px' }}>JENIS INSTANSI</label>
            <select value={filterIndukKlpd} onChange={(e) => setFilterIndukKlpd(e.target.value)} style={{ width: '100%', padding: '11px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.95rem', outline: 'none', color: '#334155', fontWeight: '600' }}>
              <option value="1">1 - Kementerian</option>
              <option value="5">5 - Lembaga</option>
              <option value="2">2 - Provinsi</option>
              <option value="3">3 - Kabupaten</option>
              <option value="4">4 - Kota</option>
            </select>
          </div>

          <div style={{ flex: 2 }}>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', marginBottom: '6px', letterSpacing: '0.5px' }}>INSTANSI (BERDASARKAN MAPPING)</label>
            <select value={filterAnakInstansi} onChange={(e) => { setFilterAnakInstansi(e.target.value); setHalamanAktif(1); }} style={{ width: '100%', padding: '11px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.95rem', outline: 'none', color: '#334155' }}>
              <option value="SEMUA">📁 -- Tampilkan Semua Instansi --</option>
              {daftarAnakInstansi.map((item, idx) => (
                <option key={item.kode || idx} value={item.kode}>
                  [{item.kode}] - {item.nama}
                </option>
              ))}
            </select>
          </div>

          <div style={{ width: '1px', height: '45px', backgroundColor: '#e2e8f0' }}></div>

          <div style={{ padding: '0 10px', minWidth: '120px' }}>
            <span style={{ fontSize: '11px', color: '#64748b', fontWeight: '700', textTransform: 'uppercase' }}>TOTAL PAKET</span>
            <h2 style={{ margin: 0, color: '#0f172a', fontWeight: '700', fontSize: '1.8rem' }}>{totalPaket.toLocaleString('id-ID')}</h2>
          </div>
        </div>

        {/* Tabel View Utama */}
        <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e2e8f0', overflowX: 'auto', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.01)' }}>
          {loading ? (
            <div style={{ padding: '50px', textAlign: 'center', color: '#64748b', fontWeight: '500' }}>⏳ Sedang memuat 20 baris data dari Supabase...</div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px', minWidth: '1100px' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>No</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Nama Instansi</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Satuan Kerja</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Kode Paket</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Nama Paket Proyek</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Metode</th>
                  <th style={{ padding: '14px 18px', color: '#475569', fontWeight: '700', textTransform: 'uppercase', fontSize: '0.75rem' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {dataRealisasi.length === 0 ? (
                  <tr>
                    <td colSpan="7" style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>📭 Tidak ada data transaksi yang cocok di database.</td>
                  </tr>
                ) : (
                  dataRealisasi.map((item, idx) => (
                    <tr key={item.id_auto || idx} style={{ borderBottom: '1px solid #e2e8f0', color: '#334155' }}>
                      <td style={{ padding: '14px 18px', color: '#64748b' }}>{(halamanAktif - 1) * itemPerHalaman + idx + 1}</td>
                      <td style={{ padding: '14px 18px', fontWeight: '600', color: '#0f172a' }}>{item.nama_instansi}</td>
                      <td style={{ padding: '14px 18px' }}>{item.nama_satuan_kerja || '-'}</td>
                      <td style={{ padding: '14px 18px', color: '#2563eb', fontWeight: '500' }}>{item.kode_paket || '-'}</td>
                      <td style={{ padding: '14px 18px', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.nama_paket}>{item.nama_paket}</td>
                      <td style={{ padding: '14px 18px' }}>{item.metode_pengadaan}</td>
                      <td style={{ padding: '14px 18px' }}>
                        <span style={{ backgroundColor: item.status_paket === 'SELESAI' ? '#d1fae5' : '#fef3c7', color: item.status_paket === 'SELESAI' ? '#065f46' : '#92400e', padding: '5px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: '700' }}>
                          {item.status_paket || 'PROSES'}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>

        {/* Kontrol Navigasi Paginasi */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px', alignItems: 'center', backgroundColor: 'white', padding: '16px 24px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <div style={{ fontSize: '0.9rem', color: '#64748b' }}>
            Halaman <strong style={{ color: '#0f172a' }}>{halamanAktif}</strong> dari <strong style={{ color: '#0f172a' }}>{totalHalaman}</strong> Halaman
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button onClick={() => setHalamanAktif(p => Math.max(p - 1, 1))} disabled={halamanAktif === 1 || loading} style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', backgroundColor: halamanAktif === 1 ? '#f8fafc' : 'white', color: '#334155', cursor: halamanAktif === 1 ? 'not-allowed' : 'pointer', fontWeight: '600', fontSize: '0.85rem' }}>&laquo; Sebelumnya</button>
            <button onClick={() => setHalamanAktif(p => Math.min(p + 1, totalHalaman))} disabled={halamanAktif === totalHalaman || loading} style={{ padding: '8px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', backgroundColor: halamanAktif === totalHalaman ? '#f8fafc' : 'white', color: '#334155', cursor: halamanAktif === totalHalaman ? 'not-allowed' : 'pointer', fontWeight: '600', fontSize: '0.85rem' }}>Selanjutnya &raquo;</button>
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;