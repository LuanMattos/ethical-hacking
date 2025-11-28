"""
gui.py

Interface Tkinter que exibe um gráfico de barras (matplotlib) atualizando
a cada segundo com as contagens de protocolos.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Import capture local module (assume execução a partir da raiz do projeto)
import capture

REFRESH_MS = 1000  # intervalo de atualização em milissegundos

class ProtocolVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simple Scanner — Network Protocol Visualizer")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Figura matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Controles
        ctrl_frame = ttk.Frame(self)
        ctrl_frame.pack(fill=tk.X)
        self.start_stop_btn = ttk.Button(ctrl_frame, text="Stop Sniffing", command=self.toggle_sniffer)
        self.start_stop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        self.clear_btn = ttk.Button(ctrl_frame, text="Clear Counts", command=self.clear_counts)
        self.clear_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self._sniffing = True
        self._after_id = None
        self._update_plot()  # inicia loop de atualização

    def toggle_sniffer(self):
        if self._sniffing:
            capture.stop_sniff()
            self._sniffing = False
            self.start_stop_btn.config(text="Start Sniffing")
        else:
            capture.start_sniff()
            self._sniffing = True
            self.start_stop_btn.config(text="Stop Sniffing")

    def clear_counts(self):
        capture.clear_counts()
        self._redraw({})

    def _redraw(self, counts_dict):
        self.ax.clear()
        if not counts_dict:
            self.ax.text(0.5, 0.5, "No packets yet", ha="center", va="center")
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            items = sorted(counts_dict.items(), key=lambda kv: kv[1], reverse=True)
            names = [k for k, v in items]
            vals = [v for k, v in items]
            bars = self.ax.bar(names, vals, color="tab:blue")
            self.ax.set_xlabel("Protocol Layer")
            self.ax.set_ylabel("Count")
            self.ax.set_xticklabels(names, rotation=45, ha="right")
            # anotar barras
            for bar, v in zip(bars, vals):
                self.ax.text(bar.get_x() + bar.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=8)
            self.fig.tight_layout()
        self.canvas.draw_idle()

    def _update_plot(self):
        counts = capture.get_counts()
        self._redraw(counts)
        self._after_id = self.after(REFRESH_MS, self._update_plot)

    def _on_close(self):
        if messagebox.askokcancel("Quit", "Stop sniffing and quit?"):
            try:
                if self._after_id:
                    self.after_cancel(self._after_id)
            except Exception:
                pass
            capture.stop_sniff()
            self.destroy()