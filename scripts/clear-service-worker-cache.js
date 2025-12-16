/**
 * Script để clear Service Worker cache
 * Chạy trong browser console hoặc inject vào trang
 */

(function() {
  console.log('🔧 Starting Service Worker cache clear...');
  
  // 1. Unregister tất cả service workers
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
      console.log(`Found ${registrations.length} service worker(s)`);
      
      for (let registration of registrations) {
        registration.unregister().then(function(success) {
          if (success) {
            console.log('✅ Service Worker unregistered:', registration.scope);
          } else {
            console.log('❌ Failed to unregister:', registration.scope);
          }
        });
      }
    });
  }
  
  // 2. Clear caches
  if ('caches' in window) {
    caches.keys().then(function(cacheNames) {
      console.log(`Found ${cacheNames.length} cache(s)`);
      
      return Promise.all(
        cacheNames.map(function(cacheName) {
          console.log('🗑️ Deleting cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(function() {
      console.log('✅ All caches cleared!');
    });
  }
  
  // 3. Clear localStorage và sessionStorage (optional)
  console.log('🧹 Clearing localStorage and sessionStorage...');
  localStorage.clear();
  sessionStorage.clear();
  console.log('✅ Storage cleared!');
  
  console.log('✅ Service Worker cache clear completed!');
  console.log('🔄 Please reload the page (Ctrl+Shift+R for hard refresh)');
})();

