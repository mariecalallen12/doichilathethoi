<script setup>
import { ref, watch } from 'vue';
import Modal from '../ui/Modal.vue';
import Input from '../ui/Input.vue';
import Button from '../ui/Button.vue';
import Card from '../ui/Card.vue';

const props = defineProps({
  show: Boolean,
  invoice: {
    type: Object,
    default: null,
  },
  loading: Boolean,
});

const emit = defineEmits(['close', 'update:show', 'submit']);

const formData = ref({
  user_id: '',
  amount: '',
  description: '',
  due_date: '',
  items: [],
});

const newItem = ref({
  name: '',
  quantity: 1,
  price: '',
  description: '',
});

const errors = ref({});

const resetForm = () => {
  formData.value = {
    user_id: '',
    amount: '',
    description: '',
    due_date: '',
    items: [],
  };
  newItem.value = {
    name: '',
    quantity: 1,
    price: '',
    description: '',
  };
  errors.value = {};
};

watch(
  () => props.invoice,
  (newInvoice) => {
    if (newInvoice) {
      formData.value = {
        user_id: newInvoice.user_id || '',
        amount: newInvoice.amount || '',
        description: newInvoice.description || '',
        due_date: newInvoice.due_date ? newInvoice.due_date.split('T')[0] : '',
        items: newInvoice.items || [],
      };
    } else {
      resetForm();
    }
  },
  { immediate: true }
);

watch(
  () => props.show,
  (show) => {
    if (!show) {
      resetForm();
    }
  }
);

const validate = () => {
  errors.value = {};
  
  if (!formData.value.user_id) {
    errors.value.user_id = 'User ID là bắt buộc';
  }
  
  if (!formData.value.amount || parseFloat(formData.value.amount) <= 0) {
    errors.value.amount = 'Số tiền phải lớn hơn 0';
  }
  
  if (!formData.value.description) {
    errors.value.description = 'Mô tả là bắt buộc';
  }
  
  if (!formData.value.due_date) {
    errors.value.due_date = 'Ngày đến hạn là bắt buộc';
  }
  
  return Object.keys(errors.value).length === 0;
};

const addItem = () => {
  if (!newItem.value.name || !newItem.value.price) {
    return;
  }
  
  formData.value.items.push({
    name: newItem.value.name,
    quantity: parseInt(newItem.value.quantity) || 1,
    price: parseFloat(newItem.value.price) || 0,
    description: newItem.value.description || '',
  });
  
  // Recalculate total amount
  const total = formData.value.items.reduce((sum, item) => sum + item.quantity * item.price, 0);
  formData.value.amount = total.toFixed(2);
  
  newItem.value = {
    name: '',
    quantity: 1,
    price: '',
    description: '',
  };
};

const removeItem = (index) => {
  formData.value.items.splice(index, 1);
  const total = formData.value.items.reduce((sum, item) => sum + item.quantity * item.price, 0);
  formData.value.amount = total.toFixed(2);
};

const handleSubmit = () => {
  if (!validate()) {
    return;
  }
  
  emit('submit', {
    ...formData.value,
    amount: parseFloat(formData.value.amount),
  });
};
</script>

<template>
  <Modal
    :show="show"
    :title="invoice ? 'Sửa hóa đơn' : 'Tạo hóa đơn mới'"
    size="xl"
    @update:show="emit('update:show', $event)"
    @close="emit('close')"
  >
    <div class="space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <Input
          v-model="formData.user_id"
          label="User ID *"
          placeholder="Nhập User ID"
          :error="errors.user_id"
        />
        <Input
          v-model="formData.amount"
          label="Số tiền ($) *"
          type="number"
          step="0.01"
          placeholder="0.00"
          :error="errors.amount"
        />
      </div>
      
      <Input
        v-model="formData.description"
        label="Mô tả *"
        placeholder="Mô tả hóa đơn"
        :error="errors.description"
      />
      
      <Input
        v-model="formData.due_date"
        label="Ngày đến hạn *"
        type="date"
        :error="errors.due_date"
      />
      
      <!-- Invoice Items -->
      <Card title="Chi tiết hóa đơn" padding="p-4">
        <div class="space-y-4">
          <div class="grid grid-cols-12 gap-2">
            <Input
              v-model="newItem.name"
              label="Tên sản phẩm/dịch vụ"
              placeholder="Tên"
              class="col-span-4"
            />
            <Input
              v-model="newItem.quantity"
              label="Số lượng"
              type="number"
              class="col-span-2"
            />
            <Input
              v-model="newItem.price"
              label="Giá ($)"
              type="number"
              step="0.01"
              class="col-span-3"
            />
            <Input
              v-model="newItem.description"
              label="Mô tả"
              placeholder="Mô tả"
              class="col-span-2"
            />
            <div class="col-span-1 flex items-end">
              <Button variant="primary" size="sm" @click="addItem">
                <i class="fas fa-plus"></i>
              </Button>
            </div>
          </div>
          
          <div v-if="formData.items.length > 0" class="space-y-2">
            <div
              v-for="(item, index) in formData.items"
              :key="index"
              class="flex items-center justify-between p-3 bg-white/5 rounded-lg"
            >
              <div class="flex-1">
                <p class="text-white font-semibold">{{ item.name }}</p>
                <p class="text-white/60 text-sm">
                  {{ item.quantity }} x ${{ item.price.toLocaleString() }} = 
                  ${{ (item.quantity * item.price).toLocaleString() }}
                </p>
                <p v-if="item.description" class="text-white/40 text-xs mt-1">{{ item.description }}</p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                icon="fas fa-trash text-red-400"
                @click="removeItem(index)"
              >
              </Button>
            </div>
          </div>
        </div>
      </Card>
      
      <div class="flex items-center justify-end gap-3 pt-4 border-t border-white/10">
        <Button variant="outline" @click="emit('close')">Hủy</Button>
        <Button variant="primary" :loading="loading" @click="handleSubmit">
          {{ invoice ? 'Cập nhật' : 'Tạo hóa đơn' }}
        </Button>
      </div>
    </div>
  </Modal>
</template>

