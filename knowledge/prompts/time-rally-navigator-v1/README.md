# NaviPRO Time Rally Navigator — prompt pack v1.0.0

**Status: TEMPLATE_ONLY.** Tanggal assessment: 23 Oktober 2026. Paket ini menyesuaikan prompt pengguna dengan satu Orchestrator dan delapan spesialis NaviPRO. Ini adalah materi instruksi dan contoh proposal; tidak memasang agent, menjalankan gate compiler atau mengaktifkan Driver.

## Assessment prompt awal

**Fakta yang diperiksa:** prompt awal mempunyai struktur input, perhitungan jadwal, pencarian PAL, regulasi dan output YAML. Delapan divisi serta 16 gate mengacu pada kontrak repo di commit `66128fdf67b6d75b942293c60ef0ff84197acc3e` (branch draft PR #3 pada saat assessment). Registry tersebut masih CONTRACT_ONLY. Referensi lampiran yang benar-benar diperiksa dicatat dengan SHA-256 di [manifest](manifest.yaml); judul referensi lain dalam prompt pengguna tidak dianggap telah dibaca.

**Penilaian desain:** kerangka awal dapat dipakai, dengan koreksi berikut sebelum dijadikan instruksi agent.

| Bagian awal | Masalah | Penyesuaian |
| --- | --- | --- |
| Satu persona mengerjakan seluruh navigasi | Tanggung jawab, izin dan handoff belum jelas | Shared policy + Orchestrator + 8 prompt spesialis; role ID mengikuti registry |
| Rantai tetap validasi -> jadwal -> peta -> penyesuaian kecepatan | Dependensi nyata bisa berbeda; konflik lokasi perlu loop kembali | Task graph adaptif, hasil terikat revisi, single state integrator |
| Mind map / penalaran eksplisit | Dapat menghasilkan uraian panjang tanpa bukti keputusan | Lima tahap AMRA dengan ringkasan fakta, dependensi, kalkulasi, konflik dan keputusan yang bisa diaudit |
| IMI 2025 dan nama file internal | Tahun/judul saja tidak membuktikan aturan berlaku atau dokumen tersedia | Event/year/rule version dan sumber yang diperiksa; gap dinyatakan |
| Dilarang keluar kabupaten/kota | Dapat menolak lintasan resmi lintas wilayah | Ikuti batas/koridor yang ditetapkan sumber event; lokasi lintas wilayah tetap diuji |
| Google Maps/Wikimapia untuk konfirmasi | Pin/link pencarian belum membuktikan objek dan jalur | Pisahkan kandidat, identitas fisik, akses, binding dan verification |
| `status_validasi: valid` | Satu boolean/label menggabungkan matematika, fisik, akses dan rilis | Status per dimensi; report resmi hanya dari validator, data belum lengkap tetap HOLD |
| Jangan membuat asumsi di luar soal | Hipotesis disambiguasi tetap diperlukan ketika soal ambigu | Asumsi eksplisit dan bersyarat, tidak dinaikkan menjadi fakta/otoritas |
| Semua estimasi dari jarak/waktu aktual | Angka soal dan estimasi router berbeda dari pengukuran kendaraan | Pisahkan sumber resmi, graph, odometer, geodesi, kalkulasi turunan dan observasi |
| YAML siap automation | Parseable belum berarti cocok schema consumer atau lolos gate | Contoh ANALYSIS_PROPOSAL; adapter kanonis dan validation diperlukan |
| Memenangkan setiap putaran | Tidak dapat dijamin oleh prompt | Sasaran terukur: kelengkapan instruksi, ketepatan TSD, bukti lokasi dan kepatuhan |

**Konflik pada bahan lama yang tidak diadopsi:** `sistem-analitis-time-rally.md` menggeneralisasi pembulatan waktu ke menit bulat dan mengabaikan jarak start-ke-zero. Framework advanced membalik arah penggunaan CF pada target odometer serta membawa konstanta gate dan klaim verifikasi yang belum terbukti pada repo ini. Aturan baru mempertahankan data resmi, memakai profile event, dan membagi target raw odometer dengan CF apabila definisinya `D_reference / Odo_raw`. Struktur AMRA dipertahankan; angka/pernyataan lama tidak otomatis menjadi otoritas.

## Peta file dan tanggung jawab

| Divisi / role | Prompt | Kontribusi gate |
| --- | --- | --- |
| Bersama | [shared.md](shared.md) | Bukti, unit, mode, coverage, authority, output |
| Orchestrator / 1 | [orchestrator.md](orchestrator.md) | Integrasi state dan dependency, tanpa menetapkan gate PASS |
| 1 / 2 | [Roadbook](specialists/01-roadbook.md) | QG-02/05/06 |
| 2 / 3 | [TSD](specialists/02-tsd.md) | QG-13/16 |
| 3 / 4 | [Route](specialists/03-route.md) | QG-09/10/11/12/14/15 |
| 4 / 5 | [Location](specialists/04-location.md) | QG-07/08 |
| 5 / 6 | [Progress](specialists/05-progress.md) | Bukti/replay pendukung, bukan GPS melalui LLM |
| 6 / 7 | [Guidance](specialists/06-guidance.md) | Review coverage/urutan/timing cue |
| 7 / 8 | [Quality](specialists/07-quality.md) | QG-01/04 dan audit lintas gate |
| 8 / 9 | [Journal](specialists/08-journal.md) | QG-03 serta provenance/receipt |

Gate pada tabel adalah tanggung jawab bukti. Evaluator deterministik menghitung hasil; authenticated reviewer dan release manager mempunyai kewenangan terpisah. Dua divisi bernama Live Position dan Guidance tidak memberi izin LLM di loop kendaraan. Current cockpit policy membatasi generative agent ke PREP/REVIEW.

## Cara memakai template

1. **Satu assistant:** muat `shared.md` dan `orchestrator.md` sebagai instruksi yang disusun bersama. Sediakan prompt spesialis yang relevan sebagai konteks tugas. Bila tidak ada agent runtime, gunakan delapan pembagian pekerjaan sebagai checklist dan nyatakan eksekusi berlangsung pada satu assistant.
2. **Host multi-agent:** susun `shared.md` + tepat satu prompt peran + task-scoped context sesuai `manifest.yaml`. Host harus menegakkan allowlist, schema, revision check, timeout dan idempotency. Manifest ini belum merupakan loader atau konfigurasi SDK.
3. **Retrieval:** pilih bagian berdasarkan tugas (roadbook, timing, geospatial, access, replay, cue, journal), event/year, revision dan source authority. Jangan menyuntikkan semua dokumen atau seluruh riwayat ke tiap peran. Referensi historis boleh membantu pencarian, dengan umur bukti dan aturan event baru diperiksa.
4. **Handoff:** gunakan field request/response dari `governance/agent-divisions.yaml`. COMPLETE/PARTIAL/CONFLICT/UNAVAILABLE adalah status tugas; bukan PASS gate atau receipt penyimpanan. Jangan mengirim schema contoh analisis langsung ke endpoint kanonis.
5. **Penyimpanan lokasi:** current role 9 belum memiliki API write journal pribadi. Prompt menyediakan perilaku target serta respons capability gap; penyimpanan baru boleh diklaim ketika tool berizin memberikan receipt. Izin pengguna menyimpan tidak menciptakan API atau sensor yang belum ada.

Struktur ini dapat menjadi bahan instruksi Custom GPT atau agent host. Integrasi produk, batas input provider dan konfigurasi tool tetap harus mengikuti lingkungan target yang benar-benar digunakan; paket ini tidak mengonfigurasi akun atau aplikasi tersebut.

## Contoh hasil terkoreksi

[subtrayek-a.analysis.yaml](examples/subtrayek-a.analysis.yaml) mengolah contoh pengguna: J=0.11 km dan W=1 menit memberi rasio aritmetika **6.6 km/jam**, dengan asumsi keduanya mengacu segmen yang sama. Ini bukan perintah kecepatan kendaraan atau bukti aturan zero point. Tanpa jam start, finish absolut tetap null. Identitas start/finish, DSL `SL`, rute dan profil event belum terverifikasi; eligibility rilis **HOLD**.

URL pencarian Pasar Kliwon disimpan sebagai referensi yang belum dibuka. Contoh ini tidak mengklaim telah melakukan survei/geocoding rute Solo. Contoh ID semuanya berawalan DEMO atau merupakan label sumber contoh.

## Verifikasi dan batas klaim

- Pemeriksaan statis pada 23 Oktober 2026 **PASS**: YAML, 10 file prompt, sembilan role/delapan division IDs, referensi policy, field handoff contoh, link lokal, empat digest lampiran dan aritmetika contoh cocok. Ini memeriksa konsistensi artefak, bukan perilaku model.
- [eval-cases.yaml](eval-cases.yaml) berisi 16 kasus penerimaan: CP hilang dari peta, skor tanpa bukti, batas wilayah, PAL ambigu, CF, timing conflict, gate duplikat, stale handoff, database tanpa write API, posisi kendaraan vs objek, LIVE, prompt injection, judul referensi saja, fase lampu tidak diketahui, dan kunjungan berulang.
- Status evaluasi perilaku model dan lapangan **NOT_EXECUTED**. Jumlah kasus ini tidak berarti 16 quality gate sudah dieksekusi. Hasil 118 tes kontrak pada perubahan gate sebelumnya juga bukan bukti kualitas prompt atau kesiapan lomba.

Tidak ada framework/model/dependency baru yang ditambahkan untuk template ini. Integrasi runtime dan evaluasi model memerlukan pekerjaan serta bukti tersendiri.
