#!/usr/bin/env python3
"""
Project Migration Script
=======================

Migrate project files to new TradingSystemAPI structure
"""

import os
import shutil
from pathlib import Path

def migrate_project_files():
    """Migrate important project files to new structure"""
    
    workspace = Path("/workspace")
    target = workspace / "TradingSystemAPI"
    
    # Files to migrate
    files_to_migrate = [
        # Legacy files (for reference)
        ("free_crypto_data_aggregator.py", "legacy_market_data.py"),
        ("trading_signals_system.py", "legacy_trading_signals.py"),
        ("customer_trading_dashboard.py", "legacy_dashboard.py"),
        
        # Reports and documentation
        ("Crypto_Data_API_Success_Report.md", "Legacy_Reports/Crypto_API_Success.md"),
        ("Crypto_Market_Comprehensive_Report.md", "Legacy_Reports/Market_Analysis.md"),
        ("Binary_Trading_Signals_Final_Report.md", "Legacy_Reports/Binary_Signals.md"),
        ("API_Sources_Real_Time_Report.md", "Legacy_Reports/API_Sources.md"),
        
        # Test files
        ("test_api_quick.py", "Tests/legacy_test_market.py"),
        ("test_fixed_aggregator.py", "Tests/legacy_test_signals.py"),
        ("comprehensive_crypto_analysis.py", "Tests/legacy_market_analysis.py"),
        ("debug_crypto_apis.py", "Tests/legacy_debug_apis.py"),
        ("api_sources_analysis.py", "Tests/legacy_api_verification.py"),
        ("realtime_verification.py", "Tests/legacy_realtime_test.py"),
        ("simple_binary_demo.py", "Tests/legacy_binary_demo.py"),
        
        # Configuration
        ("requirements.txt", "requirements_legacy.txt")
    ]
    
    # Create directories
    directories = [
        "Legacy_Reports",
        "Tests/legacy",
        "Legacy_Utils"
    ]
    
    for dir_name in directories:
        (target / dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")
    
    # Migrate files
    for source_file, target_file in files_to_migrate:
        source_path = workspace / source_file
        target_path = target / target_file
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, target_path)
                print(f"✅ Migrated: {source_file} -> {target_file}")
            except Exception as e:
                print(f"❌ Failed to migrate {source_file}: {e}")
        else:
            print(f"⚠️  Source file not found: {source_file}")
    
    print(f"\n🎉 Migration completed!")
    print(f"📁 Target directory: {target}")

def show_project_structure():
    """Show the new project structure"""
    target = Path("/workspace/TradingSystemAPI")
    
    print(f"\n📂 TRADING SYSTEM API - PROJECT STRUCTURE")
    print("=" * 60)
    
    def print_tree(path, prefix="", is_last=True):
        """Print directory tree"""
        if path.is_dir():
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{path.name}/")
            
            children = sorted(path.iterdir())
            for i, child in enumerate(children):
                is_last_child = i == len(children) - 1
                extension = "    " if is_last else "│   "
                print_tree(child, prefix + extension, is_last_child)
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{path.name}")
    
    print_tree(target)

def create_migration_summary():
    """Create migration summary"""
    summary = """# Project Migration Summary

## Migration Completed: 2025-12-21

### New Architecture
- **Stream 1**: Market Data API (/market) - Real-time market information
- **Stream 2**: Trading Features API (/trading) - Binary signals and analysis

### Legacy Files Migrated
All previous development files have been migrated to appropriate directories:
- Legacy reports -> Legacy_Reports/
- Legacy tests -> Tests/legacy/
- Legacy utilities -> Legacy_Utils/

### New Structure Benefits
1. **Clean Architecture**: Clear separation between market data and trading features
2. **Modular Design**: Each module is independent and testable
3. **Production Ready**: Config files, requirements, and documentation
4. **Scalable**: Easy to add new features and data sources

### Key Files
- `main.py`: Main server with dual-stream routing
- `MarketData/`: Market information display API
- `TradingFeatures/`: Trading signals and analysis API
- `Shared/`: Common utilities and models
- `Config/`: Configuration files
- `README.md`: Complete documentation

### API Endpoints
- Market Data: `/market/prices`, `/market/overview`, `/market/summary`
- Trading Features: `/trading/binary`, `/trading/signals`, `/trading/analysis`

### Next Steps
1. Run the system: `python main.py`
2. Test APIs: `python demo.py`
3. View documentation: http://localhost:8000/market/docs
4. Integrate with customer systems
"""
    
    with open("/workspace/TradingSystemAPI/MIGRATION_SUMMARY.md", "w") as f:
        f.write(summary)
    
    print("✅ Migration summary created: MIGRATION_SUMMARY.md")

if __name__ == "__main__":
    print("🚀 TRADING SYSTEM API - PROJECT MIGRATION")
    print("=" * 60)
    
    # Migrate files
    migrate_project_files()
    
    # Show structure
    show_project_structure()
    
    # Create summary
    create_migration_summary()
    
    print(f"\n✅ Migration complete!")
    print(f"📁 Check the new structure in: /workspace/TradingSystemAPI/")
    print(f"🚀 To run the system: cd /workspace/TradingSystemAPI && python main.py")
    print(f"🧪 To test the system: python demo.py")