"""rebuild_posts.py - Update semua post ke template terbaru dengan navbar & dark mode."""
import os
import re
from datetime import datetime

POSTS_DIR = 'posts'

def parse_old_post(filepath, folder_date):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    title = title_match.group(1).strip() if title_match else 'Tanpa Judul'
    desc_match = re.search(r'<meta\s+name="description"\s+content="(.*?)"\s*/?>', html, re.IGNORECASE)
    excerpt = desc_match.group(1).strip() if desc_match else ''
    content_match = re.search(r'<div class="post-content">(.*?)</div>', html, re.DOTALL)
    content = content_match.group(1).strip() if content_match else ''
    try:
        date_obj = datetime.strptime(folder_date, '%Y-%m-%d')
        bulan = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
        date_display = f"{date_obj.day} {bulan[date_obj.month-1]} {date_obj.year}"
    except:
        date_display = folder_date
    return {
        'title': title,
        'excerpt': excerpt,
        'content': content,
        'date_display': date_display
    }

template = '''<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{excerpt}">
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

def rebuild_all_posts():
    count = 0
    for folder in os.listdir(POSTS_DIR):
        folder_path = os.path.join(POSTS_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for fname in os.listdir(folder_path):
            if fname.endswith('.html'):
                filepath = os.path.join(folder_path, fname)
                data = parse_old_post(filepath, folder)
                new_html = template.format(**data)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_html)
                count += 1
                print(f"Updated: {filepath}")
    print(f"\n✅ {count} post berhasil diupdate ke template terbaru.")

if __name__ == '__main__':
    rebuild_all_posts()