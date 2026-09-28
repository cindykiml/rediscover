#!/usr/bin/env python3
"""Rebuild index.html from template.html + assets.
Edit template.html, then run:  python3 build/build.py
Output is written to ../index.html (self-contained; open locally, publish as an
artifact, or deploy the repo root to Vercel/GitHub Pages as a static site).

Place thumbnails live in thumbs/<key>.jpg (any size, square). They are downscaled
to THUMB_PX and re-encoded before inlining so the page stays small.
"""
import base64, io, os, subprocess, tempfile
os.chdir(os.path.dirname(os.path.abspath(__file__)))

THUMB_PX = 224   # 56px CSS tile x 4 — crisp on 3x phones and scaled-up desktops
THUMB_Q  = 74    # WebP quality (JPEG quality for the sips fallback)

def b64(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(open(path, 'rb').read()).decode()

def thumb_b64(path):
    """Square-crop + downscale, encode as WebP (Pillow). Falls back to sips JPEG."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as t:
            out = t.name
        subprocess.run(['sips', '-Z', str(THUMB_PX), '-s', 'format', 'jpeg',
                        '-s', 'formatOptions', str(THUMB_Q), path, '--out', out],
                       check=True, capture_output=True)
        data = b64(out, 'image/jpeg'); os.unlink(out)
        return data
    im = ImageOps.exif_transpose(Image.open(path)).convert('RGB')
    im = ImageOps.fit(im, (THUMB_PX, THUMB_PX), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'WEBP', quality=THUMB_Q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()

html = open('template.html').read()
for tag, path, mime in [
    ('@@IMG@@',  'base_clean.jpg',      'image/jpeg'),
    ('@@NAV@@',  'nav.png',             'image/png'),
    ('@@DETAIL@@','detail.png',         'image/png'),
    ('@@ICOH@@', 'ico_home.png',        'image/png'),
    ('@@ICOR@@', 'ico_restaurants.png', 'image/png'),
    ('@@ICOC@@', 'ico_coffee.png',      'image/png'),
    ('@@ICOB@@', 'ico_hotels.png',      'image/png')]:
    assert html.count(tag) == 1, tag
    html = html.replace(tag, b64(path, mime))

thumb_bytes = 0
for f in sorted(os.listdir('thumbs')):
    if not f.endswith('.jpg'): continue
    tag = '@@TH_' + f[:-4] + '@@'
    assert html.count(tag) == 1, tag
    data = thumb_b64(os.path.join('thumbs', f))
    thumb_bytes += len(data)
    html = html.replace(tag, data)
assert '@@TH_' not in html, 'unfilled thumbnail placeholder'

open('../index.html', 'w').write(html)
print('wrote ../index.html', len(html)//1024, 'KB  (thumbnails', thumb_bytes//1024, 'KB)')
