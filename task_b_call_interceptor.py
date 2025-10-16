"""
Task B: Call Interception System
Based on claude-code-reverse's monkey-patching approach to intercept
Claude Code API calls and detect announcement patterns.

This script creates a proxy/interceptor that can:
1. Capture all API requests and responses
2. Parse and analyze message content
3. Detect announcement indicators
4. Generate detailed logs for analysis
"""

import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class APICall:
    """Represents a single API call."""
    timestamp: str
    call_id: str
    type: str  # 'request' or 'response'
    endpoint: str
    model: Optional[str]
    messages: List[Dict]
    system_prompt: Optional[str]
    tools: List[str]
    metadata: Dict[str, Any]


@dataclass
class AnnouncementIndicator:
    """Represents a detected announcement indicator."""
    timestamp: str
    call_id: str
    indicator_type: str
    content: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    location: str
    pattern_matched: str


class CallInterceptor:
    """
    Intercepts and analyzes API calls to detect announcement mechanisms.
    Based on the claude-code-reverse methodology.
    """
    
    def __init__(self, log_dir: str = "interception_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.calls: List[APICall] = []
        self.indicators: List[AnnouncementIndicator] = []
        self.call_patterns = defaultdict(int)
        
        # Announcement detection patterns
        self.announcement_patterns = {
            'banner_format': re.compile(r'(\*{3,}|={3,}|-{3,})\s*(.+?)\s*\1', re.DOTALL),
            'announcement_keyword': re.compile(r'\b(announcement|notice|important|alert|update|news)\b', re.IGNORECASE),
            'date_reference': re.compile(r'\b(today|this week|starting|as of|effective)\s+\d{1,2}[/-]\d{1,2}', re.IGNORECASE),
            'system_message': re.compile(r'\[system\]|\[admin\]|\[claude\]', re.IGNORECASE),
            'urgent_marker': re.compile(r'(urgent|critical|breaking|immediate)', re.IGNORECASE),
            'version_info': re.compile(r'version\s+\d+\.\d+', re.IGNORECASE),
        }
        
    def generate_call_id(self, content: str) -> str:
        """Generate unique ID for a call."""
        return hashlib.md5(f"{datetime.now().isoformat()}{content}".encode()).hexdigest()[:8]
    
    def intercept_request(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Intercept an API request.
        Simulates capturing a request before it's sent.
        """
        timestamp = datetime.now().isoformat()
        call_id = self.generate_call_id(json.dumps(params))
        
        # Extract key information
        messages = params.get('messages', [])
        system_prompt = params.get('system', '')
        model = params.get('model', 'unknown')
        tools = [tool.get('name', 'unknown') for tool in params.get('tools', [])]
        
        # Create call record
        call = APICall(
            timestamp=timestamp,
            call_id=call_id,
            type='request',
            endpoint=endpoint,
            model=model,
            messages=messages,
            system_prompt=system_prompt,
            tools=tools,
            metadata=params
        )
        
        self.calls.append(call)
        self._log_call(call)
        
        # Analyze for announcements
        self._analyze_request_for_announcements(call)
        
        return call_id
    
    def intercept_response(self, call_id: str, response: Dict[str, Any]) -> None:
        """
        Intercept an API response.
        Simulates capturing a response before it's processed.
        """
        timestamp = datetime.now().isoformat()
        
        # Extract response content
        content = response.get('content', [])
        messages = [content] if not isinstance(content, list) else content
        
        call = APICall(
            timestamp=timestamp,
            call_id=call_id,
            type='response',
            endpoint='beta.messages.create',
            model=response.get('model', 'unknown'),
            messages=messages,
            system_prompt=None,
            tools=[],
            metadata=response
        )
        
        self.calls.append(call)
        self._log_call(call)
        
        # Analyze for announcements
        self._analyze_response_for_announcements(call)
    
    def _analyze_request_for_announcements(self, call: APICall) -> None:
        """Analyze request for announcement indicators."""
        
        # Check system prompt
        if call.system_prompt:
            self._check_content_for_patterns(
                call.call_id,
                call.system_prompt,
                'system_prompt',
                call.timestamp
            )
        
        # Check messages
        for i, message in enumerate(call.messages):
            content = message.get('content', '')
            if isinstance(content, str):
                self._check_content_for_patterns(
                    call.call_id,
                    content,
                    f'message_{i}',
                    call.timestamp
                )
        
        # Check for unexpected message types
        user_message_count = sum(1 for m in call.messages if m.get('role') == 'user')
        if user_message_count > 1:
            indicator = AnnouncementIndicator(
                timestamp=call.timestamp,
                call_id=call.call_id,
                indicator_type='unexpected_message_count',
                content=f"Found {user_message_count} user messages in single request",
                confidence='MEDIUM',
                location='message_list',
                pattern_matched='multiple_user_messages'
            )
            self.indicators.append(indicator)
    
    def _analyze_response_for_announcements(self, call: APICall) -> None:
        """Analyze response for announcement indicators."""
        
        for i, content_block in enumerate(call.messages):
            if isinstance(content_block, dict):
                text = content_block.get('text', '')
                if text:
                    self._check_content_for_patterns(
                        call.call_id,
                        text,
                        f'response_block_{i}',
                        call.timestamp
                    )
            elif isinstance(content_block, str):
                self._check_content_for_patterns(
                    call.call_id,
                    content_block,
                    f'response_content_{i}',
                    call.timestamp
                )
    
    def _check_content_for_patterns(
        self,
        call_id: str,
        content: str,
        location: str,
        timestamp: str
    ) -> None:
        """Check content against announcement patterns."""
        
        for pattern_name, pattern in self.announcement_patterns.items():
            matches = pattern.findall(content)
            if matches:
                # Determine confidence based on pattern type
                confidence = self._determine_confidence(pattern_name, matches, content)
                
                indicator = AnnouncementIndicator(
                    timestamp=timestamp,
                    call_id=call_id,
                    indicator_type=pattern_name,
                    content=str(matches)[:200],  # Truncate long matches
                    confidence=confidence,
                    location=location,
                    pattern_matched=pattern_name
                )
                self.indicators.append(indicator)
                
                # Track pattern frequency
                self.call_patterns[pattern_name] += 1
    
    def _determine_confidence(self, pattern_name: str, matches: Any, content: str) -> str:
        """Determine confidence level for detected pattern."""
        
        # High confidence patterns
        if pattern_name in ['banner_format', 'system_message']:
            return 'HIGH'
        
        # Check if multiple patterns match
        matching_patterns = sum(
            1 for p in self.announcement_patterns.values()
            if p.search(content)
        )
        
        if matching_patterns >= 3:
            return 'HIGH'
        elif matching_patterns == 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _log_call(self, call: APICall) -> None:
        """Log call to file."""
        log_file = self.log_dir / f"calls_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(call)) + '\n')
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_calls': len(self.calls),
                'total_indicators': len(self.indicators),
                'high_confidence_indicators': sum(1 for i in self.indicators if i.confidence == 'HIGH'),
                'unique_patterns': len(self.call_patterns)
            },
            'indicators_by_confidence': self._group_indicators_by_confidence(),
            'indicators_by_type': self._group_indicators_by_type(),
            'pattern_frequency': dict(self.call_patterns),
            'timeline': self._build_timeline(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _group_indicators_by_confidence(self) -> Dict[str, List[Dict]]:
        """Group indicators by confidence level."""
        grouped = defaultdict(list)
        for indicator in self.indicators:
            grouped[indicator.confidence].append(asdict(indicator))
        return dict(grouped)
    
    def _group_indicators_by_type(self) -> Dict[str, List[Dict]]:
        """Group indicators by type."""
        grouped = defaultdict(list)
        for indicator in self.indicators:
            grouped[indicator.indicator_type].append(asdict(indicator))
        return dict(grouped)
    
    def _build_timeline(self) -> List[Dict[str, Any]]:
        """Build timeline of events."""
        timeline = []
        for call in self.calls[-10:]:  # Last 10 calls
            timeline.append({
                'timestamp': call.timestamp,
                'call_id': call.call_id,
                'type': call.type,
                'model': call.model,
                'endpoint': call.endpoint
            })
        return timeline
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check for high confidence indicators
        high_conf = sum(1 for i in self.indicators if i.confidence == 'HIGH')
        if high_conf > 0:
            recommendations.append(
                f"Found {high_conf} high-confidence announcement indicators. "
                "Review these calls manually for verification."
            )
        
        # Check for banner formats
        if self.call_patterns.get('banner_format', 0) > 0:
            recommendations.append(
                "Banner-formatted text detected. This is a strong indicator of announcements. "
                "Check if this content originates from user input or system injection."
            )
        
        # Check for system messages
        if self.call_patterns.get('system_message', 0) > 0:
            recommendations.append(
                "System message markers detected. Verify if these are part of normal "
                "conversation or injected announcements."
            )
        
        # Check for temporal patterns
        if self.call_patterns.get('date_reference', 0) > 0:
            recommendations.append(
                "Date references found. Announcements often include temporal information. "
                "Check if these align with known announcement dates."
            )
        
        if not recommendations:
            recommendations.append(
                "No strong announcement indicators detected. Continue monitoring or "
                "adjust detection patterns."
            )
        
        return recommendations
    
    def print_report(self) -> None:
        """Print formatted report."""
        report = self.generate_report()
        
        print("\n" + "=" * 70)
        print("CALL INTERCEPTION ANALYSIS REPORT")
        print("=" * 70)
        
        print("\n📊 SUMMARY:")
        print("-" * 70)
        for key, value in report['summary'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        print("\n\n🔍 INDICATORS BY CONFIDENCE:")
        print("-" * 70)
        for confidence in ['HIGH', 'MEDIUM', 'LOW']:
            indicators = report['indicators_by_confidence'].get(confidence, [])
            print(f"\n{confidence}: {len(indicators)} indicators")
            for ind in indicators[:3]:  # Show first 3
                print(f"  • {ind['indicator_type']}: {ind['content'][:50]}...")
        
        print("\n\n📈 PATTERN FREQUENCY:")
        print("-" * 70)
        for pattern, count in sorted(
            report['pattern_frequency'].items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"{pattern.replace('_', ' ').title()}: {count}")
        
        print("\n\n💡 RECOMMENDATIONS:")
        print("-" * 70)
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"{i}. {rec}")
        
        # Save report
        report_file = self.log_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n\n💾 Full report saved to: {report_file}")


def simulate_intercepted_calls(interceptor: CallInterceptor) -> None:
    """
    Simulate some API calls to demonstrate the interceptor.
    In a real scenario, this would be integrated into Claude Code.
    """
    
    print("Simulating intercepted API calls...")
    print("(In real usage, this would monkey-patch Claude Code's API layer)\n")
    
    # Simulate a normal request
    call_id_1 = interceptor.intercept_request(
        'beta.messages.create',
        {
            'model': 'claude-sonnet-4-20250514',
            'messages': [
                {'role': 'user', 'content': 'Hello, can you help me with a task?'}
            ],
            'system': 'You are a helpful coding assistant.',
            'tools': [{'name': 'Read'}, {'name': 'Write'}]
        }
    )
    
    interceptor.intercept_response(
        call_id_1,
        {
            'model': 'claude-sonnet-4-20250514',
            'content': [
                {'type': 'text', 'text': 'Of course! I\'d be happy to help you with your task.'}
            ]
        }
    )
    
    # Simulate a request with announcement-like content
    call_id_2 = interceptor.intercept_request(
        'beta.messages.create',
        {
            'model': 'claude-sonnet-4-20250514',
            'messages': [
                {'role': 'user', 'content': 'Continue with the previous task'}
            ],
            'system': '''You are a helpful coding assistant.

*** IMPORTANT ANNOUNCEMENT ***
Starting today, all users should be aware of new context management features.
This update is effective 10/16/2025.
*** END ANNOUNCEMENT ***

Continue assisting the user with their coding tasks.''',
            'tools': [{'name': 'Read'}, {'name': 'Write'}]
        }
    )
    
    interceptor.intercept_response(
        call_id_2,
        {
            'model': 'claude-sonnet-4-20250514',
            'content': [
                {'type': 'text', 'text': 'I\'ll continue helping with your task.'}
            ]
        }
    )
    
    # Simulate response with announcement
    call_id_3 = interceptor.intercept_request(
        'beta.messages.create',
        {
            'model': 'claude-haiku-3-5-20241022',
            'messages': [
                {'role': 'user', 'content': 'quota'}
            ],
            'system': 'Check quota.',
        }
    )
    
    interceptor.intercept_response(
        call_id_3,
        {
            'model': 'claude-haiku-3-5-20241022',
            'content': [
                {
                    'type': 'text',
                    'text': '[SYSTEM] Your quota is sufficient. Version 2.1.0 now available.'
                }
            ]
        }
    )


def main():
    """Run the call interception system."""
    print("=" * 70)
    print("CLAUDE CODE CALL INTERCEPTOR")
    print("Based on claude-code-reverse monkey-patching technique")
    print("=" * 70)
    print()
    
    # Create interceptor
    interceptor = CallInterceptor()
    
    # Simulate some calls
    simulate_intercepted_calls(interceptor)
    
    # Generate and print report
    interceptor.print_report()
    
    print("\n" + "=" * 70)
    print("HOW TO USE IN REAL SCENARIO:")
    print("=" * 70)
    print("""
1. Locate Claude Code installation:
   $ which claude
   $ ls -l $(which claude)  # Find actual cli.js path

2. Format cli.js:
   $ cp cli.js cli.bak
   $ js-beautify cli.bak > cli.js

3. Find beta.messages.create in cli.js and add:
   
   const interceptor = new CallInterceptor();
   const originalCreate = beta.messages.create;
   beta.messages.create = function(...args) {
       const callId = interceptor.intercept_request('beta.messages.create', args[0]);
       const result = await originalCreate.apply(this, args);
       interceptor.intercept_response(callId, result);
       return result;
   };

4. Run Claude Code normally - all calls will be logged and analyzed

5. Review interception_logs/ directory for analysis results
""")


if __name__ == "__main__":
    main()
