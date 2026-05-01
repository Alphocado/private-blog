import os
import re
from datetime import datetime

# Folder tempat semua post disimpan
POSTS_DIR = 'posts'
INDEX_FILE = 'index.html'
# Template daftar post di index.html
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog Saya</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <main class="container">
    <h1>Blog Saya</h1>
    <section class="post-list">
      {posts_html}
    </section>
  </main>
</body>
</html>'''

POST_ITEM_TEMPLATE = '''<article class="post-item">
  <h2><a href="{link}">{title}</a></h2>
  <p class="post-meta">{date_display}</p>
  <p class="post-excerpt">{excerpt}</p>
</article>'''

def parse_post(file_path, folder_name):
    """Mengambil judul, deskripsi, dan konten dari file HTML post."""
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Ambil judul dari <title>
    title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else 'Tanpa Judul'

    # Ambil excerpt dari <meta name="description">
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
    excerpt = desc_match.group(1).strip() if desc_match else ''

    # Format tanggal dari nama folder (YYYY-MM-DD)
    try:
        date_obj = datetime.strptime(folder_name, '%Y-%m-%d')
        # Format Indonesia: 2 Mei 2026
        bulan = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"
    except ValueError:
        date_display = folder_name  # fallback

    return {
        'title': title,
        'excerpt': excerpt,
        'date_display': date_display,
        'folder': folder_name,
        'filename': os.path.basename(file_path)
    }

def build_index():
    """Membangun ulang index.html dari seluruh post."""
    posts = []

    if not os.path.isdir(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)

    # Loop semua folder di dalam posts/
    for folder in sorted(os.listdir(POSTS_DIR), reverse=True):
        folder_path = os.path.join(POSTS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        # Ambil SEMUA file .html di dalam folder ini
        html_files = [f for f in os.listdir(folder_path) if f.endswith('.html')]
        if not html_files:
            continue
        for filename in html_files:
            file_path = os.path.join(folder_path, filename)
            post = parse_post(file_path, folder)
            post['link'] = f"{POSTS_DIR}/{folder}/{filename}"
            posts.append(post)

    # Buat HTML daftar post
    posts_html = ''
    for p in posts:
        posts_html += POST_ITEM_TEMPLATE.format(
            title=p['title'],
            link=p['link'],
            date_display=p['date_display'],
            excerpt=p['excerpt']
        )

    # Tulis index.html
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE.format(posts_html=posts_html))

    print(f"{len(posts)} post berhasil dimuat ke {INDEX_FILE}")

if __name__ == '__main__':
    build_index()