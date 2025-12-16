# API Endpoints List

**Total:** 270 endpoints across 23 modules

## Endpoints by Module

### ADMIN (69 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/admin/users` | `get_users` |  |
| GET | `/api/admin/users/{user_id}` | `get_user_by_id` |  |
| PUT | `/api/admin/users/{user_id}` | `update_user` |  |
| GET | `/api/admin/customers` | `get_customers` |  |
| GET | `/api/admin/dashboard` | `get_dashboard` |  |
| GET | `/api/admin/platform-stats` | `get_platform_stats` |  |
| GET | `/api/admin/platform/stats` | `get_platform_stats_alias` |  |
| GET | `/api/admin/deposits` | `get_deposits` |  |
| GET | `/api/admin/deposits/{deposit_id}` | `get_deposit_detail` |  |
| POST | `/api/admin/deposits/{deposit_id}/approve` | `approve_deposit` |  |
| POST | `/api/admin/deposits/{deposit_id}/reject` | `reject_deposit` |  |
| GET | `/api/admin/withdrawals` | `get_withdrawals` |  |
| GET | `/api/admin/withdrawals/{withdrawal_id}` | `get_withdrawal_detail` |  |
| POST | `/api/admin/withdrawals/{withdrawal_id}/approve` | `approve_withdrawal` |  |
| POST | `/api/admin/withdrawals/{withdrawal_id}/reject` | `reject_withdrawal` |  |
| GET | `/api/admin/analytics` | `get_analytics` |  |
| GET | `/api/admin/reports` | `get_reports` |  |
| GET | `/api/admin/logs` | `get_logs` |  |
| GET | `/api/admin/settings` | `get_settings` |  |
| GET | `/api/admin/settings/market-display` | `get_market_display_settings` |  |
| PUT | `/api/admin/settings/market-display` | `update_market_display_settings` |  |
| GET | `/api/admin/settings/chart-display` | `get_chart_display_settings` |  |
| PATCH | `/api/admin/config/candle` | `update_candle_config` |  |
| GET | `/api/admin/settings/market-scenarios` | `get_market_scenarios_settings` |  |
| PUT | `/api/admin/settings/market-scenarios` | `update_market_scenarios_settings` |  |
| GET | `/api/admin/simulator/sessions` | `list_simulator_sessions` |  |
| POST | `/api/admin/simulator/sessions/start` | `start_simulator_session` |  |
| POST | `/api/admin/simulator/sessions/stop` | `stop_simulator_session` |  |
| POST | `/api/admin/simulator/sessions/reset` | `reset_simulator_sessions` |  |
| POST | `/api/admin/simulator/sessions/replay` | `replay_simulator_session` |  |
| GET | `/api/admin/simulator/monitoring` | `get_simulator_monitoring` |  |
| PUT | `/api/admin/settings` | `update_settings` |  |
| GET | `/api/admin/settings/registration-fields` | `get_registration_fields_config` |  |
| PUT | `/api/admin/settings/registration-fields` | `update_registration_fields_config` |  |
| GET | `/api/admin/trades` | `get_admin_trades` |  |
| POST | `/api/admin/trades/{trade_id}/approve` | `approve_trade` |  |
| POST | `/api/admin/trades/{trade_id}/reject` | `reject_trade` |  |
| POST | `/api/admin/trades/batch-approve` | `batch_approve_trades` |  |
| POST | `/api/admin/trading-adjustments/win-rate` | `set_win_rate` |  |
| POST | `/api/admin/trading-adjustments/position-override` | `override_position` |  |
| GET | `/api/admin/invoices` | `get_invoices` |  |
| GET | `/api/admin/invoices/{invoice_id}` | `get_invoice_detail` |  |
| POST | `/api/admin/invoices` | `create_invoice` |  |
| PUT | `/api/admin/invoices/{invoice_id}` | `update_invoice` |  |
| DELETE | `/api/admin/invoices/{invoice_id}` | `delete_invoice` |  |
| POST | `/api/admin/invoices/{invoice_id}/approve` | `approve_invoice` |  |
| POST | `/api/admin/invoices/{invoice_id}/reject` | `reject_invoice` |  |
| GET | `/api/admin/payments` | `get_payments` |  |
| GET | `/api/admin/payments/{payment_id}` | `get_payment_detail` |  |
| POST | `/api/admin/payments/{payment_id}/process` | `process_payment` |  |
| POST | `/api/admin/payments/{payment_id}/refund` | `refund_payment` |  |
| GET | `/api/admin/users/{user_id}/performance` | `get_user_performance` |  |
| POST | `/api/admin/trading-adjustments/reset-win-rate` | `reset_win_rate` |  |
| GET | `/api/admin/trading-adjustments/history` | `get_trading_adjustments_history` |  |
| GET | `/api/admin/analytics/performance` | `get_analytics_performance` |  |
| GET | `/api/admin/reports/scheduled` | `get_scheduled_reports` |  |
| PATCH | `/api/admin/reports/scheduled/{report_id}` | `update_scheduled_report` |  |
| DELETE | `/api/admin/reports/scheduled/{report_id}` | `delete_scheduled_report` |  |
| GET | `/api/admin/settings/cors-origins` | `get_cors_origins` |  |
| POST | `/api/admin/settings/cors-origins` | `add_cors_origin` |  |
| DELETE | `/api/admin/settings/cors-origins` | `remove_cors_origin` |  |
| POST | `/api/admin/users/bulk-update` | `bulk_update_users` |  |
| GET | `/api/admin/settings/auto-approve-registration` | `get_auto_approve_registration_setting` |  |
| PUT | `/api/admin/settings/auto-approve-registration` | `update_auto_approve_registration_setting` |  |
| GET | `/api/admin/registrations` | `get_pending_registrations` |  |
| POST | `/api/admin/registrations/{registration_id}/approve` | `approve_registration` |  |
| GET | `/api/admin/customers/wallet-balances` | `get_customer_wallet_balances` |  |
| GET | `/api/admin/market-preview/{symbol}` | `get_market_preview` |  |
| GET | `/api/admin/market-preview` | `get_multiple_market_preview` |  |

