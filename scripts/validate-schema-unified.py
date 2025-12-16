#!/usr/bin/env python3
"""
Script validation schema sau khi migration
Verify schema consistency giữa các environments
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Set

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = os.path.join(REPORT_DIR, f"schema_validation_{TIMESTAMP}.md")


class SchemaValidator:
    """Validate schema consistency"""
    
    def __init__(self):
        self.validation_results: Dict[str, Dict[str, any]] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def get_container_name(self, env: str) -> str:
        """Lấy tên container PostgreSQL"""
        if env == "dev":
            return "digital_utopia_postgres"
        elif env == "staging":
            return "digital_utopia_postgres_staging"
        elif env == "prod":
            return "digital_utopia_postgres_prod"
        else:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True
            )
            containers = result.stdout.strip().split('\n')
            for container in containers:
                if 'postgres' in container.lower():
                    return container
            return "digital_utopia_postgres"
    
    def get_db_name(self, env: str) -> str:
        """Lấy tên database"""
        return os.getenv(f"POSTGRES_DB_{env.upper()}", "digital_utopia")
    
    def execute_sql(self, container: str, db_name: str, sql: str) -> List[str]:
        """Thực thi SQL query"""
        try:
            cmd = [
                "docker", "exec", container,
                "psql", "-U", "postgres", "-d", db_name,
                "-t", "-A"
            ]
            
            postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
            env_vars = os.environ.copy()
            env_vars["PGPASSWORD"] = postgres_password
            
            result = subprocess.run(
                cmd,
                input=sql,
                capture_output=True,
                text=True,
                env=env_vars,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        except Exception as e:
            print(f"Error executing SQL: {e}", file=sys.stderr)
            return []
    
    def validate_tables(self, container: str, db_name: str, env: str) -> Dict[str, bool]:
        """Validate tất cả tables tồn tại"""
        print(f"Validating tables for {env}...")
        
        required_tables = [
            'users', 'user_profiles', 'roles', 'permissions', 'role_permissions',
            'trading_orders', 'portfolio_positions', 'iceberg_orders', 'oco_orders', 'trailing_stop_orders',
            'transactions', 'wallet_balances', 'exchange_rates', 'invoices', 'payments',
            'kyc_documents', 'compliance_events', 'risk_assessments', 'aml_screenings',
            'trading_bots', 'watchlists',
            'referral_codes', 'referral_registrations',
            'audit_logs', 'analytics_events',
            'market_data_history', 'market_prices', 'market_analyses',
            'system_settings', 'scheduled_reports', 'trading_adjustments',
            'trading_diagnostic_reports',
            'alert_rules', 'alert_history',
            'notifications', 'notification_preferences',
            'refresh_tokens'
        ]
        
        sql = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        ORDER BY tablename;
        """
        
        existing_tables = set(self.execute_sql(container, db_name, sql))
        
        results = {}
        for table in required_tables:
            exists = table in existing_tables
            results[table] = exists
            if not exists:
                self.errors.append(f"{env}: Table '{table}' không tồn tại")
        
        return results
    
    def validate_indexes(self, container: str, db_name: str, env: str):
        """Validate indexes quan trọng"""
        print(f"Validating indexes for {env}...")
        
        required_indexes = [
            ('users', 'ix_users_email'),
            ('users', 'ix_users_status'),
            ('trading_orders', 'ix_trading_orders_user_id'),
            ('trading_orders', 'ix_trading_orders_status'),
            ('transactions', 'ix_transactions_user_id'),
            ('wallet_balances', 'ix_wallet_balances_user_id'),
        ]
        
        sql = """
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public';
        """
        
        results = self.execute_sql(container, db_name, sql)
        existing_indexes = {}
        
        for line in results:
            parts = line.split('|')
            if len(parts) >= 2:
                table = parts[0].strip()
                index = parts[1].strip()
                if table not in existing_indexes:
                    existing_indexes[table] = set()
                existing_indexes[table].add(index)
        
        for table, index in required_indexes:
            if table not in existing_indexes or index not in existing_indexes[table]:
                self.warnings.append(f"{env}: Index '{index}' trên table '{table}' không tồn tại")
    
    def validate_constraints(self, container: str, db_name: str, env: str):
        """Validate constraints"""
        print(f"Validating constraints for {env}...")
        
        # Validate unique constraints
        sql = """
        SELECT constraint_name, table_name
        FROM information_schema.table_constraints
        WHERE constraint_type = 'UNIQUE'
        AND table_schema = 'public';
        """
        
        results = self.execute_sql(container, db_name, sql)
        existing_constraints = set()
        
        for line in results:
            parts = line.split('|')
            if len(parts) >= 2:
                existing_constraints.add((parts[1].strip(), parts[0].strip()))
        
        # Check required unique constraints
        required_constraints = [
            ('wallet_balances', 'uq_wallet_user_asset'),
            ('exchange_rates', 'uq_exchange_rate_pair'),
        ]
        
        for table, constraint in required_constraints:
            if (table, constraint) not in existing_constraints:
                self.warnings.append(f"{env}: Unique constraint '{constraint}' trên table '{table}' không tồn tại")
    
    def validate_migration_version(self, container: str, db_name: str, env: str) -> str:
        """Validate migration version"""
        print(f"Validating migration version for {env}...")
        
        sql = "SELECT version_num FROM alembic_version LIMIT 1;"
        results = self.execute_sql(container, db_name, sql)
        
        if not results:
            self.errors.append(f"{env}: Không có migration version")
            return "unknown"
        
        return results[0]
    
    def validate_environment(self, env: str):
        """Validate một environment"""
        print(f"\n{'='*60}")
        print(f"Validating environment: {env}")
        print(f"{'='*60}")
        
        container = self.get_container_name(env)
        db_name = self.get_db_name(env)
        
        # Kiểm tra container
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        
        if container not in result.stdout:
            self.errors.append(f"{env}: Container {container} không tồn tại")
            return
        
        result_data = {
            'environment': env,
            'container': container,
            'database': db_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Validate migration version
        migration_version = self.validate_migration_version(container, db_name, env)
        result_data['migration_version'] = migration_version
        
        # Validate tables
        tables_result = self.validate_tables(container, db_name, env)
        result_data['tables'] = tables_result
        result_data['tables_count'] = len([t for t in tables_result.values() if t])
        result_data['missing_tables'] = [t for t, exists in tables_result.items() if not exists]
        
        # Validate indexes
        self.validate_indexes(container, db_name, env)
        
        # Validate constraints
        self.validate_constraints(container, db_name, env)
        
        result_data['errors'] = len([e for e in self.errors if e.startswith(f"{env}:")])
        result_data['warnings'] = len([w for w in self.warnings if w.startswith(f"{env}:")])
        
        self.validation_results[env] = result_data
    
    def generate_report(self):
        """Tạo báo cáo validation"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo Validation Schema\n\n")
            f.write(f"**Ngày thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Tổng quan
            f.write("## 1. Tổng Quan\n\n")
            for env, result in self.validation_results.items():
                f.write(f"### Environment: {env}\n\n")
                f.write(f"- Container: {result.get('container', 'N/A')}\n")
                f.write(f"- Database: {result.get('database', 'N/A')}\n")
                f.write(f"- Migration Version: {result.get('migration_version', 'N/A')}\n")
                f.write(f"- Tables: {result.get('tables_count', 0)}\n")
                f.write(f"- Errors: {result.get('errors', 0)}\n")
                f.write(f"- Warnings: {result.get('warnings', 0)}\n\n")
            
            # Errors
            if self.errors:
                f.write("## 2. Errors\n\n")
                for error in self.errors:
                    f.write(f"- ❌ {error}\n")
                f.write("\n")
            
            # Warnings
            if self.warnings:
                f.write("## 3. Warnings\n\n")
                for warning in self.warnings:
                    f.write(f"- ⚠️ {warning}\n")
                f.write("\n")
            
            # Missing tables
            f.write("## 4. Missing Tables\n\n")
            for env, result in self.validation_results.items():
                missing = result.get('missing_tables', [])
                if missing:
                    f.write(f"### {env}\n\n")
                    for table in missing:
                        f.write(f"- `{table}`\n")
                    f.write("\n")
            
            # Kết luận
            f.write("## 5. Kết Luận\n\n")
            if not self.errors and not self.warnings:
                f.write("✅ **Schema validation thành công - Không có lỗi hoặc cảnh báo**\n\n")
            elif not self.errors:
                f.write("⚠️ **Schema validation có cảnh báo nhưng không có lỗi nghiêm trọng**\n\n")
            else:
                f.write("❌ **Schema validation thất bại - Có lỗi cần xử lý**\n\n")
        
        print(f"\n✅ Báo cáo đã được tạo: {REPORT_FILE}")
        print(f"   - Errors: {len(self.errors)}")
        print(f"   - Warnings: {len(self.warnings)}")


def main():
    parser = argparse.ArgumentParser(description='Validate schema consistency')
    parser.add_argument('--environments', nargs='+', default=['dev', 'staging', 'prod'],
                        help='List of environments to validate')
    
    args = parser.parse_args()
    
    validator = SchemaValidator()
    
    for env in args.environments:
        validator.validate_environment(env)
    
    validator.generate_report()
    
    # Exit với code lỗi nếu có errors
    if validator.errors:
        sys.exit(1)


if __name__ == '__main__':
    main()

