"""Lädt eine HTML-Seite und speichert Rohdatei + Textfassung (für Rulesheets). Aufruf: fetch_text.py URL ziel_ohne_endung"""
import sys, re, html, urllib.request
url, out = sys.argv[1], sys.argv[2]
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FlipperGuide/1.0'})
raw = urllib.request.urlopen(req, timeout=60).read()
open(out + '.html', 'wb').write(raw)
s = raw.decode('utf-8', 'replace')
s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
s = re.sub(r'<(br|/p|/li|/h\d|/tr|/div)[^>]*>', '\n', s, flags=re.I)
s = re.sub(r'<h(\d)[^>]*>', lambda m: '\n' + '#' * int(m.group(1)) + ' ', s)
s = re.sub(r'<li[^>]*>', '- ', s)
t = html.unescape(re.sub(r'<[^>]+>', '', s))
t = re.sub(r'[ \t]+', ' ', t); t = re.sub(r'\n\s*\n+', '\n\n', t)
open(out + '.txt', 'w', encoding='utf-8').write(t)
print(len(t))
