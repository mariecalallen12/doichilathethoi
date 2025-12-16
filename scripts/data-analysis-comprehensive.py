#!/usr/bin/env python3
"""
Script phân tích dữ liệu toàn diện
Phát hiện duplicates, orphans, inconsistencies giữa các environments
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = os.path.join(REPORT_DIR, f"data_analysis_{TIMESTAMP}.md")
JSON_REPORT_FILE = os.path.join(REPORT_DIR, f"data_analysis_{TIMESTAMP}.json")


class DataAnalyzer:
    """Phân tích dữ liệu để phát hiện vấn đề"""
    
    def __init__(self):
        self.analysis_results: Dict[str, Dict[str, Any]] = {}
        self.issues: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def get_container_name(self, env: str) -> str:
        """Lấy tên container PostgreSQL cho environment"""
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
        """Lấy tên database cho environment"""
        return os.getenv(f"POSTGRES_DB_{env.upper()}", "digital_utopia")
    
    def execute_sql(self, container: str, db_name: str, sql: str) -> List[List[str]]:
        """Thực thi SQL query và trả về kết quả dạng list of lists"""
        try:
            cmd = [
                "docker", "exec", container,
                "psql", "-U", "postgres", "-d", db_name,
                "-t", "-A", "-F", "|"
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
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"Warning: SQL execution failed: {result.stderr}", file=sys.stderr)
                return []
            
            lines = result.stdout.strip().split('\n')
            if not lines or not lines[0].strip():
                return []
            
            return [line.split('|') for line in lines if line.strip()]
        except Exception as e:
            print(f"Error executing SQL: {e}", file=sys.stderr)
            return []
    
    def analyze_duplicates(self, container: str, db_name: str, env: str):
        """Phát hiện duplicate records"""
        print(f"Analyzing duplicates for {env}...")
        
        # Duplicate emails trong users
        sql = """
        SELECT email, COUNT(*) as count
        FROM users
        GROUP BY email
        HAVING COUNT(*) > 1;
        """
        results = self.execute_sql(container, db_name, sql)
        
        if results:
            self.issues[f"{env}_duplicates"].append({
                'type': 'duplicate_emails',
                'table': 'users',
                'column': 'email',
                'count': len(results),
                'details': [{'email': r[0].strip(), 'count': r[1].strip()} for r in results]
            })
        
        # Duplicate customer_payment_id
        sql = """
        SELECT customer_payment_id, COUNT(*) as count
        FROM users
        WHERE customer_payment_id IS NOT NULL
        GROUP BY customer_payment_id
        HAVING COUNT(*) > 1;
        """
        results = self.execute_sql(container, db_name, sql)
        
        if results:
            self.issues[f"{env}_duplicates"].append({
                'type': 'duplicate_customer_payment_id',
                'table': 'users',
                'column': 'customer_payment_id',
                'count': len(results),
                'details': [{'id': r[0].strip(), 'count': r[1].strip()} for r in results]
            })
        
        # Duplicate invoice numbers
        sql = """
        SELECT invoice_number, COUNT(*) as count
        FROM invoices
        GROUP BY invoice_number
        HAVING COUNT(*) > 1;
        """
        results = self.execute_sql(container, db_name, sql)
        
        if results:
            self.issues[f"{env}_duplicates"].append({
                'type': 'duplicate_invoice_numbers',
                'table': 'invoices',
                'column': 'invoice_number',
                'count': len(results),
                'details': [{'invoice_number': r[0].strip(), 'count': r[1].strip()} for r in results]
            })
    
    def analyze_orphans(self, container: str, db_name: str, env: str):
        """Phát hiện orphaned records"""
        print(f"Analyzing orphans for {env}...")
        
        # Orphaned user_profiles
        sql = """
        SELECT COUNT(*) as count
        FROM user_profiles up
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = up.user_id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_user_profiles',
                'table': 'user_profiles',
                'count': int(results[0][0])
            })
        
        # Orphaned refresh_tokens
        sql = """
        SELECT COUNT(*) as count
        FROM refresh_tokens rt
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = rt.user_id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_refresh_tokens',
                'table': 'refresh_tokens',
                'count': int(results[0][0])
            })
        
        # Orphaned wallet_balances
        sql = """
        SELECT COUNT(*) as count
        FROM wallet_balances wb
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = wb.user_id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_wallet_balances',
                'table': 'wallet_balances',
                'count': int(results[0][0])
            })
        
        # Orphaned trading_orders
        sql = """
        SELECT COUNT(*) as count
        FROM trading_orders to
        WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id = to.user_id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_trading_orders',
                'table': 'trading_orders',
                'count': int(results[0][0])
            })
        
        # Orphaned iceberg_orders
        sql = """
        SELECT COUNT(*) as count
        FROM iceberg_orders io
        WHERE io.parent_order_id IS NOT NULL 
        AND NOT EXISTS (SELECT 1 FROM trading_orders to WHERE to.id = io.parent_order_id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_iceberg_orders',
                'table': 'iceberg_orders',
                'count': int(results[0][0])
            })
        
        # Orphaned oco_orders
        sql = """
        SELECT COUNT(*) as count
        FROM oco_orders oo
        WHERE (
            (oo.primary_order_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM trading_orders to WHERE to.id = oo.primary_order_id))
            OR
            (oo.secondary_order_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM trading_orders to WHERE to.id = oo.secondary_order_id))
        );
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_orphans"].append({
                'type': 'orphaned_oco_orders',
                'table': 'oco_orders',
                'count': int(results[0][0])
            })
    
    def analyze_inconsistencies(self, container: str, db_name: str, env: str):
        """Phát hiện dữ liệu không nhất quán"""
        print(f"Analyzing inconsistencies for {env}...")
        
        # Users không có profile
        sql = """
        SELECT COUNT(*) as count
        FROM users u
        WHERE NOT EXISTS (SELECT 1 FROM user_profiles up WHERE up.user_id = u.id);
        """
        results = self.execute_sql(container, db_name, sql)
        if results and int(results[0][0]) > 0:
            self.issues[f"{env}_inconsistencies"].append({
                'type': 'users_without_profiles',
                'count': int(results[0][0])
            })
        
        # Wallet balances không khớp với transactions
        sql = """
        SELECT 
            wb.user_id,
            wb.asset,
            wb.available_balance + wb.locked_balance as calculated_balance,
            COALESCE(SUM(t.net_amount), 0) as transaction_sum
        FROM wallet_balances wb
        LEFT JOIN transactions t ON t.user_id = wb.user_id AND t.asset = wb.asset
        GROUP BY wb.user_id, wb.asset, wb.available_balance, wb.locked_balance
        HAVING ABS((wb.available_balance + wb.locked_balance) - COALESCE(SUM(t.net_amount), 0)) > 0.01;
        """
        results = self.execute_sql(container, db_name, sql)
        if results:
            self.issues[f"{env}_inconsistencies"].append({
                'type': 'wallet_balance_mismatch',
                'count': len(results),
                'details': [{'user_id': r[0], 'asset': r[1]} for r in results[:10]]  # Limit to 10
            })
        
        # Trading orders với status không hợp lệ
        sql = """
        SELECT status, COUNT(*) as count
        FROM trading_orders
        WHERE status NOT IN ('pending', 'open', 'filled', 'partial', 'cancelled', 'rejected', 'expired')
        GROUP BY status;
        """
        results = self.execute_sql(container, db_name, sql)
        if results:
            self.issues[f"{env}_inconsistencies"].append({
                'type': 'invalid_order_status',
                'table': 'trading_orders',
                'count': sum(int(r[1]) for r in results),
                'details': [{'status': r[0], 'count': r[1]} for r in results]
            })
    
    def compare_environments(self, env1: str, env2: str):
        """So sánh số lượng records giữa các environments"""
        print(f"Comparing {env1} vs {env2}...")
        
        container1 = self.get_container_name(env1)
        container2 = self.get_container_name(env2)
        db1 = self.get_db_name(env1)
        db2 = self.get_db_name(env2)
        
        # Lấy danh sách tables
        sql = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        ORDER BY tablename;
        """
        
        tables1 = [r[0].strip() for r in self.execute_sql(container1, db1, sql)]
        tables2 = [r[0].strip() for r in self.execute_sql(container2, db2, sql)]
        
        common_tables = set(tables1) & set(tables2)
        
        comparison = {
            'env1': env1,
            'env2': env2,
            'tables': {}
        }
        
        for table in common_tables:
            sql1 = f"SELECT COUNT(*) FROM {table};"
            sql2 = f"SELECT COUNT(*) FROM {table};"
            
            count1 = self.execute_sql(container1, db1, sql1)
            count2 = self.execute_sql(container2, db2, sql2)
            
            if count1 and count2:
                c1 = int(count1[0][0])
                c2 = int(count2[0][0])
                
                comparison['tables'][table] = {
                    env1: c1,
                    env2: c2,
                    'difference': abs(c1 - c2)
                }
                
                if c1 != c2:
                    self.issues[f"{env1}_vs_{env2}_comparison"].append({
                        'type': 'record_count_mismatch',
                        'table': table,
                        env1: c1,
                        env2: c2,
                        'difference': abs(c1 - c2)
                    })
        
        return comparison
    
    def analyze_environment(self, env: str):
        """Phân tích một environment"""
        print(f"\n{'='*60}")
        print(f"Analyzing environment: {env}")
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
            print(f"Warning: Container {container} not found for environment {env}")
            return
        
        env_result = {
            'environment': env,
            'container': container,
            'database': db_name,
            'timestamp': datetime.now().isoformat()
        }
        
        # Thống kê tổng quan
        sql = """
        SELECT 
            COUNT(*) as table_count,
            SUM(n_live_tup) as total_rows
        FROM pg_stat_user_tables;
        """
        stats = self.execute_sql(container, db_name, sql)
        if stats:
            env_result['total_tables'] = len([t for t in self.execute_sql(container, db_name, "SELECT tablename FROM pg_tables WHERE schemaname = 'public';")])
            env_result['total_rows'] = int(stats[0][1]) if len(stats[0]) > 1 else 0
        
        # Phân tích
        self.analyze_duplicates(container, db_name, env)
        self.analyze_orphans(container, db_name, env)
        self.analyze_inconsistencies(container, db_name, env)
        
        env_result['issues'] = {
            'duplicates': len(self.issues.get(f"{env}_duplicates", [])),
            'orphans': len(self.issues.get(f"{env}_orphans", [])),
            'inconsistencies': len(self.issues.get(f"{env}_inconsistencies", []))
        }
        
        self.analysis_results[env] = env_result
    
    def generate_report(self):
        """Tạo báo cáo markdown"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo Phân Tích Dữ Liệu Toàn Diện\n\n")
            f.write(f"**Ngày thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Tổng quan
            f.write("## 1. Tổng Quan Các Environments\n\n")
            for env, result in self.analysis_results.items():
                f.write(f"### Environment: {env}\n\n")
                f.write(f"- Container: {result.get('container', 'N/A')}\n")
                f.write(f"- Database: {result.get('database', 'N/A')}\n")
                f.write(f"- Tổng số tables: {result.get('total_tables', 0)}\n")
                f.write(f"- Tổng số rows: {result.get('total_rows', 0):,}\n")
                f.write(f"- Duplicates phát hiện: {result['issues']['duplicates']}\n")
                f.write(f"- Orphans phát hiện: {result['issues']['orphans']}\n")
                f.write(f"- Inconsistencies phát hiện: {result['issues']['inconsistencies']}\n\n")
            
            # Chi tiết issues
            f.write("## 2. Chi Tiết Các Vấn Đề\n\n")
            
            for issue_type, issue_list in self.issues.items():
                if not issue_list:
                    continue
                
                f.write(f"### {issue_type}\n\n")
                
                for issue in issue_list:
                    if issue['type'] == 'duplicate_emails':
                        f.write(f"#### Duplicate Emails trong {issue['table']}\n\n")
                        f.write(f"- Số lượng: {issue['count']}\n\n")
                        f.write("| Email | Count |\n")
                        f.write("|-------|-------|\n")
                        for detail in issue['details'][:20]:  # Limit to 20
                            f.write(f"| {detail['email']} | {detail['count']} |\n")
                        f.write("\n")
                    
                    elif issue['type'].startswith('orphaned_'):
                        f.write(f"#### {issue['type']}\n\n")
                        f.write(f"- Table: {issue['table']}\n")
                        f.write(f"- Số lượng: {issue['count']}\n\n")
                    
                    elif issue['type'] == 'record_count_mismatch':
                        f.write(f"#### Record Count Mismatch: {issue['table']}\n\n")
                        f.write(f"- Difference: {issue['difference']}\n\n")
            
            # Khuyến nghị
            f.write("## 3. Khuyến Nghị\n\n")
            
            total_issues = sum(len(issues) for issues in self.issues.values())
            
            if total_issues == 0:
                f.write("✅ **Không có vấn đề nào được phát hiện**\n\n")
            else:
                f.write("1. **Xử lý Duplicates:**\n")
                f.write("   - Xóa hoặc merge duplicate records\n")
                f.write("   - Thêm unique constraints để ngăn chặn duplicates trong tương lai\n\n")
                
                f.write("2. **Xử lý Orphans:**\n")
                f.write("   - Xóa orphaned records hoặc fix foreign keys\n")
                f.write("   - Đảm bảo referential integrity\n\n")
                
                f.write("3. **Xử lý Inconsistencies:**\n")
                f.write("   - Fix data inconsistencies\n")
                f.write("   - Validate business rules\n\n")
        
        # Lưu JSON report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'analysis_results': self.analysis_results,
            'issues': dict(self.issues)
        }
        
        with open(JSON_REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n✅ Báo cáo đã được tạo:")
        print(f"   - Markdown: {REPORT_FILE}")
        print(f"   - JSON: {JSON_REPORT_FILE}")


def main():
    parser = argparse.ArgumentParser(description='Phân tích dữ liệu toàn diện')
    parser.add_argument('--environments', nargs='+', default=['dev', 'staging', 'prod'],
                        help='List of environments to analyze')
    parser.add_argument('--compare', action='store_true',
                        help='Compare environments with each other')
    
    args = parser.parse_args()
    
    analyzer = DataAnalyzer()
    
    # Analyze each environment
    for env in args.environments:
        analyzer.analyze_environment(env)
    
    # Compare environments if requested
    if args.compare and len(args.environments) > 1:
        for i in range(len(args.environments)):
            for j in range(i + 1, len(args.environments)):
                analyzer.compare_environments(args.environments[i], args.environments[j])
    
    # Generate report
    analyzer.generate_report()


if __name__ == '__main__':
    main()