### ADMIN_TRADING (7 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| PUT | `/api/admin/trading/orders/{order_id}` | `admin_update_order` |  |
| DELETE | `/api/admin/trading/orders/{order_id}/force` | `admin_force_cancel_order` |  |
| PUT | `/api/admin/trading/positions/{position_id}` | `admin_update_position` |  |
| POST | `/api/admin/trading/positions/{position_id}/force-close` | `admin_force_close_position` |  |
| PUT | `/api/admin/trading/prices/{symbol}` | `admin_update_price` |  |
| PUT | `/api/admin/trading/balances/{user_id}` | `admin_update_balance` |  |
| GET | `/api/admin/trading/adjustments` | `get_adjustment_history` |  |

### ALERT_RULES (8 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/alert-rules` | `create_alert_rule` |  |
| GET | `/api/alert-rules` | `get_alert_rules` |  |
| GET | `/api/alert-rules/{rule_id}` | `get_alert_rule` |  |
| PUT | `/api/alert-rules/{rule_id}` | `update_alert_rule` |  |
| DELETE | `/api/alert-rules/{rule_id}` | `delete_alert_rule` |  |
| GET | `/api/alert-history` | `get_alert_history` |  |
| POST | `/api/alert-history/{alert_id}/acknowledge` | `acknowledge_alert` |  |
| POST | `/api/alert-history/{alert_id}/resolve` | `resolve_alert` |  |

### ANALYSIS (5 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/analysis/technical/{symbol}` | `get_technical_analysis` |  |
| GET | `/api/analysis/fundamental/{symbol}` | `get_fundamental_analysis` |  |
| GET | `/api/analysis/sentiment` | `get_sentiment` |  |
| GET | `/api/analysis/signals` | `get_signals` |  |
| POST | `/api/analysis/backtest` | `run_backtest` |  |

### AUDIT (3 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/logs` | `get_audit_logs` |  |
| GET | `/api/logs/stats` | `get_audit_stats` |  |
| GET | `/api/logs/{log_id}` | `get_audit_log_detail` |  |

### AUTH (8 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/auth/register` | `register` |  |
| POST | `/api/auth/refresh` | `refresh_token` |  |
| POST | `/api/auth/logout` | `logout` |  |
| GET | `/api/auth/verify` | `verify_token_endpoint` |  |
| POST | `/api/auth/forgot-password` | `forgot_password` |  |
| POST | `/api/auth/reset-password` | `reset_password` |  |
| POST | `/api/auth/verify-email` | `verify_email` |  |
| POST | `/api/auth/verify-phone` | `verify_phone` |  |

### AUTH_NEW (9 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/login` | `login` |  |
| POST | `/api/register` | `register` |  |
| POST | `/api/refresh` | `refresh_token` |  |
| POST | `/api/logout` | `logout` |  |
| GET | `/api/verify` | `verify_token_endpoint` |  |
| POST | `/api/forgot-password` | `forgot_password` |  |
| POST | `/api/reset-password` | `reset_password` |  |
| POST | `/api/verify-email` | `verify_email` |  |
| POST | `/api/verify-phone` | `verify_phone` |  |

