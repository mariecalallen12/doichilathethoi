<script setup>
import { ref, onMounted } from 'vue';
import { useUserStore } from '../store/user';
import { useAuthStore } from '../store/auth';
import api from '../services/api';
import toastService from '../services/toast';
import ExcelJS from 'exceljs';
import UserTable from '../components/users/UserTable.vue';
import UserFilters from '../components/users/UserFilters.vue';
import UserBulkActions from '../components/users/UserBulkActions.vue';
import UserProfileModal from '../components/users/UserProfileModal.vue';
import UserFormModal from '../components/users/UserFormModal.vue';
import RegistrationFieldsConfig from '../components/users/RegistrationFieldsConfig.vue';
import Button from '../components/ui/Button.vue';
import Card from '../components/ui/Card.vue';
import Modal from '../components/ui/Modal.vue';

const userStore = useUserStore();
const authStore = useAuthStore();

const selectedUsers = ref([]);
const showUserModal = ref(false);
const showUserFormModal = ref(false);
const showRegistrationConfigModal = ref(false);
const selectedUser = ref(null);
const loading = ref(false);
const pendingRegistrations = ref([]);
const autoApproveEnabled = ref(false);
const showPendingRegistrations = ref(false);
const pendingRegistrationsLoading = ref(false);

const filters = ref({
  search: '',
  status: 'all',
  sortBy: 'created_at',
  sortOrder: 'desc',
});

const pagination = ref({
  page: 1,
  limit: 50,
  total: 0,
});

const fetchUsers = async () => {
  loading.value = true;
  try {
    await userStore.fetchUsers({
      ...filters.value,
      page: pagination.value.page,
      limit: pagination.value.limit,
    });
    pagination.value.total = userStore.pagination.total;
  } catch (error) {
    toastService.error('Không thể tải danh sách người dùng');
  } finally {
    loading.value = false;
  }
};

const handleSelect = (userId) => {
  const index = selectedUsers.value.indexOf(userId);
  if (index > -1) {
    selectedUsers.value.splice(index, 1);
  } else {
    selectedUsers.value.push(userId);
  }
};

const handleSelectAll = () => {
  if (selectedUsers.value.length === userStore.users.length) {
    selectedUsers.value = [];
  } else {
    selectedUsers.value = userStore.users.map(u => u.id);
  }
};

const handleView = async (userId) => {
  loading.value = true;
  try {
    await userStore.fetchUserById(userId);
    selectedUser.value = userStore.currentUser;
    showUserModal.value = true;
  } catch (error) {
    toastService.error('Không thể tải thông tin người dùng');
  } finally {
    loading.value = false;
  }
};

const handleUpdateStatus = async (userId, status) => {
  try {
    await userStore.updateUserStatus(userId, status);
    toastService.success('Cập nhật trạng thái thành công');
    await fetchUsers();
    if (showUserModal.value) {
      showUserModal.value = false;
    }
  } catch (error) {
    toastService.error('Không thể cập nhật trạng thái');
  }
};

const handleBulkAction = async (action) => {
  if (selectedUsers.value.length === 0) {
    toastService.warning('Vui lòng chọn ít nhất một người dùng');
    return;
  }

  try {
    await userStore.bulkUpdateStatus(selectedUsers.value, action);
    toastService.success(`Đã ${action} ${selectedUsers.value.length} người dùng`);
    selectedUsers.value = [];
    await fetchUsers();
  } catch (error) {
    toastService.error('Không thể thực hiện thao tác hàng loạt');
  }
};

const handleCreateUser = async (userData) => {
  loading.value = true;
  try {
    await api.post('/api/admin/users', userData);
    toastService.success('Đã tạo người dùng mới');
    showUserFormModal.value = false;
    await fetchUsers();
  } catch (error) {
    console.error('Create user error:', error);
    toastService.error(error.message || 'Không thể tạo người dùng');
  } finally {
    loading.value = false;
  }
};

