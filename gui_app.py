import tkinter as tk
from tkinter import messagebox, simpledialog, scrolledtext
import os
import re
import subprocess
from datetime import datetime
from build_site import build_index, POSTS_DIR

class BlogGUI:
    def __init__(self, root):
        self.root = root
        root.title("Blog Manager - Static Site Generator")
        root.geometry("700x500")

        # Frame kiri: daftar post
        left_frame = tk.Frame(root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Daftar Post", font=('Arial', 14, 'bold')).pack(pady=5)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Frame kanan: tombol aksi
        right_frame = tk.Frame(root, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(right_frame, text="🆕 Post Baru", command=self.create_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="✏️ Edit Post", command=self.edit_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🗑️ Hapus Post", command=self.delete_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🔄 Refresh Daftar", command=self.refresh_list, width=15).pack(pady=20)
        tk.Button(right_frame, text="🚀 Build & Git Push", command=self.build_and_push, width=15, bg='lightgreen').pack(pady=5)

        # Muat daftar saat pertama
        self.refresh_list()

    # =====================
    # Fungsi-fungsi helper
    # =====================
    def slugify(self, text):
        """Mengubah judul menjadi nama file: huruf kecil, spasi -> '-'."""
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)   # hapus karakter aneh
        slug = re.sub(r'[-\s]+', '-', slug)     # spasi & - berulang jadi satu -
        return slug.strip('-')

    def get_html_template(self, title, date_display, excerpt, content):
        """Menghasilkan kode HTML satu post lengkap."""
        return f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{excerpt}">
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
  <main class="container">
    <article class="post">
      <h1>{title}</h1>
      <p class="post-meta">{date_display}</p>
      <div class="post-content">
        {content}
      </div>
    </article>
  </main>
  <footer style="text-align:center; margin-top:3rem; color:#888;">
  <p>© 2026 Blog Alphocado</p>
</footer>
</body>
</html>'''

    def parse_post_file(self, filepath, folder_date):
        """Membaca file HTML dan mengembalikan dict title, excerpt, content."""
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()

        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''

        desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
        excerpt = desc_match.group(1).strip() if desc_match else ''

        # Ambil konten di dalam <div class="post-content">
        content_match = re.search(r'<div class="post-content">(.*?)</div>', html, re.DOTALL)
        content = content_match.group(1).strip() if content_match else ''

        return {
            'title': title,
            'excerpt': excerpt,
            'content': content,
            'date': folder_date
        }

    # =====================
    # Operasi Post
    # =====================
    def create_post(self):
        dialog = PostDialog(self.root, "Buat Post Baru")
        self.root.wait_window(dialog.top)
        if dialog.result:
            title, date_str, excerpt, content = dialog.result
            # Buat folder YYYY-MM-DD
            folder_name = date_str
            folder_path = os.path.join(POSTS_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # Nama file slug
            filename = self.slugify(title) + '.html'
            filepath = os.path.join(folder_path, filename)

            # Format tanggal tampilan
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            bulan = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"

            html = self.get_html_template(title, date_display, excerpt, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Rebuild dan refresh
            build_index()
            self.refresh_list()
            messagebox.showinfo("Sukses", f"Post '{title}' berhasil dibuat!")

    def edit_post(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Pilih post", "Silakan pilih post yang ingin diedit.")
            return
        idx = selection[0]
        post = self.posts[idx]

        # Baca file yang sudah ada
        folder_path = os.path.join(POSTS_DIR, post['folder'])
        filepath = os.path.join(folder_path, post['filename'])
        if not os.path.exists(filepath):
            messagebox.showerror("Error", "File post tidak ditemukan.")
            return
        data = self.parse_post_file(filepath, post['folder'])

        # Tampilkan dialog edit
        dialog = PostDialog(self.root, "Edit Post", data=data)
        self.root.wait_window(dialog.top)
        if dialog.result:
            new_title, new_date, new_excerpt, new_content = dialog.result
            # Update file
            # Jika judul berubah, rename file
            new_filename = self.slugify(new_title) + '.html'
            # Jika tanggal berubah, mungkin harus pindah folder (hanya jika beda)
            # Untuk sederhana, kita dukung judul saja yang berubah; tanggal tetap
            # Atau kalau tanggal juga berubah, kita bisa pindah file, tapi hati2.
            # Di sini saya biarkan tanggal lama saja; jika user ubah tanggal, kita abaikan.
            # Anda bisa mengembangkannya nanti.
            # Gunakan tanggal dari folder asli
            date_obj = datetime.strptime(post['folder'], '%Y-%m-%d')
            bulan = [
                'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
            ]
            date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"

            html = self.get_html_template(new_title, date_display, new_excerpt, new_content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Rename file jika judul berubah
            if new_filename != post['filename']:
                new_path = os.path.join(folder_path, new_filename)
                os.rename(filepath, new_path)

            build_index()
            self.refresh_list()
            messagebox.showinfo("Sukses", "Post berhasil diperbarui!")

    def delete_post(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        post = self.posts[idx]
        if messagebox.askyesno("Konfirmasi", f"Hapus post '{post['title']}'?"):
            folder_path = os.path.join(POSTS_DIR, post['folder'])
            filepath = os.path.join(folder_path, post['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
                # Hapus folder jika kosong
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
            build_index()
            self.refresh_list()
            messagebox.showinfo("Sukses", "Post dihapus.")

    def refresh_list(self):
        """Mengambil daftar post dari folder dan menampilkan di listbox."""
        self.listbox.delete(0, tk.END)
        self.posts = []

        if not os.path.isdir(POSTS_DIR):
            os.makedirs(POSTS_DIR)

        # Urutkan folder terbaru dulu
        folders = sorted(os.listdir(POSTS_DIR), reverse=True)
        for folder in folders:
            folder_path = os.path.join(POSTS_DIR, folder)
            if not os.path.isdir(folder_path):
                continue
            for f in os.listdir(folder_path):
                if f.endswith('.html'):
                    file_path = os.path.join(folder_path, f)
                    # Ambil judul dari file
                    data = self.parse_post_file(file_path, folder)
                    display = f"[{folder}] {data['title']}"
                    self.listbox.insert(tk.END, display)
                    self.posts.append({
                        'title': data['title'],
                        'folder': folder,
                        'filename': f
                    })

    def on_select(self, event):
        # Tidak digunakan, tapi bisa untuk preview nanti
        pass

    def build_and_push(self):
        build_index()
        # Jalankan git add, commit, push
        try:
            subprocess.run(['git', 'add', '-A'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Update blog: rebuild dan push otomatis'], check=True)
            subprocess.run(['git', 'push'], check=True)
            messagebox.showinfo("Sukses", "Build index dan git push berhasil!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Gagal menjalankan git: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Git tidak ditemukan. Pastikan git terinstal dan folder ini adalah repositori git.")


# =====================================
# Dialog untuk input/edit post
# =====================================
class PostDialog:
    def __init__(self, parent, title, data=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x400")
        self.result = None

        tk.Label(self.top, text="Judul").pack(anchor='w', padx=5, pady=2)
        self.title_var = tk.StringVar(value=data['title'] if data else '')
        tk.Entry(self.top, textvariable=self.title_var, width=60).pack(padx=5)

        tk.Label(self.top, text="Tanggal (YYYY-MM-DD)").pack(anchor='w', padx=5, pady=2)
        default_date = datetime.now().strftime('%Y-%m-%d')
        self.date_var = tk.StringVar(value=data['date'] if data else default_date)
        tk.Entry(self.top, textvariable=self.date_var, width=20).pack(anchor='w', padx=5)

        tk.Label(self.top, text="Ringkasan / Excerpt").pack(anchor='w', padx=5, pady=2)
        self.excerpt_var = tk.StringVar(value=data['excerpt'] if data else '')
        tk.Entry(self.top, textvariable=self.excerpt_var, width=60).pack(padx=5)

        tk.Label(self.top, text="Konten (HTML atau teks)").pack(anchor='w', padx=5, pady=2)
        self.content_text = scrolledtext.ScrolledText(self.top, height=12)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        if data and data['content']:
            self.content_text.insert('1.0', data['content'])

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Simpan", command=self.save, bg='lightblue').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Batal", command=self.top.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        title = self.title_var.get().strip()
        date = self.date_var.get().strip()
        excerpt = self.excerpt_var.get().strip()
        content = self.content_text.get('1.0', tk.END).strip()

        if not title:
            messagebox.showerror("Error", "Judul tidak boleh kosong.")
            return
        # Validasi format tanggal
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Format tanggal harus YYYY-MM-DD.")
            return

        self.result = (title, date, excerpt, content)
        self.top.destroy()

# ============================
if __name__ == '__main__':
    root = tk.Tk()
    app = BlogGUI(root)
    root.mainloop()