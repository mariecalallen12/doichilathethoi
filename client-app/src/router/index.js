import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../views/HomePage.vue';
import RegisterPage from '../views/RegisterPage.vue';
import LoginPage from '../views/LoginPage.vue';
import ForgotPasswordPage from '../views/ForgotPasswordPage.vue';
import MarketView from '../views/MarketView.vue';
import TradingView from '../views/TradingView.vue';
import TestPage from '../views/TestPage.vue';
import PersonalAreaLayout from '../layouts/PersonalAreaLayout.vue';

// Lazy load education view
const EducationView = () => import('../views/EducationView.vue');

// Lazy load analysis and other views
const AnalysisView = () => import('../views/AnalysisView.vue');
const HelpCenterView = () => import('../views/HelpCenterView.vue');
const ContactView = () => import('../views/ContactView.vue');
const FAQView = () => import('../views/FAQView.vue');
const TermsOfServiceView = () => import('../views/TermsOfServiceView.vue');
const PrivacyPolicyView = () => import('../views/PrivacyPolicyView.vue');
const RiskWarningView = () => import('../views/RiskWarningView.vue');
const ComplaintsView = () => import('../views/ComplaintsView.vue');

// Lazy load personal area views
const DashboardView = () => import('../views/personal/DashboardView.vue');
const PersonalUnifiedView = () => import('../views/personal/UnifiedPersonalView.vue');
const DepositView = () => import('../views/personal/DepositView.vue');
const WithdrawView = () => import('../views/personal/WithdrawView.vue');
const ProfileView = () => import('../views/personal/ProfileView.vue');
const WalletView = () => import('../views/personal/WalletView.vue');
const ExchangeRatesView = () => import('../views/personal/ExchangeRatesView.vue');
const TransactionHistoryView = () => import('../views/personal/TransactionHistoryView.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/test',
    name: 'Test',
    component: TestPage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true },
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordPage,
    meta: { requiresGuest: true },
  },
  {
    path: '/market',
    name: 'Market',
    component: MarketView,
  },
  {
    path: '/trading',
    name: 'Trading',
    component: TradingView,
  },
  {
    path: '/education',
    name: 'Education',
    component: EducationView,
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: AnalysisView,
  },
  {
    path: '/help',
    name: 'HelpCenter',
    component: HelpCenterView,
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactView,
  },
  {
    path: '/faq',
    name: 'FAQ',
    component: FAQView,
  },
  {
    path: '/terms',
    name: 'TermsOfService',
    component: TermsOfServiceView,
  },
  {
    path: '/privacy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicyView,
  },
  {
    path: '/risk-warning',
    name: 'RiskWarning',
    component: RiskWarningView,
  },
  {
    path: '/complaints',
    name: 'Complaints',
    component: ComplaintsView,
    meta: { requiresAuth: true },
  },
  // Personal Area Routes
  {
    path: '/personal',
    component: PersonalAreaLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/personal/overview',
      },
      {
        path: 'overview',
        name: 'PersonalOverview',
        component: PersonalUnifiedView,
        meta: { title: 'Trang Cá Nhân' },
      },
      {
        path: 'dashboard',
        name: 'PersonalDashboard',
        component: DashboardView,
        meta: { title: 'Tổng Quan' },
      },
      {
        path: 'deposit',
        name: 'Deposit',
        component: DepositView,
        meta: { title: 'Nạp Tiền' },
      },
      {
        path: 'withdraw',
        name: 'Withdraw',
        component: WithdrawView,
        meta: { title: 'Rút Tiền' },
      },
      {
        path: 'wallet',
        name: 'Wallet',
        component: WalletView,
        meta: { title: 'Ví Điện Tử' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: ProfileView,
        meta: { title: 'Thông Tin Cá Nhân' },
      },
      {
        path: 'rates',
        name: 'ExchangeRates',
        component: ExchangeRatesView,
        meta: { title: 'Tỷ Giá Hối Đoái' },
      },
      {
        path: 'transactions',
        name: 'TransactionHistory',
        component: TransactionHistoryView,
        meta: { title: 'Lịch Sử Giao Dịch' },
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route guard for authentication
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  
  // Get token from localStorage
  const token = localStorage.getItem('auth_token');
  const isAuthenticated = !!token;
  
  // Redirect authenticated users away from guest-only routes (login, register)
  if (requiresGuest && isAuthenticated) {
    // If user is already authenticated and trying to access login/register, redirect to personal area
    next({ name: 'PersonalOverview' });
    return;
  }
  
  // Redirect unauthenticated users away from protected routes
  if (requiresAuth && !isAuthenticated) {
    // Store the intended destination for redirect after login
    next({ 
      name: 'Login', 
      query: { redirect: to.fullPath } 
    });
    return;
  }
  
  // Allow navigation
  next();
});

export default router;

