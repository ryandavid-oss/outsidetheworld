const CACHE_NAME = 'otw-fragments-publisher-v4';
const CORE_ASSETS = [
  '/fragments_publisher.html',
  '/fragments_publisher.webmanifest',
  '/theme.css',
  '/favicon.svg',
  '/Images/Equal.svg',
  '/Images/Equal_dark.svg',
  '/Images/Profile.jpg',
  '/Images/otw_brandmark_stroke.svg',
  '/Images/iotd_icon.svg',
  '/Images/ghost_writer_lite_icon.svg',
  '/Images/ghost_writer_full_icon.svg',
  '/Images/otw_bot_summon_icon.svg'
];

const PUBLISHER_PATHS = new Set(CORE_ASSETS.concat(['/fragments_publisher_sw.js']));

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
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  const requestUrl = new URL(event.request.url);
  if (requestUrl.origin !== self.location.origin) {
    return;
  }

  const isPublisherAsset = PUBLISHER_PATHS.has(requestUrl.pathname);
  if (!isPublisherAsset) {
    return;
  }

  const isPublisherShell =
    requestUrl.pathname === '/fragments_publisher.html' ||
    requestUrl.pathname === '/fragments_publisher.webmanifest';

  if (isPublisherShell) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          }
          return response;
        })
        .catch(() => caches.match(event.request).then((cached) => cached || caches.match('/fragments_publisher.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) {
        return cached;
      }

      return fetch(event.request)
        .then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => caches.match('/fragments_publisher.html'));
    })
  );
});
