import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def generate_state_markdown(failures: list[dict]) -> str:
    """
    Generates a beautifully written Markdown state instruction file from a list of failures.
    The output is optimized with descriptive, explicit prompts for external coding agents.
    """
    if not failures:
        return (
            "# Gama State Report\n\n"
            "## ✅ All Systems Go\n\n"
            "No failures detected in the target project. The codebase is currently fully operational and production-ready.\n"
        )

    md = "# 🚨 Gama State Report: System Failures Detected\n\n"
    md += "The following high-criticality bugs and structural gaps were identified during the automated testing phase. "
    md += "External coding agents, please follow the explicit instructions provided below to repair the codebase.\n\n"
    md += "---\n\n"

    for i, failure in enumerate(failures, 1):
        md += f"## Issue {i}: {failure.get('title', 'Unknown Failure')}\n\n"
        md += f"**Category:** {failure.get('category', 'General')}\n"
        md += f"**Severity:** {failure.get('severity', 'High')}\n\n"

        md += "### 📝 Description\n"
        md += f"{failure.get('description', 'No description provided.')}\n\n"

        md += "### 🛠️ Required Action (Instructions for Agent)\n"
        md += f"> {failure.get('instructions', 'Please investigate and fix the issue.')}\n\n"

        if 'file' in failure:
            md += f"**Target File:** `{failure['file']}`\n"
            if 'line' in failure:
                md += f"**Target Line:** {failure['line']}\n"
        md += "\n---\n\n"

    md += "\n## Next Steps\n"
    md += "Once the repairs have been applied, save the files. The Gama loop will automatically detect the changes and re-evaluate the repository.\n"
    return md

def write_state_file(markdown_content: str, file_path: str = "gama_state.md"):
    """
    Writes the generated markdown content to the specified file path.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"State file written to {file_path}")

class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.change_detected = False

    def on_modified(self, event):
        # Ignore changes to the state file itself to avoid infinite loops
        if not event.is_directory and "gama_state.md" not in event.src_path:
            self.change_detected = True

    def on_created(self, event):
        if not event.is_directory and "gama_state.md" not in event.src_path:
            self.change_detected = True

def watch_and_wait(target_dir: str):
    """
    Uses watchdog to monitor the target_dir and blocks execution until a file change is detected.
    """
    print(f"Watching for changes in: {target_dir}")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, target_dir, recursive=True)
    observer.start()

    try:
        while not event_handler.change_detected:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        raise
    finally:
        observer.stop()
        observer.join()

    print("Change detected. Resuming loop...")

def run_loop(target_dir: str, evaluate_fn):
    """
    Implements the continuous testing loop.
    Repeatedly evaluates the project, writes the state file, and waits for changes if there are failures.
    """
    while True:
        print("Evaluating project...")
        failures = evaluate_fn(target_dir)

        markdown_content = generate_state_markdown(failures)
        write_state_file(markdown_content)

        if not failures:
            print("No failures detected. Exiting loop.")
            break

        print("Failures detected. Pausing and waiting for file changes to re-evaluate...")
        watch_and_wait(target_dir)
