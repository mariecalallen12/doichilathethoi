#!/usr/bin/env python3
"""
Script merge dữ liệu từ nhiều nguồn
Xử lý duplicates và conflicts với các strategies khác nhau
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
REPORT_FILE = os.path.join(REPORT_DIR, f"data_merge_{TIMESTAMP}.md")


class DataMerger:
    """Merge dữ liệu từ nhiều nguồn"""
    
    def __init__(self, merge_strategy: str = "latest_wins"):
        self.merge_strategy = merge_strategy  # "latest_wins", "master_wins", "merge_all"
        self.merge_results: Dict[str, Dict[str, Any]] = {}
        self.conflicts: List[Dict[str, Any]] = []
    
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
    
    def detect_duplicates(self, container: str, db_name: str, table: str, 
                         unique_columns: List[str]) -> List[Dict[str, Any]]:
        """Phát hiện duplicate records"""
        columns_str = ', '.join(unique_columns)
        sql = f"""
        SELECT {columns_str}, COUNT(*) as count
        FROM {table}
        GROUP BY {columns_str}
        HAVING COUNT(*) > 1;
        """
        
        # Execute và parse results
        # Implementation tương tự như data-analysis-comprehensive.py
        return []
    
    def merge_duplicates(self, container: str, db_name: str, table: str,
                        unique_columns: List[str], merge_strategy: str):
        """Merge duplicate records"""
        print(f"Merging duplicates in {table}...")
        
        # Strategy: Giữ record mới nhất (updated_at lớn nhất)
        if merge_strategy == "latest_wins":
            sql = f"""
            DELETE FROM {table} t1
            USING {table} t2
            WHERE t1.{unique_columns[0]} = t2.{unique_columns[0]}
            AND t1.updated_at < t2.updated_at;
            """
        # Implementation...
    
    def generate_report(self):
        """Tạo báo cáo merge"""
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("# Báo Cáo Merge Dữ Liệu\n\n")
            f.write(f"**Ngày thực hiện:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Merge Strategy:** {self.merge_strategy}\n\n")
            # ... rest of report


def main():
    parser = argparse.ArgumentParser(description='Merge dữ liệu từ nhiều nguồn')
    parser.add_argument('--sources', nargs='+', required=True, help='Source environments')
    parser.add_argument('--target', required=True, help='Target environment')
    parser.add_argument('--strategy', default='latest_wins', help='Merge strategy')
    
    args = parser.parse_args()
    
    merger = DataMerger(args.strategy)
    # Implementation...
    merger.generate_report()


if __name__ == '__main__':
    main()

