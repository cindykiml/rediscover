#!/usr/bin/env python3
"""Rebuild rediscover.html from template.html + assets.
Edit template.html, then run:  python3 build.py
Output is written to ../rediscover.html (self-contained, ready to open or publish).
"""
import base64, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def b64(path, mime):
    return 'data:' + mime + ';base64,' + base64.b64encode(open(path, 'rb').read()).decode()

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
open('../rediscover.html', 'w').write(html)
print('wrote ../rediscover.html', len(html)//1024, 'KB')
