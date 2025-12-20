# Debug Mode Guide

**Version**: 1.0.0  
**Last Updated**: 2025-12-16

---

## Overview

Debug mode provides comprehensive debugging capabilities for acceptance testing, including verbose logging, step-by-step execution, and interactive debugging.

---

## Debug Levels

### Minimal
- Shows only errors and summary
- Use for: Quick checks, CI/CD pipelines

### Normal (Default)
- Shows errors, warnings, and summary
- Use for: Regular testing, development

### Detailed
- Shows all above + request/response details
- Use for: Troubleshooting specific issues

### Full
- Shows everything + step-by-step execution + timing
- Use for: Deep debugging, complex issues

---

## Usage

### Basic Usage

```bash
# Run tests with default debug level (normal)
python3 run_tests_with_auth.py

# Run with specific debug level
python3 run_tests_with_auth.py --debug-level detailed

# Run with full debug mode
python3 run_tests_with_auth.py --debug-level full
```

### Debug Specific Endpoint

```bash
# Debug a specific endpoint
python3 run_tests_with_auth.py --debug-endpoint /api/client/dashboard

# Debug a specific module
python3 run_tests_with_auth.py --debug-module auth
```

### Interactive Debugging

```bash
# Enable interactive mode
python3 run_tests_with_auth.py --interactive

# Set breakpoints
python3 run_tests_with_auth.py --breakpoint /api/auth/login
```

---

## Debug Tools

### 1. Endpoint Inspector

Inspect endpoints in detail:

```python
from debug_tools.endpoint_inspector import EndpointInspector

inspector = EndpointInspector(api_url="http://localhost:8000")
result = inspector.inspect("GET", "/api/health")
inspector.print_inspection(result)
```

**Output**:
- Request details (method, URL, headers, body)
- Response details (status, body, timing)
- Analysis (issues, suggestions)

### 2. Payload Validator

Validate request payloads:

```python
from debug_tools.payload_validator import PayloadValidator

validator = PayloadValidator()
result = validator.validate("/api/auth/login", {
    "email": "test@example.com",
    "password": "Test123!"
}, "POST")

print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print(f"Suggestions: {result['suggestions']}")
```

### 3. Error Analyzer

Analyze test errors:

```python
from debug_tools.error_analyzer import ErrorAnalyzer

analyzer = ErrorAnalyzer()
analysis = analyzer.analyze(test_results)
analyzer.print_analysis(analysis)
```

**Output**:
- Error breakdown by status code
- Common issues
- Recommendations

---

## Debug Configuration

Edit `debug_config.json` to customize debug behavior:

```json
{
  "default_level": "normal",
  "color_output": true,
  "log_to_file": true,
  "log_file": "reports/acceptance/debug/debug.log",
  "breakpoints": ["/api/auth/login"],
  "auto_retry": {
    "enabled": true,
    "max_retries": 3
  }
}
```

---

## Debug Output

### Console Output

Debug mode provides color-coded console output:
- 🔴 Red: Errors
- 🟡 Yellow: Warnings
- 🔵 Blue: Info
- 🟢 Green: Success
- ⚪ Gray: Details

### Log Files

Debug logs are saved to:
- `reports/acceptance/debug/debug.log` - Main debug log
- `reports/acceptance/debug/endpoint_inspections.json` - Endpoint inspections
- `reports/acceptance/debug/error_analysis.json` - Error analysis

---

## Common Debugging Scenarios

### Scenario 1: Endpoint Returns 404

```bash
# 1. Inspect the endpoint
python3 -m debug_tools.endpoint_inspector --endpoint /api/test

# 2. Check if path is correct
python3 endpoint_verifier.py

# 3. Fix path in config
python3 scripts/fix_endpoint_paths.py
```

### Scenario 2: Authentication Fails

```bash
# 1. Check auth token
python3 -m debug_tools.endpoint_inspector \
  --endpoint /api/client/dashboard \
  --headers '{"Authorization": "Bearer <token>"}'

# 2. Fix auth issues
python3 scripts/fix_auth_issues.py

# 3. Verify token refresh
python3 scripts/fix_auth_issues.py --test-refresh
```

### Scenario 3: Validation Error (422)

```bash
# 1. Validate payload
python3 -m debug_tools.payload_validator \
  --endpoint /api/auth/register \
  --payload test_data/endpoint_payloads.json

# 2. Check error details
python3 run_tests_with_auth.py --debug-level detailed \
  --debug-endpoint /api/auth/register
```

### Scenario 4: Slow Response Times

```bash
# 1. Run with timing enabled
python3 run_tests_with_auth.py --debug-level full

# 2. Check response times in results
python3 -c "
import json
with open('reports/acceptance/test_results/latest.json') as f:
    data = json.load(f)
    times = [r['response_time'] for r in data['results'] if r.get('response_time')]
    print(f'Avg: {sum(times)/len(times):.2f}s')
    print(f'Max: {max(times):.2f}s')
"
```

---

## Tips & Best Practices

1. **Start with Normal Level**: Use normal level first, then increase if needed
2. **Use Breakpoints**: Set breakpoints for endpoints you're debugging
3. **Check Logs**: Review log files for detailed information
4. **Use Tools**: Leverage inspector, validator, and analyzer tools
5. **Save Results**: Always save debug results for later analysis

---

## Troubleshooting

### Debug mode not working?
- Check `debug_config.json` exists and is valid
- Verify debug level is set correctly
- Check log file permissions

### No color output?
- Set `color_output: true` in config
- Check terminal supports colors
- Use `--no-color` to disable if needed

### Interactive mode not responding?
- Ensure stdin is available
- Check for background processes
- Try running in foreground

---

## Examples

See `examples/` directory for more examples:
- `examples/debug_single_endpoint.py`
- `examples/debug_module.py`
- `examples/debug_with_breakpoints.py`

