# NaviPRO RallyOS — Analisis dan Pelaksanaan Lanjutan Audit

Tanggal tugas: 25 Oktober 2026, Asia/Makassar. Status: **LOCAL_REGRESSION_PASS / REAL_ENGINE_BLOCKED / NOT_RACE_READY**.

## 1. Kesimpulan dan batas pemeriksaan

**Fakta terverifikasi:** diagnosis utama kedua file audit masih berlaku: repository mempunyai kontrak dan prototipe, tetapi belum mempunyai alur operasional lengkap soal → rute tervalidasi → NaviPack → Driver. Pekerjaan ini telah menggabungkan tiga branch dalam baseline integrasi terpisah, memperbaiki bug geometri Valhalla, menambahkan workflow CI, menyatukan dependency pengujian, menyelaraskan platform, serta mengimplementasikan inti matematika waktu/kalibrasi dan demonstrasi jadwal ROTR.

**Penilaian engineering:** tahapan konsolidasi lebih mendesak daripada menambah teknologi donor atau layar baru. Semua komponen masih membutuhkan integrasi runtime dan bukti yang berbeda dari tes kontrak. Hasil tes lokal tidak menghilangkan blocker benchmark mesin routing nyata.

**Cakupan pemeriksaan ulang:** membaca penuh dua audit unggahan; mengikat tiga PR ke commit; menginspeksi routing, fixture, timing, UI registry, policy, dependency dan alat validasi; menjalankan tes baseline gabungan dan perubahan. Ini bukan audit keamanan menyeluruh, pembuktian semua algoritma donor, atau uji lapangan. Dokumen lama dan deskripsi PR tidak dipakai sebagai hasil eksekusi baru.

## 2. Sumber dan baseline yang tepat

| Sumber | Identitas |
|---|---|
| `Pasted text(1).txt` | SHA-256 `14dab7152d874914648205ec0fb8cd66001196b9b4ca3035e46946425394ead1` |
| `NaviPRO-RallyOS-Repository-Audit-2026-10-25(1).md` | SHA-256 `0b642df7c42f59095ac0b24ccd713f30bd4183bc4092e02735e15da83f85b83e` |
| Main | `af0f4e5292af388489a0514865e8b59cfd49b721`, 170 tracked files |
| PR #1 | `ca2290741fc5d7747fab84ed0d5f30b75fd758b7` |
| PR #2, di atas PR #1 | `d3d92933747cbd150d6283f6defd84e342169f09` |
| PR #3, dari main | `20bed1114ca0e051dc6b948d885f805d74c1940a` |
| Merge lokal PR #2 + PR #3 | `2b6be4f3c6c7ddc7ec37d2bbe31d07ad7439dc67` |
| Implementasi yang diuji | `7f38984245e58d838af36ac9e5ad3817db154036` |

PR #1 kini **non-draft**, berbeda dari audit unggahan, tetapi commit masih sama. PR #2 dan #3 masih draft saat diperiksa. Deskripsi PR #1 sendiri tetap meminta status draft dan menyatakan benchmark nyata belum selesai. Ketidaksesuaian metadata ini tidak menjadi alasan menganggap PR siap merge.

Publikasi memakai konektor GitHub karena Git HTTPS tidak memiliki kredensial container. Commit implementasi remote adalah `7dacaab32ea04bf8cd78ba7bd37964478b96e610`; tree `c3242ebe25818477ddb5b581ccec525f5c910ca3` identik dengan commit lokal yang diuji. Metadata commit berbeda; isi file tidak berbeda. [Binding publikasi](evidence/audit-20261025/publication-binding.json) mencatat kedua identitas tanpa mengganti receipt eksekusi lokal.

Metadata GitHub kembali menunjukkan repository **public**. Ini fakta visibilitas, bukan bukti ada kebocoran. Pekerjaan ini tidak mengubah visibilitas, branch protection, lisensi, atau data pengguna. Secret scan komprehensif dan keputusan lisensi root tetap tindak lanjut tersendiri.

## 3. Assessment temuan dan perubahan nyata

### A. Konsolidasi baseline dan dependency — selesai pada branch integrasi

PR #2 sudah membawa PR #1. Karena itu PR #2 menjadi basis, kemudian PR #3 digabung dengan mempertahankan riwayat kedua parent. Tidak ada konflik teks. Baseline gabungan **238 tes Python lulus** sebelum perbaikan baru; hasil branch terpisah tidak dijumlahkan.

