import React, { useState, useEffect, useMemo } from 'react';
import { ambilDataDariGitHub } from './utils/githubAPI';

// Mengambil seluruh isi file mapping
import * as k1 from './maping/klpd1'; 
import * as k2 from './maping/klpd2';    
import * as k3 from './maping/klpd3';    
import * as k4 from './maping/klpd4';       
import * as k5 from './maping/klpd5';  

// FUNGSI AUTO-DETECT FILE MAPPING
const ambilDataArray = (modul) => {
  if (!modul) return [];
  for (let key in modul) {
    if (Array.isArray(modul[key])) return modul[key];
  }
  return [];
};

// FUNGSI STANDARISASI NAMA KOLOM
const standardisasiDataCSV = (dataMentah) => {
  if (!Array.isArray(dataMentah)) return [];
  return dataMentah.map(baris => {
    let barisBersih = {};
    for (let key in baris) {
      let keyBersih = key.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, ''); 
      barisBersih[keyBersih] = baris[key];
    }
    return barisBersih;
  });
};

function App() {
  const [semuaData, setSemuaData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  
  // 1. MEMORY STATE: Mengambil dari localStorage
  const [filterIndukKlpd, setFilterIndukKlpd] = useState(() => localStorage.getItem('savedKlpd') || '1'); 
  const [daftarInstansi, setDaftarInstansi] = useState([]); 
  const [pilihanInstansi, setPilihanInstansi] = useState(''); 

  const [page, setPage] = useState(1);
  const [inputLompat, setInputLompat] = useState('');
  const perPage = 20;

  // State untuk Jam Realtime
  const [waktu, setWaktu] = useState(new Date());

  // Effect untuk Jam Realtime
  useEffect(() => {
    const timer = setInterval(() => setWaktu(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // 1. Sinkronisasi Dropdown & Menyimpan Memory
  useEffect(() => {
    let mapping = [];
    switch (filterIndukKlpd) {
      case '1': mapping = ambilDataArray(k1); break;
      case '2': mapping = ambilDataArray(k2); break;
      case '3': mapping = ambilDataArray(k3); break;
      case '4': mapping = ambilDataArray(k4); break;
      case '5': mapping = ambilDataArray(k5); break;
      default: mapping = [];
    }
    setDaftarInstansi(mapping);

    const savedInstansi = localStorage.getItem('savedInstansi');
    const isSavedValid = mapping.some(item => item.kode === savedInstansi);

    if (isSavedValid) {
      setPilihanInstansi(savedInstansi);
    } else {
      setPilihanInstansi(mapping.length > 0 ? (mapping[0]?.kode || '') : '');
    }
    
    localStorage.setItem('savedKlpd', filterIndukKlpd);
    setPage(1);
  }, [filterIndukKlpd]);

  // Simpan pilihan Instansi
  useEffect(() => {
    if (pilihanInstansi) {
      localStorage.setItem('savedInstansi', pilihanInstansi);
    }
  }, [pilihanInstansi]);

  // 2. Fetch Data dari GitHub
  useEffect(() => {
    const fetchData = async () => {
      if (!pilihanInstansi) return;
      setLoading(true);
      setSemuaData([]); 
      try {
        const data = await ambilDataDariGitHub(filterIndukKlpd, pilihanInstansi);
        const dataSiapPakai = standardisasiDataCSV(data);
        setSemuaData(dataSiapPakai);
      } catch (err) {
        console.error("Gagal load data dari GitHub:", err);
        setSemuaData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [filterIndukKlpd, pilihanInstansi]);

  // 3. Pencarian Pintar
  const hasilFilter = useMemo(() => {
    if (!search) return semuaData;
    const kataKunci = search.toLowerCase();
    
    return semuaData.filter(item => {
      const teksGabungan = Object.values(item).map(val => (val || '').toString().toLowerCase()).join(" ");
      return teksGabungan.includes(kataKunci);
    });
  }, [semuaData, search]);

  const totalItem = hasilFilter.length;
  const totalPage = Math.ceil(totalItem / perPage) || 1;
  const dataPage = hasilFilter.slice((page - 1) * perPage, page * perPage);

  // Fungsi Lompat Halaman
  const prosesLompatHalaman = () => {
    const target = parseInt(inputLompat);
    if (target >= 1 && target <= totalPage) {
      setPage(target);
    } else {
      alert(`Mohon masukkan angka antara 1 sampai ${totalPage}`);
    }
    setInputLompat('');
  };

  // 4. Fungsi Download CSV
  const downloadCSV = () => {
    if (semuaData.length === 0) {
      alert("Tidak ada data untuk didownload.");
      return;
    }

    const headers = Object.keys(semuaData[0]);
    const barisCSV = [];
    barisCSV.push(headers.join(','));

    for (const baris of semuaData) {
      const values = headers.map(header => {
        let nilai = baris[header] === null || baris[header] === undefined ? "" : baris[header].toString();
        nilai = nilai.replace(/"/g, '""');
        return `"${nilai}"`; 
      });
      barisCSV.push(values.join(','));
    }

    const csvString = barisCSV.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `klpd${filterIndukKlpd}instansi${pilihanInstansi}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatTanggal = waktu.toLocaleDateString('id-ID', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
  const formatJam = waktu.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  // CSS KHUSUS UNTUK KOLOM TEKS PANJANG (Agar bisa turun baris dan lebarnya pas)
  const styleKolomTeks = {
    padding: '14px 16px',
    whiteSpace: 'normal', // Mengizinkan teks turun ke bawah
    minWidth: '180px',    // Lebar minimal
    maxWidth: '280px',    // Lebar maksimal agar tidak melebar terus
    wordWrap: 'break-word',
    lineHeight: '1.4'
  };

  return (
    <div style={{ backgroundColor: '#f1f5f9', minHeight: '100vh', fontFamily: '"Inter", "Segoe UI", sans-serif', color: '#334155' }}>
      
      {/* HEADER HIJAU */}
      <header style={{ backgroundColor: '#16a34a', padding: '16px 40px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }}>
        <div>
          <h1 style={{ margin: 0, color: 'white', fontSize: '22px', fontWeight: 'bold', letterSpacing: '1px' }}>
            DATA INAPROC 2026
          </h1>
          <p style={{ margin: '4px 0 0 0', color: '#dcfce7', fontSize: '13px', fontWeight: '500' }}>
            {formatTanggal} | {formatJam} WIB
          </p>
        </div>
        <input
          type="text"
          placeholder="🔍 Pencarian pintar..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          style={{ padding: '10px 16px', width: '350px', borderRadius: '8px', border: 'none', outline: 'none', backgroundColor: '#ffffff', color: '#333', fontSize: '14px', boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.1)' }}
        />
      </header>

      {/* MAIN CONTENT WRAPPER */}
      <main style={{ padding: '24px 40px' }}>
        
        {/* TABS */}
        <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0', marginBottom: '24px' }}>
          <button style={{ padding: '12px 24px', backgroundColor: 'transparent', border: 'none', fontSize: '15px', fontWeight: '600', color: '#64748b', cursor: 'pointer' }}>
            Rencana Umum Pengadaan 
          </button>
          <button style={{ padding: '12px 24px', backgroundColor: 'transparent', border: 'none', borderBottom: '3px solid #16a34a', fontSize: '15px', fontWeight: 'bold', color: '#16a34a', cursor: 'pointer', marginBottom: '-2px' }}>
            Realisasi
          </button>
        </div>

        {/* FILTER CARD & TOMBOL DOWNLOAD */}
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', display: 'flex', gap: '24px', marginBottom: '24px', border: '1px solid #e2e8f0', alignItems: 'flex-end', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <label style={{ fontSize: '13px', fontWeight: '700', color: '#475569', textTransform: 'uppercase' }}>Jenis Instansi</label>
            <select value={filterIndukKlpd} onChange={e => setFilterIndukKlpd(e.target.value)} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', backgroundColor: '#f8fafc', outline: 'none', minWidth: '220px', fontSize: '14px', color: '#334155', cursor: 'pointer' }}>
              <option value="1">Kementerian</option>
              <option value="2">Lembaga</option>
              <option value="3">Provinsi</option>
              <option value="4">Kabupaten</option>
              <option value="5">Kota</option>
            </select>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, minWidth: '250px' }}>
            <label style={{ fontSize: '13px', fontWeight: '700', color: '#475569', textTransform: 'uppercase' }}>Instansi</label>
            <select value={pilihanInstansi} onChange={e => setPilihanInstansi(e.target.value)} style={{ padding: '10px 16px', borderRadius: '8px', border: '1px solid #cbd5e1', backgroundColor: '#f8fafc', outline: 'none', width: '100%', fontSize: '14px', color: '#334155', cursor: 'pointer' }}>
              {daftarInstansi.map((ins, i) => (
                <option key={i} value={ins.kode}>{ins.nama}</option>
              ))}
            </select>
          </div>

          <div>
            <button 
              onClick={downloadCSV} 
              style={{ padding: '10px 20px', backgroundColor: '#f59e0b', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 'bold', fontSize: '14px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', boxShadow: '0 2px 4px rgba(245, 158, 11, 0.3)' }}
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#d97706'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#f59e0b'}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
              Download CSV 
            </button>
          </div>
        </div>

        {/* INFO TOTAL PAKET */}
        <div style={{ backgroundColor: '#eff6ff', padding: '16px 24px', borderRadius: '12px', borderLeft: '5px solid #3b82f6', marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '28px' }}>📊</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '15px', color: '#1e3a8a', fontWeight: '800', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Paket Instansi Ini</h3>
            </div>
          </div>
          <div style={{ fontSize: '32px', fontWeight: '900', color: '#1d4ed8', letterSpacing: '-1px' }}>
            {semuaData.length.toLocaleString('id-ID')} <span style={{ fontSize: '16px', fontWeight: '700', color: '#60a5fa', letterSpacing: '0' }}>Paket</span>
          </div>
        </div>

        {/* TABLE SECTION */}
        <div style={{ backgroundColor: 'white', borderRadius: '12px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
          {loading ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#64748b', fontSize: '15px' }}>
               wait please... 🔄
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              {/* NOTE: whiteSpace 'nowrap' dihapus dari table agar bisa di-override */}
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', whiteSpace: 'nowrap' }}>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>No</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Nama Instansi</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Satuan Kerja</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Kode Paket</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Kode RUP</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Tahun</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Transaksi</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Sumber Dana</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Penyedia</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Metode</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Jenis</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Nama Paket</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Status</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Total Nilai</th>
                    <th style={{ padding: '16px', color: '#475569', fontWeight: '600' }}>Nilai PDN</th>
                  </tr>
                </thead>
                <tbody>
                  {dataPage.length === 0 ? (
                    <tr><td colSpan="15" style={{ padding: '30px', textAlign: 'center', color: '#94a3b8' }}>Tidak ada data yang sesuai / CSV kosong.</td></tr>
                  ) : (
                    dataPage.map((item, i) => (
                      <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                        {/* Kolom yang isinya pendek / angka (whiteSpace: nowrap) */}
                        <td style={{ padding: '14px 16px', color: '#64748b', whiteSpace: 'nowrap' }}>{((page - 1) * perPage) + i + 1}</td>
                        
                        {/* Kolom Teks Panjang (Menggunakan styleKolomTeks) */}
                        <td style={{ ...styleKolomTeks, fontWeight: '500' }}>{item?.nama_instansi || '-'}</td>
                        <td style={styleKolomTeks}>{item?.nama_satuan_kerja || item?.satuan_kerja || item?.satker || '-'}</td>
                        
                        <td style={{ padding: '14px 16px', color: '#2563eb', whiteSpace: 'nowrap' }}>{item?.kode_paket || '-'}</td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.kode_rup || '-'}</td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.tahun_anggaran || item?.tahun || '-'}</td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.sumber_transaksi || '-'}</td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.sumber_dana || '-'}</td>
                        
                        {/* Kolom Teks Panjang */}
                        <td style={styleKolomTeks}>{item?.nama_penyedia || item?.penyedia || '-'}</td>
                        
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                          <span style={{ padding: '4px 8px', backgroundColor: '#e2e8f0', borderRadius: '4px', fontSize: '11px', fontWeight: '600' }}>{item?.metode_pengadaan || item?.metode || '-'}</span>
                        </td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.jenis_pengadaan || item?.jenis || '-'}</td>
                        
                        {/* Kolom Nama Paket (Bisa lebih lebar) */}
                        <td style={{ ...styleKolomTeks, minWidth: '250px', maxWidth: '350px' }}>{item?.nama_paket || item?.paket || '-'}</td>
                        
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>
                          <span style={{ padding: '4px 8px', backgroundColor: '#dcfce7', color: '#166534', borderRadius: '4px', fontSize: '11px', fontWeight: '600' }}>{item?.status_paket || item?.status || '-'}</span>
                        </td>
                        <td style={{ padding: '14px 16px', fontWeight: '600', color: '#0f172a', whiteSpace: 'nowrap' }}>{item?.total_nilai || item?.pagu ? parseInt(item.total_nilai || item.pagu).toLocaleString('id-ID') : '-'}</td>
                        <td style={{ padding: '14px 16px', whiteSpace: 'nowrap' }}>{item?.nilai_pdn ? parseInt(item.nilai_pdn).toLocaleString('id-ID') : '-'}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {/* PAGINATION & LOMPAT HALAMAN FOOTER */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 24px', borderTop: '1px solid #e2e8f0', backgroundColor: '#f8fafc', flexWrap: 'wrap', gap: '15px' }}>
            <div style={{ fontSize: '14px', color: '#64748b' }}>
              Menampilkan {totalItem === 0 ? 0 : ((page - 1) * perPage) + 1} – {Math.min(page * perPage, totalItem)} dari {totalItem.toLocaleString('id-ID')} data
            </div>
            
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button onClick={() => setPage(1)} disabled={page === 1} style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '6px', backgroundColor: page === 1 ? '#f1f5f9' : 'white', cursor: page === 1 ? 'not-allowed' : 'pointer' }}>First</button>
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '6px', backgroundColor: page === 1 ? '#f1f5f9' : 'white', cursor: page === 1 ? 'not-allowed' : 'pointer' }}>Prev</button>
              
              <span style={{ padding: '6px 12px', fontWeight: '600', color: '#0f172a' }}>{page}</span>
              
              <button onClick={() => setPage(p => Math.min(totalPage, p + 1))} disabled={page === totalPage} style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '6px', backgroundColor: page === totalPage ? '#f1f5f9' : 'white', cursor: page === totalPage ? 'not-allowed' : 'pointer' }}>Next</button>
              <button onClick={() => setPage(totalPage)} disabled={page === totalPage} style={{ padding: '6px 12px', border: '1px solid #cbd5e1', borderRadius: '6px', backgroundColor: page === totalPage ? '#f1f5f9' : 'white', cursor: page === totalPage ? 'not-allowed' : 'pointer' }}>Last</button>
              
              <div style={{ marginLeft: '10px', display: 'flex', alignItems: 'center', gap: '5px', borderLeft: '2px solid #cbd5e1', paddingLeft: '15px' }}>
                <span style={{ fontSize: '13px', fontWeight: '600', color: '#475569' }}>Ke Hal:</span>
                <input 
                  type="number" 
                  value={inputLompat} 
                  onChange={(e) => setInputLompat(e.target.value)} 
                  onKeyDown={(e) => e.key === 'Enter' && prosesLompatHalaman()}
                  style={{ width: '60px', padding: '6px', borderRadius: '6px', border: '1px solid #cbd5e1', outline: 'none' }} 
                  placeholder="No"
                />
                <button onClick={prosesLompatHalaman} style={{ padding: '6px 12px', backgroundColor: '#16a34a', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>Go</button>
              </div>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}

export default App;
