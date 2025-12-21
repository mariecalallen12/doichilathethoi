import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../store/auth";
import LoginPage from "../views/LoginPage.vue";
import Layout from "../components/layout/Layout.vue";

// Lazy load views
const Dashboard = () => import("../views/Dashboard.vue");
const UserManagement = () => import("../views/UserManagement.vue");
const FinancialManagement = () => import("../views/FinancialManagement.vue");
const AnalyticsReports = () => import("../views/AnalyticsReports.vue");
const SystemSettings = () => import("../views/SystemSettings.vue");
const AdminTradingControls = () => import("../views/AdminTradingControls.vue");
const DiagnosticsManagement = () => import("../views/DiagnosticsManagement.vue");
const AlertManagement = () => import("../views/AlertManagement.vue");
const ScenarioBuilder = () => import("../views/ScenarioBuilder.vue");
const MarketPreview = () => import("../views/MarketPreview.vue");
const MarketRealityControl = () => import("../views/MarketRealityControl.vue");
const EducationalHub = () => import("../components/educational/EducationalHub.vue");
const AuditLogViewer = () => import("../views/AuditLogViewer.vue");
const MicroservicesMonitor = () => import("../views/MicroservicesMonitor.vue");
const ChatView = () => import("../views/ChatView.vue");

const routes = [
  {
    path: "/",
    // Always show login page for root path (/admin)
    name: "RootLogin",
    component: LoginPage,
    meta: { requiresAuth: false, isRoot: true },
  },
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    meta: { requiresAuth: false },
  },
  {
    path: "/dashboard",
    component: Layout,
    meta: { requiresAuth: true, permission: "admin.dashboard" },
    children: [
      {
        path: "",
        name: "Dashboard",
        component: Dashboard,
      },
    ],
  },
  {
    path: "/users",
    component: Layout,
    meta: { requiresAuth: true, permission: "user:read" },
    children: [
      {
        path: "",
        name: "UserManagement",
        component: UserManagement,
      },
    ],
  },
  {
    path: "/chat",
    component: Layout,
    meta: { requiresAuth: true, permission: "support:chat" },
    children: [
      {
        path: "",
        name: "Chat",
        component: ChatView,
      },
    ],
  },
  {
    path: "/financial",
    component: Layout,
    meta: { requiresAuth: true, permission: "financial:read" },
    children: [
      {
        path: "",
        name: "FinancialManagement",
        component: FinancialManagement,
      },
    ],
  },
  {
    path: "/analytics",
    component: Layout,
    meta: { requiresAuth: true, permission: "analytics:read" },
    children: [
      {
        path: "",
        name: "AnalyticsReports",
        component: AnalyticsReports,
      },
    ],
  },
  {
    path: "/settings",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "SystemSettings",
        component: SystemSettings,
      },
    ],
  },
  {
    path: "/diagnostics",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "DiagnosticsManagement",
        component: DiagnosticsManagement,
      },
    ],
  },
  {
    path: "/alerts",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "AlertManagement",
        component: AlertManagement,
      },
    ],
  },
  {
    path: "/scenario-builder",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "ScenarioBuilder",
        component: ScenarioBuilder,
      },
    ],
  },
  {
    path: "/market-preview",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "MarketPreview",
        component: MarketPreview,
      },
    ],
  },
  {
    path: "/market-reality-control",
    component: Layout,
    meta: { requiresAuth: true, permission: "market:manipulate" },
    children: [
      {
        path: "",
        name: "MarketRealityControl",
        component: MarketRealityControl,
      },
    ],
  },
  {
    path: "/session-manager",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "SessionManager",
        component: ScenarioBuilder,
      },
    ],
  },
  {
    path: "/monitoring-hub",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "MonitoringHub",
        component: MicroservicesMonitor,
      },
    ],
  },
  {
    path: "/educational-hub",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "EducationalHub",
        component: EducationalHub,
      },
    ],
  },
  {
    path: "/audit-logs",
    component: Layout,
    meta: { requiresAuth: true, permission: "system:read" },
    children: [
      {
        path: "",
        name: "AuditLogViewer",
        component: AuditLogViewer,
      },
    ],
  },
  {
    path: "/admin-controls",
    component: Layout,
    meta: { requiresAuth: true, permission: "admin:trading:control" },
    children: [
      {
        path: "",
        name: "AdminTradingControls",
        component: AdminTradingControls,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory("/admin/"),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Always check auth state from localStorage to ensure it's up to date
  // This is important after login to ensure the guard recognizes authentication
  await authStore.checkAuth();
  
  // Root path "/" always shows login page (no redirect)
  // This ensures /admin always displays login page
  if (to.path === "/" || to.path === "" || to.name === "RootLogin") {
    // Allow navigation to login page (which is now the root path)
    // Don't redirect authenticated users - let LoginPage handle it if needed
    next();
    return;
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Not authenticated, redirect to login with return path
      console.log('[Router] Not authenticated, redirecting to login from:', to.fullPath);
      // Redirect to root path (/) which shows login page
      next({ path: "/", query: { redirect: to.fullPath } });
      return;
    }

    // Check permissions - temporarily disabled for testing
    // Admin users should have all permissions, so we'll allow access
    // if (to.meta.permission) {
    //   if (!authStore.hasPermission(to.meta.permission)) {
    //     next({ name: "Dashboard" }); // Redirect to dashboard if no permission
    //     return;
    //   }
    // }
  }

  // Redirect authenticated users away from login page (but not from root path)
  // Root path "/" should always show login page per user requirement
  if ((to.name === "Login" || to.name === "RootLogin") && authStore.isAuthenticated) {
    // Only redirect if explicitly accessing /login, not root path
    if (to.name === "Login" && to.path === "/login") {
      console.log('[Router] Already authenticated, redirecting from /login to dashboard');
      // Check if there's a redirect query param, otherwise go to dashboard
      const redirectPath = to.query.redirect;
      if (redirectPath && typeof redirectPath === 'string') {
        // Try to navigate to the redirect path
        try {
          // Remove /admin/ prefix if present as router base handles it
          const path = redirectPath.startsWith('/admin/') 
            ? redirectPath.replace('/admin/', '/') 
            : redirectPath;
          next(path);
          return;
        } catch (error) {
          console.warn('[Router] Failed to redirect to:', redirectPath, error);
          next({ name: "Dashboard" });
          return;
        }
      }
      next({ name: "Dashboard" });
      return;
    }
    // For root path, allow showing login page even if authenticated
    // LoginPage component can handle auto-redirect if needed
  }

  // Allow navigation
  next();
});

export default router;