`requirements-test.txt` sekarang menunjuk `requirements-test.lock`; tidak ada lagi dua rentang dependency yang berbeda. Lock yang sudah ada memasang dependency lengkap dalam virtual environment terisolasi. Versi terkunci; lock ini belum memakai hash untuk setiap wheel dan bukan SBOM atau audit CVE.

### B. Valhalla menerima geometri salah — diperbaiki, masih candidate-only

**Fakta kode sebelumnya:** `normalize_valhalla_route` menggabungkan titik leg yang tidak tersambung menjadi satu LineString. Array lokasi/`original_index` tidak membuktikan bahwa shape benar-benar mengikuti anchor itu. Fixture sebelumnya justru mengulang shape dekat `(0,0)` ketika input berada di Bali.

**Dampak:** garis penghubung buatan bisa muncul tanpa menambah jarak provider; urutan metadata A→B→C dapat menyertai geometri yang berbeda. Selisih jarak kecil atau nol tidak cukup mendeteksi kesalahan ini.

**Perubahan:**

- Titik akhir leg dan titik awal leg berikutnya harus identik pada representasi polyline6; gap ditolak, tidak dijembatani.
- Start/end setiap leg diperiksa terhadap anchor input yang sesuai urutan.
- Toleransi snapping kandidat dicatat bersama residual endpoint. Default 50 m adalah **pilihan engineering untuk ingest kandidat**, dapat diperketat/diganti pemanggil; bukan batas resmi event atau QG-14.
- Parameter snapping invalid ditolak sebelum transport. Hanya titik sambungan identik yang dibuang; loop dan kemunculan koordinat berulang tetap ada.
- Fixture diperbaiki dan regresi mencakup gap, leg tertukar, rute terbalik yang tetap kontinu, wilayah salah, snapping kecil, dan loop.

**Batas:** kedekatan tidak membuktikan jalan legal, sisi jalan, landmark fisik, atau directed-edge occurrence. Dua lintasan dengan endpoint sama masih membutuhkan pemeriksaan traversal. Keluaran tetap `CANDIDATE_REVIEW`, `route_authority=false`, `directed_traversal_status=NOT_VERIFIED`. Real-server compatibility belum diuji.

Kode: [Valhalla adapter](../../python/src/navipro_rallyos/route/valhalla_adapter.py) dan [regresi geometri](../../tests/contracts/test_valhalla_geometry.py).

### C. CI dan reproducibility — workflow tersedia, hasil hosted terpisah

[Workflow CI](../../.github/workflows/ci.yml) menjalankan Python 3.11/3.12, JavaScript Node 24, OpenAPI, registry spasial/Cesium, drift registry MCP dan pemeriksaan struktur prompt. Actions dipin ke commit; token hanya `contents: read`, credential checkout tidak disimpan, job memiliki timeout dan pembatalan run lama. Tidak ada deploy atau release.

`build_mcp_registry.py --check` sekarang menolak hasil generator yang berbeda tanpa menulis ulang file. `make verify` mencakup seluruh pemeriksaan di atas. Validator prompt memeriksa 9 identitas peran, file/binding, mode, contoh HOLD dan daftar kasus. Ini **bukan** evaluasi perilaku model atas 16 skenario.

Branch protection/required checks belum dikonfigurasi oleh perubahan ini. Workflow yang tersedia belum dengan sendirinya berarti suatu commit lulus GitHub Actions. Baca hasil hosted untuk head yang akan direview.

### D. Arsitektur hybrid — diselaraskan pada kontrak, aplikasi belum dibuat

[ADR-0001](../architecture/ADR-0001-HYBRID-PLATFORMS.md) menetapkan arah implementasi Navigator Web/PWA + Driver Android Native, mengikuti rekomendasi audit yang diminta untuk dilanjutkan. Registry naik ke versi 1.1.0; owner Page 1–3 berada pada `apps/navigator-web`, renderer Navigator MapLibre GL JS dan Driver MapLibre Native.

Placeholder Android Navigator menjadi pointer historis, sehingga tidak ada dua target Navigator aktif. SSOT, build plan, README dan tes kontrak diselaraskan. Integrasi TSD/Driver mempunyai batas service/bridge dan device adapter yang eksplisit.

**Asumsi desain:** browser target, ukuran penyimpanan, perangkat, transport lokal dan strategi offline PWA belum dibuktikan. PWA bukan bukti offline-ready. Transfer membutuhkan idempotency, revision/hash, otorisasi dan ACK penerima yang nyata. Driver LIVE tetap independen jaringan dan generative AI.

