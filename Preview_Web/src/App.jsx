import { useState, useRef } from 'react'; // Tambahkan useRef
import axios from 'axios';
import './index.css';

function App() {
  // ... state lainnya tetap sama ...
  const [data, setData] = useState([]);
  const [activeTab, setActiveTab] = useState('Realisasi');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageInput, setPageInput] = useState('1');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const rowsPerPage = 20;

  // Logika Drag-to-Scroll
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
    const walk = (x - startX) * 2; // Kecepatan scroll
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  // ... (fungsi formatRupiah, kementerianList, handleFetch tetap sama) ...
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

  // ... (kementerianList dan handleFetch di sini) ...
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

  const handleFetch = async (kode) => {
    if (!kode) return;
    setLoading(true);
    setCurrentPage(1); setSearchTerm(''); setPageInput('1');
    try { 
      const res = await axios.get(`/data/${kode}.json?t=${Date.now()}`); 
      setData(res.data); 
    } catch (e) { console.error(e); setData([]); } finally { setLoading(false); }
  };

  return (
    <div className="container">
      {/* ... header & filter box sama ... */}
      <header className="hero-header">
        <h1>DATA INAPROC 2026</h1>
        <input className="search-bar" placeholder="Pencarian pintar..." value={searchTerm} onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); setPageInput('1'); }} />
      </header>

      <div className="tab-container">
        <button className={activeTab === 'RUP' ? 'active' : ''} onClick={() => {setActiveTab('RUP'); setData([]);}}>Rencana Umum Pengadaan</button>
        <button className={activeTab === 'Realisasi' ? 'active' : ''} onClick={() => {setActiveTab('Realisasi'); setData([]);}}>Realisasi</button>
      </div>

      <div className="filter-box">
        <div><label>JENIS INSTANSI</label><br/><select><option>Kementerian</option></select></div>
        <div><label>INSTANSI</label><br/><select onChange={(e) => handleFetch(e.target.value)}><option value="">-- Pilih Instansi --</option>{kementerianList.map(k => <option key={k.kode} value={k.kode}>{k.nama}</option>)}</select></div>
      </div>

      {loading ? <div className="loading">Memuat data...</div> : (
        // Pasang ref dan handler di sini
        <div 
          className="table-wrapper"
          ref={scrollRef}
          onMouseDown={handleMouseDown}
          onMouseLeave={handleMouseLeave}
          onMouseUp={handleMouseUp}
          onMouseMove={handleMouseMove}
        >
          <table>
            {/* ... isi tabel sama ... */}
            <thead>
              <tr>
                <th>No</th><th>Nama Instansi</th><th>Nama Satuan Kerja</th><th>Kode Paket</th><th>Kode RUP</th><th>Tahun Anggaran</th>
                <th>Sumber Transaksi</th><th>Sumber Dana</th><th>Nama Penyedia</th><th>Metode Pengadaan</th><th>Jenis Pengadaan</th>
                <th>Nama Paket</th><th>Status Paket</th><th>Total Nilai (Rp)</th><th>Nilai PDN (Rp)</th>
              </tr>
            </thead>
            <tbody>
              {currentRows.map((item, i) => (
                <tr key={i}>
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