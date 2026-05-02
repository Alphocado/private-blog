import os
import re

posts_dir = 'posts'
# Urutan yang diinginkan: dari paling baru ke lama? user ingin urut dari baru ke lama sesuai waktu.
# Kita set jam agar "Kenapa Aku Mau Upgrade Blog Ini Lagi?" paling baru, lalu "Menutup Satu Bab dengan Tenang", lalu "Kenapa Aku Membuat Blog Ini Sendiri?"
# Jadi waktu: upgrade (paling baru), menutup, membuat
# Agar descending: upgrade jam 10:20, menutup 10:10, membuat 10:00
order = [
    ("Kenapa Aku Mau Upgrade Blog Ini Lagi?", "2026-05-02T10:20:00"),
    ("Menutup Satu Bab dengan Tenang", "2026-05-02T10:10:00"),
    ("Kenapa Aku Membuat Blog Ini Sendiri? (Cerita Tengah Malam)", "2026-05-02T10:00:00"),
]

for folder in os.listdir(posts_dir):
    folder_path = os.path.join(posts_dir, folder)
    if not os.path.isdir(folder_path):
        continue
    for fname in os.listdir(folder_path):
        if not fname.endswith('.html'):
            continue
        filepath = os.path.join(folder_path, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ''
        # Cari timestamp yang cocok
        for t, stamp in order:
            if title == t:
                if '<meta name="datetime"' not in html:
                    html = html.replace('</head>', f'<meta name="datetime" content="{stamp}">\n</head>', 1)
                else:
                    html = re.sub(r'<meta\s+name="datetime"\s+content=".*?"\s*/?>', f'<meta name="datetime" content="{stamp}">', html)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✅ Timestamp {stamp} → {title}")
                break