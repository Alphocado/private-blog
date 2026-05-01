# 📝 Blog Manager — Static Site Generator dengan GUI

Sebuah aplikasi desktop sederhana berbasis Python + Tkinter untuk membuat, mengedit, dan menghapus postingan blog. Hasil akhirnya berupa website statis murni yang siap di-hosting di **GitHub Pages** (atau hosting statis lainnya).

**Tidak pakai Jekyll, tidak pakai database.**  
Semua postingan disimpan dalam folder dan file HTML biasa, lalu sebuah builder akan merangkai `index.html` secara otomatis setiap kali ada perubahan.

---

## 🧱 Struktur Proyek

```
blog-project/
├── build_site.py        # Program pembangun index.html
├── gui_app.py           # Aplikasi GUI untuk mengelola blog
├── style.css            # Tampilan blog (untuk index & halaman post)
├── index.html           # (otomatis dibuat) Halaman depan blog
├── README.md            # Kamu sedang membaca ini
└── posts/               # Folder penyimpanan semua postingan
    ├── 2026-05-02/
    │   ├── halo-dunia.html
    │   └── belajar-git.html
    └── 2026-05-03/
        └── python-asyik.html
```

### Penjelasan Masing-masing File

| File            | Fungsi                                                                                                                                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gui_app.py`    | Aplikasi GUI utama. Menyediakan form untuk membuat, mengedit, dan menghapus post. Setiap aksi akan otomatis membangun ulang `index.html` dan melakukan `git push`.                                                        |
| `build_site.py` | Modul yang berisi fungsi `build_index()`. Bertugas membaca semua folder di `posts/`, mengambil informasi (judul, excerpt, tanggal) dari setiap file `.html`, lalu menulis `index.html` dengan daftar postingan yang rapi. |
| `style.css`     | Stylesheet tunggal untuk seluruh blog. Digunakan oleh `index.html` dan setiap halaman post (via tautan `../../style.css`).                                                                                                |
| `index.html`    | Halaman depan yang di-generate otomatis. Tidak perlu diedit manual. Berisi daftar semua postingan dalam bentuk kartu yang menarik.                                                                                        |
| `posts/`        | Folder tempat semua postingan disimpan. Setiap postingan diletakkan dalam subfolder dengan format **YYYY-MM-DD** (tanggal posting). Di dalamnya ada 1 atau lebih file `.html` dengan nama sesuai slug judul.              |

---

## 🚀 Cara Menjalankan

### Persyaratan

- **Python 3.7+** terpasang di komputer kamu.
- **Git** (jika ingin fitur push otomatis).
- Modul Python: `tkinter` (biasanya sudah bawaan Python).

> ⚠️ **Catatan untuk Linux**: Jika tkinter belum terpasang, instal dengan  
> `sudo apt-get install python3-tk` (Ubuntu/Debian) atau sesuai distro.

### Langkah 1: Clone atau buat folder proyek

```bash
git clone <repo-kamu> blog-project
cd blog-project
```

Atau buat folder kosong dan salin semua file ke dalamnya.

### Langkah 2: Jalankan GUI

```bash
python gui_app.py
```

Akan muncul jendela **Blog Manager**.

---

## ✍️ Cara Menggunakan

### Membuat Post Baru

1. Klik tombol **🆕 Post Baru**.
2. Isi:
   - **Judul**: judul artikel (otomatis jadi slug nama file).
   - **Tanggal**: format `YYYY-MM-DD` (default hari ini).
   - **Ringkasan / Excerpt**: kalimat pendek untuk preview di halaman depan.
   - **Konten**: isi artikel, bisa HTML atau teks biasa.
3. Klik **Simpan**.
4. Aplikasi akan:
   - Membuat folder `posts/YYYY-MM-DD/` bila belum ada.
   - Menyimpan file HTML (contoh: `judul-artikel.html`).
   - Membangun ulang `index.html` agar memuat postingan baru.
   - Melakukan `git add . && git commit && git push` (jika folder ini adalah repo Git).
5. Daftar postingan di GUI langsung diperbarui.

### Mengedit Post

1. Klik salah satu postingan di daftar sebelah kiri.
2. Klik tombol **✏️ Edit Post**.
3. Ubah data yang diinginkan (judul, ringkasan, konten).
4. Klik **Simpan**.
5. Aplikasi akan memperbarui file, merebuild `index.html`, dan push otomatis.

### Menghapus Post

1. Pilih postingan di daftar.
2. Klik **🗑️ Hapus Post**.
3. Konfirmasi penghapusan.
4. File akan dihapus, folder tanggal akan ikut terhapus jika kosong, lalu rebuild & push otomatis.

### Melihat Daftar Post Terbaru

Tombol **🔄 Refresh Daftar** akan membaca ulang folder `posts/` tanpa rebuild atau git push. Berguna jika kamu melakukan perubahan manual di luar GUI.

### Build & Push Manual

Tombol **🚀 Build & Git Push** menjalankan `build_index()` diikuti `git add . && git commit && git push`. Berguna untuk memastikan semuanya sinkron.

---

## 🌐 Cara Deploy ke GitHub Pages

1. **Inisialisasi Git** (jika belum):
   ```bash
   git init
   git remote add origin https://github.com/username/namarepo.git
   ```
2. **Set GitHub Pages**:
   - Buka repositori di GitHub → **Settings** → **Pages**.
   - Pilih branch `main` (atau `master`) dan folder root `/`.
   - Simpan.
3. **Push pertama** bisa melalui GUI (tombol Build & Git Push) atau manual:
   ```bash
   git add -A
   git commit -m "Initial commit"
   git push -u origin main
   ```
4. Website akan tersedia di `https://username.github.io/namarepo/`.

