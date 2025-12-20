#!/usr/bin/env python3
"""
Data Integrity Validator
Cross-reference frontend data with API responses and verify calculations
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIntegrityValidator:
    """Validate data consistency between frontend and backend"""
    
    def __init__(self, api_url: str = "http://localhost:8000", 
                 client_url: str = "http://localhost:3002",
                 access_token: Optional[str] = None):
        """Initialize validator"""
        self.api_url = api_url
        self.client_url = client_url
        self.access_token = access_token
        self.results: List[Dict] = []
    
    def get_headers(self) -> Dict:
        """Get request headers with auth if available"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def verify_wallet_balance(self) -> Dict:
        """Verify wallet balance calculations"""
        try:
            # Get balance from API
            response = requests.get(
                f"{self.api_url}/api/client/wallet-balances",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "test": "wallet_balance",
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
            
            api_data = response.json()
            
            # Extract balances
            balances = []
            if isinstance(api_data, dict):
                if "data" in api_data:
                    balances = api_data["data"].get("balances", [])
                elif "balances" in api_data:
                    balances = api_data["balances"]
            
            # Verify calculations
            issues = []
            for balance in balances:
                asset = balance.get("asset", "")
                total = balance.get("totalBalance", 0)
                available = balance.get("availableBalance", 0)
                locked = balance.get("lockedBalance", 0)
                pending = balance.get("pendingBalance", 0)
                reserved = balance.get("reservedBalance", 0)
                
                # Check: total = available + locked + pending + reserved
                calculated_total = available + locked + pending + reserved
                if abs(total - calculated_total) > 0.01:  # Allow small floating point differences
                    issues.append({
                        "asset": asset,
                        "expected_total": calculated_total,
                        "actual_total": total,
                        "difference": abs(total - calculated_total)
                    })
            
            result = {
                "test": "wallet_balance",
                "success": len(issues) == 0,
                "total_balances": len(balances),
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test": "wallet_balance",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def verify_transaction_history(self, limit: int = 10) -> Dict:
        """Verify transaction history consistency"""
        try:
            # Get transactions from API
            response = requests.get(
                f"{self.api_url}/api/client/transactions?limit={limit}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "test": "transaction_history",
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
            
            api_data = response.json()
            
            # Extract transactions
            transactions = []
            if isinstance(api_data, dict):
                if "data" in api_data:
                    transactions = api_data["data"].get("transactions", [])
                elif "transactions" in api_data:
                    transactions = api_data["transactions"]
            
            # Verify transaction calculations
            issues = []
            for tx in transactions:
                amount = tx.get("amount", 0)
                fee = tx.get("fee", 0)
                net_amount = tx.get("netAmount", 0)
                
                # Check: net_amount = amount - fee
                calculated_net = amount - fee
                if abs(net_amount - calculated_net) > 0.01:
                    issues.append({
                        "transaction_id": tx.get("id", "unknown"),
                        "expected_net": calculated_net,
                        "actual_net": net_amount,
                        "difference": abs(net_amount - calculated_net)
                    })
            
            result = {
                "test": "transaction_history",
                "success": len(issues) == 0,
                "total_transactions": len(transactions),
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test": "transaction_history",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def verify_portfolio_calculations(self) -> Dict:
        """Verify portfolio calculations"""
        try:
            # Get portfolio analytics
            response = requests.get(
                f"{self.api_url}/api/portfolio/analytics",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "test": "portfolio_calculations",
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
            
            api_data = response.json()
            
            # Extract portfolio data
            portfolio = {}
            if isinstance(api_data, dict):
                if "data" in api_data:
                    portfolio = api_data["data"]
                else:
                    portfolio = api_data
            
            # Verify calculations
            issues = []
            
            # Check total value calculation
            total_value = portfolio.get("totalValue", 0)
            positions = portfolio.get("positions", [])
            calculated_total = sum(pos.get("value", 0) for pos in positions)
            
            if abs(total_value - calculated_total) > 0.01:
                issues.append({
                    "calculation": "total_value",
                    "expected": calculated_total,
                    "actual": total_value,
                    "difference": abs(total_value - calculated_total)
                })
            
            result = {
                "test": "portfolio_calculations",
                "success": len(issues) == 0,
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test": "portfolio_calculations",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def verify_exchange_rates(self) -> Dict:
        """Verify exchange rates consistency"""
        try:
            # Get exchange rates from API
            response = requests.get(
                f"{self.api_url}/api/client/exchange-rates",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "test": "exchange_rates",
                    "success": False,
                    "error": f"API returned {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }
            
            api_data = response.json()
            
            # Extract rates
            rates = []
            if isinstance(api_data, dict):
                if "data" in api_data:
                    rates = api_data["data"].get("rates", [])
                elif "rates" in api_data:
                    rates = api_data["rates"]
            
            # Verify rate consistency
            issues = []
            rate_map = {}
            for rate in rates:
                from_curr = rate.get("from", "")
                to_curr = rate.get("to", "")
                value = rate.get("rate", 0)
                rate_map[f"{from_curr}_{to_curr}"] = value
            
            # Check inverse rates (USD/EUR should be inverse of EUR/USD)
            for from_curr in ["USD", "EUR", "GBP"]:
                for to_curr in ["USD", "EUR", "GBP"]:
                    if from_curr != to_curr:
                        forward_key = f"{from_curr}_{to_curr}"
                        reverse_key = f"{to_curr}_{from_curr}"
                        
                        if forward_key in rate_map and reverse_key in rate_map:
                            forward_rate = rate_map[forward_key]
                            reverse_rate = rate_map[reverse_key]
                            
                            # Check if they're approximately inverse
                            if forward_rate > 0 and abs(forward_rate * reverse_rate - 1.0) > 0.1:
                                issues.append({
                                    "pair": f"{from_curr}/{to_curr}",
                                    "forward_rate": forward_rate,
                                    "reverse_rate": reverse_rate,
                                    "product": forward_rate * reverse_rate
                                })
            
            result = {
                "test": "exchange_rates",
                "success": len(issues) == 0,
                "total_rates": len(rates),
                "issues": issues,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results.append(result)
            return result
            
        except Exception as e:
            result = {
                "test": "exchange_rates",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(result)
            return result
    
    def run_all_checks(self) -> Dict:
        """Run all data integrity checks"""
        logger.info("Running data integrity checks...")
        
        checks = [
            self.verify_wallet_balance,
            self.verify_transaction_history,
            self.verify_portfolio_calculations,
            self.verify_exchange_rates
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                logger.error(f"Error running check {check.__name__}: {e}")
        
        # Calculate summary
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success", False))
        
        summary = {
            "total_checks": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }
        
        return summary
    
    def save_results(self, output_path: str):
        """Save validation results to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_checks": len(self.results),
                    "passed": sum(1 for r in self.results if r.get("success", False)),
                    "failed": sum(1 for r in self.results if not r.get("success", False))
                },
                "results": self.results
            }, f, indent=2)
        
        logger.info(f"Results saved to: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate data integrity")
    parser.add_argument("-u", "--api-url", default="http://localhost:8000", help="API URL")
    parser.add_argument("-t", "--token", help="Access token")
    parser.add_argument("-o", "--output", default="data_integrity_results.json", help="Output file")
    
    args = parser.parse_args()
    
    validator = DataIntegrityValidator(api_url=args.api_url, access_token=args.token)
    summary = validator.run_all_checks()
    
    print("="*80)
    print("DATA INTEGRITY VALIDATION RESULTS")
    print("="*80)
    print(f"Total Checks: {summary['total_checks']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']*100:.1f}%")
    print()
    
    for result in summary['results']:
        status = "✅" if result.get("success") else "❌"
        print(f"{status} {result.get('test', 'unknown')}")
        if not result.get("success"):
            if "error" in result:
                print(f"   Error: {result['error']}")
            if "issues" in result:
                print(f"   Issues: {len(result['issues'])}")
    
    validator.save_results(args.output)
    print(f"\nResults saved to: {args.output}")

