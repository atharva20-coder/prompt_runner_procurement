"""Automated Chat Log Analyzer

Reads a generated chat log and uses the LiteLLMProvider to critically evaluate 
it against the SVP2 Collections and Prompt Engineer skills.
Outputs a markdown report mapping suggested optimizations directly to the source script files.
"""

import argparse
import glob
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path to import main app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing application modules
from config_loader import load_config
from litellm_provider import LiteLLMProvider

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def get_latest_log_file(log_dir: str = "logs") -> str:
    """Finds the most recently modified .md file in the logs directory."""
    try:
        files = glob.glob(os.path.join(log_dir, "*.md"))
        if not files:
            raise FileNotFoundError(f"No markdown files found in {log_dir}/")
        # Sort lexicographically since filenames have timestamps in ISO format
        return sorted(files)[-1]
    except Exception as e:
        logging.error(f"Failed to find latest log: {e}")
        raise

def read_directory_contents(dir_path: str, ext: str = ".md") -> str:
    """Reads all files with a specific extension in a directory and concatenates their contents."""
    content = ""
    if not os.path.exists(dir_path):
        logging.warning(f"Directory {dir_path} does not exist.")
        return content
        
    for filename in os.listdir(dir_path):
        if filename.endswith(ext) or ext == "*":
            filepath = os.path.join(dir_path, filename)
            if os.path.isfile(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content += f"\n\n--- FILE: {filepath} ---\n\n"
                        content += f.read()
                except Exception as e:
                    logging.warning(f"Could not read {filepath}: {e}")
    return content

def generate_analysis_prompt(log_content: str, skills_context: str, scripts_context: str) -> str:
    """Constructs the master prompt for the LLM to process the log."""
    return f"""You are a Lead Prompt Engineer & System Architect (as defined in your skills profile).
Your task is to critically analyze a recent Agent-Customer chat log from the Orchestrator stage.

You must evaluate the agent's performance strictly against the SVP2 Collections Agent Skill specifications AND the Prompt Engineering constraints.

### The Objective
1. Identify systemic failures or behavioral breakdown (e.g., lack of empathy, robotic looping, premature anchoring, failure to verify identity).
2. Point out specific instances in the log where the agent violated the RBI compliance or LARA framework.
3. Suggest EXACT optimizations required. 
4. CRITICAL: You must map these optimizations exactly to the targeted prompt script files provided in the context below. You must reference the specific file path (e.g., `scripts/Recovery_stage_prompt.md` or `scripts/Intro_stage_prompt.md`) where the logic or instructions need to be fixed.
5. Do NOT output a new, fully rewritten file. DO output the specific rules, zero-shot constraints, or tactical instructions that the human engineer needs to ADD or MODIFY in those specific files.

### 1. SKILLS & PLAYBOOK CONTEXT (How the agent SHOULD behave)
{skills_context}

### 2. EXISTING SCRIPTS/PROMPTS CONTEXT (The current instructions running the agent)
{scripts_context}

### 3. THE CHAT LOG TO ANALYZE
{log_content}

### OUTPUT FORMAT
Provide a highly professional, structured Markdown report.
Include sections for:
- **Executive Summary**
- **Critical Violations (RBI, LARA, Negotiation)**
- **Prompt Engineering Optimization Plan (MAPPED TO EXACT FILES)** -> list the exact file paths and the text/rules that need to be injected into them.
"""

def main(log_file: str | None = None, config_path: str = "config.yaml"):
    """Run analysis. Can be called directly or imported.

    Args:
        log_file: Specific log file to analyze. If None, uses latest in logs/.
        config_path: Path to config file.
    """
    # When run standalone, parse CLI args
    if log_file is None and len(sys.argv) > 1 and sys.argv[0].endswith("run_analysis.py"):
        parser = argparse.ArgumentParser(description="Automated Chat Log Analyzer")
        parser.add_argument("--log", "-l", type=str, help="Specific log file path")
        parser.add_argument("--config", "-c", type=str, default="config.yaml")
        args = parser.parse_args()
        log_file = args.log
        config_path = args.config

    setup_logging()
    logger = logging.getLogger("Analyzer")

    # 1. Load config and Setup LLM
    logger.info(f"Loading config from {config_path}...")
    config = load_config(config_path)
    provider = LiteLLMProvider(
        model=config.llm.model,
        api_key=config.llm.api_key,
        api_base=config.llm.api_base,
        temperature=config.llm.temperature,
        reasoning_effort=config.llm.reasoning_effort,
        extra_params=config.llm.extra_params,
    )

    # 2. Determine target log file
    target_log = log_file if log_file else get_latest_log_file()
    logger.info(f"Target log file: {target_log}")

    with open(target_log, "r", encoding="utf-8") as f:
        log_content = f.read()

    # 3. Gather Context
    logger.info("Gathering Context from team/ and scripts/ directories...")
    skills_context = read_directory_contents("team", ext=".md")
    scripts_context = read_directory_contents("scripts", ext=".md")

    # 4. Generate the Prompt
    logger.info("Generating LLM evaluation prompt...")
    prompt = generate_analysis_prompt(log_content, skills_context, scripts_context)
    
    messages = [
        {"role": "system", "content": "You are a master Prompt Engineer & AI Architect. Your output is deep, highly structured, and actionable."},
        {"role": "user", "content": prompt}
    ]

    # 5. Execute LLM Call
    logger.info(f"Executing LLM Analysis using model {config.llm.model}...")
    try:
        response = provider.chat(messages=messages)
        # Handle LiteLLM response object
        analysis_result = response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM Call failed: {e}")
        return

    # 6. Save Report
    os.makedirs("analyzer", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_filename = f"analyzer/analysis_{timestamp}.md"
    
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(f"# Automated Log Analysis Report\n")
        f.write(f"**Log Evaluated:** `{target_log}`\n")
        f.write(f"**Date Analyzed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model Used:** `{config.llm.model}`\n\n")
        f.write("---\n\n")
        f.write(analysis_result)

    logger.info(f"✅ Analysis complete! Report saved to: {report_filename}")

if __name__ == "__main__":
    main()
