import tkinter as tk
from tkinter import messagebox, scrolledtext
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

        left_frame = tk.Frame(root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(left_frame, text="Daftar Post", font=('Arial', 14, 'bold')).pack(pady=5)

        self.listbox = tk.Listbox(left_frame)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        right_frame = tk.Frame(root, width=200)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Button(right_frame, text="🆕 Post Baru", command=self.create_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="✏️ Edit Post", command=self.edit_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🗑️ Hapus Post", command=self.delete_post, width=15).pack(pady=5)
        tk.Button(right_frame, text="🔄 Refresh Daftar", command=self.refresh_list, width=15).pack(pady=20)
        tk.Button(right_frame, text="🚀 Build & Git Push", command=self.manual_git_push, width=15, bg='lightgreen').pack(pady=5)

        self.refresh_list()

    # ============ FUNGSI GIT OTOMATIS ============
    def git_auto(self, commit_message="Update blog"):
        """Jalankan build_index lalu git add, commit, push."""
        try:
            # 1. Bangun ulang index.html
            build_index()
            # 2. Git add semua perubahan
            subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
            # 3. Cek apakah ada perubahan yang bisa di-commit
            result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            if result.stdout.strip():  # ada perubahan
                subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
                subprocess.run(['git', 'push'], check=True, capture_output=True)
                print("Git push berhasil.")
            else:
                print("Tidak ada perubahan untuk di-commit.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Gagal menjalankan git:\n{e.stderr}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Git tidak ditemukan. Pastikan git terinstal dan folder ini repositori git.")

    def manual_git_push(self):
        self.git_auto()
        self.refresh_list()

    # ============ HELPER ============
    def slugify(self, text):
        slug = text.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')

    def get_html_template(self, title, date_display, excerpt, content):
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
</body>
</html>'''

    def parse_post_file(self, filepath, folder_date):
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
        excerpt = desc_match.group(1).strip() if desc_match else ''
        content_match = re.search(r'<div class="post-content">(.*?)</div>', html, re.DOTALL)
        content = content_match.group(1).strip() if content_match else ''
        return {
            'title': title,
            'excerpt': excerpt,
            'content': content,
            'date': folder_date
        }

    # ============ CRUD ============
    def create_post(self):
        dialog = PostDialog(self.root, "Buat Post Baru")
        self.root.wait_window(dialog.top)
        if dialog.result:
            title, date_str, excerpt, content = dialog.result
            folder_name = date_str
            folder_path = os.path.join(POSTS_DIR, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            filename = self.slugify(title) + '.html'
            filepath = os.path.join(folder_path, filename)

            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"

            html = self.get_html_template(title, date_display, excerpt, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html)

            # Otomatis build index + git push
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
            new_title, new_date, new_excerpt, new_content = dialog.result
            # Gunakan tanggal asli (abaikan perubahan tanggal untuk stabilitas)
            date_obj = datetime.strptime(post['folder'], '%Y-%m-%d')
            bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                     'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
            date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"

            html = self.get_html_template(new_title, date_display, new_excerpt, new_content)
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

        folders = sorted(os.listdir(POSTS_DIR), reverse=True)
        for folder in folders:
            folder_path = os.path.join(POSTS_DIR, folder)
            if not os.path.isdir(folder_path):
                continue
            # Ambil semua file .html di folder
            html_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.html')])
            for fname in html_files:
                file_path = os.path.join(folder_path, fname)
                data = self.parse_post_file(file_path, folder)
                display = f"[{folder}] {data['title']}"
                self.listbox.insert(tk.END, display)
                self.posts.append({
                    'title': data['title'],
                    'folder': folder,
                    'filename': fname
                })

    def on_select(self, event):
        pass

# ============ DIALOG ============
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
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Format tanggal harus YYYY-MM-DD.")
            return

        self.result = (title, date, excerpt, content)
        self.top.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = BlogGUI(root)
    root.mainloop()