### CLIENT (18 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/client/dashboard` | `get_dashboard` |  |
| GET | `/api/client/wallet-balances` | `get_wallet_balances` |  |
| GET | `/api/client/transactions` | `get_transactions` |  |
| GET | `/api/client/exchange-rates` | `get_exchange_rates` |  |
| POST | `/api/client/crypto-deposit-address` | `create_crypto_deposit_address` |  |
| POST | `/api/client/generate-vietqr` | `generate_vietqr` |  |
| GET | `/api/client/profile` | `get_client_profile` |  |
| PUT | `/api/client/profile` | `update_client_profile` |  |
| GET | `/api/client/settings` | `get_client_settings` |  |
| PUT | `/api/client/settings` | `update_client_settings` |  |
| GET | `/api/client/preferences` | `get_client_preferences` |  |
| PUT | `/api/client/preferences` | `update_client_preferences` |  |
| POST | `/api/client/2fa/setup` | `setup_two_factor_auth` |  |
| POST | `/api/client/2fa/verify` | `verify_two_factor_auth` |  |
| POST | `/api/client/2fa/disable` | `disable_two_factor_auth` |  |
| GET | `/api/client/onboarding/status` | `get_onboarding_status` |  |
| POST | `/api/client/onboarding/complete` | `complete_onboarding_step` |  |
| GET | `/api/client/settings/registration-fields` | `get_registration_fields_config` |  |

### COMPLIANCE (37 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/compliance/aml` | `get_aml_screening` |  |
| POST | `/api/compliance/aml` | `perform_aml_screening` |  |
| POST | `/api/compliance/aml/monitor` | `monitor_transaction_aml` |  |
| PATCH | `/api/compliance/aml` | `update_aml_screening` |  |
| GET | `/api/compliance/aml/metrics` | `get_aml_metrics` | Get compliance metrics (admin only) |
| GET | `/api/compliance/audit` | `get_audit_logs` |  |
| POST | `/api/compliance/audit` | `create_audit_log` |  |
| GET | `/api/compliance/audit/security` | `get_security_events` |  |
| POST | `/api/compliance/audit/security` | `create_security_event` |  |
| PATCH | `/api/compliance/audit/security/{event_id}` | `update_security_event` |  |
| GET | `/api/compliance/kyc` | `get_kyc_status` | Get KYC status for authenticated user |
| POST | `/api/compliance/kyc` | `submit_kyc_application` |  |
| PATCH | `/api/compliance/kyc` | `update_kyc_status` |  |
| DELETE | `/api/compliance/kyc` | `delete_kyc_profile` |  |
| GET | `/api/compliance/dashboard` | `get_compliance_dashboard` |  |
| GET | `/api/compliance/dashboard/metrics` | `get_dashboard_metrics` |  |
| POST | `/api/compliance/dashboard/alerts` | `create_dashboard_alert` |  |
| PATCH | `/api/compliance/dashboard/alerts/{alert_id}` | `update_dashboard_alert` |  |
| GET | `/api/compliance/reports` | `get_regulatory_reports` |  |
| POST | `/api/compliance/reports` | `generate_regulatory_report` |  |
| PATCH | `/api/compliance/reports/{report_id}` | `update_regulatory_report` |  |
| POST | `/api/compliance/reports/auto-generate` | `auto_generate_reports` | Auto-generate reports (admin only) |
| GET | `/api/compliance/reports/metrics` | `get_reporting_metrics` | Get reporting metrics (admin only) |
| GET | `/api/compliance/rules` | `get_compliance_rules` |  |
| POST | `/api/compliance/rules` | `create_compliance_rule` |  |
| PATCH | `/api/compliance/rules/{rule_id}` | `update_compliance_rule` |  |
| DELETE | `/api/compliance/rules/{rule_id}` | `delete_compliance_rule` |  |
| POST | `/api/compliance/rules/{rule_id}/evaluate` | `evaluate_rule` |  |
| GET | `/api/compliance/rules/{rule_id}/executions` | `get_rule_executions` |  |
| GET | `/api/compliance/sanctions` | `search_sanctions_lists` |  |
| POST | `/api/compliance/sanctions/screen` | `perform_sanctions_screening` |  |
| GET | `/api/compliance/sanctions/screenings` | `get_screening_results` |  |
| PATCH | `/api/compliance/sanctions/screenings/{screening_id}` | `update_screening_result` |  |
| GET | `/api/compliance/transaction-monitoring` | `get_transaction_monitoring` |  |
| POST | `/api/compliance/transaction-monitoring` | `start_transaction_monitoring` |  |
| PATCH | `/api/compliance/transaction-monitoring` | `update_monitoring_status` |  |
| GET | `/api/compliance/transaction-monitoring/suspicious-activities` | `get_suspicious_activities` |  |

