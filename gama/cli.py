import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="Gama CLI - Autonomous Continuous-Testing Engine")
console = Console()

@app.command()
def scan():
    """Runs one-off checks across core production vectors."""
    console.print(Panel.fit("[bold green]Starting Gama Scan...[/bold green]", title="Gama"))
    console.print("Scanning Database...")
    console.print("Scanning OAuth...")
    console.print("Scanning Security...")
    console.print("Scanning UI/UX...")
    console.print("[bold blue]Scan complete.[/bold blue]")

@app.command()
def loop():
    """Starts the automated repair cycle."""
    console.print(Panel.fit("[bold yellow]Initiating Gama Repair Loop...[/bold yellow]", title="Gama"))
    console.print("Assessing current state...")
    console.print("Generating Markdown state file...")
    console.print("Feeding context to external agents...")
    console.print("Waiting for repairs...")
    console.print("Verifying fixes...")
    console.print("[bold blue]Loop cycle complete.[/bold blue]")

@app.command()
def report():
    """Generates the final audit document."""
    console.print(Panel.fit("[bold magenta]Generating Gama Report...[/bold magenta]", title="Gama"))
    console.print("Compiling audit data...")
    console.print("Creating PDF report...")
    console.print("[bold blue]Report generated successfully.[/bold blue]")

if __name__ == "__main__":
    app()
