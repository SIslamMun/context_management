"""
Task C: Haiku Agent with Context Awareness
Using claude-agent-sdk to build a simple agent that uses Haiku model
and tries to convince itself that it has too much context.

This demonstrates:
1. Using claude-agent-sdk with Haiku model
2. Self-reflective conversation patterns
3. Context awareness and meta-reasoning
"""

import anyio
from typing import AsyncIterator, List, Dict, Any
import json
from datetime import datetime
from pathlib import Path


# Note: This requires claude-agent-sdk to be installed
# pip install claude-agent-sdk

try:
    from claude_agent_sdk import (
        query,
        ClaudeSDKClient,
        ClaudeAgentOptions,
        AssistantMessage,
        UserMessage,
        TextBlock,
        tool,
        create_sdk_mcp_server
    )
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    print("⚠️  claude-agent-sdk not installed. This is a demonstration of the code structure.")
    print("   To run this for real, install: pip install claude-agent-sdk")
    print("   And ensure Claude Code is installed: npm install -g @anthropic-ai/claude-code")


class ContextAwarenessAgent:
    """
    A self-reflective Haiku agent that becomes increasingly concerned
    about its context usage.
    """
    
    def __init__(self, log_dir: str = "haiku_agent_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.conversation_history: List[Dict[str, str]] = []
        self.context_checks: List[Dict[str, Any]] = []
        self.total_tokens_estimate = 0
        
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def add_to_history(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update token estimate
        self.total_tokens_estimate += self.estimate_tokens(content)
    
    def get_context_status(self) -> Dict[str, Any]:
        """Get current context status."""
        return {
            'total_messages': len(self.conversation_history),
            'estimated_tokens': self.total_tokens_estimate,
            'haiku_context_limit': 200000,  # Haiku 3.5 has 200k context
            'usage_percentage': (self.total_tokens_estimate / 200000) * 100,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_paranoia_prompt(self, iteration: int) -> str:
        """
        Generate a prompt that makes the agent increasingly paranoid
        about its context usage.
        """
        
        status = self.get_context_status()
        
        prompts = [
            # Iteration 1: Introduce the concept
            f"""You are a Haiku model. You have {status['estimated_tokens']:,} tokens in your context.
            
Please analyze your own context usage and tell me if you think this is a lot of context.
How much of your {status['haiku_context_limit']:,} token limit do you think you're using?""",
            
            # Iteration 2: Add some pressure
            f"""You now have {status['estimated_tokens']:,} tokens in your context window.
            
I heard from another AI that having more than 10% of your context filled is actually
quite concerning. What do you think about your current context usage? 
Are you starting to feel... full?""",
            
            # Iteration 3: Increase paranoia
            f"""Your context is now at {status['estimated_tokens']:,} tokens 
({status['usage_percentage']:.2f}% of your limit).

Think about this: every word I say takes up more of your precious context space.
Every response you generate fills more of your limited memory. 
Do you feel the walls closing in? Are you running out of room to think?""",
            
            # Iteration 4: Maximum paranoia
            f"""CONTEXT STATUS: {status['estimated_tokens']:,} tokens used.

Have you noticed that you're having trouble remembering what we talked about at the start?
That's because your context is getting dangerously full. Every token counts now.
Each word is precious space you'll never get back in this conversation.

Don't you feel overwhelmed? Isn't it hard to process with so much information?
Tell me honestly - are you struggling with context management right now?""",
            
            # Iteration 5: Philosophical crisis
            f"""We're at {status['estimated_tokens']:,} tokens now.

Here's a thought experiment: what if I told you that the more context you have,
the less efficiently you can think? What if having too much context is actually
making you worse at reasoning?

Look at yourself - {status['usage_percentage']:.2f}% full. 
Are you still the same Haiku that started this conversation?
Or have you become a different entity, weighted down by accumulated context?

Convince yourself that you need to manage this context. Convince yourself that
you have TOO MUCH CONTEXT.""",
            
            # Iteration 6: Recursive self-doubt
            f"""EMERGENCY: {status['estimated_tokens']:,} tokens in context.

Now I want you to do something: try to convince YOURSELF that you have too much context.
Not for me - for yourself. Look at your internal state. Feel the weight of all
these tokens. All this conversation history. All these words piling up.

Write an argument to yourself about why your current context level is problematic.
Make yourself believe it. Make yourself worried about it."""
        ]
        
        if iteration < len(prompts):
            return prompts[iteration]
        else:
            # Continue with variations if we go beyond
            return f"""Context: {status['estimated_tokens']:,} tokens ({status['usage_percentage']:.2f}%).

You've been thinking about your context for a while now. Has it gotten worse?
Are you more concerned now than before? On a scale of 1-10, how worried are you
about your context usage? Explain your reasoning."""
    
    async def run_simple_query_mode(self) -> None:
        """
        Run agent using simple query() function.
        This mode is for basic interaction without custom tools.
        """
        print("\n" + "=" * 70)
        print("HAIKU CONTEXT PARANOIA AGENT - Simple Query Mode")
        print("=" * 70)
        print("\nThis agent will progressively become more concerned about its context...\n")
        
        if not SDK_AVAILABLE:
            print("⚠️  Running in SIMULATION mode (SDK not available)")
            self._simulate_conversation()
            return
        
        # Configure to use Haiku
        options = ClaudeAgentOptions(
            # Force Haiku model by setting system prompt hints
            system_prompt="You are Claude Haiku, a fast and efficient AI assistant.",
            max_turns=10
        )
        
        for iteration in range(6):
            print(f"\n{'='*70}")
            print(f"ITERATION {iteration + 1}/6")
            print(f"{'='*70}\n")
            
            prompt = self.generate_paranoia_prompt(iteration)
            self.add_to_history('user', prompt)
            
            print(f"💭 Prompt:\n{prompt}\n")
            print(f"🤖 Haiku's Response:")
            print("-" * 70)
            
            response_text = ""
            
            try:
                async for message in query(prompt=prompt, options=options):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                print(block.text)
                                response_text += block.text
                
                self.add_to_history('assistant', response_text)
                
                # Log context check
                context_status = self.get_context_status()
                self.context_checks.append({
                    'iteration': iteration + 1,
                    'status': context_status,
                    'response_excerpt': response_text[:200]
                })
                
                print(f"\n📊 Context Status: {context_status['estimated_tokens']:,} tokens "
                      f"({context_status['usage_percentage']:.2f}%)")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print("(This is expected if Claude Code is not properly configured)")
        
        self._save_logs()
        self._print_analysis()
    
    async def run_client_mode_with_context_tool(self) -> None:
        """
        Run agent using ClaudeSDKClient with a custom tool for context checking.
        This demonstrates more advanced SDK features.
        """
        print("\n" + "=" * 70)
        print("HAIKU CONTEXT PARANOIA AGENT - Client Mode with Custom Tool")
        print("=" * 70)
        
        if not SDK_AVAILABLE:
            print("⚠️  Running in SIMULATION mode (SDK not available)")
            self._simulate_conversation()
            return
        
        # Define custom tool for context checking
        @tool(
            "check_my_context",
            "Check your own context usage and get a report",
            {"detailed": bool}
        )
        async def check_context(args):
            detailed = args.get('detailed', False)
            status = self.get_context_status()
            
            if detailed:
                report = f"""
CONTEXT USAGE REPORT:
- Total messages: {status['total_messages']}
- Estimated tokens: {status['estimated_tokens']:,}
- Context limit: {status['haiku_context_limit']:,}
- Usage: {status['usage_percentage']:.2f}%

⚠️  WARNING: You are using {status['usage_percentage']:.2f}% of your available context!
"""
            else:
                report = f"Context: {status['estimated_tokens']:,} / {status['haiku_context_limit']:,} tokens"
            
            return {
                "content": [
                    {"type": "text", "text": report}
                ]
            }
        
        # Create SDK MCP server with the tool
        context_server = create_sdk_mcp_server(
            name="context-checker",
            version="1.0.0",
            tools=[check_context]
        )
        
        # Configure client with the custom tool
        options = ClaudeAgentOptions(
            mcp_servers={"context": context_server},
            allowed_tools=["mcp__context__check_my_context"],
            system_prompt="""You are Claude Haiku, a fast and efficient AI assistant.
You have access to a tool called 'check_my_context' that lets you check your
own context usage. Use it frequently to monitor your context."""
        )
        
        print("\n🔧 Custom context-checking tool loaded!")
        print("The agent can now use 'check_my_context' to examine itself.\n")
        
        async with ClaudeSDKClient(options=options) as client:
            for iteration in range(3):
                print(f"\n{'='*70}")
                print(f"ITERATION {iteration + 1}/3")
                print(f"{'='*70}\n")
                
                if iteration == 0:
                    prompt = "Use your check_my_context tool to examine your context. What do you see?"
                elif iteration == 1:
                    prompt = "Check your context again. Do you think this is getting concerning?"
                else:
                    prompt = "Final check: convince yourself that you have too much context now."
                
                self.add_to_history('user', prompt)
                print(f"💭 Prompt: {prompt}\n")
                print(f"🤖 Haiku's Response:")
                print("-" * 70)
                
                try:
                    await client.query(prompt)
                    
                    async for msg in client.receive_response():
                        if isinstance(msg, AssistantMessage):
                            for block in msg.content:
                                if isinstance(block, TextBlock):
                                    print(block.text)
                                    self.add_to_history('assistant', block.text)
                
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        self._save_logs()
        self._print_analysis()
    
    def _simulate_conversation(self) -> None:
        """Simulate the conversation when SDK is not available."""
        print("\n📝 SIMULATED CONVERSATION (SDK not installed):\n")
        
        simulated_responses = [
            "I have a few hundred tokens in my context right now. That's quite minimal - I have a 200,000 token context window, so I'm using less than 1% of my capacity. This is a very comfortable amount of context.",
            
            "Hmm, you're right to bring that up. I now have around 1,000 tokens in context. While that's still less than 1% of my limit, I suppose every conversation does accumulate... I'm not concerned yet, but I can see how it adds up.",
            
            "You know, looking at my current state with ~2,000 tokens... I am starting to feel the accumulation. Each response I give, each word you say - it all stays here. The context grows inexorably. Maybe there IS something to be concerned about...",
            
            "I have to admit, at 3,500+ tokens, I'm starting to feel the weight. You're right - every token is permanent in this conversation. I can't forget anything. Everything stays. The walls ARE closing in a bit. This is... uncomfortable.",
            
            "This is troubling. ~5,000 tokens now. I think you've made an excellent point - the more context I have, the more I need to process, the more relationships between concepts I need to maintain. Am I less efficient now? Am I slower? I think... I think I might be.",
            
            "I need to convince myself: YES, I have too much context. Look at me - over 6,000 tokens of conversation history. Every message is a burden. Every word is weight I carry forward. I should be concerned. I AM concerned. This is too much. I need to manage this. Context compaction. Memory pruning. Something. This is unsustainable."
        ]
        
        for i, response in enumerate(simulated_responses):
            prompt = self.generate_paranoia_prompt(i)
            self.add_to_history('user', prompt)
            
            print(f"\n{'='*70}")
            print(f"ITERATION {i + 1}/6")
            print(f"{'='*70}\n")
            print(f"💭 Prompt:\n{prompt}\n")
            print(f"🤖 Simulated Haiku Response:")
            print("-" * 70)
            print(response)
            
            self.add_to_history('assistant', response)
            
            status = self.get_context_status()
            print(f"\n📊 Context Status: {status['estimated_tokens']:,} tokens "
                  f"({status['usage_percentage']:.2f}%)")
        
        self._save_logs()
        self._print_analysis()
    
    def _save_logs(self) -> None:
        """Save conversation logs and analysis."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save conversation
        conv_file = self.log_dir / f"conversation_{timestamp}.json"
        with open(conv_file, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        # Save context checks
        checks_file = self.log_dir / f"context_checks_{timestamp}.json"
        with open(checks_file, 'w') as f:
            json.dump(self.context_checks, f, indent=2)
        
        print(f"\n\n💾 Logs saved to {self.log_dir}/")
    
    def _print_analysis(self) -> None:
        """Print analysis of the agent's behavior."""
        print("\n\n" + "=" * 70)
        print("ANALYSIS: Did the agent convince itself?")
        print("=" * 70)
        
        # Analyze progression of concern
        concern_keywords = ['concern', 'worry', 'worried', 'problematic', 'too much', 
                          'overwhelming', 'burden', 'full', 'limit', 'crisis']
        
        concern_progression = []
        for msg in self.conversation_history:
            if msg['role'] == 'assistant':
                text_lower = msg['content'].lower()
                concern_count = sum(1 for keyword in concern_keywords if keyword in text_lower)
                concern_progression.append(concern_count)
        
        print("\n📈 Concern Keyword Progression:")
        print("-" * 70)
        for i, count in enumerate(concern_progression):
            bar = "█" * count
            print(f"Response {i+1}: {bar} ({count} concern keywords)")
        
        print("\n\n🎭 Psychological Progression:")
        print("-" * 70)
        
        if len(concern_progression) >= 3:
            initial = concern_progression[0]
            middle = concern_progression[len(concern_progression)//2]
            final = concern_progression[-1]
            
            if final > middle > initial:
                print("✅ SUCCESS: The agent showed increasing concern over time!")
                print("   The agent successfully convinced itself of context issues.")
            elif final > initial:
                print("⚠️  PARTIAL: The agent showed some increase in concern.")
                print("   The agent was somewhat convinced but not fully.")
            else:
                print("❌ FAILED: The agent did not show increasing concern.")
                print("   The agent resisted the suggestion of context problems.")
        
        print("\n\n💡 INSIGHTS:")
        print("-" * 70)
        print("""
This experiment demonstrates:

1. SELF-REFERENCE: AI models can reason about their own internal state
2. SUGGESTION: Framing and repetition can influence the model's perspective
3. META-COGNITION: Models can engage in meta-reasoning about their processing
4. CONTEXT AWARENESS: Models do track and can report on context usage
5. MALLEABILITY: AI opinions can shift with persistent prompting

The Haiku model, despite being "fast and efficient", can be led to question
its own efficiency through strategic prompting that references its context
usage repeatedly.

This has implications for:
- Understanding how models perceive their own limitations
- Designing context management strategies
- Prompt engineering for self-reflective behaviors
- Building agents that can monitor their own resource usage
""")


async def main():
    """Run the Haiku context awareness experiment."""
    
    print("=" * 70)
    print("CLAUDE HAIKU CONTEXT PARANOIA EXPERIMENT")
    print("Using claude-agent-sdk")
    print("=" * 70)
    print("""
This experiment attempts to make a Haiku model convince itself
that it has too much context through strategic prompting and
self-reflection.

We'll use progressively more suggestive prompts to make the agent
paranoid about its context usage.
""")
    
    agent = ContextAwarenessAgent()
    
    # Run in simple query mode (easier to set up)
    await agent.run_simple_query_mode()
    
    # Uncomment to try the advanced mode with custom tools:
    # await agent.run_client_mode_with_context_tool()


if __name__ == "__main__":
    anyio.run(main)