### DIAGNOSTICS (3 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/diagnostics/trading-report` | `create_trading_diagnostic_report` |  |
| GET | `/api/diagnostics/trading-reports` | `get_trading_diagnostic_reports` |  |
| GET | `/api/diagnostics/trading-reports/{report_id}` | `get_trading_diagnostic_report` |  |

### EDUCATION (8 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/education/videos` | `get_videos` |  |
| GET | `/api/education/videos/{video_id}` | `get_video_by_id` |  |
| GET | `/api/education/ebooks` | `get_ebooks` |  |
| GET | `/api/education/ebooks/{ebook_id}` | `get_ebook_by_id` |  |
| GET | `/api/education/calendar` | `get_calendar` |  |
| GET | `/api/education/reports` | `get_reports` |  |
| GET | `/api/education/reports/{report_id}` | `get_report_by_id` |  |
| POST | `/api/education/progress` | `update_progress` |  |

### FINANCIAL (9 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/financial/deposits` | `create_deposit` |  |
| GET | `/api/financial/deposits` | `get_deposits` |  |
| POST | `/api/financial/withdrawals` | `create_withdrawal` |  |
| GET | `/api/financial/withdrawals` | `get_withdrawals` |  |
| GET | `/api/financial/balance` | `get_balance` |  |
| GET | `/api/financial/transactions` | `get_transactions` |  |
| POST | `/api/financial/exchange` | `currency_exchange` |  |
| POST | `/api/financial/payments/process` | `process_payment` |  |
| GET | `/api/financial/reports` | `get_financial_reports` |  |

### LEGAL (9 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/legal/terms` | `get_terms` |  |
| GET | `/api/legal/terms/version/{version}` | `get_terms_by_version` |  |
| GET | `/api/legal/privacy` | `get_privacy` |  |
| GET | `/api/legal/privacy/version/{version}` | `get_privacy_by_version` |  |
| GET | `/api/legal/risk-warning` | `get_risk_warning` |  |
| GET | `/api/legal/complaints` | `get_complaints` |  |
| POST | `/api/legal/complaints` | `submit_complaint` |  |
| GET | `/api/legal/complaints/{complaint_id}` | `get_complaint_by_id` |  |
| PUT | `/api/legal/complaints/{complaint_id}` | `update_complaint` |  |

### MARKET (8 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/market/prices` | `get_market_prices` |  |
| GET | `/api/market/orderbook/{symbol}` | `get_order_book` |  |
| GET | `/api/market/trade-history/{symbol}` | `get_trade_history` |  |
| GET | `/api/market/historical-data/{symbol}` | `get_historical_data` |  |
| GET | `/api/market/analysis/{symbol}` | `get_market_analysis` |  |
| GET | `/api/market/data-feeds` | `get_data_feeds` |  |
| GET | `/api/market/instruments` | `get_market_instruments` |  |
| GET | `/api/market/summary` | `get_market_summary` |  |

### NOTIFICATIONS (8 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| POST | `/api/notifications` | `create_notification` |  |
| GET | `/api/notifications` | `get_notifications` |  |
| GET | `/api/notifications/unread-count` | `get_unread_count` |  |
| POST | `/api/notifications/{notification_id}/read` | `mark_notification_read` |  |
| POST | `/api/notifications/mark-all-read` | `mark_all_notifications_read` |  |
| POST | `/api/notifications/{notification_id}/dismiss` | `dismiss_notification` |  |
| GET | `/api/notification-preferences` | `get_notification_preferences` |  |
| PUT | `/api/notification-preferences/{category}` | `update_notification_preference` |  |

### OPEX_MARKET (6 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/market/health` | `market_health_check` | Health check endpoint for market service |
| GET | `/api/market/orderbook/{symbol}` | `get_orderbook` |  |
| GET | `/api/market/trades/{symbol}` | `get_trades` |  |
| GET | `/api/market/candles/{symbol}` | `get_candles` |  |
| GET | `/api/market/ticker/{symbol}` | `get_ticker` |  |
| GET | `/api/market/symbols` | `get_symbols` |  |

