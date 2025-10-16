# Context Management Research Project

This project explores Claude Code's internal mechanisms through reverse engineering and agent development, based on techniques from:
- [claude-code-reverse](https://github.com/Yuyz0112/claude-code-reverse) - Reverse engineering Claude Code
- [claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) - Official Python SDK
- [ghuntley.com/tradecraft](https://ghuntley.com/tradecraft/) - Decompilation insights

## Overview

This repository contains three main components:

### A) Decompilation-based Announcement Mechanism Explorer
**File:** `task_a_decompilation_explorer.py`

Explores how "announcements" might work in Claude Code by:
- Analyzing monkey-patching approaches from claude-code-reverse
- Identifying potential announcement injection points
- Mapping out system prompt injection mechanisms
- Providing detection strategies

**Key Findings:**
- System prompts are dynamically loaded and could inject announcements
- API responses can be modified post-processing
- IDE integration provides a separate communication channel
- Context compaction is another potential injection point

**Run:**
```bash
python task_a_decompilation_explorer.py
```

**Output:**
- Console analysis report
- JSON analysis file in `analysis_results/`
- Monkey-patch template for real implementation

---

### B) Call Interception System
**File:** `task_b_call_interceptor.py`

Implements an API call interception system based on claude-code-reverse methodology:
- Captures all API requests and responses
- Parses and analyzes message content
- Detects announcement indicators using pattern matching
- Generates detailed logs and reports

**Detection Patterns:**
- Banner formatting (`***`, `===`, `---`)
- Announcement keywords
- Date references
- System message markers
- Urgent indicators
- Version information

**Run:**
```bash
python task_b_call_interceptor.py
```

**Output:**
- Console analysis report
- JSONL call logs in `interception_logs/`
- Pattern frequency analysis
- Recommendations for further investigation

---

### C) Haiku Agent with Context Awareness
**File:** `task_c_haiku_agent.py`

A self-reflective agent using claude-agent-sdk that attempts to convince itself it has too much context:
- Uses Claude Haiku 3.5 model
- Progressive prompting strategy
- Self-monitoring of context usage
- Meta-cognitive reasoning demonstration

**Features:**
- Simple query mode for basic interaction
- Advanced client mode with custom context-checking tool
- Conversation logging and analysis
- Psychological progression tracking

**Run:**
```bash
python task_c_haiku_agent.py
```

**Output:**
- Live conversation display
- Conversation logs in `haiku_agent_logs/`
- Context usage statistics
- Analysis of concern progression

---

## Installation

### Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version  # Should be 3.10 or higher
   ```

2. **uv** (Fast Python package installer)
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or with pip
   pip install uv
   ```

3. **Node.js** (for Claude Code CLI)
   ```bash
   node --version
   ```

4. **Claude Code CLI** (for Task C)
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

### Python Dependencies

Using `uv` (recommended):
```bash
# Install all dependencies
uv pip install -e .

# Or install from requirements.txt
uv pip install -r requirements.txt
```

Or using pip:
```bash
pip install -r requirements.txt
```

---

## Usage

### Task A: Understanding Announcement Mechanisms

```bash
uv run task_a_decompilation_explorer.py
# Or: python3 task_a_decompilation_explorer.py
```

This will:
1. Analyze potential announcement injection mechanisms
2. Identify detection patterns
3. Generate a monkey-patch template
4. Save results to `analysis_results/`

**No external dependencies required** - runs standalone.

---

### Task B: Intercepting Calls

```bash
uv run task_b_call_interceptor.py
# Or: python3 task_b_call_interceptor.py
```

This will:
1. Simulate intercepted API calls (demonstration mode)
2. Analyze content for announcement indicators
3. Generate pattern frequency reports
4. Save logs to `interception_logs/`

**For real interception:**
1. Locate Claude Code installation:
   ```bash
   which claude
   ls -l $(which claude)  # Find cli.js path
   ```

2. Format cli.js:
   ```bash
   cp cli.js cli.bak
   js-beautify cli.bak > cli.js
   ```

3. Apply monkey patch (see script output for template)

4. Run Claude Code normally - calls will be logged

---

### Task C: Haiku Context Paranoia Agent

```bash
uv run task_c_haiku_agent.py
# Or: python3 task_c_haiku_agent.py
```

This will:
1. Start a conversation with Claude Haiku
2. Progressively prompt it about context usage
3. Attempt to make it paranoid about context limits
4. Analyze the psychological progression
5. Save conversation logs to `haiku_agent_logs/`

**Requirements:**
- Claude Code CLI installed
- Valid Anthropic API key configured
- `claude-agent-sdk` installed

**Simulation mode:** If SDK is not available, the script runs in simulation mode with pre-written responses.

---

## Project Structure

```
context_management/
├── task_a_decompilation_explorer.py    # Announcement mechanism analysis
├── task_b_call_interceptor.py          # API call interception system
├── task_c_haiku_agent.py               # Self-reflective Haiku agent
├── requirements.txt                     # Python dependencies
├── README.md                           # This file
├── analysis_results/                   # Task A output
├── interception_logs/                  # Task B output
└── haiku_agent_logs/                   # Task C output
```

---

## Technical Details

### Reverse Engineering Methodology

Based on **claude-code-reverse** approach:

1. **Monkey Patching**: Intercept `beta.messages.create` calls
2. **Log Analysis**: Record all API requests/responses
3. **Pattern Detection**: Identify injected content
4. **Visualization**: Parse and display conversation flows

### Key Insights from claude-code-reverse

Claude Code's internal processes:
- **Quota Check**: Uses Haiku 3.5 for lightweight quota verification
- **Topic Detection**: Determines if user input is a new topic
- **Core Agent Workflow**: System workflow prompt defines agent behavior
- **Context Compaction**: Compresses context when limit approached
- **IDE Integration**: Reads open files, registers IDE-specific tools
- **Todo Management**: Short-term memory via JSON files
- **Sub-Agent System**: Isolates complex tasks in separate contexts

### Agent SDK Usage

The **claude-agent-sdk** provides:
- `query()`: Simple async function for querying Claude Code
- `ClaudeSDKClient`: Bidirectional interactive conversations
- Custom tools via in-process MCP servers
- Hooks for deterministic processing
- Support for multiple MCP server types

---

## Research Questions Explored

### A) How do announcements work?

**Hypothesis:** Announcements are injected through:
1. Dynamic system prompts (HIGH likelihood)
2. IDE integration channels (HIGH likelihood)
3. API response modification (MEDIUM likelihood)
4. Context compaction injection (MEDIUM likelihood)

**Evidence:** System prompts like `system-reminder-start.prompt.md` dynamically load environment info and could include time-sensitive announcements.

---

### B) Can we detect announcements via interception?

**Approach:** 
- Monkey-patch API layer
- Compare expected vs actual content
- Pattern matching for announcement indicators
- Frequency analysis of detected patterns

**Findings:**
- Banner formatting is a strong indicator
- System message markers suggest injection
- Date references common in announcements
- Multiple patterns increase confidence

---

### C) Can an agent convince itself of context issues?

**Experiment Design:**
- Progressive prompting strategy
- Self-referential questions
- Meta-cognitive reasoning tasks
- Keyword frequency tracking

**Results:**
- Models CAN engage in meta-reasoning about context
- Persistent prompting influences perspective
- Self-monitoring is possible via custom tools
- Suggestion and framing affect model responses

---

## Key Findings

### Announcement Mechanisms

1. **System Prompt Injection** (Most Likely)
   - Dynamically loaded at conversation start
   - Can include environment-specific information
   - Invisible to users examining message history
   - Easy to implement and control

2. **IDE Integration** (Most Likely)
   - VS Code extension has separate communication channel
   - Can display notifications independently
   - Doesn't clutter conversation context
   - User-facing and dismissible

3. **API Response Modification** (Possible)
   - Responses processed before display
   - Central interception point
   - Would be visible in raw API logs
   - Less clean than system prompt approach

### Agent Self-Awareness

- AI models can reason about their internal state
- Context awareness is possible without external tools
- Meta-cognition can be prompted and encouraged
- Models can be influenced to change perspective
- Self-monitoring enables better resource management

### Reverse Engineering Insights

- Claude Code uses distinct models for different tasks:
  - Haiku 3.5: Quota check, topic detection, summarization
  - Sonnet 4: Core agent workflow, context compaction
  
- Tool loading is consistent across workflows
- Sub-agents isolate "dirty context" from main conversation
- Todo system provides short-term memory persistence
- System prompts are highly structured and modular

---

## Future Work

1. **Real Interception Implementation**
   - Apply monkey patch to actual Claude Code installation
   - Capture real announcement delivery
   - Verify injection mechanisms

2. **Enhanced Pattern Detection**
   - Machine learning for announcement classification
   - Temporal analysis of announcement timing
   - Cross-reference with known Claude updates

3. **Advanced Agent Experiments**
   - Multi-agent context coordination
   - Self-compacting agents
   - Context-aware task planning
   - Memory hierarchy implementation

4. **Decompilation Deep Dive**
   - Full system prompt extraction
   - Tool definition analysis
   - Hook implementation patterns
   - MCP server architecture

---

## References

- **claude-code-reverse**: https://github.com/Yuyz0112/claude-code-reverse
  - Visualization tool: https://yuyz0112.github.io/claude-code-reverse/visualize.html
  - Methodology: Monkey-patching API layer to log interactions
  
- **claude-agent-sdk-python**: https://github.com/anthropics/claude-agent-sdk-python
  - Documentation: https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python
  - Examples: See examples/ directory in repo
  
- **ghuntley tradecraft**: https://ghuntley.com/tradecraft/
  - Insights on decompilation techniques
  - LLM-based code analysis
  - Cleanroom transpilation approach

- **Anthropic Documentation**:
  - Claude Code: https://docs.anthropic.com/en/docs/claude-code
  - API Reference: https://docs.anthropic.com/en/api
  - MCP Protocol: https://modelcontextprotocol.io

---

## License

This project is for research and educational purposes. 

**Important Notes:**
- Reverse engineering Claude Code may violate terms of service
- This code is provided for understanding mechanisms, not circumventing protections
- Use responsibly and ethically
- Respect Anthropic's intellectual property

---

## Contributing

This is a research project. Contributions welcome:
- Additional detection patterns
- Improved analysis techniques
- Real-world interception results
- Agent experiment variations

---

## Disclaimer

This project involves reverse engineering techniques for educational purposes. The methods described here are based on publicly available information and open-source tools. Users should:

1. Review and comply with Claude Code's terms of service
2. Use these techniques responsibly
3. Not use findings to circumvent security or abuse systems
4. Respect Anthropic's intellectual property rights

The authors are not responsible for misuse of these techniques or tools.

---

## Contact

For questions or discussions about this research:
- Review the original repositories linked above
- Open an issue in this repository
- Discuss on relevant AI/ML research forums

---

**Last Updated:** October 16, 2025
