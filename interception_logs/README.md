# Example Outputs

This directory contains example outputs from running the call interception system.

## Files

### `example_calls.jsonl`
Raw intercepted API calls (JSONL format - one JSON object per line)
- Request and response pairs
- Timestamps for each call
- Model information
- System prompts and messages

### `example_report.json`
Analysis report generated from intercepted calls
- Summary statistics
- Detected indicators grouped by confidence
- Pattern frequency analysis
- Actionable recommendations

**Generated:** October 16, 2025

---

## Key Results

From the example report:
- **Total Calls:** 6
- **Total Indicators:** 5
- **High Confidence:** 4 indicators
- **Detected Patterns:** Banner formatting, announcement keywords, date references, system messages, version info

---

## Usage

These files demonstrate what the interceptor generates. When you run the script, new files will be created with current dates.

To generate your own results:
```bash
uv run python task_b_call_interceptor.py
```

Outputs:
- `calls_YYYYMMDD.jsonl` - Raw call logs
- `report_YYYYMMDD_HHMMSS.json` - Analysis report
