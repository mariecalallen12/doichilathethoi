/**
 * Session Manager Utility
 * Manages dynamic session IDs and debug logging
 */

// Generate a unique session ID
function generateSessionId() {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

// Get or create session ID
let sessionId = null
export function getSessionId() {
  if (!sessionId) {
    sessionId = generateSessionId()
    // Store in sessionStorage for persistence
    if (typeof window !== 'undefined' && window.sessionStorage) {
      try {
        sessionId = window.sessionStorage.getItem('app_session_id') || generateSessionId()
        window.sessionStorage.setItem('app_session_id', sessionId)
      } catch (e) {
        // Fallback if sessionStorage is not available
        sessionId = generateSessionId()
      }
    }
  }
  return sessionId
}

// Reset session ID (useful for testing)
export function resetSessionId() {
  sessionId = null
  if (typeof window !== 'undefined' && window.sessionStorage) {
    try {
      window.sessionStorage.removeItem('app_session_id')
    } catch (e) {
      // Ignore errors
    }
  }
}

// Check if debug logging is enabled
export function isDebugLoggingEnabled() {
  if (typeof window === 'undefined') return false
  // Check environment variable or localStorage flag
  return import.meta.env.VITE_ENABLE_DEBUG_LOGGING === 'true' || 
         (window.localStorage && window.localStorage.getItem('debug_logging') === 'true')
}

// Debug log function (only logs if enabled)
export function debugLog(location, message, data = {}) {
  if (!isDebugLoggingEnabled()) return
  
  const debugEndpoint = import.meta.env.VITE_DEBUG_ENDPOINT || 'http://localhost:7242/ingest/a94652aa-f954-45ed-8dd8-1c88a5bdb78d'
  
  try {
    fetch(debugEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location,
        message,
        data,
        timestamp: Date.now(),
        sessionId: getSessionId(),
        runId: 'run1',
        hypothesisId: 'E'
      })
    }).catch(() => {
      // Silently fail - debug logging should not break the app
    })
  } catch (e) {
    // Silently fail
  }
}

