import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { io } from 'socket.io-client';

export const useChatStore = defineStore('chat', () => {
  // State
  const messages = ref([]);
  const unreadCount = ref(0);
  const isConnected = ref(false);
  const isLoading = ref(false);
  const error = ref(null);
  const socket = ref(null);
  const hasMoreMessages = ref(true);
  const currentPage = ref(1);
  const pageSize = ref(50);

  // Computed
  const sortedMessages = computed(() => {
    return [...messages.value].sort((a, b) => {
      return new Date(a.timestamp) - new Date(b.timestamp);
    });
  });

  // Actions
  function connect() {
    if (socket.value?.connected) {
      return; // Already connected
    }

    try {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      const chatUrl = wsUrl.replace('/ws', '/ws/support/chat');

      socket.value = io(chatUrl, {
        transports: ['websocket'],
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionAttempts: 5,
        reconnectionDelayMax: 5000,
      });

      socket.value.on('connect', () => {
        isConnected.value = true;
        error.value = null;
        console.log('Chat connected');
      });

      socket.value.on('disconnect', () => {
        isConnected.value = false;
        console.log('Chat disconnected');
      });

      socket.value.on('connect_error', (err) => {
        error.value = 'Không thể kết nối đến chat. Vui lòng thử lại sau.';
        isConnected.value = false;
        console.error('Chat connection error:', err);
      });

      // Message events
      socket.value.on('message', (message) => {
        addMessage(message);
        if (message.sender === 'support') {
          unreadCount.value++;
        }
      });

      socket.value.on('message_history', (history) => {
        messages.value = history.messages || [];
        hasMoreMessages.value = history.has_more || false;
        isLoading.value = false;
      });

      socket.value.on('typing', (data) => {
        // Handle typing indicator
        // This would typically update a typing state
      });

      socket.value.on('read_receipt', (data) => {
        // Update message read status
        const message = messages.value.find(m => m.id === data.message_id);
        if (message) {
          message.read = true;
        }
      });

      socket.value.on('error', (err) => {
        error.value = err.message || 'Có lỗi xảy ra trong chat';
        console.error('Chat error:', err);
      });
    } catch (err) {
      error.value = 'Không thể khởi tạo kết nối chat';
      console.error('Error connecting to chat:', err);
    }
  }

  function disconnect() {
    if (socket.value) {
      socket.value.disconnect();
      socket.value = null;
      isConnected.value = false;
    }
  }

  function sendMessage(content, files = []) {
    if (!socket.value?.connected) {
      error.value = 'Chưa kết nối đến chat';
      return Promise.reject(new Error('Not connected'));
    }

    return new Promise((resolve, reject) => {
      const messageData = {
        content,
        files: files.map(file => ({
          name: file.name,
          type: file.type,
          size: file.size,
          // In production, files would be uploaded first and URLs returned
          url: URL.createObjectURL(file)
        })),
        timestamp: new Date().toISOString()
      };

      // Optimistically add message
      const tempMessage = {
        id: `temp-${Date.now()}`,
        ...messageData,
        sender: 'user',
        delivered: false,
        read: false
      };
      addMessage(tempMessage);

      socket.value.emit('send_message', messageData, (response) => {
        if (response.success) {
          // Replace temp message with real message
          const index = messages.value.findIndex(m => m.id === tempMessage.id);
          if (index !== -1) {
            messages.value[index] = {
              ...response.message,
              delivered: true
            };
          }
          resolve(response.message);
        } else {
          // Remove temp message on error
          messages.value = messages.value.filter(m => m.id !== tempMessage.id);
          error.value = response.error || 'Không thể gửi tin nhắn';
          reject(new Error(response.error));
        }
      });
    });
  }

  function loadMessages() {
    if (isLoading.value || !hasMoreMessages.value) {
      return;
    }

    isLoading.value = true;
    
    if (socket.value?.connected) {
      socket.value.emit('get_messages', {
        page: currentPage.value,
        page_size: pageSize.value
      });
    } else {
      // Fallback to API if WebSocket not available
      loadMessagesFromAPI();
    }
  }

  async function loadMessagesFromAPI() {
    try {
      const response = await fetch('/api/support/chat/messages', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        messages.value = data.messages || [];
        hasMoreMessages.value = data.has_more || false;
      }
    } catch (err) {
      console.error('Error loading messages:', err);
      error.value = 'Không thể tải tin nhắn';
    } finally {
      isLoading.value = false;
    }
  }

  function loadMoreMessages() {
    if (isLoading.value || !hasMoreMessages.value) {
      return;
    }

    currentPage.value++;
    loadMessages();
  }

  function addMessage(message) {
    // Check if message already exists
    const exists = messages.value.find(m => m.id === message.id);
    if (!exists) {
      messages.value.push(message);
      // Keep only last 1000 messages in memory
      if (messages.value.length > 1000) {
        messages.value = messages.value.slice(-1000);
      }
    }
  }

  function markAsRead() {
    if (unreadCount.value > 0) {
      unreadCount.value = 0;
      
      // Mark messages as read on server
      if (socket.value?.connected) {
        const unreadIds = messages.value
          .filter(m => m.sender === 'support' && !m.read)
          .map(m => m.id);
        
        if (unreadIds.length > 0) {
          socket.value.emit('mark_read', { message_ids: unreadIds });
        }
      }
    }
  }

  function sendTypingIndicator(typing) {
    if (socket.value?.connected) {
      socket.value.emit('typing', { typing });
    }
  }

  function clearMessages() {
    messages.value = [];
    unreadCount.value = 0;
    currentPage.value = 1;
    hasMoreMessages.value = true;
  }

  // Initialize connection on store creation
  // connect();

  return {
    // State
    messages: sortedMessages,
    unreadCount,
    isConnected,
    isLoading,
    error,
    hasMoreMessages,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    loadMessages,
    loadMoreMessages,
    markAsRead,
    sendTypingIndicator,
    clearMessages
  };
});

