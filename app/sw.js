/* Service Worker – generiert von tools/build_sw.py. Nicht von Hand bearbeiten. */
const VERSION = 'c49b3c02a85e';
const ASSETS = ["./", "app.css", "app.js", "index.html", "manifest.webmanifest", "data/lotr.json", "data/rct.json", "data/tables.json", "icons/icon-180.png", "icons/icon-192.png", "icons/icon-512.png", "icons/icon.svg", "img/ball.png", "img/lotr-real.jpg", "img/lotr-thumb.jpg", "img/lotr-vpw16.jpg", "img/rct-thumb.jpg", "img/rct-vpw24.jpg", "img/lotr/fs-aragorn.png", "img/lotr/fs-boromir.png", "img/lotr/fs-frodo.png", "img/lotr/fs-gandalf.png", "img/lotr/fs-gimli.png", "img/lotr/fs-legolas.png", "img/lotr/fs-merry.png", "img/lotr/fs-pippin.png", "img/lotr/fs-sam.png", "sw-manifest.json"];
const CACHE = 'fg-' + VERSION;

self.addEventListener('install', event => {
  // Vollständiges Paket in einen NEUEN Cache laden. Schlägt eine Datei fehl, scheitert die
  // Installation – der bisher aktive Service Worker und sein Cache bleiben unverändert.
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    try {
      for (const url of ASSETS) {
        const res = await fetch(url, { cache: 'reload', redirect: 'error' });
        if (!res.ok) throw new Error(url + ' ' + res.status);
        await cache.put(url, res);
      }
      for (const url of ASSETS) if (!(await cache.match(url))) throw new Error('fehlt ' + url);
    } catch (e) {
      await caches.delete(CACHE);
      throw e;
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const k of await caches.keys()) if (k.startsWith('fg-') && k !== CACHE) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.endsWith('/sw-manifest.json')) {
    event.respondWith(fetch(req, { cache: 'no-store' }).catch(() => caches.match('sw-manifest.json', { ignoreSearch: true })));
    return;
  }
  if (req.mode === 'navigate') {
    event.respondWith(caches.match('index.html').then(r => r || fetch(req)));
    return;
  }
  event.respondWith(caches.match(req, { ignoreSearch: true }).then(r => r || fetch(req)));
});
