/* Firebase Cloud Messaging service worker — handles web push while the tab is
 * in the background or closed. The firebase_messaging Flutter web plugin looks
 * for this file at the site root by default and registers it automatically.
 *
 * The config is duplicated from lib/firebase_options.dart (the `web` options)
 * on purpose: a service worker runs outside the Flutter bundle and can't read
 * Dart, so these values are maintained by hand. Keep the two in sync. There is
 * no VAPID key here — that belongs to getToken() in the app, not the worker.
 */
importScripts('https://www.gstatic.com/firebasejs/10.14.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.14.0/firebase-messaging-compat.js');

firebase.initializeApp({
  apiKey: 'AIzaSyDceGMu8twuV5li69vF6agjvOv1hfQfCJE',
  authDomain: 'gym-management-system-b3e71.firebaseapp.com',
  projectId: 'gym-management-system-b3e71',
  storageBucket: 'gym-management-system-b3e71.firebasestorage.app',
  messagingSenderId: '77722937663',
  appId: '1:77722937663:web:3885a408e0863f556f0b8a',
});

const messaging = firebase.messaging();

// Background messages that carry a `data` payload (no `notification` block)
// won't be shown by the browser automatically, so draw them ourselves. Pushes
// that already include a `notification` block are displayed by the browser and
// would double up if we also handled them here.
messaging.onBackgroundMessage((payload) => {
  if (payload.notification) return;
  const data = payload.data || {};
  const title = data.title || 'PowerFit';
  self.registration.showNotification(title, {
    body: data.body || '',
    icon: '/icons/Icon-192.png',
    data: data,
  });
});

// Focus (or open) the app when a notification is clicked.
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if ('focus' in client) return client.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow('/');
    })
  );
});
