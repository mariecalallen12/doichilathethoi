<template>
  <div class="glass-panel rounded-lg p-6">
    <h3 class="text-lg font-bold text-white mb-4 flex items-center">
      <i class="fas fa-bolt mr-2 text-purple-400"></i>
      Hành Động Nhanh
    </h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <router-link
        to="/personal/deposit"
        class="flex flex-col items-center justify-center p-4 bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-lg hover:from-green-500/30 hover:to-emerald-500/30 transition-all group"
      >
        <div class="w-12 h-12 bg-green-500/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-green-500/50 transition-all">
          <i class="fas fa-arrow-down text-green-300 text-xl"></i>
        </div>
        <span class="text-white font-medium text-sm">Nạp Tiền</span>
      </router-link>

      <router-link
        to="/personal/withdraw"
        class="flex flex-col items-center justify-center p-4 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/30 rounded-lg hover:from-blue-500/30 hover:to-cyan-500/30 transition-all group"
      >
        <div class="w-12 h-12 bg-blue-500/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-blue-500/50 transition-all">
          <i class="fas fa-arrow-up text-blue-300 text-xl"></i>
        </div>
        <span class="text-white font-medium text-sm">Rút Tiền</span>
      </router-link>

      <router-link
        to="/personal/transactions"
        class="flex flex-col items-center justify-center p-4 bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border border-purple-500/30 rounded-lg hover:from-purple-500/30 hover:to-indigo-500/30 transition-all group"
      >
        <div class="w-12 h-12 bg-purple-500/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-purple-500/50 transition-all">
          <i class="fas fa-history text-purple-300 text-xl"></i>
        </div>
        <span class="text-white font-medium text-sm">Lịch Sử</span>
      </router-link>

      <router-link
        to="/personal/rates"
        class="flex flex-col items-center justify-center p-4 bg-gradient-to-br from-yellow-500/20 to-orange-500/20 border border-yellow-500/30 rounded-lg hover:from-yellow-500/30 hover:to-orange-500/30 transition-all group"
      >
        <div class="w-12 h-12 bg-yellow-500/30 rounded-lg flex items-center justify-center mb-3 group-hover:bg-yellow-500/50 transition-all">
          <i class="fas fa-exchange-alt text-yellow-300 text-xl"></i>
        </div>
        <span class="text-white font-medium text-sm">Tỷ Giá</span>
      </router-link>
    </div>
  </div>
</template>