### E. Timing dan kalibrasi — kernel berjalan, solver event belum lengkap

`python/src/navipro_rallyos/timing/core.py` menggunakan integer mm/ms dan `Fraction` untuk rasio. Fungsi durasi, kecepatan, CF, raw→corrected dan corrected→raw terpisah. Input float/bool/string tidak dikonversi diam-diam menjadi satuan integer.

| Pemeriksaan | Hasil teruji |
|---|---|
| CF 10.000.000 / 9.410.000 mm | `1000/941` |
| Target corrected 10.790.000 mm → raw | `10.153.390 mm` = 10,15339 km |
| Target raw di atas → corrected | `10.790.000 mm` |
| 0,11 km / 1 menit | `33/5` = 6,6 km/jam |
| 10,790 km / 35 menit | `3237/175` km/jam; tidak dibulatkan untuk menghitung jadwal |
| Menggunakan tampilan 18,50 km/jam | Durasi 12.000/37 ms lebih singkat daripada 35 menit |

Draft schedule mengakumulasi durasi sumber, mempertahankan mode/sub, tidak menciptakan jarak A/E, dan menolak lintasan tengah malam tanpa model tanggal. CLI M1 menerima `--start-time` opsional; tanpa start tidak dibuat jam finish. Start pemanggil diberi status `CALLER_SUPPLIED_UNVERIFIED`, bukan jam resmi peserta.

**Belum diimplementasikan:** authority profile, clock-scale event, neutralisasi, semantik lengkap semua mode waktu, penalti/skor, pembulatan resmi, adapter `TimingComputeResult`, TSD ACK, dan QG-16 evaluator. Kernel bukan solver rute, bukan perintah kecepatan berkendara, dan tidak mengesahkan rilis.

## 4. Bukti verifikasi pada satu snapshot

[Receipt](evidence/audit-20261025/receipt.json) mengikat commit/tree, argv, environment, exit code, waktu eksekusi dan hash log. Worktree bersih saat pemeriksaan dimulai. Bukti ini mengikat commit implementasi; penambahan laporan sesudahnya hanya dokumentasi/bukti.

| Pemeriksaan | Hasil aktual |
|---|---|
| `make verify` — Python | **272 passed**, termasuk 34 kasus tambahan terhadap baseline gabungan 238 |
| JavaScript | **11 passed** |
| OpenAPI | **82 operations / 110 schemas** |
| Spatial / Cesium | **75 / 69 capabilities**, 9 operasi Cesium |
| MCP tanpa perubahan generator | **71 tools / 11 blocked operations** |
| Struktur prompt | **9 peran / 16 skenario**, perilaku model **NOT_EXECUTED** |
| `pip check` | Lulus |
| ROTR diagnostic CLI | **ARITHMETIC_VALID / ROUTE_UNRESOLVED** |
| Routing preflight | **BLOCKED**, exit 2: executable Docker tidak tersedia |

Environment lokal: Python **3.12.14**, Node **24.22.1**. Python 3.11 berada dalam matriks CI, tidak diklaim telah diuji lokal pada pekerjaan ini.

Demonstrasi ROTR menggunakan **asumsi start 10:00:00**: A selesai 10:02, B 10:27, C 10:47, D 11:09, E 12:00. Jarak yang diketahui hanya B–D = 19,60 km; total durasi A–E = 120 menit. Itu bukan total jarak fisik seluruh trayek. Waktu di atas adalah hasil aritmetika atas asumsi start, bukan jadwal resmi lomba. Hasil lengkap: [M1 summary](evidence/audit-20261025/m1-summary.json).

Docker OOM yang tercantum pada audit berasal dari host sebelumnya. Lingkungan sekarang gagal karena executable tidak tersedia; keduanya tidak disamakan. Tidak ada engine, graf nyata, benchmark performa, sensor, APK, atau data lapangan yang diklaim berhasil.

## 5. Kondisi lima surface setelah pekerjaan ini

| Surface | Kemajuan nyata | Gap tersisa |
|---|---|---|
| Page 1 | Parser ROTR, kernel waktu dan draft jadwal teruji | OCR umum, source review runtime, aturan event, UI dan TSD delivery |
| Page 2 | Adapter provider dan guard geometri; kepemilikan Web diputuskan | Graf nyata, directed solver, MapLibre UI, bukti fisik dan human confirm |
| Page 3 | Prompt/role/gate terintegrasi dan pemeriksaan statis otomatis | Authenticated tool execution, retrieval, voice dan evaluasi model |
| Driver Overview | Kontrak tetap satu Android app dengan paket read-only | Reader/signature verifier, map assets dan aplikasi |
| Driver Driving | Aturan immutable LIVE/off-route tetap dipertahankan | GNSS, cue FSM, monotonic timer, replay dan uji perangkat |

