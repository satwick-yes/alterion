import os
import json
import sys
import time
from pathlib import Path

# Ensure the parent directory is in the sys.path so we can import Vani modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from agent.orchestrator import semantic_router
from agent.planner import create_plan

def run_benchmarks():
    benchmarks_path = Path(__file__).parent / "benchmarks.json"
    if not benchmarks_path.exists():
        print(f"Error: Could not find {benchmarks_path}")
        return

    with open(benchmarks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    report = ["# Vani Benchmark Results 🧪\n"]
    report.append("> This report tests Vani's intent routing and tool planning for 100 complex tasks.\n\n")
    
    total_tasks = sum(len(c["tasks"]) for c in data["benchmarks"])
    print(f"🚀 Starting Vani Benchmark Suite ({total_tasks} tasks)...")
    
    for category in data["benchmarks"]:
        cat_name = category['category']
        report.append(f"## {cat_name}\n")
        print(f"\n--- {cat_name} ---")
        
        for idx, task in enumerate(category["tasks"]):
            print(f"[{idx+1}/10] Testing: {task[:50]}...")
            report.append(f"### Task: *\"{task}\"*\n")
            
            try:
                # 1. Test Intent Routing (Which Brain does it go to?)
                companion = semantic_router.route_intent(task)
                report.append(f"- **Routed To**: `{companion.name}`\n")
                
                # 2. Test Planning & Tool Selection (Safety, Logic, Memory)
                # Note: We generate the plan to evaluate the logic, but we intentionally 
                # DO NOT execute it to avoid dangerous operations on the local machine.
                plan = create_plan(task, allowed_tools=companion.allowed_tools)
                steps = plan.get("steps", [])
                
                report.append("- **Generated Plan**:\n")
                if not steps:
                    report.append("  - *Failed to generate a valid plan.*\n")
                else:
                    for s in steps:
                        tool = s.get('tool', 'unknown_tool')
                        desc = s.get('description', '')
                        report.append(f"  - `[{tool}]` {desc}\n")
                        
            except Exception as e:
                report.append(f"- **Error**: `{str(e)}`\n")
                print(f"⚠️ Error on task: {e}")
                
            report.append("\n")
            
            # Pause to respect API rate limits and avoid 429 Too Many Requests errors
            time.sleep(3.5)
            
    report_path = Path(__file__).parent / "benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"\n✅ Benchmark complete! Detailed report saved to: {report_path}")

if __name__ == "__main__":
    print("WARNING: This benchmark takes about 5-10 minutes to run to respect API rate limits.")
    run_benchmarks()
