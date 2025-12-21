import { defineStore } from 'pinia';
import api from '../services/api';
import { useAuthStore } from './auth'; // Assuming auth store exists for token

const getWsBaseUrl = () => {
  const url = api.baseURL;
  if (url.startsWith('https')) {
    return url.replace('https', 'wss');
  }
  return url.replace('http', 'ws');
};

export const useChatStore = defineStore('clientChat', { // Changed name to clientChat to avoid conflict
  state: () => ({
    conversation: null, // User will likely have one active conversation with support
    messages: [],
    isLoading: false,
    error: null,
    socket: null,
    isConnected: false,
    unreadCount: 0,
    isChatOpen: false, // To control the visibility of the ChatWindow
  }),
  actions: {
    async fetchOrCreateConversation() {
      this.isLoading = true;
      this.error = null;
      try {
        // First, try to fetch existing conversations for the user
        const existingConversations = await api.get('/api/conversations/me');
        if (existingConversations && existingConversations.length > 0) {
          // Assuming user has only one primary conversation with support
          this.conversation = existingConversations[0];
          this.messages = this.conversation.messages;
          this.calculateUnreadMessages();
        } else {
          // If no conversation exists, create a new one with a default message
          const initialMessageContent = "Hello, I need support."; // Default message for starting a new chat
          const newConversation = await api.post('/api/conversations', { first_message: initialMessageContent });
          this.conversation = newConversation;
          this.messages = newConversation.messages;
          this.unreadCount = 0;
        }
        this.connectWebSocket();
      } catch (error) {
        this.error = error;
        console.error("Failed to fetch or create conversation:", error);
      } finally {
        this.isLoading = false;
      }
    },

    connectWebSocket() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.isConnected = true;
        return;
      }
      if (!this.conversation) return;

      const conversationId = this.conversation.id;
      const socketUrl = `${getWsBaseUrl()}/ws/chat/${conversationId}`;
      this.socket = new WebSocket(socketUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log(`WebSocket connected for conversation ${conversationId}`);
        const authStore = useAuthStore();
        if (authStore.token) {
            this.socket.send(JSON.stringify({ token: authStore.token }));
        } else {
            console.error("No auth token found for WebSocket connection.");
            this.socket.close();
        }
      };

      this.socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleIncomingMessage(message);
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        this.socket = null;
        console.log('WebSocket disconnected');
      };

      this.socket.onerror = (error) => {
        this.error = error;
        this.isConnected = false;
        console.error('WebSocket error:', error);
      };
    },

    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
        this.isConnected = false;
      }
    },

    sendMessage(messageContent) {
      if (!this.socket || !this.isConnected || !this.conversation) {
        console.error("WebSocket is not connected or no active conversation.");
        return;
      }
      const message = {
        content: messageContent,
      };
      this.socket.send(JSON.stringify(message));
    },

    handleIncomingMessage(message) {
      if (message.type === 'system') {
        console.log('System message:', message.message);
        return;
      }
      if (this.conversation && this.conversation.id === message.conversation_id) {
        const existingMessage = this.messages.find(m => m.id === message.id);
        if (!existingMessage) {
            this.messages.push(message);
            if (!this.isChatOpen && message.sender_type !== 'user') { // Increment unread if chat is closed and message is from admin
                this.unreadCount++;
            }
        }
      }
    },

    markAsRead() {
        this.unreadCount = 0;
        // In a real app, you might also send an API call to mark messages as read in DB
    },

    setChatOpen(isOpen) {
        this.isChatOpen = isOpen;
        if (isOpen) {
            this.markAsRead();
        }
    },

    calculateUnreadMessages() {
        // This would require a 'read' status on messages and a user's last read timestamp
        // For simplicity, we'll assume all messages not sent by 'user' are unread
        if (this.messages && this.messages.length > 0) {
            this.unreadCount = this.messages.filter(msg => msg.sender_type !== 'user').length;
        } else {
            this.unreadCount = 0;
        }
    }
  },
});

// Export with alias for compatibility
export const useClientChatStore = useChatStore;