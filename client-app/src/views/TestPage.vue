<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900 text-white p-8">
    <h1 class="text-4xl font-bold mb-4">Test Page - Trading Dashboard</h1>
    <p class="text-xl mb-8">Nếu bạn thấy trang này, Vue đang hoạt động!</p>
    
    <div class="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-purple-500/20 p-6">
      <h2 class="text-2xl font-bold mb-4">Thông tin hệ thống:</h2>
      <ul class="space-y-2">
        <li>✅ Vue Router: Hoạt động</li>
        <li>✅ TailwindCSS: Hoạt động</li>
        <li>✅ Components: Đang load...</li>
      </ul>
    </div>
    
    <div class="mt-8">
      <router-link 
        to="/trading" 
        class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-lg font-bold hover:from-purple-700 hover:to-indigo-700 transition-all"
      >
        Đi đến Trading Dashboard →
      </router-link>
    </div>
  </div>
</template>

<script setup>
</script>





