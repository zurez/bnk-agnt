"""
HTML Report Generator for DeepEval Results.

Generates a styled HTML report from JSON evaluation results.

Usage:
    python evaluations/scripts/generate_report.py
    python evaluations/scripts/generate_report.py --latest
    python evaluations/scripts/generate_report.py --file results/dev_eval_*.json
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add backend directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluations.config import eval_config


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evaluation Report - {timestamp}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e4e4e4;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .subtitle {{ color: #888; margin-bottom: 2rem; }}
        .card {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .card h2 {{
            font-size: 1.4rem;
            color: #667eea;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat {{
            background: rgba(102, 126, 234, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.25rem;
        }}
        .stat-label {{ color: #aaa; font-size: 0.85rem; }}
        
        .metric-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .metric-stat {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1rem;
            border-left: 4px solid;
        }}
        .metric-stat.high {{ border-color: #4ade80; }}
        .metric-stat.medium {{ border-color: #fbbf24; }}
        .metric-stat.low {{ border-color: #f87171; }}
        .metric-stat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .metric-stat-name {{ font-weight: 600; color: #e4e4e4; }}
        .metric-stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        .metric-stat.high .metric-stat-value {{ color: #4ade80; }}
        .metric-stat.medium .metric-stat-value {{ color: #fbbf24; }}
        .metric-stat.low .metric-stat-value {{ color: #f87171; }}
        
        .test-case {{
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.2s;
        }}
        .test-case:hover {{
            background: rgba(255, 255, 255, 0.04);
            border-color: rgba(102, 126, 234, 0.3);
        }}
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
            gap: 1rem;
        }}
        .test-name {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #667eea;
            flex: 1;
        }}
        .test-status {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}
        .badge {{
            padding: 0.35rem 0.85rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge.pass {{ background: rgba(74, 222, 128, 0.2); color: #4ade80; }}
        .badge.fail {{ background: rgba(248, 113, 113, 0.2); color: #f87171; }}
        
        .io-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1rem;
        }}
        .io-box {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 0.75rem;
        }}
        .io-label {{
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .io-content {{
            color: #e4e4e4;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        .io-content.empty {{
            color: #f87171;
            font-style: italic;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 0.75rem;
        }}
        .metric {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            padding: 0.85rem;
            border-left: 3px solid;
        }}
        .metric.pass {{ border-color: #4ade80; }}
        .metric.fail {{ border-color: #f87171; }}
        .metric-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .metric-name {{
            font-weight: 600;
            font-size: 0.9rem;
            color: #e4e4e4;
        }}
        .score {{
            font-size: 1.1rem;
            font-weight: 700;
        }}
        .metric.pass .score {{ color: #4ade80; }}
        .metric.fail .score {{ color: #f87171; }}
        .metric-reason {{
            font-size: 0.85rem;
            color: #aaa;
            line-height: 1.4;
            margin-top: 0.5rem;
        }}
        
        .context {{
            background: rgba(102, 126, 234, 0.1);
            border-radius: 8px;
            padding: 0.75rem;
            margin-top: 1rem;
        }}
        .context-label {{
            font-size: 0.75rem;
            color: #667eea;
            text-transform: uppercase;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }}
        .context-items {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .context-item {{
            background: rgba(102, 126, 234, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.8rem;
            color: #a5b4fc;
        }}
        
        footer {{
            text-align: center;
            color: #666;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        @media (max-width: 768px) {{
            .io-section {{
                grid-template-columns: 1fr;
            }}
            .metrics {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 Evaluation Report</h1>
        <p class="subtitle">Generated: {timestamp}</p>
        
        {content}
        
        <footer>
            Generated by DeepEval HTML Reporter • {model_name}
        </footer>
    </div>
</body>
</html>
"""


