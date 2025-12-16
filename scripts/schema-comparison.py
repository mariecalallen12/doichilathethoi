#!/usr/bin/env python3
"""
Script so sánh schema giữa các environments (dev/staging/prod)
Phát hiện tables/columns/indexes/constraints khác biệt
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict

# Thêm project root vào path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

REPORT_DIR = os.path.join(PROJECT_ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_FILE = os.path.join(REPORT_DIR, f"schema_comparison_{TIMESTAMP}.md")
JSON_REPORT_FILE = os.path.join(REPORT_DIR, f"schema_comparison_{TIMESTAMP}.json")


class SchemaComparator:
    """So sánh schema giữa các PostgreSQL databases"""
    
    def __init__(self):
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.differences: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    
    def get_container_name(self, env: str) -> str:
        """Lấy tên container PostgreSQL cho environment"""
        # Có thể customize theo naming convention của dự án
        if env == "dev":
            return "digital_utopia_postgres"
        elif env == "staging":
            return "digital_utopia_postgres_staging"
        elif env == "prod":
            return "digital_utopia_postgres_prod"
        else:
            # Fallback: tìm container có chứa postgres
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
    
    def execute_sql(self, container: str, db_name: str, sql: str) -> List[Dict[str, Any]]:
        """Thực thi SQL query và trả về kết quả"""
        try:
            cmd = [
                "docker", "exec", container,
                "psql", "-U", "postgres", "-d", db_name,
                "-t", "-A", "-F", "|"
            ]
            
            # Thêm password nếu cần
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
                print(f"Warning: SQL execution failed: {result.stderr}", file=sys.stderr)
                return []
            
            lines = result.stdout.strip().split('\n')
            if not lines or lines[0].strip() == '':
                return []
            
            # Parse kết quả (giả định format pipe-separated)
            # Cần customize theo từng query cụ thể
            return [line.strip() for line in lines if line.strip()]
        except Exception as e:
            print(f"Error executing SQL: {e}", file=sys.stderr)
            return []
    
    def get_tables(self, container: str, db_name: str) -> Set[str]:
        """Lấy danh sách tables"""
        sql = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        ORDER BY tablename;
        """
        result = self.execute_sql(container, db_name, sql)
        return {line.strip() for line in result if line.strip()}
    
    def get_columns(self, container: str, db_name: str, table: str) -> List[Dict[str, str]]:
        """Lấy danh sách columns của một table"""
        sql = f"""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' 
        AND table_name = '{table}'
        ORDER BY ordinal_position;
        """
        result = self.execute_sql(container, db_name, sql)
        columns = []
        for line in result:
            parts = line.split('|')
            if len(parts) >= 5:
                columns.append({
                    'name': parts[0].strip(),
                    'type': parts[1].strip(),
                    'max_length': parts[2].strip() if parts[2].strip() != '' else None,
                    'nullable': parts[3].strip() == 'YES',
                    'default': parts[4].strip() if len(parts) > 4 else None
                })
        return columns
    
    def get_indexes(self, container: str, db_name: str, table: str) -> Set[str]:
        """Lấy danh sách indexes của một table"""
        sql = f"""
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public' 
        AND tablename = '{table}';
        """
        result = self.execute_sql(container, db_name, sql)
        return {line.strip() for line in result if line.strip()}
    
    def get_constraints(self, container: str, db_name: str, table: str) -> List[Dict[str, str]]:
        """Lấy danh sách constraints của một table"""
        sql = f"""
        SELECT 
            constraint_name,
            constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = 'public' 
        AND table_name = '{table}';
        """
        result = self.execute_sql(container, db_name, sql)
        constraints = []
        for line in result:
            parts = line.split('|')
            if len(parts) >= 2:
                constraints.append({
                    'name': parts[0].strip(),
                    'type': parts[1].strip()
                })
        return constraints
    
    def scan_schema(self, env: str) -> Dict[str, Any]:
        """Quét schema của một environment"""
        print(f"Scanning schema for environment: {env}")
        
        container = self.get_container_name(env)
        db_name = self.get_db_name(env)
        
        # Kiểm tra container có tồn tại không
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        
        if container not in result.stdout:
            print(f"Warning: Container {container} not found for environment {env}")
            return {}
        
        schema = {
            'environment': env,
            'container': container,
            'database': db_name,
            'tables': {},
            'migration_version': None
        }
        
        # Lấy migration version
        migration_sql = "SELECT version_num FROM alembic_version LIMIT 1;"
        migration_result = self.execute_sql(container, db_name, migration_sql)
        if migration_result:
            schema['migration_version'] = migration_result[0].strip()
        
        # Lấy danh sách tables
        tables = self.get_tables(container, db_name)
        
        for table in tables:
            schema['tables'][table] = {
                'columns': self.get_columns(container, db_name, table),
                'indexes': list(self.get_indexes(container, db_name, table)),
                'constraints': self.get_constraints(container, db_name, table)
            }
        
        return schema
    
    def compare_schemas(self, env1: str, env2: str):
        """So sánh schema giữa hai environments"""
        schema1 = self.schemas.get(env1, {})
        schema2 = self.schemas.get(env2, {})
        
        if not schema1 or not schema2:
            print(f"Warning: Cannot compare {env1} and {env2} - missing schemas")
            return
        
        tables1 = set(schema1.get('tables', {}).keys())
        tables2 = set(schema2.get('tables', {}).keys())
        
        # Tables chỉ có trong env1
        only_in_env1 = tables1 - tables2
        if only_in_env1:
            self.differences[f"{env1}_vs_{env2}"].append({
                'type': 'missing_tables',
                'environment': env2,
                'tables': list(only_in_env1)
            })
        
        # Tables chỉ có trong env2
        only_in_env2 = tables2 - tables1
        if only_in_env2:
            self.differences[f"{env1}_vs_{env2}"].append({
                'type': 'extra_tables',
                'environment': env2,
                'tables': list(only_in_env2)
            })
        
        # So sánh từng table chung
        common_tables = tables1 & tables2
        for table in common_tables:
            self._compare_table(env1, env2, table, schema1['tables'][table], schema2['tables'][table])
    
    def _compare_table(self, env1: str, env2: str, table: str, table1: Dict, table2: Dict):
        """So sánh chi tiết một table"""
        # So sánh columns
        cols1 = {col['name']: col for col in table1.get('columns', [])}
        cols2 = {col['name']: col for col in table2.get('columns', [])}
        
        only_in_cols1 = set(cols1.keys()) - set(cols2.keys())
        only_in_cols2 = set(cols2.keys()) - set(cols1.keys())
        
        if only_in_cols1:
            self.differences[f"{env1}_vs_{env2}"].append({
                'type': 'missing_columns',
                'table': table,
                'environment': env2,
                'columns': [cols1[col] for col in only_in_cols1]
            })
        
        if only_in_cols2:
            self.differences[f"{env1}_vs_{env2}"].append({
                'type': 'extra_columns',
                'table': table,
                'environment': env2,
                'columns': [cols2[col] for col in only_in_cols2]
            })
        
        # So sánh columns chung
        common_cols = set(cols1.keys()) & set(cols2.keys())
        for col_name in common_cols:
            col1 = cols1[col_name]
            col2 = cols2[col_name]
            
            if col1['type'] != col2['type']:
                self.differences[f"{env1}_vs_{env2}"].append({
                    'type': 'column_type_mismatch',
                    'table': table,
                    'column': col_name,
                    env1: col1['type'],
                    env2: col2['type']
                })
        
        # So sánh indexes
        idx1 = set(table1.get('indexes', []))
        idx2 = set(table2.get('indexes', []))
        
        if idx1 != idx2:
            only_in_idx1 = idx1 - idx2
            only_in_idx2 = idx2 - idx1
            
            if only_in_idx1:
                self.differences[f"{env1}_vs_{env2}"].append({
                    'type': 'missing_indexes',
                    'table': table,
                    'environment': env2,
                    'indexes': list(only_in_idx1)
                })
            
            if only_in_idx2:
                self.differences[f"{env1}_vs_{env2}"].append({
                    'type': 'extra_indexes',
                    'table': table,
                    'environment': env2,
                    'indexes': list(only_in_idx2)
                })
    
    def generate_report(self):
        """Tạo báo cáo markdown"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo So Sánh Schema Giữa Các Environments\n\n")
            f.write(f"**Ngày thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Tổng quan
            f.write("## 1. Tổng Quan\n\n")
            for env, schema in self.schemas.items():
                f.write(f"### Environment: {env}\n\n")
                f.write(f"- Container: {schema.get('container', 'N/A')}\n")
                f.write(f"- Database: {schema.get('database', 'N/A')}\n")
                f.write(f"- Migration Version: {schema.get('migration_version', 'N/A')}\n")
                f.write(f"- Số lượng tables: {len(schema.get('tables', {}))}\n\n")
            
            # Differences
            f.write("## 2. Phát Hiện Khác Biệt\n\n")
            
            if not self.differences:
                f.write("✅ **Không có khác biệt nào được phát hiện**\n\n")
            else:
                for comparison, diffs in self.differences.items():
                    f.write(f"### {comparison}\n\n")
                    
                    for diff in diffs:
                        diff_type = diff['type']
                        
                        if diff_type == 'missing_tables':
                            f.write(f"#### Tables thiếu trong {diff['environment']}\n\n")
                            for table in diff['tables']:
                                f.write(f"- `{table}`\n")
                            f.write("\n")
                        
                        elif diff_type == 'extra_tables':
                            f.write(f"#### Tables thừa trong {diff['environment']}\n\n")
                            for table in diff['tables']:
                                f.write(f"- `{table}`\n")
                            f.write("\n")
                        
                        elif diff_type == 'missing_columns':
                            f.write(f"#### Columns thiếu trong table `{diff['table']}` ({diff['environment']})\n\n")
                            for col in diff['columns']:
                                f.write(f"- `{col['name']}` ({col['type']})\n")
                            f.write("\n")
                        
                        elif diff_type == 'column_type_mismatch':
                            f.write(f"#### Column type mismatch: `{diff['table']}.{diff['column']}`\n\n")
                            f.write(f"- {comparison.split('_vs_')[0]}: {diff[comparison.split('_vs_')[0]]}\n")
                            f.write(f"- {comparison.split('_vs_')[1]}: {diff[comparison.split('_vs_')[1]]}\n\n")
            
            # Khuyến nghị
            f.write("## 3. Khuyến Nghị\n\n")
            if self.differences:
                f.write("1. Tạo migration để đồng bộ schema giữa các environments\n")
                f.write("2. Chạy migration trên tất cả environments\n")
                f.write("3. Verify schema consistency sau migration\n")
            else:
                f.write("✅ Schema đã nhất quán giữa các environments\n")
        
        # Lưu JSON report
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'schemas': self.schemas,
            'differences': dict(self.differences)
        }
        
        with open(JSON_REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"\n✅ Báo cáo đã được tạo:")
        print(f"   - Markdown: {REPORT_FILE}")
        print(f"   - JSON: {JSON_REPORT_FILE}")


def main():
    parser = argparse.ArgumentParser(description='So sánh schema giữa các environments')
    parser.add_argument('--environments', nargs='+', default=['dev', 'staging', 'prod'],
                        help='List of environments to compare')
    parser.add_argument('--compare-all', action='store_true',
                        help='Compare all environments with each other')
    
    args = parser.parse_args()
    
    comparator = SchemaComparator()
    
    # Scan schemas
    for env in args.environments:
        schema = comparator.scan_schema(env)
        if schema:
            comparator.schemas[env] = schema
    
    # Compare schemas
    if args.compare_all:
        envs = list(comparator.schemas.keys())
        for i in range(len(envs)):
            for j in range(i + 1, len(envs)):
                comparator.compare_schemas(envs[i], envs[j])
    else:
        # Chỉ so sánh với environment đầu tiên (thường là dev hoặc prod)
        if len(comparator.schemas) > 1:
            base_env = list(comparator.schemas.keys())[0]
            for env in list(comparator.schemas.keys())[1:]:
                comparator.compare_schemas(base_env, env)
    
    # Generate report
    comparator.generate_report()


if __name__ == '__main__':
    main()

