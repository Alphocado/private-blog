import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, simpledialog
import os
import re
import subprocess
import shutil
from datetime import datetime
from build_site import build_index, POSTS_DIR, IMAGES_DIR

class BlogGUI:
    def __init__(self, root):
        self.root = root
        root.title("Blog Manager - LienardyBlog")
        root.geometry("700x500")

        left_frame = tk.Frame(root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Daftar Post", font=('Arial', 14, 'bold')).pack(pady=5)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_frame = tk.Frame(root, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(right_frame, text="🆕 Post Baru", command=self.create_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="✏️ Edit Post", command=self.edit_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🗑️ Hapus Post", command=self.delete_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🔄 Refresh Daftar", command=self.refresh_list, width=15).pack(pady=20)
        tk.Button(right_frame, text="🚀 Build & Git Push", command=self.manual_git_push, width=15, bg='lightgreen').pack(pady=5)
        tk.Button(right_frame, text="⚙️ Build .exe", command=self.build_exe, width=15, bg='lightyellow').pack(pady=5)

        self.refresh_list()

    def git_auto(self, commit_message="Update blog"):
        try:
            build_index()
            subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():
                subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
                subprocess.run(['git', 'push'], check=True, capture_output=True)
                print("Git push berhasil.")
            else:
                print("Tidak ada perubahan untuk di-commit.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Gagal menjalankan git:\n{e.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Git tidak ditemukan.")

    def manual_git_push(self):
        self.git_auto()
        self.refresh_list()

    def build_exe(self):
        """Membuat file .exe dari gui_app.py menggunakan PyInstaller."""
        if not os.path.exists('gui_app.py'):
            messagebox.showerror("Error", "File gui_app.py tidak ditemukan.")
            return
        confirm = messagebox.askyesno("Konfirmasi", "Ini akan membuat LienardyBlog.exe di folder yang sama. Lanjutkan?")
        if not confirm:
            return
        try:
            # Pastikan PyInstaller terinstall
            subprocess.run(['pyinstaller', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror("Error", "PyInstaller belum terinstall. Jalankan 'pip install pyinstaller' dulu.")
            return

        try:
            # Hapus folder build & spec sementara
            for path in ['build', 'dist', 'LienardyBlog.spec']:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                elif os.path.isfile(path):
                    os.remove(path)

            # Jalankan pyinstaller
            subprocess.run([
                'pyinstaller', '--onefile', '--noconsole',
                '--distpath', '.',
                '--name', 'LienardyBlog',
                'gui_app.py'
            ], check=True)
            # Hapus folder build dan spec yang dihasilkan
            if os.path.isdir('build'):
                shutil.rmtree('build')
            if os.path.isfile('LienardyBlog.spec'):
                os.remove('LienardyBlog.spec')
            messagebox.showinfo("Sukses", "LienardyBlog.exe berhasil dibuat di folder yang sama.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Gagal membuat exe:\n{e}")

    def slugify(self, text):
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def get_html_template(self, title, date_display, excerpt, content, datetime_iso, thumbnail=''):
        return f'''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{excerpt}">
  <meta name="datetime" content="{datetime_iso}">
  <meta name="thumbnail" content="{thumbnail}">
  <link rel="stylesheet" href="../../style.css">
</head>
<body>
  <nav class="navbar">
    <a href="../../index.html" class="logo">LienardyBlog</a>
    <button id="theme-toggle" aria-label="Toggle dark mode"></button>
  </nav>
  <main class="container">
    <article class="post">
      <h1>{title}</h1>
      <p class="post-meta">{date_display}</p>
      <div class="post-content">
        {content}
      </div>
    </article>
  </main>
  <script src="../../script.js"></script>
</body>
</html>'''

    def parse_post_file(self, filepath, folder_date):
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
        excerpt = desc_match.group(1).strip() if desc_match else ''
        dt_match = re.search(r'<meta\s+name="datetime"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
        dt_str = dt_match.group(1).strip() if dt_match else None
        thumb_match = re.search(r'<meta\s+name="thumbnail"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
        thumbnail = thumb_match.group(1).strip() if thumb_match else ''
        content_match = re.search(r'<div class="post-content">(.*?)</div>', html, re.DOTALL)
        content = content_match.group(1).strip() if content_match else ''
        return {
            'title': title,
            'excerpt': excerpt,
            'content': content,
            'date': folder_date,
            'datetime_iso': dt_str,
            'thumbnail': thumbnail
        }

    def create_post(self):
        dialog = PostDialog(self.root, "Buat Post Baru")
        self.root.wait_window(dialog.top)
        if dialog.result:
            title, date_str, excerpt, content, datetime_iso, thumbnail = dialog.result
            folder_name = date_str
            folder_path = os.path.join(POSTS_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            filename = self.slugify(title) + '.html'
            filepath = os.path.join(folder_path, filename)

            dt_obj = datetime.strptime(datetime_iso, '%Y-%m-%dT%H:%M:%S')
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_display = f"{dt_obj.day} {bulan[dt_obj.month-1]} {dt_obj.year}, {dt_obj.hour:02d}:{dt_obj.minute:02d}"

            html = self.get_html_template(title, date_display, excerpt, content, datetime_iso, thumbnail)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            self.git_auto(f"Create post: {title}")
            self.refresh_list()
            messagebox.showinfo("Sukses", f"Post '{title}' berhasil dibuat!")

    def edit_post(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Pilih post", "Silakan pilih post yang ingin diedit.")
            return
        idx = selection[0]
        post = self.posts[idx]
        folder_path = os.path.join(POSTS_DIR, post['folder'])
        filepath = os.path.join(folder_path, post['filename'])
        if not os.path.exists(filepath):
            messagebox.showerror("Error", "File post tidak ditemukan.")
            return
        data = self.parse_post_file(filepath, post['folder'])
        dialog = PostDialog(self.root, "Edit Post", data=data)
        self.root.wait_window(dialog.top)
        if dialog.result:
            new_title, new_date, new_excerpt, new_content, new_datetime_iso, new_thumbnail = dialog.result
            dt_obj = datetime.strptime(new_datetime_iso, '%Y-%m-%dT%H:%M:%S')
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_display = f"{dt_obj.day} {bulan[dt_obj.month-1]} {dt_obj.year}, {dt_obj.hour:02d}:{dt_obj.minute:02d}"

            html = self.get_html_template(new_title, date_display, new_excerpt, new_content, new_datetime_iso, new_thumbnail)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            new_filename = self.slugify(new_title) + '.html'
            if new_filename != post['filename']:
                new_path = os.path.join(folder_path, new_filename)
                os.rename(filepath, new_path)

            self.git_auto(f"Edit post: {new_title}")
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
                if not os.listdir(folder_path):
                    os.rmdir(folder_path)
            self.git_auto(f"Delete post: {post['title']}")
            self.refresh_list()
            messagebox.showinfo("Sukses", "Post dihapus.")

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        self.posts = []
        if not os.path.isdir(POSTS_DIR):
            os.makedirs(POSTS_DIR)

        raw_posts = []
        for folder in os.listdir(POSTS_DIR):
            folder_path = os.path.join(POSTS_DIR, folder)
            if not os.path.isdir(folder_path):
                continue
            for fname in sorted(os.listdir(folder_path)):
                if fname.endswith('.html'):
                    file_path = os.path.join(folder_path, fname)
                    data = self.parse_post_file(file_path, folder)
                    dt_str = data.get('datetime_iso')
                    if dt_str:
                        try:
                            dt_obj = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%S')
                        except:
                            dt_obj = datetime.strptime(folder, '%Y-%m-%d')
                    else:
                        dt_obj = datetime.strptime(folder, '%Y-%m-%d')
                    raw_posts.append({
                        'title': data['title'],
                        'folder': folder,
                        'filename': fname,
                        'datetime_obj': dt_obj
                    })

        raw_posts.sort(key=lambda p: p['datetime_obj'], reverse=True)
        self.posts = raw_posts
        for p in self.posts:
            display = f"[{p['folder']}] {p['title']}"
            self.listbox.insert(tk.END, display)


# ============ DIALOG ============
class PostDialog:
    def __init__(self, parent, title, data=None):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("500x550")
        self.result = None

        tk.Label(self.top, text="Judul").pack(anchor='w', padx=5, pady=2)
        self.title_var = tk.StringVar(value=data['title'] if data else '')
        tk.Entry(self.top, textvariable=self.title_var, width=60).pack(padx=5)

        tk.Label(self.top, text="Tanggal (YYYY-MM-DD)").pack(anchor='w', padx=5, pady=2)
        default_date = datetime.now().strftime('%Y-%m-%d')
        self.date_var = tk.StringVar(value=data['date'] if data else default_date)
        tk.Entry(self.top, textvariable=self.date_var, width=20).pack(anchor='w', padx=5)

        tk.Label(self.top, text="Jam (HH:MM)").pack(anchor='w', padx=5, pady=2)
        if data and data.get('datetime_iso'):
            dt = datetime.strptime(data['datetime_iso'], '%Y-%m-%dT%H:%M:%S')
            default_time = f"{dt.hour:02d}:{dt.minute:02d}"
        else:
            default_time = datetime.now().strftime('%H:%M')
        self.time_var = tk.StringVar(value=default_time)
        tk.Entry(self.top, textvariable=self.time_var, width=10).pack(anchor='w', padx=5)

        # --- THUMBNAIL WAJIB ---
        tk.Label(self.top, text="Thumbnail (wajib) - URL atau pilih gambar").pack(anchor='w', padx=5, pady=2)
        thumb_frame = tk.Frame(self.top)
        thumb_frame.pack(anchor='w', padx=5, fill='x')

        self.thumb_var = tk.StringVar(value=data['thumbnail'] if data and 'thumbnail' in data else '')
        tk.Entry(thumb_frame, textvariable=self.thumb_var, width=40).pack(side=tk.LEFT)

        def upload_thumb():
            file_path = filedialog.askopenfilename(
                title="Pilih Gambar Thumbnail",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
            )
            if not file_path:
                return
            os.makedirs(IMAGES_DIR, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            new_name = f"thumb-{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            dest = os.path.join(IMAGES_DIR, new_name)
            shutil.copy(file_path, dest)
            self.thumb_var.set(f"images/{new_name}")

        tk.Button(thumb_frame, text="Upload Gambar", command=upload_thumb).pack(side=tk.LEFT, padx=5)

        tk.Label(self.top, text="Ringkasan / Excerpt").pack(anchor='w', padx=5, pady=2)
        self.excerpt_var = tk.StringVar(value=data['excerpt'] if data else '')
        tk.Entry(self.top, textvariable=self.excerpt_var, width=60).pack(padx=5)

        # --- KONTEN DENGAN TOOLBAR GAMBAR ---
        tk.Label(self.top, text="Konten (HTML atau teks)").pack(anchor='w', padx=5, pady=2)

        # DULUAN bikin content_text, baru toolbar
        self.content_text = scrolledtext.ScrolledText(self.top, height=12)
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        if data and data['content']:
            self.content_text.insert('1.0', data['content'])

        # Toolbar di bawah content_text
        toolbar_frame = tk.Frame(self.top)
        toolbar_frame.pack(anchor='w', padx=5, pady=(0,5))

        def insert_image_url():
            url = simpledialog.askstring("URL Gambar", "Masukkan URL gambar:")
            if url:
                img_tag = f'<img src="{url}" alt="gambar">'
                self.content_text.insert(tk.INSERT, img_tag)

        def upload_image_to_content():
            file_path = filedialog.askopenfilename(
                title="Pilih Gambar untuk Konten",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
            )
            if not file_path:
                return
            os.makedirs(IMAGES_DIR, exist_ok=True)
            ext = os.path.splitext(file_path)[1]
            new_name = f"img-{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            dest = os.path.join(IMAGES_DIR, new_name)
            shutil.copy(file_path, dest)
            # Path RELATIF dari halaman post (posts/YYYY-MM-DD/nama.html) -> ../../images/
            img_tag = f'<img src="../../images/{new_name}" alt="gambar">'
            self.content_text.insert(tk.INSERT, img_tag)

        tk.Button(toolbar_frame, text="Sisipkan URL Gambar", command=insert_image_url).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar_frame, text="Upload Gambar ke Konten", command=upload_image_to_content).pack(side=tk.LEFT, padx=2)

        btn_frame = tk.Frame(self.top)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Simpan", command=self.save, bg='lightblue').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Batal", command=self.top.destroy).pack(side=tk.LEFT, padx=5)
    def save(self):
        title = self.title_var.get().strip()
        date = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        excerpt = self.excerpt_var.get().strip()
        content = self.content_text.get('1.0', tk.END).strip()
        thumbnail = self.thumb_var.get().strip()

        if not title:
            messagebox.showerror("Error", "Judul tidak boleh kosong.")
            return
        if not thumbnail:
            messagebox.showerror("Error", "Thumbnail wajib diisi (URL atau upload gambar).")
            return
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Format tanggal harus YYYY-MM-DD.")
            return
        try:
            hour, minute = map(int, time_str.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except:
            messagebox.showerror("Error", "Format jam harus HH:MM (00-23:00-59).")
            return

        datetime_iso = f"{date}T{hour:02d}:{minute:02d}:00"
        self.result = (title, date, excerpt, content, datetime_iso, thumbnail)
        self.top.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = BlogGUI(root)
    root.mainloop()