def parse_test_results(results_str: str) -> List[Dict[str, Any]]:
    """Parse the test_results string to extract structured data."""
    test_cases = []
    
    # Use regex to extract TestResult objects
    pattern = r"TestResult\(name='([^']+)', success=(True|False), metrics_data=\[(.*?)\], conversational=(True|False), multimodal=(True|False), input='([^']*(?:\\'[^']*)*)', actual_output='([^']*(?:\\'[^']*)*)', expected_output='([^']*(?:\\'[^']*)*)', context=(\[.*?\]), retrieval_context=(None|\[.*?\])"
    
    # Split by TestResult to handle each separately
    test_result_chunks = results_str.split("TestResult(")[1:]
    
    for chunk in test_result_chunks:
        try:
            # Extract basic fields
            name_match = re.search(r"name='([^']+)'", chunk)
            success_match = re.search(r"success=(True|False)", chunk)
            input_match = re.search(r"input='([^']*(?:\\'[^']*)*)'", chunk)
            actual_match = re.search(r"actual_output='([^']*(?:\\'[^']*)*)'", chunk)
            expected_match = re.search(r"expected_output='([^']*(?:\\'[^']*)*)'", chunk)
            context_match = re.search(r"context=(\[.*?\])", chunk)
            
            if name_match and success_match:
                test_case = {
                    "name": name_match.group(1),
                    "success": success_match.group(1) == "True",
                    "input": input_match.group(1) if input_match else "",
                    "actual_output": actual_match.group(1) if actual_match else "",
                    "expected_output": expected_match.group(1) if expected_match else "",
                    "context": eval(context_match.group(1)) if context_match else [],
                    "metrics": []
                }
                
                # Extract metrics
                metrics_pattern = r"MetricData\(name='([^']+)', threshold=([\d.]+), success=(True|False), score=([\d.]+), reason=\\*\"([^\"]*(?:\\\\\"[^\"]*)*)\""
                for metric_match in re.finditer(metrics_pattern, chunk):
                    metric = {
                        "name": metric_match.group(1),
                        "threshold": float(metric_match.group(2)),
                        "success": metric_match.group(3) == "True",
                        "score": float(metric_match.group(4)),
                        "reason": metric_match.group(5).replace("\\\\'", "'").replace("\\\\n", "\n")
                    }
                    test_case["metrics"].append(metric)
                
                test_cases.append(test_case)
        except Exception as e:
            print(f"Warning: Failed to parse test case chunk: {e}")
            continue
    
    return test_cases


def calculate_metric_summaries(test_cases: List[Dict]) -> Dict[str, Dict]:
    """Calculate pass rates for each metric across all test cases."""
    metric_stats = {}
    
    for test_case in test_cases:
        for metric in test_case.get("metrics", []):
            name = metric["name"]
            if name not in metric_stats:
                metric_stats[name] = {
                    "total": 0,
                    "passed": 0,
                    "avg_score": 0,
                    "scores": []
                }
            
            metric_stats[name]["total"] += 1
            if metric["success"]:
                metric_stats[name]["passed"] += 1
            metric_stats[name]["scores"].append(metric["score"])
    
    # Calculate averages
    for name, stats in metric_stats.items():
        if stats["scores"]:
            stats["avg_score"] = sum(stats["scores"]) / len(stats["scores"])
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100
    
    return metric_stats


