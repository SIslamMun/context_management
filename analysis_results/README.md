# Example Outputs

This directory contains example outputs from running the context management experiments.

## Files

### `example_output.json`
Output from **Task A: Decompilation Explorer**
- Analysis of announcement mechanisms
- Likelihood ratings for each mechanism
- Detection patterns and strategies
- Generated: October 16, 2025

**Key Findings:**
- System Prompt Injection: HIGH likelihood
- IDE Integration Channel: HIGH likelihood
- API Response Modification: MEDIUM likelihood
- Context Compaction Injection: MEDIUM likelihood
- Tool Result Injection: LOW likelihood

---

## Usage

These files demonstrate what the analysis tools generate. When you run the scripts, new files will be created with current timestamps.

To generate your own results:
```bash
uv run python task_a_decompilation_explorer.py
```

New output will be saved as `announcement_analysis_YYYYMMDD_HHMMSS.json`