### OPEX_TRADING (10 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/trading/health` | `trading_health_check` | Health check endpoint for trading service |
| POST | `/api/trading/orders` | `place_order` |  |
| GET | `/api/trading/orders` | `get_orders` |  |
| DELETE | `/api/trading/orders/{order_id}` | `cancel_order` |  |
| GET | `/api/trading/positions` | `get_positions` |  |
| POST | `/api/trading/positions/{position_id}/close` | `close_position` |  |
| GET | `/api/trading/orderbook` | `get_trading_orderbook` |  |
| GET | `/api/trading/statistics` | `get_trading_statistics` |  |
| POST | `/api/trading/cache/invalidate` | `invalidate_trading_cache` |  |
| GET | `/api/trading/cache/stats` | `get_cache_stats` |  |

### PERFORMANCE (2 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/metrics` | `get_performance_metrics` |  |
| POST | `/api/metrics/reset` | `reset_performance_metrics` |  |

### PORTFOLIO (14 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/portfolio/analytics` | `get_portfolio_analytics` |  |
| POST | `/api/portfolio/analytics/report` | `generate_portfolio_report` |  |
| GET | `/api/portfolio/metrics` | `get_portfolio_metrics` |  |
| POST | `/api/portfolio/metrics/recalculate` | `recalculate_portfolio_metrics` |  |
| POST | `/api/portfolio/positions/{position_id}/close` | `close_portfolio_position` |  |
| POST | `/api/portfolio/rebalancing` | `create_rebalancing_order` |  |
| GET | `/api/portfolio/rebalancing/recommendations` | `get_rebalancing_recommendations` |  |
| GET | `/api/portfolio/trading-bots` | `get_trading_bots` |  |
| POST | `/api/portfolio/trading-bots` | `create_trading_bot` |  |
| PATCH | `/api/portfolio/trading-bots` | `update_trading_bot` |  |
| DELETE | `/api/portfolio/trading-bots` | `delete_trading_bot` |  |
| GET | `/api/portfolio/watchlist` | `get_watchlist` |  |
| POST | `/api/portfolio/watchlist` | `add_to_watchlist` |  |
| DELETE | `/api/portfolio/watchlist/{symbol}` | `remove_from_watchlist` |  |

### RISK_MANAGEMENT (10 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/risk-management/assessment` | `get_risk_assessment` |  |
| POST | `/api/risk-management/assessment/stress-test` | `perform_stress_test` |  |
| DELETE | `/api/risk-management/assessment/cache` | `clear_risk_cache` |  |
| GET | `/api/risk-management/limits` | `get_risk_limits` |  |
| POST | `/api/risk-management/limits` | `create_risk_limit` |  |
| PATCH | `/api/risk-management/limits` | `update_risk_limit` |  |
| DELETE | `/api/risk-management/limits` | `delete_risk_limit` |  |
| GET | `/api/risk-management/alerts` | `get_risk_alerts` |  |
| GET | `/api/risk-management/margin-calls` | `get_margin_calls` |  |
| GET | `/api/risk-management/metrics` | `get_risk_metrics` |  |

### STAFF_REFERRALS (4 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/staff/referrals` | `get_staff_referrals` |  |
| POST | `/api/staff/referrals/generate-link` | `generate_referral_link_endpoint` |  |
| GET | `/api/staff/referrals/links` | `get_staff_referral_links` |  |
| DELETE | `/api/staff/referrals/links/{link_id}` | `delete_referral_link` |  |

### SUPPORT (10 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/support/articles` | `get_articles` |  |
| GET | `/api/support/articles/{article_id}` | `get_article_by_id` |  |
| GET | `/api/support/categories` | `get_categories` |  |
| POST | `/api/support/search` | `search_articles` |  |
| POST | `/api/support/contact` | `submit_contact` |  |
| GET | `/api/support/offices` | `get_offices` |  |
| GET | `/api/support/channels` | `get_channels` |  |
| GET | `/api/support/faq` | `get_faq` |  |
| GET | `/api/support/faq/{category}` | `get_faq_by_category` |  |
| POST | `/api/support/faq/search` | `search_faq` |  |

### USERS (5 endpoints)

| Method | Path | Function | Description |
|--------|------|----------|-------------|
| GET | `/api/users` | `get_user_profile_endpoint` |  |
| PUT | `/api/users` | `update_user_profile_endpoint` |  |
| DELETE | `/api/users` | `delete_user_account_endpoint` |  |
| GET | `/api/users/preferences` | `get_user_preferences_endpoint` |  |
| GET | `/api/users/activity` | `get_user_activity_endpoint` |  |

