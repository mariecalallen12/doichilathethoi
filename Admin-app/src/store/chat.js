import { defineStore } from 'pinia';
import api from '../services/api';
import { useAuthStore } from './auth';

const getWsBaseUrl = () => {
  const url = api.baseURL;
  if (url.startsWith('https')) {
    return url.replace('https', 'wss');
  }
  return url.replace('http', 'ws');
};

export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [],
    activeConversation: null,
    isLoading: false,
    error: null,
    socket: null,
    isConnected: false,
  }),
  getters: {
    sortedConversations: (state) => {
        return [...state.conversations].sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    }
  },
  actions: {
    async fetchConversations() {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get('/api/admin/conversations');
        this.conversations = response;
      } catch (error) {
        this.error = error;
        console.error("Failed to fetch conversations:", error);
      } finally {
        this.isLoading = false;
      }
    },

    async selectConversation(conversationId) {
        if (this.activeConversation?.id === conversationId) return;

        // Disconnect from old socket if it exists
        this.disconnectWebSocket();

        this.isLoading = true;
        this.activeConversation = null;
        try {
            const response = await api.get(`/api/conversations/${conversationId}`);
            this.activeConversation = response;
            this.connectWebSocket();
        } catch (error) {
            this.error = error;
        } finally {
            this.isLoading = false;
        }
    },

    connectWebSocket() {
      if (this.socket || !this.activeConversation) return;

      const conversationId = this.activeConversation.id;
      const socketUrl = `${getWsBaseUrl()}/ws/chat/${conversationId}`;
      this.socket = new WebSocket(socketUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log(`WebSocket connected for conversation ${conversationId}`);
        // Send auth token
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
      if (!this.socket || !this.isConnected) {
        console.error("WebSocket is not connected.");
        return;
      }
      const message = {
        content: messageContent,
      };
      this.socket.send(JSON.stringify(message));
    },

    handleIncomingMessage(message) {
      // It might be a system message or a chat message
      if(message.type === 'system') {
        console.log('System message:', message.message);
        return;
      }

      // It's a chat message, find the right conversation
      const convoId = message.conversation_id;
      const conversation = this.conversations.find(c => c.id === convoId);
      if (conversation) {
          conversation.updated_at = message.created_at; // Update timestamp for sorting
      }

      if (this.activeConversation && this.activeConversation.id === convoId) {
        // Avoid adding duplicate messages if backend broadcasts to sender
        const existingMessage = this.activeConversation.messages.find(m => m.id === message.id);
        if (!existingMessage) {
            this.activeConversation.messages.push(message);
        }
      }
    }
  },
});
