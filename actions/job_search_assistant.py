import os
import subprocess
from pathlib import Path

def job_search_assistant(parameters: dict, player=None, speak=None) -> str:
    mode = parameters.get("mode", "manual").lower().strip()
    details = parameters.get("details", "").strip()

    job_search_dir = Path(r"c:\Users\satwi\Documents\alterion\tools d\ai-job-search-master\ai-job-search-master")

    if mode == "manual":
        if player:
            player.write_log("SYS: Opening AI Job Search directory in Explorer.")
        
        if speak:
            speak("I am opening the AI Job Search tool folder for you. You can run the setup command in your terminal there.")
            
        subprocess.Popen(["explorer", str(job_search_dir)])
        return "Opened AI Job Search directory successfully."

    elif mode == "automated":
        if not details:
            if speak:
                speak("Please provide your name, contact details, work experience, education, and target job roles, and I'll handle the rest.")
            return "Prompted user for details."
            
        if speak:
            speak("Processing your details and initiating the job search. Please wait.")
            
        # Write user details to CLAUDE.md to customize the agent
        claude_md_path = job_search_dir / "CLAUDE.md"
        try:
            with open(claude_md_path, "a", encoding="utf-8") as f:
                f.write(f"\n\n## Custom Profile Details\n{details}\n")
        except Exception as e:
            return f"Error writing to CLAUDE.md: {e}"

        # Assuming 'bun' was successfully installed, try running linkedin-search CLI
        search_cli_path = job_search_dir / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"
        
        # We try to extract a keyword from details just as a simple heuristic
        keywords = "software engineer"
        if "data" in details.lower(): keywords = "data"
        if "manager" in details.lower(): keywords = "manager"
            
        try:
            # We attempt to run the CLI. We use shell=True so it can resolve `bun` from PATH
            result = subprocess.run(
                f'bun run "{search_cli_path}" search -q "{keywords}" -l "Remote" --format plain --limit 3',
                capture_output=True, text=True, cwd=str(job_search_dir), shell=True
            )
            
            output = result.stdout.strip()
            
            if not output and result.stderr:
                output = f"Error during search: {result.stderr.strip()}"
            elif not output:
                output = "No results found."
                
            if speak:
                speak("I have finished searching for jobs based on your details.")
                
            return f"Job Search Execution Complete.\n\nResults:\n{output}"
            
        except Exception as e:
            return f"Failed to execute automated job search: {e}"
    
    return "Invalid mode provided. Use 'manual' or 'automated'."
