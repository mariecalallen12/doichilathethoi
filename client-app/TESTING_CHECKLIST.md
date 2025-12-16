# Testing Checklist - Post-Fixes Deployment

**Date**: 2025-01-08  
**Version**: 1.0  
**Status**: Ready for Testing

---

## Overview

This checklist covers all testing scenarios for the fixes deployed:
1. Desktop Navigation Links Fix
2. Double Redirect Issue Fix
3. Environment Variables Verification

---

## Phase 1: Production Environment Testing

### 1.1 API Integration Testing

#### API Base URL Configuration
- [ ] Verify `VITE_API_BASE_URL` is set correctly in production
- [ ] Test API health endpoint: `GET /api/health`
- [ ] Verify API responses are correct
- [ ] Test with production URL (not localhost)
- [ ] Verify error handling when API is unavailable

**Test Command**:
```bash
node scripts/test-production-api.mjs --api-url=https://your-production-api.com
```

#### WebSocket Connection Testing
- [ ] Verify `VITE_WS_URL` is set correctly in production
- [ ] Test WebSocket connection establishment
- [ ] Verify WebSocket reconnection on disconnect
- [ ] Test WebSocket message handling
- [ ] Verify WebSocket with production URL (wss://)

**Test Command**:
```bash
node scripts/test-production-api.mjs --ws-url=wss://your-production-api.com/ws
```

#### Authentication Flow Testing
- [ ] Test login endpoint: `POST /api/auth/login`
- [ ] Test registration endpoint: `POST /api/auth/register`
- [ ] Verify token storage in localStorage
- [ ] Test token refresh mechanism
- [ ] Verify logout functionality
- [ ] Test authentication error handling

#### CORS Configuration
- [ ] Verify CORS headers are present
- [ ] Test from different origins
- [ ] Verify preflight requests work
- [ ] Test with credentials

---

### 1.2 Environment Variables Verification

#### Docker Build Configuration
- [ ] Verify `Dockerfile` has ARG declarations for `VITE_API_BASE_URL`
- [ ] Verify `Dockerfile` has ARG declarations for `VITE_WS_URL`
- [ ] Verify `Dockerfile` has ENV declarations
- [ ] Test Docker build with custom environment variables

**Test Command**:
```bash
docker build --build-arg VITE_API_BASE_URL=https://api.example.com \
             --build-arg VITE_WS_URL=wss://api.example.com/ws \
             -t client-app:test ./client-app
```

#### Docker Compose Configuration
- [ ] Verify `docker-compose.yml` passes environment variables
- [ ] Verify `docker-compose.prod.yml` has production overrides
- [ ] Test environment variables in running container
- [ ] Verify variables are accessible in browser console

**Test Command**:
```bash
# Check environment variables in container
docker exec digital_utopia_client printenv | grep VITE
```

#### Runtime Environment Variables
- [ ] Verify variables are available at runtime
- [ ] Test with different environment values
- [ ] Verify fallback values work correctly
- [ ] Test in browser console: `import.meta.env.VITE_API_BASE_URL`

---

### 1.3 Navigation Flow Testing

#### Desktop Navigation Links
- [ ] Test Home link (`/`) - should navigate to homepage
- [ ] Test Market link (`/market`) - should navigate to market page
- [ ] Test Trading link (`/trading`) - should navigate to trading dashboard
- [ ] Test Education link (`/education`) - should navigate to education page
- [ ] Test Analysis link (`/analysis`) - should navigate to analysis page

**Test Steps**:
1. Open application in browser
2. Click each navigation link
3. Verify URL changes correctly
4. Verify page content loads
5. Verify active state highlighting works

#### Active State Highlighting
- [ ] Verify active route is highlighted
- [ ] Test active state on page load
- [ ] Test active state when navigating
- [ ] Verify active class is applied correctly

#### Cross-Browser Testing
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Test in Edge
- [ ] Test in mobile browsers (iOS Safari, Chrome Mobile)

#### Mobile Navigation
- [ ] Verify mobile navigation still works
- [ ] Test hamburger menu functionality
- [ ] Verify mobile navigation doesn't conflict with desktop fixes
- [ ] Test responsive breakpoints

---

### 1.4 Login Redirect Testing

#### Login from Modal
- [ ] Open login modal from homepage
- [ ] Enter valid credentials
- [ ] Submit login form
- [ ] Verify redirect to `/personal/dashboard`
- [ ] Verify no double navigation in browser history
- [ ] Verify token is stored in localStorage

#### Login from Standalone Page
- [ ] Navigate to `/login` page
- [ ] Enter valid credentials
- [ ] Submit login form
- [ ] Verify redirect to `/personal/dashboard`
- [ ] Verify no double navigation
- [ ] Verify token is stored

#### Redirect Query Parameter
- [ ] Navigate to `/login?redirect=/market`
- [ ] Login with valid credentials
- [ ] Verify redirect to `/market` (not dashboard)
- [ ] Test with different redirect paths
- [ ] Verify redirect parameter is respected

#### Browser History Verification
- [ ] Open browser DevTools
- [ ] Navigate to History tab
- [ ] Perform login
- [ ] Verify only one navigation entry
- [ ] Verify no duplicate entries

#### Error Handling
- [ ] Test login with invalid credentials
- [ ] Verify error message displays
- [ ] Verify no redirect on error
- [ ] Test network error handling
- [ ] Verify modal stays open on error

---

## Phase 2: User Acceptance Testing (UAT)

### 2.1 Navigation User Testing

#### User Scenarios
- [ ] **Scenario 1**: New user browsing the site
  - User opens homepage
  - User clicks through all navigation links
  - User verifies all pages load correctly
  
- [ ] **Scenario 2**: Returning user navigation
  - User logs in
  - User navigates between pages
  - User verifies active state highlighting
  
- [ ] **Scenario 3**: Mobile user navigation
  - User opens site on mobile device
  - User uses mobile navigation menu
  - User verifies all links work

#### Feedback Collection
- [ ] Collect user feedback on navigation experience
- [ ] Document any issues reported
- [ ] Track user satisfaction scores
- [ ] Note any confusion or difficulties

---

### 2.2 Login Flow User Testing

#### User Scenarios
- [ ] **Scenario 1**: First-time login
  - User registers new account
  - User logs in for first time
  - User verifies redirect works correctly
  
- [ ] **Scenario 2**: Returning user login
  - User logs in with existing account
  - User verifies redirect to dashboard
  - User verifies no double navigation
  
- [ ] **Scenario 3**: Login with redirect
  - User tries to access protected page
  - User is redirected to login
  - User logs in
  - User is redirected back to original page

#### Feedback Collection
- [ ] Collect user feedback on login experience
- [ ] Document any issues reported
- [ ] Track login success rate
- [ ] Note any confusion or difficulties

---

## Phase 3: Wallet, Trading & 2FA Flows

### 3.1 Login → Overview → Mini Wallet
- [ ] Login with valid account and verify redirect to `/personal/overview`
- [ ] Confirm Mini Wallet widget appears only when logged in
- [ ] Verify Mini Wallet shows loading skeleton before balance is available
- [ ] Confirm available/locked/pending balances match `Overview` and `Wallet` views
- [ ] Verify Mini Wallet action buttons navigate to `/personal/deposit`, `/personal/withdraw`, `/trading`
- [ ] Test keyboard access to Mini Wallet toggle (Enter/Space) and check `aria-expanded` state

### 3.2 Deposits & Withdrawals
- [ ] Create crypto deposit request and verify address/QR are returned
- [ ] Create VietQR deposit request and verify QR data/expiry
- [ ] Create withdrawal request (bank) and verify limits and fee are shown
- [ ] Verify toast notifications appear for success and failure on deposit/withdraw
- [ ] Verify error messages surface backend validation (min amount, insufficient balance, etc.)

### 3.3 Trading CTA & Balance Sync
- [ ] Place market order from trading dashboard and verify:
  - [ ] Order list updates
  - [ ] Open positions reflect new position (if filled)
  - [ ] Account balance and locked balance update correctly
  - [ ] Success toast shown, error toast on failure
- [ ] Cancel pending order and verify locked balance is released
- [ ] Close open position and verify PnL is reflected in wallet balance

### 3.4 Exchange Rates & Portfolio
- [ ] Verify `/api/client/exchange-rates` returns active rates from database
- [ ] Confirm Exchange Rates view and portfolio analytics use real rates (no mock values)
- [ ] Check that USDT→VND, BTC/ETH→USDT mapping is correct in overview and portfolio charts
- [ ] Simulate API/network error and verify user-friendly error message and no crash

### 3.5 2FA & Security
- [ ] Verify phone verification status is displayed correctly in profile verification panel
- [ ] Attempt withdrawal with account missing phone verification:
  - [ ] Expect 2FA/phone verification error
  - [ ] Error message is surfaced via toast and form error
- [ ] Attempt withdrawal with fully verified account and confirm success
- [ ] Confirm security panel shows 2FA status in sync with backend (based on phone verification)
- [ ] Verify warning text clearly states 2FA requirement for sensitive actions (withdraw, password changes)

## Phase 4: Documentation Verification

### 3.1 Setup Guide
- [ ] Verify `ENV_EXAMPLE.md` is up to date
- [ ] Verify environment variables are documented
- [ ] Verify setup instructions are clear
- [ ] Test setup instructions with fresh environment

### 3.2 Troubleshooting Guide
- [ ] Verify troubleshooting guide exists
- [ ] Verify common issues are documented
- [ ] Verify solutions are provided
- [ ] Test troubleshooting steps

---

## Test Results Summary

### Test Execution
- **Date**: _______________
- **Tester**: _______________
- **Environment**: _______________

### Results
- **Total Tests**: _______________
- **Passed**: _______________
- **Failed**: _______________
- **Blocked**: _______________

### Issues Found
1. _______________
2. _______________
3. _______________

### Notes
_______________
_______________
_______________

---

## Sign-off

- [ ] All Phase 1 tests completed
- [ ] All Phase 2 tests completed
- [ ] All Phase 3 tests completed
- [ ] All critical issues resolved
- [ ] Ready for production deployment

**Approved by**: _______________  
**Date**: _______________
