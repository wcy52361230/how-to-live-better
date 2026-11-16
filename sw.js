/* 高性价比人生指南 · Service Worker
 *
 * 目标：装到手机主屏幕后，断网也能打开，联网时自动拿到最新内容。
 *
 * 策略：
 *   导航请求（打开页面）  → 网络优先，4 秒超时或失败则回退缓存
 *   同源静态资源         → 缓存优先，同时后台更新
 *   跨域请求（文献外链）  → 不拦截，直接走网络
 *
 * index.html 每天由 GitHub Actions 重新生成，所以导航一律先试网络，
 * 避免用户长期停留在旧版本。
 */

const VERSION = 'v1';
const CACHE = 'hltb-' + VERSION;
const PAGE = './index.html';
const ASSETS = [
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png'
];
const NAV_TIMEOUT = 4000;

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);

    // 预缓存页面本体；失败不阻断安装（离线时再兜底）
    try {
      const res = await fetch(new Request(PAGE, { cache: 'reload' }));
      if (res && res.ok) {
        await cache.put(PAGE, res.clone());
        await cache.put('./', res.clone());
      }
    } catch (e) {
      /* 忽略：首次安装时没网就跳过，等联网后由 fetch 事件补上 */
    }

    // 逐个缓存静态资源，单项缺失不影响整体
    await Promise.all(ASSETS.map((url) =>
      cache.add(new Request(url, { cache: 'reload' })).catch(() => {})
    ));

    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys
        .filter((k) => k.startsWith('hltb-') && k !== CACHE)
        .map((k) => caches.delete(k))
    );
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // 文献外链：不接管

  if (req.mode === 'navigate') {
    event.respondWith(networkFirst(req));
  } else {
    event.respondWith(staleWhileRevalidate(req));
  }
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), NAV_TIMEOUT);
    let res;
    try {
      res = await fetch(req, { signal: ctrl.signal });
    } finally {
      clearTimeout(timer);
    }

    if (res && res.ok) {
      const copy = res.clone();
      cache.put(PAGE, copy.clone()).catch(() => {});
      cache.put('./', copy).catch(() => {});
    }
    return res;
  } catch (e) {
    const hit =
      (await cache.match(req, { ignoreSearch: true })) ||
      (await cache.match(PAGE)) ||
      (await cache.match('./'));

    if (hit) return hit;

    return new Response('当前离线，且本机还没有缓存页面。\n请联网后重新打开一次，之后就能离线阅读。', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' }
    });
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const hit = await cache.match(req);

  const network = fetch(req)
    .then((res) => {
      if (res && res.ok) cache.put(req, res.clone()).catch(() => {});
      return res;
    })
    .catch(() => null);

  if (hit) return hit;

  const res = await network;
  if (res) return res;
  return new Response('', { status: 504, statusText: 'offline' });
}