Sembilan donor tetap sumber kemampuan/prototipe; pekerjaan ini tidak mengubahnya menjadi sembilan integrasi produksi. REST API, location backend, evaluator 16 gate dan pack compiler belum beroperasi. Direktori `services/api`, `python/.../locations`, `python/.../validation` masih placeholder pada snapshot yang diperiksa.

## 6. Tanggung jawab delapan divisi

Nomor divisi tetap 1–8, dengan role 2–9. Orchestrator adalah role 1 dan tidak dihitung sebagai divisi kesembilan.

| Divisi | Hasil yang kini tersedia/harus dikonsumsi | Kewenangan tetap |
|---|---|---|
| 1 Roadbook | Parser, sumber mentah, urutan dan occurrence | Interpretasi proposal; cakupan sumber masih perlu review |
| 2 TSD | Kernel rasional, CF dan draft jadwal | Diagnosis; tidak menetapkan aturan atau skor resmi |
| 3 Route | Kandidat dengan guard kontinuitas/endpoint | Proposal; tidak menganggap proximity sebagai directed proof |
| 4 Location | Kontrak tiga entitas lokasi dan provenance | Kandidat/evidence; belum ada write service persisten |
| 5 Progress | Kontrak/replay assessment | Tidak mengambil alih GNSS/progres LIVE |
| 6 Guidance | Kontrak review cue | Tidak menjalankan cue FSM generatif LIVE |
| 7 Quality | Laporan gate, negative tests dan permintaan validasi | Tidak mengotorisasi PASS atau review sendiri |
| 8 Journal | Revisi, sumber dan receipt pengujian engineering | Runtime journal/write ACK belum tersedia |

Registry dan prompt menyediakan pembagian tugas; tidak ada delapan agent yang dijalankan atau diberi kredensial oleh pekerjaan ini. Semua 16 gate tetap kontrak; guard adapter dan tes bukan pengganti evaluator rilis. Satu blocking FAIL/NOT_RUN tetap mengharuskan HOLD.

## 7. Status prioritas audit dan pekerjaan berikutnya

| Prioritas | Status setelah patch | Syarat selesai berikutnya |
|---|---|---|
| P0.1 Konsolidasi | **Selesai di branch review; main belum berubah** | Review baseline gabungan, hasil hosted, real-engine evidence sebelum merge |
| P0.2 CI/lock | **Workflow + satu lock tersedia** | Run hosted pada head; required checks, secret scan dan SBOM masih tindak lanjut |
| P0.3 Platform | **ADR + registry/owner konsisten** | Implementasi browser/Android dan pengujian batas device |
| P0.4 Domain/timing | **Parsial: kernel deterministik** | Aturan event berversi, corpus parser umum, coverage ledger lengkap, directed solver |
| P0.5 Real routing | **BLOCKED** | Host Docker sehat, PBF/admin yang layak, graf identik berversi, native route capture |
| P1.1 Lokasi | **Belum diimplementasikan** | Database/provenance, physical/access separation, idempotent observation, human decision dan receipt |
| P1.2–P1.4 Workbench/agent | **Kontrak, bukan UI/runtime** | Input → draft schedule → candidate → evidence review pada layanan nyata |
| P2 NaviPack/Driver | **Belum diimplementasikan** | 16 evaluator + auth + signing/verifier + delivery ACK + offline replay |

Urutan berikutnya: pulihkan lingkungan benchmark dan data → buktikan provider menghasilkan geometri/manuver nyata → bangun domain/coverage dan layanan bukti → integrasikan Page 1/2 → implementasikan gate/auth/pack → uji Driver offline. Lokasi yang tidak ada di peta harus tetap berada dalam ledger dan antrean verifikasi; confidence tinggi tidak menggantikan bukti fisik atau receipt penyimpanan.

**Keputusan review:** patch konsolidasi layak diperiksa sebagai kemajuan engineering dengan bukti lokal. Merge/release/aktivasi lomba tetap **HOLD** sampai syarat yang berlaku terpenuhi. Tidak ada perubahan `main`, penggabungan PR remote, deployment, atau pengesahan rute oleh pekerjaan ini.
