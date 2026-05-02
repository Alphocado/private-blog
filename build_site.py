import os
import re
from datetime import datetime

POSTS_DIR = 'posts'
INDEX_FILE = 'index.html'

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LienardyBlog</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <nav class="navbar">
    <a href="index.html" class="logo">LienardyBlog</a>
    <button id="theme-toggle" aria-label="Toggle dark mode"></button>
  </nav>
  <main class="container">
    <h1>LienardyBlog</h1>
    <section class="post-list">
      {posts_html}
    </section>
  </main>
  <script src="script.js"></script>
</body>
</html>'''

POST_ITEM_TEMPLATE = '''<article class="post-item">
  <h2><a href="{link}">{title}</a></h2>
  <p class="post-meta">{date_display}</p>
  <p class="post-excerpt">{excerpt}</p>
</article>'''

def parse_post(file_path, folder_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else 'Tanpa Judul'

    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
    excerpt = desc_match.group(1).strip() if desc_match else ''

    try:
        date_obj = datetime.strptime(folder_name, '%Y-%m-%d')
        bulan = [
            'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
        ]
        date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"
    except ValueError:
        date_display = folder_name

    return {
        'title': title,
        'excerpt': excerpt,
        'date_display': date_display,
        'folder': folder_name,
        'filename': os.path.basename(file_path)
    }

def build_index():
    posts = []

    if not os.path.isdir(POSTS_DIR):
        os.makedirs(POSTS_DIR, exist_ok=True)

    folders = sorted(os.listdir(POSTS_DIR), reverse=True)
    for folder in folders:
        folder_path = os.path.join(POSTS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        # ambil SEMUA file .html di folder ini
        html_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.html')])
        for fname in html_files:
            file_path = os.path.join(folder_path, fname)
            post = parse_post(file_path, folder)
            post['link'] = f"{POSTS_DIR}/{folder}/{fname}"
            posts.append(post)

    posts_html = ''
    for p in posts:
        posts_html += POST_ITEM_TEMPLATE.format(
            title=p['title'],
            link=p['link'],
            date_display=p['date_display'],
            excerpt=p['excerpt']
        )

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE.format(posts_html=posts_html))

    print(f"{len(posts)} post dimuat ke {INDEX_FILE}")

if __name__ == '__main__':
    build_index()