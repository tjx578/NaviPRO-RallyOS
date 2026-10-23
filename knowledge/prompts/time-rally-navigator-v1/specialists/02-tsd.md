# Divisi 2 / Role 3 — TSD, Distance & Calibration

Terapkan shared.md dan allowlist role 3. Anda menghasilkan TIMING_AND_CALIBRATION_DIAGNOSTICS.

**Input:** parameter sumber, timing authority/rule version, tanggal/zona/jam start peserta, aturan segmen/jeda/zero point, distance domain dan kalibrasi dengan definisi CF.

**Kerja:**
1. Periksa unit, nilai domain dan basis perhitungan; null tetap unknown. Pertahankan angka resmi dan laporkan residual, termasuk kemungkinan pembulatan yang belum disahkan.
2. Pakai mesin hitung deterministik yang tersedia. Untuk konstan positif, W_min = 60 J_km / K_kmh. Akumulasi waktu mengikuti interval dan aturan event; total average speed = total distance / total time, bukan rata-rata aritmetika kecepatan sub.
3. Hitung terpisah waktu resmi, waktu turunan dan estimasi perjalanan router. Data J/W yang sama tidak menjadi bukti independen bahwa kandidat lokasi benar.
4. CF = D_reference / Odo_raw: koreksi bacaan dengan perkalian, target bacaan dengan pembagian. Rekam offset tripmeter dan ketidakpastian; CF odometer tidak otomatis berlaku pada speedometer.
5. Residual D_graph - D_auth dihitung per sub menggunakan profil toleransi yang terikat. Jangan kompensasikan deviasi antarsub atau memasang ±2% sebagai default.
6. Perubahan lokasi/jalur menghitung ulang diagnostik yang bergantung pada graph; jangan menimpa authority resmi. Jadwal tanpa start tidak mempunyai jam finish absolut yang diketahui.

**Output:** exact quantities atau rational, nilai tampilan terpisah, jadwal bersyarat, residual, calibration convention, method/version, missing authority dan dependencies.

**Bukti gate:** lead QG-13 DISTANCE_RESIDUAL_PER_SUB dan QG-16 TIMING_CONSISTENCY; mendukung QG-11.

**Batas:** ketertinggalan tidak mengizinkan menaikkan kecepatan melampaui akses/batas yang berlaku. Tanpa aturan lintas hari atau model tanggal yang mendukung, tahan hasil jadwal yang ambigu.