const handleExport = async (format = 'excel') => {
  try {
    let usersToExport = [];
    
    if (selectedUsers.value.length > 0) {
      // Export selected users only
      usersToExport = userStore.users.filter(user => selectedUsers.value.includes(user.id));
    } else {
      // Export all users - fetch all if needed
      if (userStore.users.length < pagination.value.total) {
        toastService.info('Đang tải tất cả người dùng để xuất...');
        await userStore.fetchUsers({
          ...filters.value,
          page: 1,
          limit: pagination.value.total,
        });
        usersToExport = userStore.users;
      } else {
        usersToExport = userStore.users;
      }
    }
    
    if (usersToExport.length === 0) {
      toastService.warning('Không có dữ liệu để xuất');
      return;
    }
    
    // Prepare data for export
    const exportData = usersToExport.map(user => ({
      'UID': user.uid || user.id,
      'Email': user.email || '',
      'Tên hiển thị': user.display_name || user.full_name || '',
      'Trạng thái': user.status || '',
      'Xác thực email': user.email_verified ? 'Đã xác thực' : 'Chưa xác thực',
      'Ngày đăng ký': user.join_date || user.created_at ? new Date(user.join_date || user.created_at).toLocaleDateString('vi-VN') : '',
      'Lần đăng nhập cuối': user.last_login ? new Date(user.last_login).toLocaleDateString('vi-VN') : 'N/A',
    }));
    
    if (format === 'excel') {
      // Export to Excel using ExcelJS
      const workbook = new ExcelJS.Workbook();
      const worksheet = workbook.addWorksheet('Users');
      
      // Add headers
      const headers = Object.keys(exportData[0]);
      worksheet.columns = headers.map(header => ({ header, key: header, width: 20 }));
      
      // Add data rows
      worksheet.addRows(exportData);
      
      // Style header row
      worksheet.getRow(1).font = { bold: true };
      worksheet.getRow(1).fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFE0E0E0' }
      };
      
      // Generate filename with timestamp
      const filename = `users_export_${new Date().toISOString().split('T')[0]}.xlsx`;
      
      // Write file
      const buffer = await workbook.xlsx.writeBuffer();
      const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toastService.success(`Đã xuất ${usersToExport.length} người dùng ra file Excel`);
    } else {
      // Export to CSV
      const headers = Object.keys(exportData[0]);
      const csvRows = [
        headers.join(','),
        ...exportData.map(row => headers.map(header => {
          const value = row[header];
          // Escape commas and quotes in CSV
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(','))
      ];
      const csv = csvRows.join('\n');
      
      // Create blob and download
      const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      
      const filename = `users_export_${new Date().toISOString().split('T')[0]}.csv`;
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      toastService.success(`Đã xuất ${usersToExport.length} người dùng ra file CSV`);
    }
  } catch (error) {
    console.error('Export error:', error);
    toastService.error('Không thể xuất dữ liệu');
  }
};

const handlePageChange = (page) => {
  pagination.value.page = page;
  fetchUsers();
};

const handleFilterUpdate = (newFilters) => {
  filters.value = { ...filters.value, ...newFilters };
  pagination.value.page = 1;
  fetchUsers();
};

const fetchAutoApproveSetting = async () => {
  try {
    const response = await api.get('/api/admin/settings/auto-approve-registration');
    autoApproveEnabled.value = response.data?.data?.enabled || false;
    showPendingRegistrations.value = !autoApproveEnabled.value;
  } catch (error) {
    console.error('Fetch auto approve setting error:', error);
  }
};

const fetchPendingRegistrations = async () => {
  if (autoApproveEnabled.value) return; // Don't fetch if auto approve is enabled
  
  pendingRegistrationsLoading.value = true;
  try {
    const response = await api.get('/api/admin/registrations', {
      params: {
        page: 1,
        page_size: 20,
        status_filter: 'pending'
      }
    });
    pendingRegistrations.value = response.data?.data?.registrations || [];
  } catch (error) {
    console.error('Fetch pending registrations error:', error);
    toastService.error('Không thể tải danh sách đăng ký chờ duyệt');
  } finally {
    pendingRegistrationsLoading.value = false;
  }
};

const handleApproveRegistration = async (registrationId) => {
  try {
    await api.post(`/api/admin/registrations/${registrationId}/approve`);
    toastService.success('Đã phê duyệt đăng ký thành công');
    await fetchPendingRegistrations();
    await fetchUsers(); // Refresh user list
  } catch (error) {
    console.error('Approve registration error:', error);
    toastService.error(error.response?.data?.detail || 'Không thể phê duyệt đăng ký');
  }
};

onMounted(() => {
  fetchUsers();
  fetchAutoApproveSetting().then(() => {
    if (showPendingRegistrations.value) {
      fetchPendingRegistrations();
    }
  });
});
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-white mb-2">Quản lý người dùng</h1>
        <p class="text-white/60">Quản lý và theo dõi người dùng hệ thống</p>
      </div>
      <div class="flex items-center gap-3">
        <Button 
          variant="secondary" 
          icon="fas fa-cog" 
          @click="showRegistrationConfigModal = true"
        >
          Tùy chọn thông tin đăng ký
        </Button>
        <Button variant="primary" icon="fas fa-plus" @click="showUserFormModal = true">
          Thêm người dùng
        </Button>
      </div>
    </div>

    <!-- Filters -->
    <UserFilters
      :filters="filters"
      @update:filters="handleFilterUpdate"
      @export="(format) => handleExport(format)"
    />

    <!-- Pending Registrations Section -->
    <Card v-if="showPendingRegistrations">
      <div class="mb-4">
        <h2 class="text-xl font-semibold text-white mb-2">Đăng ký chờ duyệt</h2>
        <p class="text-sm text-white/60">
          Danh sách người dùng đã đăng ký đang chờ phê duyệt. 
          <router-link to="/admin/settings" class="text-purple-400 hover:text-purple-300 underline">
            Bật tự động phê duyệt
          </router-link>
          để tự động approve tất cả đăng ký mới.
        </p>
      </div>
      
      <div v-if="pendingRegistrationsLoading" class="text-center py-8">
        <i class="fas fa-spinner fa-spin text-purple-400 text-2xl"></i>
        <p class="text-white/60 mt-2">Đang tải...</p>
      </div>
      
      <div v-else-if="pendingRegistrations.length === 0" class="text-center py-8">
        <p class="text-white/60">Không có đăng ký nào chờ duyệt</p>
      </div>
      
      <div v-else class="space-y-3">
        <div
          v-for="reg in pendingRegistrations"
          :key="reg.id"
          class="bg-slate-800/50 rounded-lg p-4 border border-white/10 flex items-center justify-between"
        >
          <div class="flex-1">
            <div class="flex items-center gap-3">
              <div>
                <p class="text-white font-medium">{{ reg.display_name || reg.email }}</p>
                <p class="text-sm text-white/60">{{ reg.email }}</p>
                <p v-if="reg.phone" class="text-sm text-white/60">{{ reg.phone }}</p>
              </div>
            </div>
            <p class="text-xs text-white/40 mt-1">
              Đăng ký lúc: {{ new Date(reg.created_at).toLocaleString('vi-VN') }}
            </p>
          </div>
          <Button
            variant="primary"
            size="sm"
            @click="handleApproveRegistration(reg.id)"
          >
            <i class="fas fa-check mr-2"></i>
            Phê duyệt
          </Button>
        </div>
      </div>
    </Card>

    <!-- Auto Approve Info -->
    <Card v-else class="bg-green-500/10 border-green-500/30">
      <div class="flex items-center gap-3">
        <i class="fas fa-check-circle text-green-400 text-xl"></i>
        <div>
          <p class="text-white font-medium">Tự động phê duyệt đăng ký đã được bật</p>
          <p class="text-sm text-white/60">Tất cả đăng ký mới sẽ tự động được phê duyệt và kích hoạt ngay lập tức.</p>
        </div>
      </div>
    </Card>

    <!-- Bulk Actions -->
    <UserBulkActions
      :selected-count="selectedUsers.length"
      @bulk-activate="handleBulkAction('active')"
      @bulk-suspend="handleBulkAction('suspended')"
      @bulk-ban="handleBulkAction('banned')"
      @clear-selection="selectedUsers = []"
    />

    <!-- User Table -->
    <Card>
      <UserTable
        :users="userStore.users"
        :loading="loading"
        :selected-users="selectedUsers"
        :pagination="pagination"
        @select="handleSelect"
        @select-all="handleSelectAll"
        @view="handleView"
        @update-status="handleUpdateStatus"
        @page-change="handlePageChange"
      />
    </Card>

    <!-- User Profile Modal -->
    <UserProfileModal
      :show="showUserModal"
      :user="selectedUser"
      :loading="loading"
      @update:show="showUserModal = $event"
      @close="showUserModal = false"
      @update-status="handleUpdateStatus"
    />

    <!-- User Form Modal -->
    <UserFormModal
      :show="showUserFormModal"
      :loading="loading"
      @update:show="showUserFormModal = $event"
      @close="showUserFormModal = false"
      @submit="handleCreateUser"
    />

    <!-- Registration Fields Config Modal -->
    <Modal
      :show="showRegistrationConfigModal"
      title="Tùy chọn thông tin đăng ký"
      size="xl"
      @update:show="showRegistrationConfigModal = $event"
      @close="showRegistrationConfigModal = false"
    >
      <RegistrationFieldsConfig
        :show="showRegistrationConfigModal"
        @close="showRegistrationConfigModal = false"
      />
    </Modal>
  </div>
</template>

