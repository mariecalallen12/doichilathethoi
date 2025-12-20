#!/usr/bin/env python3
"""
Debug Mode for Acceptance Testing
Provides verbose logging, step-by-step execution, and interactive debugging
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

# Color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'


class DebugMode:
    """Debug mode manager for acceptance testing"""
    
    def __init__(self, config_path: Optional[str] = None, level: str = "normal"):
        """Initialize debug mode"""
        if config_path is None:
            config_path = Path(__file__).parent / "debug_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.level = level
        self.level_config = self.config["debug_levels"].get(level, self.config["debug_levels"]["normal"])
        self.color_output = self.config.get("color_output", True)
        self.log_to_file = self.config.get("log_to_file", True)
        self.log_file = Path(self.config.get("log_file", "debug.log"))
        self.breakpoints = set(self.config.get("breakpoints", []))
        self.interactive = self.config.get("interactive_mode", False) or self.level_config.get("interactive_mode", False)
        
        # Setup logging
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger("debug_mode")
        self.logger.setLevel(logging.DEBUG)
        
        if self.log_to_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _colorize(self, text: str, color: str) -> str:
        """Add color to text if color output is enabled"""
        if not self.color_output:
            return text
        return f"{color}{text}{Colors.RESET}"
    
    def _log(self, level: str, message: str, color: str = Colors.RESET):
        """Log message with appropriate level and color"""
        colored_message = self._colorize(message, color)
        print(colored_message)
        
        if self.log_to_file:
            if level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
            elif level == "info":
                self.logger.info(message)
            else:
                self.logger.debug(message)
    
    def error(self, message: str):
        """Log error message"""
        if self.level_config.get("show_errors", True):
            self._log("error", f"❌ ERROR: {message}", Colors.RED)
    
    def warning(self, message: str):
        """Log warning message"""
        if self.level_config.get("show_warnings", True):
            self._log("warning", f"⚠️  WARNING: {message}", Colors.YELLOW)
    
    def info(self, message: str):
        """Log info message"""
        if self.level_config.get("show_info", False):
            self._log("info", f"ℹ️  INFO: {message}", Colors.BLUE)
    
    def success(self, message: str):
        """Log success message"""
        if self.level_config.get("show_info", False):
            self._log("info", f"✅ SUCCESS: {message}", Colors.GREEN)
    
    def detail(self, message: str):
        """Log detail message"""
        if self.level_config.get("show_details", False):
            self._log("debug", f"   {message}", Colors.GRAY)
    
    def section(self, title: str):
        """Log section header"""
        if self.level_config.get("show_info", False):
            separator = "=" * 60
            self._log("info", f"\n{separator}", Colors.CYAN)
            self._log("info", f"{title}", Colors.CYAN + Colors.BOLD)
            self._log("info", f"{separator}\n", Colors.CYAN)
    
    def endpoint_start(self, method: str, path: str):
        """Log endpoint test start"""
        if self.level_config.get("show_info", False):
            self._log("info", f"\n🔍 Testing: {method} {path}", Colors.CYAN)
    
    def endpoint_request(self, method: str, url: str, headers: Dict, data: Optional[Dict] = None):
        """Log request details"""
        if self.level_config.get("show_request", False):
            self.detail("Request Details:")
            self.detail(f"  Method: {method}")
            self.detail(f"  URL: {url}")
            self.detail(f"  Headers: {json.dumps(headers, indent=2)}")
            if data:
                self.detail(f"  Body: {json.dumps(data, indent=2)}")
    
    def endpoint_response(self, status_code: int, response_time: float, response_data: Any):
        """Log response details"""
        if self.level_config.get("show_response", False):
            self.detail("Response Details:")
            self.detail(f"  Status: {status_code}")
            if self.level_config.get("show_timing", False):
                self.detail(f"  Response Time: {response_time*1000:.2f}ms")
            if response_data:
                self.detail(f"  Body: {json.dumps(response_data, indent=2)[:500]}")
    
    def timing(self, operation: str, duration: float):
        """Log timing information"""
        if self.level_config.get("show_timing", False):
            self.detail(f"⏱️  {operation}: {duration*1000:.2f}ms")
    
    def suggestion(self, message: str):
        """Log suggestion for fixing issues"""
        if self.level_config.get("show_suggestions", False):
            self._log("info", f"💡 SUGGESTION: {message}", Colors.MAGENTA)
    
    def check_breakpoint(self, path: str) -> bool:
        """Check if breakpoint is set for this path"""
        if path in self.breakpoints:
            return True
        return False
    
    def pause(self, message: str = "Press Enter to continue..."):
        """Pause execution for interactive debugging"""
        if self.interactive or self.check_breakpoint(""):
            input(f"\n{self._colorize('⏸️  PAUSE: ' + message, Colors.YELLOW)}")
    
    def summary(self, total: int, passed: int, failed: int, duration: float):
        """Log test summary"""
        pass_rate = (passed / total * 100) if total > 0 else 0
        color = Colors.GREEN if pass_rate >= 90 else Colors.YELLOW if pass_rate >= 50 else Colors.RED
        
        self.section("Test Summary")
        self._log("info", f"Total Tests: {total}", Colors.RESET)
        self._log("info", f"Passed: {passed}", Colors.GREEN)
        self._log("info", f"Failed: {failed}", Colors.RED)
        self._log("info", f"Pass Rate: {pass_rate:.2f}%", color)
        self._log("info", f"Duration: {duration:.2f}s", Colors.RESET)
    
    def stack_trace(self, exception: Exception):
        """Log stack trace"""
        if self.level_config.get("show_stack_trace", False):
            import traceback
            self.error(f"Stack Trace:\n{traceback.format_exc()}")


# Global debug instance
_debug_instance: Optional[DebugMode] = None


def get_debug_mode(level: str = "normal") -> DebugMode:
    """Get or create debug mode instance"""
    global _debug_instance
    if _debug_instance is None:
        _debug_instance = DebugMode(level=level)
    return _debug_instance


def set_debug_level(level: str):
    """Set debug level"""
    global _debug_instance
    _debug_instance = DebugMode(level=level)


if __name__ == "__main__":
    # Test debug mode
    debug = DebugMode(level="full")
    debug.section("Debug Mode Test")
    debug.info("This is an info message")
    debug.warning("This is a warning")
    debug.error("This is an error")
    debug.success("This is a success")
    debug.detail("This is a detail")
    debug.timing("Test operation", 0.123)
    debug.suggestion("Try checking the API endpoint")
    debug.summary(100, 85, 15, 45.67)

