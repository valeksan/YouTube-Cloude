#!/usr/bin/env python3
"""Tkinter GUI for YouTube File Storage.

Improvements based on work by @Hinderchik, @IvanSCP, and @sosatel30000.
See: https://github.com/Hinderchik/YouTube-Cloude-Fork
     https://github.com/IvanSCP/YouTube-Cloude
     https://github.com/sosatel30000/YouTube-Cloude
GUI concepts from @Maksim4081862.
"""
from __future__ import annotations

import io
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Optional

# Ensure project modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from encoder import YouTubeEncoder  # noqa: E402
from decoder import YouTubeDecoder  # noqa: E402


# ── Dark theme colours ──────────────────────────────────────────────────────
_BG = '#0d1117'
_BG_SECONDARY = '#161b22'
_BG_TERTIARY = '#21262d'
_FG = '#c9d1d9'
_FG_DIM = '#8b949e'
_ACCENT = '#58a6ff'
_ACCENT_HOVER = '#79c0ff'
_GREEN = '#3fb950'
_RED = '#f85149'
_YELLOW = '#d29922'


class App(tk.Tk):
    """Main application window with tabbed Encode / Decode / Settings."""

    def __init__(self) -> None:
        super().__init__()
        self.title("\U0001f3a5 YouTube File Storage")
        self.geometry("720x620")
        self.minsize(600, 500)
        self.configure(bg=_BG)

        self._apply_theme()
        self._build_ui()

    # ── Theme ───────────────────────────────────────────────────────────
    def _apply_theme(self) -> None:
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('.', background=_BG, foreground=_FG, borderwidth=0)
        style.configure('TNotebook', background=_BG, borderwidth=0)
        style.configure(
            'TNotebook.Tab',
            background=_BG_SECONDARY,
            foreground=_FG_DIM,
            padding=[14, 6],
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', _BG_TERTIARY)],
            foreground=[('selected', _ACCENT)],
        )
        style.configure('TFrame', background=_BG)
        style.configure('TLabel', background=_BG, foreground=_FG)
        style.configure('TButton', background=_BG_TERTIARY, foreground=_FG)
        style.map(
            'TButton',
            background=[('active', _ACCENT)],
            foreground=[('active', _BG)],
        )
        style.configure('TEntry', fieldbackground=_BG_TERTIARY, foreground=_FG)
        style.configure(
            'TProgressbar',
            background=_ACCENT,
            troughcolor=_BG_TERTIARY,
        )

    # ── UI skeleton ─────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.encode_tab = ttk.Frame(notebook)
        self.decode_tab = ttk.Frame(notebook)
        self.settings_tab = ttk.Frame(notebook)

        notebook.add(self.encode_tab, text='  Encode  ')
        notebook.add(self.decode_tab, text='  Decode  ')
        notebook.add(self.settings_tab, text='  Settings  ')

        self._build_encode_tab()
        self._build_decode_tab()
        self._build_settings_tab()

    # ── Encode tab ──────────────────────────────────────────────────────
    def _build_encode_tab(self) -> None:
        frame = self.encode_tab

        ttk.Label(frame, text="Input file:").grid(
            row=0, column=0, sticky='w', padx=8, pady=(10, 2)
        )
        self.enc_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.enc_input_var, width=52).grid(
            row=1, column=0, sticky='we', padx=8
        )
        ttk.Button(frame, text="Browse...", command=self._browse_enc_input).grid(
            row=1, column=1, padx=8
        )

        ttk.Label(frame, text="Output video:").grid(
            row=2, column=0, sticky='w', padx=8, pady=(10, 2)
        )
        self.enc_output_var = tk.StringVar(value='output.mp4')
        ttk.Entry(frame, textvariable=self.enc_output_var, width=52).grid(
            row=3, column=0, sticky='we', padx=8
        )
        ttk.Button(frame, text="Browse...", command=self._browse_enc_output).grid(
            row=3, column=1, padx=8
        )

        self.enc_btn = ttk.Button(
            frame, text="\u25b6  Encode", command=self._start_encode
        )
        self.enc_btn.grid(row=4, column=0, columnspan=2, pady=12)

        self.enc_progress = ttk.Progressbar(
            frame, mode='determinate', length=400
        )
        self.enc_progress.grid(row=5, column=0, columnspan=2, padx=8)

        self.enc_log = scrolledtext.ScrolledText(
            frame,
            height=12,
            bg=_BG_SECONDARY,
            fg=_FG,
            insertbackground=_FG,
            font=('Consolas', 10),
            state='disabled',
        )
        self.enc_log.grid(
            row=6, column=0, columnspan=2, sticky='nsew', padx=8, pady=8
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(6, weight=1)

    # ── Decode tab ──────────────────────────────────────────────────────
    def _build_decode_tab(self) -> None:
        frame = self.decode_tab

        ttk.Label(frame, text="Video file:").grid(
            row=0, column=0, sticky='w', padx=8, pady=(10, 2)
        )
        self.dec_input_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.dec_input_var, width=52).grid(
            row=1, column=0, sticky='we', padx=8
        )
        ttk.Button(frame, text="Browse...", command=self._browse_dec_input).grid(
            row=1, column=1, padx=8
        )

        ttk.Label(frame, text="Output directory:").grid(
            row=2, column=0, sticky='w', padx=8, pady=(10, 2)
        )
        self.dec_output_var = tk.StringVar(value='.')
        ttk.Entry(frame, textvariable=self.dec_output_var, width=52).grid(
            row=3, column=0, sticky='we', padx=8
        )
        ttk.Button(frame, text="Browse...", command=self._browse_dec_output).grid(
            row=3, column=1, padx=8
        )

        self.dec_btn = ttk.Button(
            frame, text="\u25b6  Decode", command=self._start_decode
        )
        self.dec_btn.grid(row=4, column=0, columnspan=2, pady=12)

        self.dec_progress = ttk.Progressbar(
            frame, mode='determinate', length=400
        )
        self.dec_progress.grid(row=5, column=0, columnspan=2, padx=8)

        self.dec_log = scrolledtext.ScrolledText(
            frame,
            height=12,
            bg=_BG_SECONDARY,
            fg=_FG,
            insertbackground=_FG,
            font=('Consolas', 10),
            state='disabled',
        )
        self.dec_log.grid(
            row=6, column=0, columnspan=2, sticky='nsew', padx=8, pady=8
        )

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(6, weight=1)

    # ── Settings tab ────────────────────────────────────────────────────
    def _build_settings_tab(self) -> None:
        frame = self.settings_tab

        ttk.Label(frame, text="Encryption key (optional):").grid(
            row=0, column=0, sticky='w', padx=8, pady=(14, 2)
        )
        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(frame, textvariable=self.key_var, width=50, show='*')
        key_entry.grid(row=1, column=0, sticky='we', padx=8)

        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text='Show',
            variable=self.show_key_var,
            command=lambda: key_entry.config(
                show='' if self.show_key_var.get() else '*'
            ),
        ).grid(row=1, column=1, padx=8)

        info = (
            "The key is hashed with SHA-256 before use.\n"
            "Leave blank to disable encryption.\n\n"
            "Credits:\n"
            "  @Hinderchik  - original concept\n"
            "  @IvanSCP     - improvements\n"
            "  @sosatel30000 - improvements\n"
            "  @Maksim4081862 - GUI concepts"
        )
        ttk.Label(frame, text=info, justify='left').grid(
            row=2, column=0, columnspan=2, sticky='w', padx=12, pady=16
        )

        frame.columnconfigure(0, weight=1)

    # ── File browsers ───────────────────────────────────────────────────
    def _browse_enc_input(self) -> None:
        path = filedialog.askopenfilename(title="Select file to encode")
        if path:
            self.enc_input_var.set(path)

    def _browse_enc_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Save video as",
            defaultextension='.mp4',
            filetypes=[('MP4 video', '*.mp4')],
        )
        if path:
            self.enc_output_var.set(path)

    def _browse_dec_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select video to decode",
            filetypes=[('MP4 video', '*.mp4'), ('All files', '*.*')],
        )
        if path:
            self.dec_input_var.set(path)

    def _browse_dec_output(self) -> None:
        path = filedialog.askdirectory(title="Select output directory")
        if path:
            self.dec_output_var.set(path)

    # ── Logging helpers ─────────────────────────────────────────────────
    def _log(self, widget: scrolledtext.ScrolledText, msg: str) -> None:
        widget.configure(state='normal')
        widget.insert(tk.END, msg + '\n')
        widget.see(tk.END)
        widget.configure(state='disabled')

    def _clear_log(self, widget: scrolledtext.ScrolledText) -> None:
        widget.configure(state='normal')
        widget.delete('1.0', tk.END)
        widget.configure(state='disabled')

    # ── Encode ──────────────────────────────────────────────────────────
    def _start_encode(self) -> None:
        input_file = self.enc_input_var.get().strip()
        output_file = self.enc_output_var.get().strip() or 'output.mp4'
        key = self.key_var.get().strip() or None

        if not input_file:
            messagebox.showwarning("Input needed", "Please select a file to encode.")
            return

        self.enc_btn.configure(state='disabled')
        self._clear_log(self.enc_log)
        self.enc_progress['value'] = 0

        def _worker() -> None:
            try:
                encoder = YouTubeEncoder(key)

                def _cb(done: int, total: int) -> None:
                    pct = int(done / total * 100) if total else 0
                    self.after(0, self._update_enc_progress, pct)

                ok = encoder.encode(input_file, output_file, progress_callback=_cb)
                self.after(
                    0,
                    self._encode_done,
                    ok,
                    output_file if ok else None,
                )
            except Exception as exc:
                self.after(0, self._encode_error, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_enc_progress(self, pct: int) -> None:
        self.enc_progress['value'] = pct
        self._log(self.enc_log, f"  Progress: {pct}%")

    def _encode_done(self, ok: bool, path: Optional[str]) -> None:
        self.enc_btn.configure(state='normal')
        if ok:
            self._log(self.enc_log, f"\nDone! Video saved to: {path}")
            messagebox.showinfo("Encode complete", f"Video saved to:\n{path}")
        else:
            self._log(self.enc_log, "\nEncoding failed.")
            messagebox.showerror("Encode failed", "Encoding failed. See log.")

    def _encode_error(self, msg: str) -> None:
        self.enc_btn.configure(state='normal')
        self._log(self.enc_log, f"\nError: {msg}")
        messagebox.showerror("Error", msg)

    # ── Decode ──────────────────────────────────────────────────────────
    def _start_decode(self) -> None:
        video_file = self.dec_input_var.get().strip()
        output_dir = self.dec_output_var.get().strip() or '.'
        key = self.key_var.get().strip() or None

        if not video_file:
            messagebox.showwarning("Input needed", "Please select a video to decode.")
            return

        self.dec_btn.configure(state='disabled')
        self._clear_log(self.dec_log)
        self.dec_progress['value'] = 0

        def _worker() -> None:
            try:
                decoder = YouTubeDecoder(key)

                def _cb(done: int, total: int) -> None:
                    pct = int(done / total * 100) if total else 0
                    self.after(0, self._update_dec_progress, pct)

                ok = decoder.decode(video_file, output_dir, progress_callback=_cb)
                self.after(0, self._decode_done, ok)
            except Exception as exc:
                self.after(0, self._decode_error, str(exc))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_dec_progress(self, pct: int) -> None:
        self.dec_progress['value'] = pct
        self._log(self.dec_log, f"  Progress: {pct}%")

    def _decode_done(self, ok: bool) -> None:
        self.dec_btn.configure(state='normal')
        if ok:
            self._log(self.dec_log, "\nDecode complete!")
            messagebox.showinfo("Decode complete", "File recovered successfully.")
        else:
            self._log(self.dec_log, "\nDecode incomplete. See log.")
            messagebox.showwarning("Decode", "Decode finished with issues. See log.")

    def _decode_error(self, msg: str) -> None:
        self.dec_btn.configure(state='normal')
        self._log(self.dec_log, f"\nError: {msg}")
        messagebox.showerror("Error", msg)


# ── Entry point ─────────────────────────────────────────────────────────────
def main() -> None:
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()
