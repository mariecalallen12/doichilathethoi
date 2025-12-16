#!/usr/bin/env python3
"""
Script đồng bộ dữ liệu từ master database đến các environments khác
Xử lý conflicts và đảm bảo referential integrity
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups")
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = os.path.join(REPORT_DIR, f"data_sync_{TIMESTAMP}.md")
JSON_REPORT_FILE = os.path.join(REPORT_DIR, f"data_sync_{TIMESTAMP}.json")


class DataSyncer:
    """Đồng bộ dữ liệu giữa các databases"""
    
    def __init__(self, master_env: str, conflict_strategy: str = "master_wins"):
        self.master_env = master_env
        self.conflict_strategy = conflict_strategy  # "master_wins" or "merge"
        self.sync_results: Dict[str, Dict[str, Any]] = {}
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
    
    def backup_database(self, env: str) -> str:
        """Backup database trước khi sync"""
        print(f"Backing up {env} database...")
        
        container = self.get_container_name(env)
        db_name = self.get_db_name(env)
        backup_file = os.path.join(BACKUP_DIR, f"{env}_backup_{TIMESTAMP}.sql")
        
        try:
            cmd = [
                "docker", "exec", container,
                "pg_dump", "-U", "postgres", "-d", db_name,
                "-F", "c", "-f", f"/tmp/{env}_backup_{TIMESTAMP}.sql"
            ]
            
            postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
            env_vars = os.environ.copy()
            env_vars["PGPASSWORD"] = postgres_password
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env_vars,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Backup failed: {result.stderr}")
            
            # Copy backup file từ container ra host
            subprocess.run(
                ["docker", "cp", f"{container}:/tmp/{env}_backup_{TIMESTAMP}.sql", backup_file],
                check=True
            )
            
            print(f"✅ Backup created: {backup_file}")
            return backup_file
        except Exception as e:
            self.errors.append(f"Backup failed for {env}: {e}")
            raise
    
    def get_table_list(self, container: str, db_name: str) -> List[str]:
        """Lấy danh sách tables"""
        sql = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        AND tablename != 'alembic_version'
        ORDER BY tablename;
        """
        
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
    
    def sync_table(self, master_container: str, master_db: str, 
                   target_container: str, target_db: str, 
                   table: str, order_by: str = "id") -> Dict[str, Any]:
        """Đồng bộ một table từ master đến target"""
        print(f"  Syncing table: {table}...")
        
        result = {
            'table': table,
            'rows_synced': 0,
            'rows_skipped': 0,
            'errors': []
        }
        
        try:
            # Export data từ master
            export_sql = f"""
            COPY (
                SELECT * FROM {table} ORDER BY {order_by}
            ) TO STDOUT WITH CSV HEADER;
            """
            
            cmd_export = [
                "docker", "exec", "-i", master_container,
                "psql", "-U", "postgres", "-d", master_db
            ]
            
            postgres_password = os.getenv("POSTGRES_PASSWORD", "postgres")
            env_vars = os.environ.copy()
            env_vars["PGPASSWORD"] = postgres_password
            
            export_result = subprocess.run(
                cmd_export,
                input=export_sql,
                capture_output=True,
                text=True,
                env=env_vars,
                timeout=300
            )
            
            if export_result.returncode != 0:
                raise Exception(f"Export failed: {export_result.stderr}")
            
            if not export_result.stdout.strip():
                print(f"    Table {table} is empty in master")
                return result
            
            # Import vào target với conflict handling
            # Strategy: DELETE existing và INSERT new (master_wins)
            if self.conflict_strategy == "master_wins":
                # Xóa dữ liệu cũ trong target
                delete_sql = f"TRUNCATE TABLE {table} CASCADE;"
                
                cmd_delete = [
                    "docker", "exec", "-i", target_container,
                    "psql", "-U", "postgres", "-d", target_db
                ]
                
                delete_result = subprocess.run(
                    cmd_delete,
                    input=delete_sql,
                    capture_output=True,
                    text=True,
                    env=env_vars,
                    timeout=60
                )
                
                if delete_result.returncode != 0:
                    raise Exception(f"Delete failed: {delete_result.stderr}")
            
            # Import dữ liệu mới
            # Parse CSV và insert
            lines = export_result.stdout.strip().split('\n')
            if len(lines) < 2:  # Header + ít nhất 1 row
                return result
            
            header = lines[0].split(',')
            rows = [line.split(',') for line in lines[1:] if line.strip()]
            
            # Insert từng batch để tránh timeout
            batch_size = 100
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i+batch_size]
                
                # Tạo INSERT statement
                values_list = []
                for row in batch:
                    values = []
                    for val in row:
                        if val == '' or val.lower() == 'null':
                            values.append('NULL')
                        else:
                            # Escape và quote
                            val_escaped = val.replace("'", "''")
                            values.append(f"'{val_escaped}'")
                    values_list.append(f"({', '.join(values)})")
                
                columns = ', '.join(header)
                insert_sql = f"""
                INSERT INTO {table} ({columns})
                VALUES {', '.join(values_list)}
                ON CONFLICT DO NOTHING;
                """
                
                cmd_insert = [
                    "docker", "exec", "-i", target_container,
                    "psql", "-U", "postgres", "-d", target_db
                ]
                
                insert_result = subprocess.run(
                    cmd_insert,
                    input=insert_sql,
                    capture_output=True,
                    text=True,
                    env=env_vars,
                    timeout=300
                )
                
                if insert_result.returncode != 0:
                    result['errors'].append(f"Batch {i//batch_size + 1}: {insert_result.stderr}")
                else:
                    result['rows_synced'] += len(batch)
            
            print(f"    ✅ Synced {result['rows_synced']} rows")
            
        except Exception as e:
            error_msg = f"Error syncing {table}: {e}"
            result['errors'].append(error_msg)
            self.errors.append(error_msg)
            print(f"    ❌ {error_msg}")
        
        return result
    
    def sync_environment(self, target_env: str):
        """Đồng bộ từ master đến một environment"""
        print(f"\n{'='*60}")
        print(f"Syncing {target_env} from {self.master_env}...")
        print(f"{'='*60}")
        
        master_container = self.get_container_name(self.master_env)
        target_container = self.get_container_name(target_env)
        master_db = self.get_db_name(self.master_env)
        target_db = self.get_db_name(target_env)
        
        # Kiểm tra containers
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        
        if master_container not in result.stdout:
            raise Exception(f"Master container {master_container} not found")
        
        if target_container not in result.stdout:
            raise Exception(f"Target container {target_container} not found")
        
        # Backup target trước khi sync
        backup_file = self.backup_database(target_env)
        
        sync_result = {
            'target_env': target_env,
            'master_env': self.master_env,
            'backup_file': backup_file,
            'timestamp': datetime.now().isoformat(),
            'tables': {},
            'total_rows_synced': 0,
            'total_errors': 0
        }
        
        # Lấy danh sách tables từ master
        tables = self.get_table_list(master_container, master_db)
        
        # Sync từng table theo thứ tự dependency
        # Tables cần sync trước: roles, permissions, users, ...
        dependency_order = [
            'roles',
            'permissions',
            'role_permissions',
            'users',
            'user_profiles',
            'refresh_tokens',
            'wallet_balances',
            'exchange_rates',
            'trading_orders',
            'portfolio_positions',
            'transactions',
            'invoices',
            'payments',
            'kyc_documents',
            'compliance_events',
            'risk_assessments',
            'aml_screenings',
            'trading_bots',
            'watchlists',
            'referral_codes',
            'referral_registrations',
            'audit_logs',
            'analytics_events',
            'market_data_history',
            'market_prices',
            'market_analyses',
            'system_settings',
            'scheduled_reports',
            'trading_adjustments',
            'trading_diagnostic_reports',
            'alert_rules',
            'alert_history',
            'notifications',
            'notification_preferences',
            'iceberg_orders',
            'oco_orders',
            'trailing_stop_orders'
        ]
        
        # Sync tables theo dependency order, sau đó sync các tables còn lại
        ordered_tables = []
        for table in dependency_order:
            if table in tables:
                ordered_tables.append(table)
        
        for table in tables:
            if table not in ordered_tables:
                ordered_tables.append(table)
        
        for table in ordered_tables:
            table_result = self.sync_table(
                master_container, master_db,
                target_container, target_db,
                table
            )
            sync_result['tables'][table] = table_result
            sync_result['total_rows_synced'] += table_result['rows_synced']
            sync_result['total_errors'] += len(table_result['errors'])
        
        self.sync_results[target_env] = sync_result
        
        print(f"\n✅ Sync completed for {target_env}")
        print(f"   Rows synced: {sync_result['total_rows_synced']}")
        print(f"   Errors: {sync_result['total_errors']}")
    
    def generate_report(self):
        """Tạo báo cáo sync"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo Đồng Bộ Dữ Liệu\n\n")
            f.write(f"**Ngày thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Master Environment:** {self.master_env}\n")
            f.write(f"**Conflict Strategy:** {self.conflict_strategy}\n\n")
            f.write("---\n\n")
            
            for env, result in self.sync_results.items():
                f.write(f"## Environment: {env}\n\n")
                f.write(f"- Backup File: {result['backup_file']}\n")
                f.write(f"- Total Rows Synced: {result['total_rows_synced']:,}\n")
                f.write(f"- Total Errors: {result['total_errors']}\n\n")
                
                f.write("### Tables Synced\n\n")
                f.write("| Table | Rows Synced | Errors |\n")
                f.write("|-------|-------------|--------|\n")
                
                for table, table_result in result['tables'].items():
                    f.write(f"| {table} | {table_result['rows_synced']} | {len(table_result['errors'])} |\n")
                
                f.write("\n")
                
                # Errors
                if result['total_errors'] > 0:
                    f.write("### Errors\n\n")
                    for table, table_result in result['tables'].items():
                        if table_result['errors']:
                            f.write(f"#### {table}\n\n")
                            for error in table_result['errors']:
                                f.write(f"- {error}\n")
                            f.write("\n")
            
            # Tổng kết
            f.write("## Tổng Kết\n\n")
            total_rows = sum(r['total_rows_synced'] for r in self.sync_results.values())
            total_errors = sum(r['total_errors'] for r in self.sync_results.values())
            
            f.write(f"- Total Rows Synced: {total_rows:,}\n")
            f.write(f"- Total Errors: {total_errors}\n\n")
            
            if total_errors == 0:
                f.write("✅ **Đồng bộ thành công - Không có lỗi**\n\n")
            else:
                f.write("⚠️ **Đồng bộ hoàn thành nhưng có lỗi**\n\n")
        
        # Lưu JSON report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'master_env': self.master_env,
            'conflict_strategy': self.conflict_strategy,
            'sync_results': self.sync_results,
            'errors': self.errors
        }
        
        with open(JSON_REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n✅ Báo cáo đã được tạo:")
        print(f"   - Markdown: {REPORT_FILE}")
        print(f"   - JSON: {JSON_REPORT_FILE}")


def main():
    parser = argparse.ArgumentParser(description='Đồng bộ dữ liệu từ master đến các environments')
    parser.add_argument('--master', required=True, help='Master environment (dev/staging/prod)')
    parser.add_argument('--targets', required=True, nargs='+', help='Target environments to sync')
    parser.add_argument('--strategy', default='master_wins', choices=['master_wins', 'merge'],
                        help='Conflict resolution strategy')
    parser.add_argument('--skip-backup', action='store_true', help='Skip backup (not recommended)')
    
    args = parser.parse_args()
    
    syncer = DataSyncer(args.master, args.strategy)
    
    for target in args.targets:
        try:
            syncer.sync_environment(target)
        except Exception as e:
            print(f"❌ Error syncing {target}: {e}")
            syncer.errors.append(f"{target}: {e}")
    
    syncer.generate_report()
    
    if syncer.errors:
        sys.exit(1)


if __name__ == '__main__':
    main()