Karena struktur kita sederhana (file HTML statis), GitHub Pages bisa langsung menyajikannya tanpa proses build tambahan.

> 📌 **Penting**: Pastikan file `style.css` dan folder `posts/` ikut ter-push. Path CSS di setiap post menggunakan `../../style.css` agar tetap bekerja di GitHub Pages.

---

## 🔄 Alur Kerja Otomatis

```
[ GUI ] → Create / Edit / Delete Post
     ↓
Simpan file HTML di posts/YYYY-MM-DD/
     ↓
build_index() → scan semua folder & file → tulis ulang index.html
     ↓
git add . → git commit → git push
```

Tidak ada database, tidak ada server-side scripting. Semuanya dilakukan oleh program Python di sisi lokal.

---

## ❓ Troubleshooting

| Masalah                                     | Solusi                                                                                                                                                                                       |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GUI tidak muncul**                        | Pastikan Python 3 terinstal dan tkinter tersedia. Jalankan `python gui_app.py` dari terminal untuk melihat error.                                                                            |
| **Hanya satu post muncul di index.html**    | Pastikan kamu menggunakan versi terbaru `build_site.py` yang sudah mendukung banyak file dalam satu folder. Jangan gunakan versi yang hanya membaca `html_files[0]`.                         |
| **CSS tidak termuat di halaman post**       | Cek path di file HTML post: harus berisi `<link rel="stylesheet" href="../../style.css">`. Jika masih polos, buka Developer Tools (F12) untuk melihat error 404.                             |
| **Git push gagal**                          | Pastikan folder sudah diinisialisasi git (`git init`), remote sudah diatur, dan kamu memiliki akses push. GUI akan menampilkan pesan error dari git.                                         |
| **Error "Git tidak ditemukan"**             | Install Git dari [git-scm.com](https://git-scm.com/) dan pastikan bisa dipanggil dari terminal (masuk PATH).                                                                                 |
| **Tanggal di index.html tidak sesuai**      | Format folder harus persis `YYYY-MM-DD` (misal `2026-05-02`). Jika tidak, tampilan tanggal akan fallback ke nama folder.                                                                     |
| **Ingin mengubah judul blog**               | Edit variabel `<h1>Blog Saya</h1>` di `HTML_TEMPLATE` dalam `build_site.py`, lalu rebuild.                                                                                                   |
| **Ingin menambah footer / navigasi**        | Edit `HTML_TEMPLATE` di `build_site.py`, tambahkan HTML yang diinginkan, lalu rebuild. Semua halaman post juga bisa kamu sesuaikan templatenya di `gui_app.py` (fungsi `get_html_template`). |
| **File post bertumpuk di folder yang sama** | Memang sengaja: satu folder tanggal bisa berisi beberapa postingan (misalnya beberapa artikel di hari yang sama). Semuanya akan tampil di index. Tidak ada batasan.                          |

---

## 🎨 Kustomisasi Tampilan

Kamu bisa mengubah `style.css` sesuai selera. CSS ini dipakai oleh:

- **index.html** (daftar post)
- **halaman post** (detail artikel)

Beberapa ide kustomisasi:

- Ganti warna latar: ubah `background-color` pada `body`.
- Ganti font: ubah `font-family` di `body`.
- Ubah ukuran kartu: atur `max-width`, `padding`, dll.
- Tambahkan dark mode: gunakan CSS variables dan kelas `.dark`.

Template HTML post bisa kamu temukan di fungsi `get_html_template()` di `gui_app.py`. Ubah di sana jika ingin menambahkan kelas atau struktur baru.

Template `index.html` ada di variabel `HTML_TEMPLATE` di `build_site.py`.

---

## 📄 Lisensi

Proyek ini bebas digunakan untuk keperluan pribadi maupun belajar. Tidak ada lisensi khusus. Kamu bebas memodifikasi dan menyebarluaskannya.

---

## 🧠 Konsep Dasar

Blog ini menganut filosofi **"semua adalah file"**. Tidak ada database rumit, tidak ada ketergantungan pada framework, sehingga:

- Mudah dipahami siapa saja.
- Bisa di-deploy hanya dengan meng-upload file statis.
- Proses edit dilakukan melalui GUI yang langsung menyentuh file.
- Cocok untuk penulis tunggal atau proyek dokumentasi pribadi.

Jika suatu saat kamu ingin pindah ke generator lain, file postinganmu sudah berupa HTML lengkap – tinggal diimpor.

---

## 🤝 Kontribusi

Kamu bisa mengembangkan sendiri. Beberapa ide pengembangan:

- Menambahkan field tags/kategori.
- Navigasi bulan atau arsip.
- Dark mode otomatis.
- Preview gambar.
- Backup otomatis sebelum push.

---

Dibuat oleh Alphocado. Selamat ngeblog!
