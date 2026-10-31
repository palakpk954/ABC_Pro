// Empty service worker to satisfy browser service worker requests cleanly
self.addEventListener('install', () => {
  self.skipWaiting();
});
self.addEventListener('activate', () => {
  self.clients.claim();
});
