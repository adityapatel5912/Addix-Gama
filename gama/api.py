import sys
import json
from gama.loop import run_loop, StateManager, generate_state_markdown, write_state_file, get_default_evaluators
from gama.reporter import generate_audit_report

def handle_command(command, args):
    try:
        evaluators = get_default_evaluators()

        if command == "scan":
            state_manager = StateManager()
            state_context = state_manager.run(evaluators)
            markdown_content = generate_state_markdown(state_context)
            write_state_file(markdown_content)
            return {"status": "success", "message": "Scan complete", "state_file": "gama_state.md"}

        elif command == "loop":
            target_dir = args.get("target_dir", ".")
            run_loop(target_dir, evaluators)
            return {"status": "success", "message": "Loop cycle complete"}

        elif command == "report":
            state_manager = StateManager()
            state_context = state_manager.run(evaluators)
            report_file = args.get("report_file", "gama_audit_report.pdf")
            generate_audit_report(state_context, report_file)
            return {"status": "success", "message": "Report generated successfully", "report_file": report_file}

        else:
            return {"status": "error", "message": f"Unknown command: {command}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
            command = req.get("command")
            args = req.get("args", {})

            result = handle_command(command, args)

            # Send result back via stdout
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError:
            err = {"status": "error", "message": "Invalid JSON format"}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
