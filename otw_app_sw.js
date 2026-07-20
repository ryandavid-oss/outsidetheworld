const CACHE_NAME = 'otw-app-v3';
const CORE_ASSETS = [
  '/otw_app.html',
  '/otw_app.webmanifest',
  '/theme.css',
  '/otw_markdown.js',
  '/favicon.svg',
  '/Images/Equal.svg',
  '/Images/Equal_dark.svg'
];

const APP_PATHS = new Set(CORE_ASSETS.concat(['/otw_app_sw.js', '/fragments_publisher.html']));

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CORE_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key.startsWith('otw-fragments-publisher-') || key.startsWith('otw-app-'))
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  const requestUrl = new URL(event.request.url);
  if (requestUrl.origin !== self.location.origin) return;
  if (!APP_PATHS.has(requestUrl.pathname)) return;

  const isShell =
    requestUrl.pathname === '/otw_app.html' ||
    requestUrl.pathname === '/fragments_publisher.html' ||
    requestUrl.pathname === '/otw_app.webmanifest';

  if (isShell) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, response.clone()));
          }
          return response;
        })
        .catch(() => caches.match(event.request).then((cached) => cached || caches.match('/otw_app.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          if (response && response.status === 200 && response.type === 'basic') {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, response.clone()));
          }
          return response;
        })
        .catch(() => caches.match('/otw_app.html'));
    })
  );
});
