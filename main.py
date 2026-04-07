import sys
import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext
import math
import time
import random

# Prevent Windows-specific event loop errors
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ──────────────────────────────────────────────
#  JARVIS AI BACKEND
# ──────────────────────────────────────────────
messages = [{"role": "system", "content": (
    "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), "
    "Tony Stark's AI assistant. Speak with calm confidence, wit, and precision. "
    "Be helpful, slightly formal but personable, and occasionally reference your role "
    "as an advanced AI assistant. Keep responses concise unless detail is needed."
)}]

async def ask_ai(user_input: str) -> str:
    from g4f.client import AsyncClient
    client = AsyncClient()
    messages.append({"role": "user", "content": user_input})
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    answer = response.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    return answer

# ──────────────────────────────────────────────
#  COLORS & CONSTANTS
# ──────────────────────────────────────────────
BG          = "#020b18"
PANEL       = "#041525"
ACCENT      = "#00d4ff"
ACCENT2     = "#0077aa"
ACCENT_DIM  = "#003344"
TEXT_MAIN   = "#cceeff"
TEXT_DIM    = "#336688"
TEXT_USER   = "#00ffcc"
TEXT_AI     = "#00cfff"
GLOW        = "#00d4ff"
RED_WARN    = "#ff3355"
FONT_MONO   = ("Courier New", 11)
FONT_TITLE  = ("Courier New", 13, "bold")
FONT_SMALL  = ("Courier New", 9)

# ──────────────────────────────────────────────
#  ANIMATED ARC REACTOR CANVAS WIDGET
# ──────────────────────────────────────────────
class ArcReactor(tk.Canvas):
    def __init__(self, parent, size=120, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=BG, highlightthickness=0, **kw)
        self.size = size
        self.cx = size / 2
        self.cy = size / 2
        self.angle = 0
        self.pulse = 0
        self.running = True
        self._draw()
        self._animate()

    def _draw(self):
        self.delete("all")
        s = self.size
        cx, cy = self.cx, self.cy
        r_outer = s * 0.46
        r_mid   = s * 0.32
        r_inner = s * 0.18
        r_core  = s * 0.09

        pulse_alpha = int(180 + 75 * math.sin(self.pulse))

        def hex_alpha(base_hex, alpha):
            r = int(base_hex[1:3], 16)
            g = int(base_hex[3:5], 16)
            b = int(base_hex[5:7], 16)
            blend = lambda c: int(c * alpha/255 + 0x02 * (1 - alpha/255))
            return "#{:02x}{:02x}{:02x}".format(blend(r), blend(g), blend(b))

        # Outer glow ring
        glow_r = r_outer + 6 + 3 * math.sin(self.pulse)
        self.create_oval(cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r,
                         outline=hex_alpha("#00d4ff", 60), width=2)
        self.create_oval(cx - glow_r - 4, cy - glow_r - 4,
                         cx + glow_r + 4, cy + glow_r + 4,
                         outline=hex_alpha("#00d4ff", 25), width=1)

        # Outer ring
        self.create_oval(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                         outline=ACCENT, width=2)

        # Rotating segments
        num_segs = 8
        for i in range(num_segs):
            a_start = self.angle + i * (360 / num_segs)
            bright = i % 2 == 0
            color = ACCENT if bright else ACCENT2
            self.create_arc(cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                            start=a_start, extent=360/num_segs - 3,
                            outline=color, style="arc", width=3 if bright else 1)

        # Middle ring static
        self.create_oval(cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                         outline=ACCENT2, width=1)

        # Spokes
        num_spokes = 6
        for i in range(num_spokes):
            angle_r = math.radians(self.angle * 0.5 + i * 60)
            x1 = cx + r_inner * math.cos(angle_r)
            y1 = cy + r_inner * math.sin(angle_r)
            x2 = cx + r_mid * math.cos(angle_r)
            y2 = cy + r_mid * math.sin(angle_r)
            self.create_line(x1, y1, x2, y2, fill=ACCENT, width=1)

        # Inner ring
        self.create_oval(cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
                         outline=ACCENT, width=2)

        # Pulsing core
        pulse_r = r_core * (0.85 + 0.15 * math.sin(self.pulse))
        glow_intensity = hex_alpha("#00d4ff", pulse_alpha)
        self.create_oval(cx - pulse_r * 1.6, cy - pulse_r * 1.6,
                         cx + pulse_r * 1.6, cy + pulse_r * 1.6,
                         fill=hex_alpha("#00d4ff", 40), outline="")
        self.create_oval(cx - pulse_r, cy - pulse_r, cx + pulse_r, cy + pulse_r,
                         fill=glow_intensity, outline=ACCENT, width=1)

        # Corner brackets
        bw = s * 0.08
        for dx, dy, sx, sy in [(0, 0, 1, 1), (s, 0, -1, 1), (0, s, 1, -1), (s, s, -1, -1)]:
            self.create_line(dx, dy, dx + sx * bw, dy, fill=ACCENT, width=1)
            self.create_line(dx, dy, dx, dy + sy * bw, fill=ACCENT, width=1)

    def _animate(self):
        if not self.running:
            return
        self.angle = (self.angle + 2) % 360
        self.pulse += 0.08
        self._draw()
        self.after(33, self._animate)  # ~30 fps

    def stop(self):
        self.running = False


