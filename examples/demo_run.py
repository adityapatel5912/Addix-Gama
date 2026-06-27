import sys
import os
from pathlib import Path

# Ensure the root directory is in the path to import gama
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gama.loop import StateManager, get_default_evaluators, generate_state_markdown

def run_custom_pipeline(target_directory: str):
    print(f"Starting custom Gama pipeline for target: {target_directory}")

    # 1. Instantiate the StateManager
    state_manager = StateManager()

    # 2. Get the core evaluation vectors (Security, DB, OAuth, UI/UX, etc.)
    evaluators = get_default_evaluators()

    # 3. Run the evaluation loop to produce the Pydantic StateContext
    state_context = state_manager.run(evaluators=evaluators, target_dir=target_directory)

    # 4. Output the results
    print(f"Overall Status: {state_context.overall_status}")
    print(f"Pass/Fail: {state_context.summary.passed}/{state_context.summary.failed}")

    # 5. Programmatically utilize the state (e.g., feed to an LLM chain)
    if state_context.overall_status != "PASSED":
        print("\nFailures detected. Generating Agent Prompt Context...")
        prompt_context = generate_state_markdown(state_context)
        # In a real pipeline, you would pass `prompt_context` to an LLM via LangChain/LlamaIndex
        print(f"\n[Preview of Agent Context]\n{prompt_context[:300]}...\n")
    else:
         print("\nCodebase is pristine. No agent repair loop necessary.")

if __name__ == "__main__":
    target = "."
    if len(sys.argv) > 1:
        target = sys.argv[1]
    run_custom_pipeline(target)
