<template>
  <div ref="editorContainer" class="monaco-editor-container"></div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue';
import * as monaco from 'monaco-editor';

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'javascript',
  },
  theme: {
    type: String,
    default: 'vs-dark',
  },
  readOnly: {
    type: Boolean,
    default: false,
  },
  height: {
    type: String,
    default: '300px',
  },
});

const emit = defineEmits(['update:modelValue', 'change']);

const editorContainer = ref(null);
let editor = null;

onMounted(() => {
  if (!editorContainer.value) return;

  // Tạo Monaco Editor instance
  editor = monaco.editor.create(editorContainer.value, {
    value: props.modelValue,
    language: props.language,
    theme: props.theme,
    readOnly: props.readOnly,
    automaticLayout: true,
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: false,
    cursorStyle: 'line',
    wordWrap: 'on',
    // Autocomplete suggestions
    quickSuggestions: true,
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    tabCompletion: 'on',
  });

  // Custom autocomplete cho các biến có sẵn
  monaco.languages.registerCompletionItemProvider('javascript', {
    provideCompletionItems: () => {
      return {
        suggestions: [
          {
            label: 'price',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'price',
            documentation: 'Giá hiện tại',
          },
          {
            label: 'dt',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'dt',
            documentation: 'Delta time (seconds)',
          },
          {
            label: 'trend',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'trend',
            documentation: 'Xu hướng: UPTREND, DOWNTREND, SIDEWAY',
          },
          {
            label: 'target',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'target',
            documentation: 'Target price (nếu có)',
          },
          {
            label: 'drift',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'drift',
            documentation: 'Drift rate',
          },
          {
            label: 'volatility',
            kind: monaco.languages.CompletionItemKind.Variable,
            insertText: 'volatility',
            documentation: 'Volatility',
          },
          {
            label: 'math',
            kind: monaco.languages.CompletionItemKind.Module,
            insertText: 'math.',
            documentation: 'Math functions: sin, cos, exp, log, sqrt, etc.',
          },
          {
            label: 'random',
            kind: monaco.languages.CompletionItemKind.Module,
            insertText: 'random',
            documentation: 'Random number generator: random.random()',
          },
        ],
      };
    },
  });

  // Listen for changes
  editor.onDidChangeModelContent(() => {
    const value = editor.getValue();
    emit('update:modelValue', value);
    emit('change', value);
  });

  // Set container height
  if (editorContainer.value) {
    editorContainer.value.style.height = props.height;
  }
});

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose();
  }
});

watch(
  () => props.modelValue,
  (newValue) => {
    if (editor && editor.getValue() !== newValue) {
      editor.setValue(newValue);
    }
  }
);

watch(
  () => props.language,
  (newLanguage) => {
    if (editor) {
      monaco.editor.setModelLanguage(editor.getModel(), newLanguage);
    }
  }
);
</script>

<style scoped>
.monaco-editor-container {
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}
</style>