def generate_single_report(result_file: Path) -> tuple[str, str]:
    """Generate HTML content for a single result file."""
    with open(result_file) as f:
        data = json.load(f)
    
    model = data.get("model", "Unknown")
    num_cases = data.get("num_test_cases", 0)
    results_str = data.get("results", "")
    timestamp = data.get("timestamp", "Unknown")
    
    # Parse test results
    test_cases = parse_test_results(results_str)
    
    # Calculate overall stats
    passed_tests = sum(1 for tc in test_cases if tc["success"])
    failed_tests = num_cases - passed_tests
    pass_rate = (passed_tests / num_cases * 100) if num_cases > 0 else 0
    
    # Calculate metric summaries
    metric_summaries = calculate_metric_summaries(test_cases)
    
    # Generate metric summary cards
    metric_summary_html = ""
    for metric_name, stats in metric_summaries.items():
        pass_rate_val = stats["pass_rate"]
        color_class = "high" if pass_rate_val >= 70 else "medium" if pass_rate_val >= 40 else "low"
        
        metric_summary_html += f"""
            <div class="metric-stat {color_class}">
                <div class="metric-stat-header">
                    <div class="metric-stat-name">{metric_name}</div>
                </div>
                <div class="metric-stat-value">{pass_rate_val:.0f}%</div>
                <div class="stat-label">{stats['passed']}/{stats['total']} passed • Avg: {stats['avg_score']:.2f}</div>
            </div>
        """
    
    # Generate test case cards
    test_cases_html = ""
    for tc in test_cases:
        status_badge = "pass" if tc["success"] else "fail"
        status_text = "PASS" if tc["success"] else "FAIL"
        
        # Input/Output section
        io_html = f"""
            <div class="io-section">
                <div class="io-box">
                    <div class="io-label">Input</div>
                    <div class="io-content">{tc['input'] or '<i>No input</i>'}</div>
                </div>
                <div class="io-box">
                    <div class="io-label">Expected Output</div>
                    <div class="io-content">{tc['expected_output'] or '<i>No expected output</i>'}</div>
                </div>
            </div>
            <div class="io-box">
                <div class="io-label">Actual Output</div>
                <div class="io-content {'empty' if not tc['actual_output'] else ''}">{tc['actual_output'] or '(empty - no response generated)'}</div>
            </div>
        """
        
        # Metrics section
        metrics_html = ""
        for metric in tc["metrics"]:
            metric_status = "pass" if metric["success"] else "fail"
            score_pct = metric["score"] * 100
            threshold_pct = metric["threshold"] * 100
            
            metrics_html += f"""
                <div class="metric {metric_status}">
                    <div class="metric-header">
                        <span class="metric-name">{metric['name']}</span>
                        <span class="score">{score_pct:.0f}%</span>
                    </div>
                    <div class="stat-label">Threshold: {threshold_pct:.0f}%</div>
                    <div class="metric-reason">{metric['reason']}</div>
                </div>
            """
        
        # Context section
        context_html = ""
        if tc.get("context"):
            context_items = "".join([f'<div class="context-item">{ctx}</div>' for ctx in tc["context"]])
            context_html = f"""
                <div class="context">
                    <div class="context-label">Context</div>
                    <div class="context-items">{context_items}</div>
                </div>
            """
        
        test_cases_html += f"""
            <div class="test-case">
                <div class="test-header">
                    <div class="test-name">{tc['name']}</div>
                    <div class="test-status">
                        <span class="badge {status_badge}">{status_text}</span>
                    </div>
                </div>
                {io_html}
                <div class="metrics">
                    {metrics_html}
                </div>
                {context_html}
            </div>
        """
    
    content = f"""
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{num_cases}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #4ade80;">{passed_tests}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #f87171;">{failed_tests}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat">
                <div class="stat-value">{pass_rate:.0f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 Metric Performance</h2>
            <div class="metric-summary">
                {metric_summary_html}
            </div>
        </div>
        
        <div class="card">
            <h2>🧪 Test Cases</h2>
            {test_cases_html}
        </div>
    """
    
    return content, model


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report from evaluation results")
    parser.add_argument("--latest", action="store_true", help="Use latest result files")
    parser.add_argument("--file", type=str, help="Specific result file to use")
    
    args = parser.parse_args()
    
    results_dir = Path(eval_config.results_dir)
    
    if args.file:
        result_file = Path(args.file)
    else:
        # Find latest result file
        json_files = sorted(results_dir.glob("*.json"), key=os.path.getmtime, reverse=True)
        if not json_files:
            print("❌ No result files found in", results_dir)
            return
        result_file = json_files[0]
    
    if not result_file.exists():
        print(f"❌ Result file not found: {result_file}")
        return
    
    print(f"📄 Processing: {result_file.name}")
    
    # Generate content
    content, model_name = generate_single_report(result_file)
    
    # Generate HTML
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = HTML_TEMPLATE.format(timestamp=timestamp, content=content, model_name=model_name)
    
    # Save report
    report_file = results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, "w") as f:
        f.write(html)
    
    print(f"✅ Report generated: {report_file}")
    print(f"📂 Open in browser: file://{report_file.absolute()}")


if __name__ == "__main__":
    main()
