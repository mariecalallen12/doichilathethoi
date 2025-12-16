# Troubleshooting Guide - Client App

**Last Updated**: 2025-01-08  
**Version**: 1.0

---

## Table of Contents

1. [Navigation Issues](#navigation-issues)
2. [Login Redirect Issues](#login-redirect-issues)
3. [Environment Variables Issues](#environment-variables-issues)
4. [API Connection Issues](#api-connection-issues)
5. [WebSocket Connection Issues](#websocket-connection-issues)
6. [Build and Deployment Issues](#build-and-deployment-issues)
7. [Common Errors](#common-errors)

---

## Navigation Issues

### Problem: Navigation links not working

**Symptoms**:
- Clicking navigation links doesn't navigate
- URL doesn't change when clicking links
- Page doesn't load when clicking links

**Possible Causes**:
1. Router not properly configured
2. Routes not defined in router
3. JavaScript errors preventing navigation

**Solutions**:

1. **Check Router Configuration**
   ```javascript
   // Verify router/index.js has all routes defined
   // Check that routes match navigation links:
   // - / (Home)
   // - /market (Market)
   // - /trading (Trading)
   // - /education (Education)
   // - /analysis (Analysis)
   ```

2. **Check Browser Console**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Look for router-related errors

3. **Verify Navigation Component**
   - Check `HomePage.vue` lines 223-242
   - Verify all links use `<router-link>` not `<a>`
   - Verify `to` attribute matches route paths

4. **Clear Browser Cache**
   - Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
   - Clear browser cache
   - Try incognito/private mode

**Debug Steps**:
```javascript
// In browser console:
import { useRouter } from 'vue-router';
const router = useRouter();
console.log(router.getRoutes()); // Check all routes
```

---

### Problem: Active state not highlighting

**Symptoms**:
- Current route not highlighted in navigation
- Active link doesn't have visual indication

**Solutions**:

1. **Check Active Class**
   - Verify `active-class` prop is set on `<router-link>`
   - Check CSS for active state styling

2. **Verify Route Matching**
   ```javascript
   // Check if route is matching correctly
   // Active class should be: "text-transparent bg-gradient-to-r from-purple-300 to-indigo-300 bg-clip-text"
   ```

3. **Check CSS Classes**
   - Verify Tailwind classes are available
   - Check if custom CSS conflicts

---

### Problem: Mobile navigation not working

**Symptoms**:
- Hamburger menu doesn't open
- Mobile menu links don't work
- Mobile navigation conflicts with desktop

**Solutions**:

1. **Check Mobile Menu Component**
   - Verify mobile menu is separate from desktop navigation
   - Check that mobile menu uses `<router-link>` as well

2. **Check Responsive Breakpoints**
   - Verify Tailwind breakpoints are correct
   - Test on different screen sizes

3. **Check JavaScript Errors**
   - Open mobile menu
   - Check browser console for errors

---

## Login Redirect Issues

### Problem: Double redirect after login

**Symptoms**:
- Browser history shows duplicate entries
- Page navigates twice
- Redirect happens multiple times

**Solutions**:

1. **Verify LoginModal Redirect Logic**
   - Check `LoginModal.vue` lines 280-294
   - Verify redirect only happens once in LoginModal
   - Ensure `HomePage.vue` handleLoginSuccess doesn't redirect

2. **Check handleLoginSuccess**
   - Verify `HomePage.vue` lines 41-52
   - Ensure no `router.push()` in handleLoginSuccess
   - Only LoginModal should handle redirect

3. **Clear Browser State**
   - Clear localStorage
   - Clear sessionStorage
   - Hard refresh browser

**Debug Steps**:
```javascript
// In browser console, check redirect logic:
console.log('LoginModal redirect:', router.currentRoute.value.query.redirect);
console.log('HomePage handler:', handleLoginSuccess);
```

---

### Problem: Login redirects to wrong page

**Symptoms**:
- Login redirects to homepage instead of dashboard
- Redirect query parameter not respected
- Always redirects to same page

**Solutions**:

1. **Check Redirect Logic**
   ```javascript
   // In LoginModal.vue, verify:
   const redirect = router.currentRoute.value.query.redirect;
   router.push(redirect || "/personal/dashboard");
   ```

2. **Verify Query Parameter**
   - Check URL has `?redirect=/path` parameter
   - Verify parameter is read correctly
   - Test with different redirect paths

3. **Check Route Guards**
   - Verify router guards don't interfere
   - Check authentication requirements

---

### Problem: Login doesn't redirect at all

**Symptoms**:
- Login succeeds but no redirect
- User stays on login page
- Modal doesn't close

**Solutions**:

1. **Check Login Response**
   - Verify API returns success response
   - Check token is stored in localStorage
   - Verify user data is stored

2. **Check Router Push**
   - Verify `router.push()` is called
   - Check for JavaScript errors
   - Verify router is available

3. **Check Modal Close**
   - Verify `handleClose()` is called
   - Check modal state management

**Debug Steps**:
```javascript
// In browser console:
console.log('Token:', localStorage.getItem('auth_token'));
console.log('User:', localStorage.getItem('user'));
console.log('Current route:', router.currentRoute.value.path);
```

---

## Environment Variables Issues

### Problem: API calls fail with wrong URL

**Symptoms**:
- API calls go to localhost instead of production
- Network errors in browser console
- CORS errors

**Solutions**:

1. **Check Environment Variables**
   ```bash
   # In Docker container:
   docker exec digital_utopia_client printenv | grep VITE
   
   # Should show:
   # VITE_API_BASE_URL=https://api.example.com
   # VITE_WS_URL=wss://api.example.com/ws
   ```

2. **Verify Docker Build Args**
   ```bash
   # Check Dockerfile has ARG declarations:
   # ARG VITE_API_BASE_URL
   # ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
   ```

3. **Check docker-compose.yml**
   ```yaml
   # Verify build args are set:
   build:
     args:
       VITE_API_BASE_URL: ${CLIENT_API_BASE_URL}
       VITE_WS_URL: ${CLIENT_WS_URL}
   ```

4. **Rebuild with Correct Variables**
   ```bash
   docker-compose build --build-arg VITE_API_BASE_URL=https://api.example.com client-app
   ```

---

### Problem: Environment variables not available at runtime

**Symptoms**:
- `import.meta.env.VITE_API_BASE_URL` is undefined
- Variables not accessible in browser
- Default values used instead

**Solutions**:

1. **Check Build Process**
   - Vite replaces env vars at build time
   - Variables must be available during build
   - Rebuild after changing variables

2. **Verify Variable Names**
   - Must start with `VITE_` prefix
   - Case-sensitive
   - No spaces or special characters

3. **Check .env File**
   ```bash
   # For local development, create .env file:
   VITE_API_BASE_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000/ws
   ```

4. **Rebuild Application**
   ```bash
   # After changing env vars, rebuild:
   npm run build
   # or
   docker-compose build client-app
   ```

---

## API Connection Issues

### Problem: Cannot connect to API

**Symptoms**:
- Network errors in console
- "Failed to fetch" errors
- API calls timeout

**Solutions**:

1. **Check API URL**
   ```javascript
   // In browser console:
   console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
   ```

2. **Test API Endpoint**
   ```bash
   # Test API health endpoint:
   curl https://api.example.com/api/health
   ```

3. **Check CORS Configuration**
   - Verify backend CORS allows frontend origin
   - Check CORS headers in response
   - Verify credentials are handled correctly

4. **Check Network Connectivity**
   - Verify firewall rules
   - Check DNS resolution
   - Test from different network

---

### Problem: API returns 401 Unauthorized

**Symptoms**:
- API calls fail with 401 status
- Token not sent with requests
- Authentication errors

**Solutions**:

1. **Check Token Storage**
   ```javascript
   // In browser console:
   console.log('Token:', localStorage.getItem('auth_token'));
   ```

2. **Verify Token Format**
   - Token should be JWT format
   - Check token is not expired
   - Verify token is valid

3. **Check Request Headers**
   ```javascript
   // Verify Authorization header is set:
   // Authorization: Bearer <token>
   ```

4. **Refresh Token**
   - Try logging out and logging in again
   - Check token refresh mechanism
   - Verify refresh token is valid

---

## WebSocket Connection Issues

### Problem: WebSocket cannot connect

**Symptoms**:
- WebSocket connection fails
- Real-time updates not working
- Connection errors in console

**Solutions**:

1. **Check WebSocket URL**
   ```javascript
   // In browser console:
   console.log('WebSocket URL:', import.meta.env.VITE_WS_URL);
   ```

2. **Verify URL Format**
   - Should be `ws://` or `wss://`
   - Should include `/ws` path
   - Should include token parameter

3. **Test WebSocket Connection**
   ```javascript
   // In browser console:
   const ws = new WebSocket('wss://api.example.com/ws?token=YOUR_TOKEN');
   ws.onopen = () => console.log('Connected');
   ws.onerror = (e) => console.error('Error:', e);
   ```

4. **Check Backend WebSocket Server**
   - Verify WebSocket server is running
   - Check WebSocket endpoint is correct
   - Verify authentication is working

---

### Problem: WebSocket disconnects frequently

**Symptoms**:
- WebSocket connects then disconnects
- Frequent reconnection attempts
- Connection unstable

**Solutions**:

1. **Check Network Stability**
   - Verify network connection is stable
   - Check for network interruptions
   - Test from different network

2. **Check Heartbeat Mechanism**
   - Verify heartbeat is working
   - Check heartbeat interval settings
   - Verify pong responses

3. **Check Reconnection Logic**
   - Verify exponential backoff is working
   - Check max reconnection attempts
   - Verify reconnection delay

---

## Build and Deployment Issues

### Problem: Build fails

**Symptoms**:
- `npm run build` fails
- Docker build fails
- Build errors in console

**Solutions**:

1. **Check Node Version**
   ```bash
   node --version  # Should be 18+ or 20+
   ```

2. **Clear Dependencies**
   ```bash
   rm -rf node_modules package-lock.json
   npm install --legacy-peer-deps
   ```

3. **Check for Errors**
   - Read build error messages carefully
   - Check for missing dependencies
   - Verify all files are present

4. **Check Environment Variables**
   - Verify all required env vars are set
   - Check for syntax errors in .env
   - Verify variable names are correct

---

### Problem: Production build doesn't work

**Symptoms**:
- Build succeeds but app doesn't work
- API calls fail in production
- Environment variables not working

**Solutions**:

1. **Verify Build Args**
   ```bash
   # Check Docker build used correct args:
   docker build --build-arg VITE_API_BASE_URL=... client-app
   ```

2. **Check Build Output**
   - Verify dist folder is created
   - Check for build warnings
   - Verify all assets are included

3. **Test Production Build Locally**
   ```bash
   npm run build
   npm run preview  # Test production build
   ```

---

## Common Errors

### Error: "Cannot read property 'push' of undefined"

**Cause**: Router not properly initialized

**Solution**:
```javascript
// Verify router is imported and used correctly:
import { useRouter } from 'vue-router';
const router = useRouter();
```

---

### Error: "Network Error" or "Failed to fetch"

**Cause**: API server not accessible or CORS issue

**Solution**:
1. Check API URL is correct
2. Verify API server is running
3. Check CORS configuration
4. Verify network connectivity

---

### Error: "401 Unauthorized"

**Cause**: Authentication token missing or invalid

**Solution**:
1. Check token is stored in localStorage
2. Verify token is sent with requests
3. Try logging in again
4. Check token expiration

---

### Error: "WebSocket connection failed"

**Cause**: WebSocket server not accessible or URL incorrect

**Solution**:
1. Check WebSocket URL is correct
2. Verify WebSocket server is running
3. Check authentication token
4. Verify network connectivity

---

## Getting Help

If you're still experiencing issues:

1. **Check Browser Console**
   - Open DevTools (F12)
   - Check Console for errors
   - Check Network tab for failed requests

2. **Check Server Logs**
   - Review backend logs
   - Check for error messages
   - Verify server is running

3. **Review Documentation**
   - Check `ENV_EXAMPLE.md`
   - Review `README.md`
   - Check deployment guides

4. **Contact Support**
   - Document the issue
   - Include error messages
   - Provide steps to reproduce

---

**Last Updated**: 2025-01-08

