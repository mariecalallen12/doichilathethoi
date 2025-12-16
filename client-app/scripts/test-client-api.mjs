import axios from "axios";

const BASE_URL = process.env.VITE_API_BASE_URL || "http://localhost:8000";

const results = [];

function record(step, ok, status, info = "") {
  const entry = { step, ok, status, info };
  results.push(entry);
  const statusLabel = ok ? "OK" : "FAIL";
  console.log(`[${statusLabel}] ${step} -> HTTP ${status}${info ? " - " + info : ""}`);
}

async function main() {
  console.log("=== Client → Backend API Integration Test ===");
  console.log(`Base URL: ${BASE_URL}`);

  const client = axios.create({
    baseURL: BASE_URL,
    validateStatus: () => true,
  });

  // 1. Health check
  try {
    const res = await client.get("/api/health");
    const ok = res.status === 200 && res.data?.status === "ok";
    record("health_check", ok, res.status, ok ? "" : JSON.stringify(res.data).slice(0, 200));
    if (!ok) {
      throw new Error("Health check failed, aborting further tests.");
    }
  } catch (err) {
    record("health_check_exception", false, 0, err.message);
    throw err;
  }

  // 2. Login with pre-created active test user
  const testEmail = process.env.CLIENT_TEST_USER_EMAIL || "client_api_tester@example.com";
  const testPassword = process.env.CLIENT_TEST_USER_PASSWORD || "Test1234!";

  let accessToken = null;
  let refreshToken = null;

  try {
    const res = await client.post("/api/auth/login", {
      email: testEmail,
      password: testPassword,
    });
    const data = res.data && (res.data.data || res.data);
    accessToken = data?.access_token;
    refreshToken = data?.refresh_token;
    const ok = res.status === 200 && !!accessToken;
    record("auth_login", ok, res.status, ok ? "" : JSON.stringify(res.data).slice(0, 200));
    if (!ok) {
      throw new Error("Login failed, cannot continue authenticated tests.");
    }
    client.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
  } catch (err) {
    record("auth_login_exception", false, 0, err.message);
    throw err;
  }

  // 3. Refresh token (optional but useful)
  if (refreshToken) {
    try {
      const res = await client.post(
        "/api/auth/refresh",
        {},
        {
          headers: {
            Authorization: `Bearer ${refreshToken}`,
          },
        },
      );
      const data = res.data && (res.data.data || res.data);
      const newAccessToken = data?.access_token;
      const ok = res.status === 200 && !!newAccessToken;
      if (ok && newAccessToken) {
        accessToken = newAccessToken;
        client.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
      }
      record("auth_refresh", ok, res.status, ok ? "" : JSON.stringify(res.data).slice(0, 200));
    } catch (err) {
      record("auth_refresh_exception", false, 0, err.message);
    }
  }

  // Helper to run a generic GET and only fail hard on 5xx
  async function checkGet(step, url, requireAuth = true) {
    try {
      if (requireAuth && !accessToken) {
        record(step, false, 0, "Missing access token");
        return;
      }
      const res = await client.get(url);
      const ok = res.status >= 200 && res.status < 300;
      const info = ok ? "" : JSON.stringify(res.data).slice(0, 200);
      record(step, ok, res.status, info);
    } catch (err) {
      record(step + "_exception", false, 0, err.message);
    }
  }

  // 4. Client module endpoints
  await checkGet("client_dashboard", "/api/client/dashboard", true);
  await checkGet("client_wallet_balances", "/api/client/wallet-balances", true);
  await checkGet("client_transactions", "/api/client/transactions", true);
  await checkGet("client_exchange_rates", "/api/client/exchange-rates", true);

  // 5. Financial module (balance/transactions)
  await checkGet("financial_balance", "/api/financial/balance", true);
  await checkGet("financial_transactions", "/api/financial/transactions", true);
  await checkGet("financial_deposits", "/api/financial/deposits", true);
  await checkGet("financial_withdrawals", "/api/financial/withdrawals", true);

  // 6. Trading module
  await checkGet("trading_pairs", "/api/trading/pairs", false);
  await checkGet("trading_statistics", "/api/trading/statistics", true);
  await checkGet("trading_risk_assessment", "/api/trading/risk-assessment", true);

  // 7. Market data module
  await checkGet("market_prices", "/api/market/prices", false);

  console.log("\n=== SUMMARY ===");
  const summary = {
    baseUrl: BASE_URL,
    steps: results,
    allCriticalOk: results
      .filter((r) => ["health_check", "auth_login"].includes(r.step))
      .every((r) => r.ok),
  };
  console.log(JSON.stringify(summary, null, 2));

  if (!summary.allCriticalOk) {
    process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error("Integration test run failed:", err);
  if (!results.length) {
    record("fatal_error", false, 0, err.message);
  }
  process.exitCode = 1;
});
