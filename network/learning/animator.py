"""Generic terminal animation engine for the 'Learning Network' protocol demos.

Renders packets travelling between two endpoints and step-by-step narration,
using Rich Live rendering. No packets are sent over a real interface unless
the caller explicitly opts in (see scapy_demos.maybe_send).
"""
import time
from rich.console import Console, Group
from rich.text import Text
from rich.panel import Panel
from rich import box

ARROW_STYLES = {
    "send": ("green", "-->"),
    "request": ("green", "-->"),
    "recv": ("yellow", "<--"),
    "response": ("yellow", "<--"),
    "info": ("blue", "---"),
}


def _render_wire(pos, width, marker, direction, left, right, style):
    if direction in ("send", "request"):
        bar = "-" * pos + marker + "-" * (width - pos)
    else:
        bar = "-" * (width - pos) + marker + "-" * pos
    line = Text()
    line.append(f"{left:<8}", style="bold cyan")
    line.append(" [")
    line.append(bar, style=style)
    line.append("] ")
    line.append(f"{right:>8}", style="bold magenta")
    return line


def animate_packet_crossing(console: Console, packet_summary: str, direction: str = "send",
                             left: str = "Client", right: str = "Server", width: int = 28,
                             delay: float = 0.02):
    """Animate a packet marker moving across the 'wire' with Rich Live."""
    from rich.live import Live
    style, _ = ARROW_STYLES.get(direction, ARROW_STYLES["info"])
    marker = "#" if direction in ("send", "request") else "*"
    with Live(console=console, refresh_per_second=40, transient=True) as live:
        for pos in range(width + 1):
            wire = _render_wire(pos, width, marker, direction, left, right, style)
            sub = Text(f"  {packet_summary}", style="dim italic")
            live.update(Group(wire, sub))
            time.sleep(delay)


def _safe_print(console, text):
    """Degrade to ASCII on legacy consoles that can't encode some characters."""
    try:
        console.print(text)
    except UnicodeEncodeError:
        console.print(text.encode("ascii", "replace").decode("ascii"))


def run_flow(console: Console, title: str, steps: list, left: str = "Client",
             right: str = "Server", delay: float = 0.55):
    """Play a full protocol flow: a list of step dicts with keys:
    - label: short text describing the step
    - detail: optional longer explanation
    - direction: 'send' | 'recv' | 'request' | 'response' | 'info'
    - packet_summary: optional text describing the simulated packet/frame
    """
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]", box=box.ROUNDED, border_style="cyan"))
    filters = sorted({step.get("wireshark_filter") for step in steps if step.get("wireshark_filter")})
    if filters:
        console.print("[bold yellow]Wireshark display filter:[/bold yellow] " + " | ".join(filters))
    total = len(steps)
    for i, step in enumerate(steps, 1):
        label = step.get("label", "")
        detail = step.get("detail")
        direction = step.get("direction", "info")
        packet_summary = step.get("packet_summary")

        _safe_print(console, f"[dim][{i}/{total}][/dim] [bold white]{label}[/bold white]")
        if packet_summary:
            if direction in ("send", "recv", "request", "response"):
                animate_packet_crossing(console, packet_summary, direction, left, right)
            arrow_style, arrow = ARROW_STYLES.get(direction, ARROW_STYLES["info"])
            _safe_print(console, f"    [{arrow_style}]{arrow} {packet_summary}[/{arrow_style}]")
        if detail:
            _safe_print(console, f"    [dim italic]{detail}[/dim italic]")
        time.sleep(delay)
    console.print("[bold green]OK - Demo finished / Demo concluida / Demo zaversheno[/bold green]\n")
