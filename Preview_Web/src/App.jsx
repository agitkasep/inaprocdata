import { useState, useRef } from 'react';
import axios from 'axios';
import './index.css';

function App() {
  const [data, setData] = useState([]);
  const [activeTab, setActiveTab] = useState('Realisasi');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageInput, setPageInput] = useState('1');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [instansiType, setInstansiType] = useState('Kementerian');
  const rowsPerPage = 20;

  const scrollRef = useRef(null);
  const [isDown, setIsDown] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  const handleMouseDown = (e) => {
    setIsDown(true);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };
  const handleMouseLeave = () => setIsDown(false);
  const handleMouseUp = () => setIsDown(false);
  const handleMouseMove = (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2;
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  const formatRupiah = (angka) => {
    const num = Number(angka);
    if (isNaN(num)) return "Rp 0";
    return new Intl.NumberFormat('id-ID', {
      style: 'currency', currency: 'IDR', minimumFractionDigits: 0, maximumFractionDigits: 0,
    }).format(num);
  };

  const filteredData = data.filter((item) =>
    Object.values(item).some((val) => val !== null && val !== undefined && String(val).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;
  const currentRows = filteredData.slice(indexOfFirstRow, indexOfLastRow);
  const totalPages = Math.ceil(filteredData.length / rowsPerPage) || 1;

  const kementerianList = [
    {kode: "K1", nama: "KEMENTERIAN AGAMA"}, {kode: "K2", nama: "KEMENTERIAN BUMN"}, {kode: "K3", nama: "KEMENTERIAN KETENAGAKERJAAN"}, {kode: "K4", nama: "KEMENTERIAN PERINDUSTRIAN"}, {kode: "K8", nama: "KEMENTERIAN KELAUTAN DAN PERIKANAN"},
    {kode: "K9", nama: "KEMENTERIAN KESEHATAN"}, {kode: "K10", nama: "KEMENTERIAN KEUANGAN"}, {kode: "K13", nama: "KEMENTERIAN KOORDINATOR BIDANG PEREKONOMIAN"}, {kode: "K17", nama: "KEMENTERIAN LUAR NEGERI"}, {kode: "K20", nama: "KEMENTERIAN PEMBERDAYAAN PEREMPUAN DAN PERLINDUNGAN ANAK"},
    {kode: "K21", nama: "KEMENTERIAN PEMUDA DAN OLAH RAGA"}, {kode: "K22", nama: "KEMENTERIAN PENDAYAGUNAAN APARATUR NEGARA DAN REFORMASI BIROKRASI"}, {kode: "K24", nama: "KEMENTERIAN PERDAGANGAN"}, {kode: "K25", nama: "KEMENTERIAN PERENCANAAN PEMBANGUNAN NASIONAL"}, {kode: "K26", nama: "KEMENTERIAN PERHUBUNGAN"},
    {kode: "K27", nama: "KEMENTERIAN PERINDUSTRIAN"}, {kode: "K28", nama: "KEMENTERIAN PERTAHANAN"}, {kode: "K29", nama: "KEMENTERIAN PERTANIAN"}, {kode: "K32", nama: "KEMENTERIAN SEKRETARIAT NEGARA"}, {kode: "K33", nama: "KEMENTERIAN SOSIAL"},
    {kode: "K35", nama: "KEMENTERIAN PARIWISATA"}, {kode: "K38", nama: "KEMENTERIAN AGRARIA DAN TATA RUANG/BPN"}, {kode: "K41", nama: "KEMENTERIAN KOORDINATOR BIDANG PEMBANGUNAN MANUSIA DAN KEBUDAYAAN"}, {kode: "K48", nama: "KEMENTERIAN KOPERASI"},
    {kode: "K49", nama: "KEMENTERIAN USAHA MIKRO, KECIL, DAN MENENGAH"}, {kode: "K50", nama: "KEMENTERIAN KOORDINATOR BIDANG POLITIK DAN KEAMANAN"}, {kode: "K51", nama: "KEMENTERIAN KOORDINATOR BIDANG HUKUM, HAK ASASI MANUSIA, IMIGRASI, DAN PEMASYARAKATAN"}, {kode: "K52", nama: "KEMENTERIAN KOORDINATOR BIDANG INFRASTRUKTUR DAN PEMBANGUNAN KEWILAYAHAN"}, {kode: "K53", nama: "KEMENTERIAN KOORDINATOR BIDANG PEMBERDAYAAN MASYARAKAT"},
    {kode: "K54", nama: "KEMENTERIAN KOORDINATOR BIDANG PANGAN"}, {kode: "K55", nama: "KEMENTERIAN HUKUM"}, {kode: "K56", nama: "KEMENTERIAN HAK ASASI MANUSIA"}, {kode: "K57", nama: "KEMENTERIAN IMIGRASI DAN PEMASYARAKATAN"}, {kode: "K58", nama: "KEMENTERIAN PENDIDIKAN DASAR DAN MENENGAH"},
    {kode: "K59", nama: "KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI"}, {kode: "K60", nama: "KEMENTERIAN KEBUDAYAAN"}, {kode: "K61", nama: "KEMENTERIAN PELINDUNGAN PEKERJA MIGRAN INDONESIA/BPPMI"}, {kode: "K62", nama: "KEMENTERIAN PERUMAHAN DAN KAWASAN PERMUKIMAN"}, {kode: "K63", nama: "KEMENTERIAN DESA DAN PEMBANGUNAN DAERAH TERTINGGAL"},
    {kode: "K64", nama: "KEMENTERIAN TRANSMIGRASI"}, {kode: "K65", nama: "KEMENTERIAN KOMUNIKASI DAN DIGITAL"}, {kode: "K66", nama: "KEMENTERIAN KEPENDUDUKAN DAN PEMBANGUNAN KELUARGA/BKKBN"}, {kode: "K67", nama: "KEMENTERIAN INVESTASI DAN HILIRISASI/BKPM"}, {kode: "K68", nama: "KEMENTERIAN EKONOMI KREATIF/BADAN EKONOMI KREATIF"},
    {kode: "K69", nama: "KEMENTERIAN LINGKUNGAN HIDUP/BADAN PENGENDALIAN LINGKUNGAN HIDUP"}, {kode: "K73", nama: "KEMENTERIAN PEKERJAAN UMUM"}, {kode: "K74", nama: "KEMENTERIAN KEHUTANAN"}, {kode: "K75", nama: "KEMENTERIAN HAJI DAN UMRAH REPUBLIK INDONESIA"}, {kode: "L25", nama: "BENDAHARA UMUM NEGARA (KEMENTERIAN KEUANGAN)"}
  ];

  const lembagaList = [
    {kode: "L112", nama: "BADAN GIZI NASIONAL"}, {kode: "L1", nama: "ARSIP NASIONAL REPUBLIK INDONESIA"}, {kode: "L6", nama: "BADAN INFORMASI GEOSPASIAL"}, {kode: "L2", nama: "BADAN INTELIJEN NEGARA"}, {kode: "L106", nama: "BADAN KARANTINA INDONESIA"}, {kode: "L58", nama: "BADAN KEAMANAN LAUT"}, {kode: "L3", nama: "BADAN KEPEGAWAIAN NEGARA"}, {kode: "L7", nama: "BADAN METEOROLOGI, KLIMATOLOGI DAN GEOFISIKA"}, {kode: "L8", nama: "BADAN NARKOTIKA NASIONAL"}, {kode: "L9", nama: "BADAN NASIONAL PENANGGULANGAN BENCANA"}, {kode: "L10", nama: "BADAN NASIONAL PENANGGULANGAN TERORISME"}, {kode: "L100", nama: "BADAN NASIONAL PENCARIAN DAN PERTOLONGAN"}, {kode: "L12", nama: "BADAN NASIONAL PENGELOLA PERBATASAN"}, {kode: "L114", nama: "BADAN OTORITA PENGELOLA PANTAI UTARA JAWA"}, {kode: "L104", nama: "BADAN PANGAN NASIONAL"}, {kode: "L101", nama: "BADAN PEMBINAAN IDEOLOGI PANCASILA"}, {kode: "L13", nama: "BADAN PEMERIKSA KEUANGAN"}, {kode: "L17", nama: "BADAN PENGAWASAN KEUANGAN DAN PEMBANGUNAN"}, {kode: "L15", nama: "BADAN PENGAWAS OBAT DAN MAKANAN"}, {kode: "L57", nama: "BADAN PENGAWAS PEMILIHAN UMUM"}, {kode: "L16", nama: "BADAN PENGAWAS TENAGA NUKLIR"}, {kode: "I81", nama: "BADAN PENGUSAHAAN KAWASAN BATAM"}, {kode: "I100", nama: "BADAN PENGUSAHAAN KAWASAN BATAM 984423"}, {kode: "I82", nama: "BADAN PENGUSAHAAN KAWASAN SABANG"}, {kode: "L110", nama: "BADAN PENYELENGGARA JAMINAN PRODUK HALAL"}, {kode: "L21", nama: "BADAN PUSAT STATISTIK"}, {kode: "L103", nama: "BADAN RISET DAN INOVASI NASIONAL"}, {kode: "L39", nama: "BADAN SIBER DAN SANDI NEGARA"}, {kode: "L23", nama: "BADAN STANDARDISASI NASIONAL"}, {kode: "L27", nama: "DEWAN PERWAKILAN DAERAH"}, {kode: "L28", nama: "DEWAN PERWAKILAN RAKYAT"}, {kode: "L46", nama: "KEJAKSAAN REPUBLIK INDONESIA"}, {kode: "L47", nama: "KEPOLISIAN NEGARA REPUBLIK INDONESIA"}, {kode: "L29", nama: "KOMISI NASIONAL HAK ASASI MANUSIA"}, {kode: "L30", nama: "KOMISI PEMBERANTASAN KORUPSI"}, {kode: "L31", nama: "KOMISI PEMILIHAN UMUM"}, {kode: "L32", nama: "KOMISI PENGAWAS PERSAINGAN USAHA"}, {kode: "L33", nama: "KOMISI YUDISIAL RI"}, {kode: "L34", nama: "LEMBAGA ADMINISTRASI NEGARA"}, {kode: "L36", nama: "LEMBAGA KEBIJAKAN PENGADAAN BARANG/JASA"}, {kode: "L37", nama: "LEMBAGA KETAHANAN NASIONAL"}, {kode: "L51", nama: "LPP TELEVISI REPUBLIK INDONESIA"}, {kode: "L52", nama: "LPP RADIO REPUBLIK INDONESIA"}, {kode: "L102", nama: "LEMBAGA PERLINDUNGAN SAKSI DAN KORBAN"}, {kode: "L40", nama: "MAHKAMAH AGUNG"}, {kode: "L41", nama: "MAHKAMAH KONSTITUSI RI"}, {kode: "L42", nama: "MAJELIS PERMUSYAWARATAN RAKYAT"}, {kode: "L43", nama: "OMBUDSMAN REPUBLIK INDONESIA"}, {kode: "L105", nama: "OTORITA IBU KOTA NUSANTARA (OIKN)"}, {kode: "L44", nama: "PERPUSTAKAAN NASIONAL REPUBLIK INDONESIA"}, {kode: "L45", nama: "PPATK"}, {kode: "L56", nama: "SEKRETARIAT KABINET"}
  ];

  const handleFetch = async (kode) => {
    if (!kode) return;
    setLoading(true); setData([]); setCurrentPage(1); setSearchTerm(''); setPageInput('1');
    const subFolder = instansiType === 'Kementerian' ? 'kementerian' : 'lembaga';
    try { 
      const res = await axios.get(`/data/${subFolder}/${kode}.json?t=${Date.now()}`); 
      setData(res.data); 
    } catch (e) { console.error(e); setData([]); } finally { setLoading(false); }
  };

  const currentInstansiList = instansiType === 'Kementerian' ? kementerianList : lembagaList;

  return (
    <div className="container">
      <header className="hero-header">
        <h1>DATA INAPROC 2026</h1>
        <input className="search-bar" placeholder="Pencarian pintar..." value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); setPageInput('1'); }} />
      </header>

      <div className="tab-container">
        <button className={activeTab === 'RUP' ? 'active' : ''} onClick={() => setActiveTab('RUP')}>Rencana Umum Pengadaan</button>
        <button className={activeTab === 'Realisasi' ? 'active' : ''} onClick={() => setActiveTab('Realisasi')}>Realisasi</button>
      </div>

      <div className="filter-box">
        <div><label>JENIS INSTANSI</label><br/>
            <select value={instansiType} onChange={(e) => { setInstansiType(e.target.value); setData([]); }}>
                <option value="Kementerian">Kementerian</option>
                <option value="Lembaga">Lembaga</option>
            </select>
        </div>
        <div><label>INSTANSI</label><br/>
            <select onChange={(e) => handleFetch(e.target.value)}>
                <option value="">-- Pilih Instansi --</option>
                {currentInstansiList.map(k => <option key={k.kode} value={k.kode}>{k.nama}</option>)}
            </select>
        </div>
      </div>

      {loading ? <div className="loading">Memuat data...</div> : (
        <div className="table-wrapper" ref={scrollRef} onMouseDown={handleMouseDown} onMouseLeave={handleMouseLeave} onMouseUp={handleMouseUp} onMouseMove={handleMouseMove}>
          <table>
            <thead>
              <tr>
                <th>No</th><th>Nama Instansi</th><th>Nama Satuan Kerja</th><th>Kode Paket</th><th>Kode RUP</th><th>Tahun Anggaran</th>
                <th>Sumber Transaksi</th><th>Sumber Dana</th><th>Nama Penyedia</th><th>Metode Pengadaan</th><th>Jenis Pengadaan</th>
                <th>Nama Paket</th><th>Status Paket</th><th>Total Nilai (Rp)</th><th>Nilai PDN (Rp)</th>
              </tr>
            </thead>
            <tbody>
              {currentRows.map((item, i) => (
                <tr key={item['Kode Paket'] || i}>
                  <td>{indexOfFirstRow + i + 1}</td>
                  <td>{item['Nama Instansi']}</td><td>{item['Nama Satuan Kerja']}</td><td>{item['Kode Paket']}</td>
                  <td>{item['Kode RUP']}</td><td>{item['Tahun Anggaran']}</td><td>{item['Sumber Transaksi']}</td>
                  <td>{item['Sumber Dana']}</td><td>{item['Nama Penyedia']}</td><td>{item['Metode Pengadaan']}</td>
                  <td>{item['Jenis Pengadaan']}</td><td>{item['Nama Paket']}</td><td>{item['Status Paket']}</td>
                  <td className="pro-currency">{formatRupiah(item['Total Nilai (Rp)'])}</td>
                  <td className="pro-currency">{formatRupiah(item['Nilai PDN (Rp)'])}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <div className="pagination-footer">
            <span>Halaman {currentPage} dari {totalPages} ({filteredData.length} data)</span>
            <div>
              <input type="number" value={pageInput} onChange={(e) => {setPageInput(e.target.value); const p = parseInt(e.target.value); if(p >= 1 && p <= totalPages) setCurrentPage(p);}} style={{width:50}} />
              <button disabled={currentPage === 1} onClick={() => {setCurrentPage(currentPage-1); setPageInput((currentPage-1).toString());}}>Prev</button>
              <button disabled={currentPage >= totalPages} onClick={() => {setCurrentPage(currentPage+1); setPageInput((currentPage+1).toString());}}>Next</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default App;