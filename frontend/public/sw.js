// GoviSense PWA Service Worker
// Enables offline field operation for Sri Lankan farmers with limited/intermittent connectivity.

const CACHE_NAME = "govisense-pwa-v3";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/favicon.svg",
  "/favicon.png"
];

// Install: Cache essential shell assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch((err) => {
        console.warn("[GoviSense SW] Cache addAll warning:", err);
      });
    })
  );
  self.skipWaiting();
});

// Activate: Clean up old cache versions (purges stale HTML/asset caches)
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

function isHtmlResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("text/html");
}

// Fetch: Network-first for HTML/navigations and API; safe asset caching for offline resiliency
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname === "/sw.js") return;

  // For API calls, try network first; if offline, return cached or offline payload
  if (url.pathname.startsWith("/api/")) {
    event.respondWith(
      fetch(req).catch(async () => {
        const cached = await caches.match(req);
        if (cached) return cached;
        return new Response(
          JSON.stringify({
            offline: true,
            status: "offline",
            message: "Offline mode active. Using locally stored data.",
          }),
          {
            headers: { "Content-Type": "application/json" },
            status: 200,
          }
        );
      })
    );
    return;
  }

  // For page navigations / HTML shell: ALWAYS network-first so new deployments
  // never serve stale index.html referencing deleted hashed asset bundles.
  const acceptsHtml = (req.headers.get("accept") || "").includes("text/html");
  if (req.mode === "navigate" || url.pathname === "/" || url.pathname === "/index.html" || acceptsHtml) {
    event.respondWith(
      fetch(req)
        .then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(req, responseClone);
            });
          }
          return networkResponse;
        })
        .catch(async () => {
          return (await caches.match(req)) || (await caches.match("/index.html"));
        })
    );
    return;
  }

  // For static JS/CSS/media assets: cache-first for performance, but NEVER cache
  // an HTML fallback response under an asset URL.
  event.respondWith(
    caches.match(req).then((cachedResponse) => {
      if (cachedResponse && !isHtmlResponse(cachedResponse)) {
        return cachedResponse;
      }
      return fetch(req).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && !isHtmlResponse(networkResponse)) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, responseClone);
          });
        }
        return networkResponse;
      });
    })
  );
});
