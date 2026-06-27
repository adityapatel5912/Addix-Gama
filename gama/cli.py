import typer
from rich.console import Console
from rich.panel import Panel
from gama.loop import run_loop, StateManager, generate_state_markdown, write_state_file, get_default_evaluators
from gama.reporter import generate_audit_report

app = typer.Typer(help="Gama CLI - Autonomous Continuous-Testing Engine")
console = Console()

@app.command()
def scan(target: str = typer.Option(".", "--target", help="Target directory to scan")):
    """Runs one-off checks across core production vectors."""
    console.print(Panel.fit("[bold green]Starting Gama Scan...[/bold green]", title="Gama"))
    console.print("Scanning Database...")
    console.print("Scanning OAuth...")
    console.print("Scanning Security...")
    console.print("Scanning UI/UX...")

    evaluators = get_default_evaluators()

    state_manager = StateManager()
    state_context = state_manager.run(evaluators, target_dir=target)

    markdown_content = generate_state_markdown(state_context)
    write_state_file(markdown_content)

    console.print("[bold blue]Scan complete.[/bold blue]")

@app.command()
def loop():
    """Starts the automated repair cycle."""
    console.print(Panel.fit("[bold yellow]Initiating Gama Repair Loop...[/bold yellow]", title="Gama"))
    console.print("Assessing current state...")

    evaluators = get_default_evaluators()
    run_loop(".", evaluators)

    console.print("[bold blue]Loop cycle complete.[/bold blue]")

@app.command()
def report(state: str = typer.Option("gama_state.md", "--state", help="State markdown file"), output: str = typer.Option("gama_audit_report.pdf", "--output", help="Output PDF file"), target: str = typer.Option(".", "--target", help="Target directory to report")):
    """Generates the final audit document."""
    console.print(Panel.fit("[bold magenta]Generating Gama Report...[/bold magenta]", title="Gama"))
    console.print("Compiling audit data...")

    evaluators = get_default_evaluators()

    state_manager = StateManager()
    state_context = state_manager.run(evaluators, target_dir=target)

    # Pass the Pydantic StateContext model directly
    generate_audit_report(state_context, output)

    console.print("Creating PDF report...")
    console.print("[bold blue]Report generated successfully.[/bold blue]")

def main():
    app()

if __name__ == "__main__":
    main()