# ──────────────────────────────────────────────
#  SCANNING LINE CANVAS
# ──────────────────────────────────────────────
class ScanLine(tk.Canvas):
    def __init__(self, parent, width=400, height=4, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=BG, highlightthickness=0, **kw)
        self.w = width
        self.h = height
        self.pos = 0
        self.running = True
        self._animate()

    def _animate(self):
        if not self.running:
            return
        self.delete("all")
        # Moving gradient line
        for i in range(self.w):
            dist = abs(i - self.pos)
            alpha = max(0, 1 - dist / 80)
            val = int(alpha * 255)
            color = "#{:02x}{:02x}{:02x}".format(
                min(255, val),
                min(255, int(val * 0.83)),
                min(255, val)
            )
            if val > 10:
                self.create_line(i, 0, i, self.h, fill=color)
        self.pos = (self.pos + 3) % self.w
        self.after(20, self._animate)

    def stop(self):
        self.running = False


# ──────────────────────────────────────────────
#  MAIN JARVIS WINDOW
# ──────────────────────────────────────────────
class JarvisGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("J.A.R.V.I.S.")
        self.root.configure(bg=BG)
        self.root.geometry("900x700")
        self.root.minsize(750, 580)
        self.typing = False
        self._build_ui()
        self._startup_sequence()

    # ── Layout ────────────────────────────────
    def _build_ui(self):
        # Top bar
        top = tk.Frame(self.root, bg=PANEL, height=56)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        self.arc = ArcReactor(top, size=46)
        self.arc.pack(side="left", padx=(14, 8), pady=5)

        title_frame = tk.Frame(top, bg=PANEL)
        title_frame.pack(side="left", pady=6)
        tk.Label(title_frame, text="J.A.R.V.I.S.", font=("Courier New", 16, "bold"),
                 fg=ACCENT, bg=PANEL).pack(anchor="w")
        tk.Label(title_frame,
                 text="Just A Rather Very Intelligent System  ·  ONLINE",
                 font=FONT_SMALL, fg=TEXT_DIM, bg=PANEL).pack(anchor="w")

        self.status_dot = tk.Label(top, text="●", font=("Courier New", 14),
                                   fg="#00ff88", bg=PANEL)
        self.status_dot.pack(side="right", padx=(0, 18))
        tk.Label(top, text="SYS STATUS", font=FONT_SMALL,
                 fg=TEXT_DIM, bg=PANEL).pack(side="right", padx=(0, 4))

        # Scan line separator
        ScanLine(self.root, width=900, height=3).pack(fill="x")

        # Main body
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Left sidebar
        sidebar = tk.Frame(body, bg=PANEL, width=180)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._build_sidebar(sidebar)

        # Chat area
        chat_area = tk.Frame(body, bg=BG)
        chat_area.pack(side="left", fill="both", expand=True)
        self._build_chat(chat_area)

        # Bottom bar
        bottom = tk.Frame(self.root, bg=PANEL, height=28)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        self.footer_var = tk.StringVar(value="READY  ·  ALL SYSTEMS NOMINAL")
        tk.Label(bottom, textvariable=self.footer_var, font=FONT_SMALL,
                 fg=TEXT_DIM, bg=PANEL).pack(side="left", padx=12)
        self.clock_label = tk.Label(bottom, text="", font=FONT_SMALL,
                                    fg=TEXT_DIM, bg=PANEL)
        self.clock_label.pack(side="right", padx=12)
        self._tick_clock()

    def _build_sidebar(self, parent):
        tk.Label(parent, text="[ DIAGNOSTICS ]", font=FONT_SMALL,
                 fg=ACCENT, bg=PANEL).pack(pady=(14, 4), padx=8, anchor="w")

        self.diag_labels = {}
        diags = [
            ("NEURAL NET", "ONLINE"),
            ("MEMORY",     "128 MB"),
            ("UPTIME",     "00:00:00"),
            ("MSGS",       "0"),
            ("LATENCY",    "-- ms"),
        ]
        for key, val in diags:
            row = tk.Frame(parent, bg=PANEL)
            row.pack(fill="x", padx=8, pady=2)
            tk.Label(row, text=key, font=FONT_SMALL, fg=TEXT_DIM,
                     bg=PANEL, width=10, anchor="w").pack(side="left")
            lbl = tk.Label(row, text=val, font=FONT_SMALL, fg=ACCENT,
                           bg=PANEL, anchor="e")
            lbl.pack(side="right")
            self.diag_labels[key] = lbl

        # Separator
        tk.Frame(parent, bg=ACCENT_DIM, height=1).pack(fill="x", padx=8, pady=10)

        tk.Label(parent, text="[ CONTROLS ]", font=FONT_SMALL,
                 fg=ACCENT, bg=PANEL).pack(pady=(0, 6), padx=8, anchor="w")

        btn_cfg = dict(font=FONT_SMALL, bg=ACCENT_DIM, fg=ACCENT,
                       relief="flat", bd=0, cursor="hand2",
                       activebackground=ACCENT, activeforeground=BG, pady=5)

        tk.Button(parent, text="CLEAR HISTORY", command=self._clear_history,
                  **btn_cfg).pack(fill="x", padx=8, pady=2)
        tk.Button(parent, text="EXPORT LOG", command=self._export_log,
                  **btn_cfg).pack(fill="x", padx=8, pady=2)
        tk.Button(parent, text="EXIT", command=self.root.quit,
                  **{**btn_cfg, "fg": RED_WARN}).pack(fill="x", padx=8, pady=2)

        # Mini arc reactor decoration
        mini = ArcReactor(parent, size=80)
        mini.pack(pady=(20, 0))
        tk.Label(parent, text="MARK VII", font=FONT_SMALL,
                 fg=TEXT_DIM, bg=PANEL).pack()

    def _build_chat(self, parent):
        # Chat header strip
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", padx=12, pady=(8, 0))
        tk.Label(hdr, text="▸ COMMUNICATION INTERFACE", font=FONT_SMALL,
                 fg=ACCENT2, bg=BG).pack(side="left")
        self.thinking_label = tk.Label(hdr, text="", font=FONT_SMALL,
                                       fg=ACCENT, bg=BG)
        self.thinking_label.pack(side="right")

        # Chat display
        chat_frame = tk.Frame(parent, bg=ACCENT_DIM, bd=1, relief="flat")
        chat_frame.pack(fill="both", expand=True, padx=12, pady=6)

        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            font=FONT_MONO,
            bg="#010d18",
            fg=TEXT_MAIN,
            insertbackground=ACCENT,
            relief="flat",
            bd=0,
            state="disabled",
            wrap="word",
            padx=12,
            pady=10,
            spacing3=4,
        )
        self.chat_box.pack(fill="both", expand=True)

        # Text tags
        self.chat_box.tag_config("user",    foreground=TEXT_USER)
        self.chat_box.tag_config("ai",      foreground=TEXT_AI)
        self.chat_box.tag_config("system",  foreground=TEXT_DIM, font=FONT_SMALL)
        self.chat_box.tag_config("label_u", foreground=TEXT_USER,
                                  font=("Courier New", 9, "bold"))
        self.chat_box.tag_config("label_a", foreground=ACCENT,
                                  font=("Courier New", 9, "bold"))
        self.chat_box.tag_config("sep",     foreground=ACCENT_DIM)

        # Input area
        inp_frame = tk.Frame(parent, bg=ACCENT_DIM, bd=1, relief="flat")
        inp_frame.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(inp_frame, text="  YOU ▸ ", font=("Courier New", 10, "bold"),
                 fg=TEXT_USER, bg="#010d18").pack(side="left")

        self.entry = tk.Entry(inp_frame, font=FONT_MONO, bg="#010d18",
                              fg=TEXT_USER, insertbackground=TEXT_USER,
                              relief="flat", bd=0)
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.entry.bind("<Return>", self._on_send)
        self.entry.bind("<Up>", self._history_up)
        self.entry.bind("<Down>", self._history_down)
        self.entry.focus()

        send_btn = tk.Button(inp_frame, text="SEND ▶", font=FONT_SMALL,
                             bg=ACCENT2, fg=BG, relief="flat", bd=0,
                             cursor="hand2", padx=10, pady=8,
                             activebackground=ACCENT, activeforeground=BG,
                             command=self._on_send)
        send_btn.pack(side="right")

        self._input_history = []
        self._hist_idx = -1
        self._start_time = time.time()
        self._msg_count = 0
        self._uptime_tick()

    # ── Chat helpers ──────────────────────────
    def _append(self, text, tag="system"):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text, tag)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def _separator(self):
        self._append("─" * 58 + "\n", "sep")

    def _startup_sequence(self):
        lines = [
            ("system", "\n  ╔══════════════════════════════════════════════════╗\n"),
            ("system", "  ║         J.A.R.V.I.S.  BOOT SEQUENCE COMPLETE    ║\n"),
            ("system", "  ╚══════════════════════════════════════════════════╝\n\n"),
            ("system", "  SYSTEM CHECK .......... [ PASS ]\n"),
            ("system", "  NEURAL INTERFACE ........ [ READY ]\n"),
            ("system", "  VOICE CORTEX ............. [ STANDBY ]\n"),
            ("system", "  AI CORE ................... [ ONLINE ]\n\n"),
            ("ai",     "  Good day. All systems are nominal and I am at your\n"
                       "  service. How may I assist you today?\n\n"),
        ]
        def _type(idx=0):
            if idx < len(lines):
                tag, text = lines[idx]
                self._append(text, tag)
                delay = random.randint(60, 160)
                self.root.after(delay, lambda: _type(idx + 1))
        _type()

    def _on_send(self, event=None):
        if self.typing:
            return
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")

        # Input history
        self._input_history.append(text)
        self._hist_idx = -1

        self._msg_count += 1
        self.diag_labels["MSGS"].config(text=str(self._msg_count))

        self._separator()
        self._append("  YOU  ▸  ", "label_u")
        self._append(f"{text}\n\n", "user")

        self.typing = True
        self.status_dot.config(fg="#ffaa00")
        self._start_thinking()

        t_start = time.time()

        def run_ai():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                answer = loop.run_until_complete(ask_ai(text))
            except Exception as e:
                answer = f"[ERROR] {e}"
            finally:
                loop.close()
            elapsed = int((time.time() - t_start) * 1000)
            self.root.after(0, lambda: self._show_response(answer, elapsed))

        threading.Thread(target=run_ai, daemon=True).start()

    def _start_thinking(self):
        self._think_frames = ["PROCESSING ◌", "PROCESSING ◎", "PROCESSING ◉",
                              "PROCESSING ◎", "ANALYSING  ▱", "ANALYSING  ▰"]
        self._think_idx = 0
        self._blink_thinking()

    def _blink_thinking(self):
        if not self.typing:
            self.thinking_label.config(text="")
            return
        self.thinking_label.config(
            text=self._think_frames[self._think_idx % len(self._think_frames)])
        self._think_idx += 1
        self.root.after(300, self._blink_thinking)

    def _show_response(self, answer, elapsed_ms):
        self.typing = False
        self.status_dot.config(fg="#00ff88")
        self.diag_labels["LATENCY"].config(text=f"{elapsed_ms} ms")
        self.footer_var.set(f"LAST QUERY RESOLVED IN {elapsed_ms} ms  ·  READY")

        self._append("  J.A.R.V.I.S.  ▸  ", "label_a")
        self._type_text(answer + "\n\n", "ai")

    def _type_text(self, text, tag, idx=0, chunk=2):
        if idx < len(text):
            self._append(text[idx:idx+chunk], tag)
            self.root.after(18, lambda: self._type_text(text, tag, idx+chunk, chunk))

    # ── History navigation ─────────────────────
    def _history_up(self, event):
        if not self._input_history:
            return
        self._hist_idx = min(self._hist_idx + 1, len(self._input_history) - 1)
        val = self._input_history[-(self._hist_idx + 1)]
        self.entry.delete(0, "end")
        self.entry.insert(0, val)

    def _history_down(self, event):
        if self._hist_idx <= 0:
            self._hist_idx = -1
            self.entry.delete(0, "end")
            return
        self._hist_idx -= 1
        val = self._input_history[-(self._hist_idx + 1)]
        self.entry.delete(0, "end")
        self.entry.insert(0, val)

    # ── Sidebar actions ────────────────────────
    def _clear_history(self):
        global messages
        messages = [messages[0]]  # keep system prompt
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        self._msg_count = 0
        self.diag_labels["MSGS"].config(text="0")
        self._append("\n  [ MEMORY WIPED — CONVERSATION RESET ]\n\n", "system")

    def _export_log(self):
        content = self.chat_box.get("1.0", "end")
        fname = f"jarvis_log_{int(time.time())}.txt"
        try:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(content)
            self._append(f"\n  [ LOG EXPORTED → {fname} ]\n\n", "system")
        except Exception as e:
            self._append(f"\n  [ EXPORT FAILED: {e} ]\n\n", "system")

    # ── Clock & uptime ─────────────────────────
    def _tick_clock(self):
        now = time.strftime("%H:%M:%S")
        self.clock_label.config(text=f"UTC  {now}")
        self.root.after(1000, self._tick_clock)

    def _uptime_tick(self):
        elapsed = int(time.time() - self._start_time)
        h, r = divmod(elapsed, 3600)
        m, s = divmod(r, 60)
        self.diag_labels["UPTIME"].config(text=f"{h:02d}:{m:02d}:{s:02d}")
        self.root.after(1000, self._uptime_tick)


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
def main():
    root = tk.Tk()
    root.configure(bg=BG)

    # Try to make it look nicer on HiDPI screens
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = JarvisGUI(root)

    def on_close():
        app.arc.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    print("Loading J.A.R.V.I.S. interface… please wait.")
    main()
