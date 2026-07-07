import Papa from 'papaparse';

// Fungsi untuk menarik dan mem-parsing CSV dari GitHub
export const ambilDataDariGitHub = (klpdId, instansiKode) => {
  return new Promise((resolve, reject) => {
    // Merakit URL Raw persis seperti struktur folder di GitHub Anda
    const url = `https://raw.githubusercontent.com/agitkasep/inaprocdata/main/filecsv/klpd${klpdId}/klpd${klpdId}instansi${instansiKode}.csv`;

    Papa.parse(url, {
      download: true,       // Menginstruksikan PapaParse untuk mengunduh dari URL
      header: true,         // Mengubah baris pertama CSV menjadi kunci (key) JSON
      skipEmptyLines: true, // Mengabaikan baris kosong di akhir file
      complete: (results) => {
        // Jika sukses, data JSON siap digunakan
        resolve(results.data);
      },
      error: (error) => {
        // Jika gagal (misal file tidak ditemukan/koneksi putus)
        console.error("Gagal menarik data dari GitHub:", error);
        reject(error);
      }
    });
  });
};