<template>
  <footer class="bg-slate-900 py-16 mt-16">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid md:grid-cols-4 gap-8 mb-12">
        <div>
          <div class="flex items-center space-x-2 mb-6">
            <div class="w-10 h-10 bg-gradient-to-r from-purple-400 via-violet-500 to-indigo-500 rounded-lg flex items-center justify-center">
              <i class="fas fa-gem text-white text-lg"></i>
            </div>
            <span class="text-white font-bold text-xl">CMEETRADING</span>
          </div>
          <p class="text-gray-300 mb-4">Nền tảng giao dịch Forex, Crypto và hàng hóa hàng đầu Việt Nam</p>
          <div class="flex space-x-4">
            <a class="text-gray-400 hover:text-purple-400 cursor-pointer transition-colors"><i class="fab fa-facebook text-xl"></i></a>
            <a class="text-gray-400 hover:text-purple-400 cursor-pointer transition-colors"><i class="fab fa-twitter text-xl"></i></a>
            <a class="text-gray-400 hover:text-purple-400 cursor-pointer transition-colors"><i class="fab fa-linkedin text-xl"></i></a>
            <a class="text-gray-400 hover:text-purple-400 cursor-pointer transition-colors"><i class="fab fa-youtube text-xl"></i></a>
          </div>
        </div>

        <div>
          <h3 class="text-white font-bold mb-4">Giao Dịch</h3>
          <ul class="space-y-2">
            <li><router-link to="/market" class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Thị trường</router-link></li>
            <li><router-link to="/trading" class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Giao dịch</router-link></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Forex</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Cryptocurrency</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Hàng hóa</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Chỉ số</a></li>
          </ul>
        </div>

        <div>
          <h3 class="text-white font-bold mb-4">Hỗ Trợ</h3>
          <ul class="space-y-2">
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Trung tâm trợ giúp</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Liên hệ</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">FAQ</a></li>
          </ul>
        </div>

        <div>
          <h3 class="text-white font-bold mb-4">Pháp Lý</h3>
          <ul class="space-y-2">
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Điều khoản sử dụng</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Chính sách bảo mật</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Cảnh báo rủi ro</a></li>
            <li><a class="text-gray-300 hover:text-purple-400 cursor-pointer transition-colors">Khiếu nại</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-slate-700 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-start gap-4 md:items-center">
          <div class="text-gray-400 text-sm">
            <div>© 2025 CMEETRADING. Tất cả quyền được bảo lưu.</div>
            <div class="mt-1">Địa chỉ: 123 Nguyễn Huệ, Quận 1, TP.HCM</div>
            <div class="mt-1">Hotline: +84 1900 1234 • Email: support@cmeetrading.vn</div>
          </div>
          <div class="flex items-center space-x-4 text-gray-400 text-2xl">
            <i class="fab fa-cc-visa"></i>
            <i class="fab fa-cc-mastercard"></i>
            <i class="fab fa-paypal"></i>
            <i class="fas fa-university"></i>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
// Footer component - no logic needed
</script>

