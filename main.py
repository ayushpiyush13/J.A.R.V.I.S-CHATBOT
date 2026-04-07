import tkinter as tk
from tkinter import scrolledtext
import threading
import math
import time
from g4f.client import Client

# ── CONFIG ──────────────────────────────────────────────────────────────────
BG        = "#0a0f1a"
PANEL     = "#0d1525"
ACCENT    = "#00d4ff"
ACCENT2   = "#0066ff"
DIM       = "#1a2a3a"
TEXT_USER = "#00d4ff"
TEXT_BOT  = "#e0f7ff"
TEXT_DIM  = "#3a5a7a"
FONT_MAIN = ("Consolas", 12)
FONT_BIG  = ("Consolas", 22, "bold")
FONT_MED  = ("Consolas", 10)

client = Client()

# ── MAIN WINDOW ──────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("J.A.R.V.I.S")
root.geometry("900x700")
root.configure(bg=BG)
root.resizable(True, True)

# ── CANVAS (animated rings) ───────────────────────────────────────────────────
canvas = tk.Canvas(root, width=900, height=120, bg=BG, highlightthickness=0)
canvas.pack(fill="x")

# ── TITLE ────────────────────────────────────────────────────────────────────
title_frame = tk.Frame(root, bg=BG)
title_frame.place(x=0, y=0, width=900, height=120)

tk.Label(title_frame, text="J.A.R.V.I.S", font=FONT_BIG,
         bg=BG, fg=ACCENT).place(relx=0.5, rely=0.35, anchor="center")
tk.Label(title_frame,
         text="Just A Rather Very Intelligent System",
         font=FONT_MED, bg=BG, fg=TEXT_DIM).place(relx=0.5, rely=0.65, anchor="center")

# ── DIVIDER ───────────────────────────────────────────────────────────────────
div = tk.Frame(root, bg=ACCENT, height=1)
div.pack(fill="x", padx=20)

# ── CHAT AREA ─────────────────────────────────────────────────────────────────
chat_frame = tk.Frame(root, bg=PANEL, bd=0)
chat_frame.pack(fill="both", expand=True, padx=20, pady=(12, 0))

chat_box = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    font=FONT_MAIN,
    bg=PANEL,
    fg=TEXT_BOT,
    insertbackground=ACCENT,
    relief="flat",
    padx=14,
    pady=10,
    state="disabled",
    cursor="arrow",
)
chat_box.pack(fill="both", expand=True)

chat_box.tag_config("user",   foreground=ACCENT,    font=("Consolas", 12, "bold"))
chat_box.tag_config("jarvis", foreground=TEXT_BOT,  font=FONT_MAIN)
chat_box.tag_config("label_u",foreground=ACCENT2,   font=("Consolas", 10, "bold"))
chat_box.tag_config("label_j",foreground=TEXT_DIM,  font=("Consolas", 10, "bold"))
chat_box.tag_config("think",  foreground=TEXT_DIM,  font=("Consolas", 11, "italic"))
chat_box.tag_config("divider",foreground=DIM)
chat_box.tag_config("error",  foreground="#ff4444")

# ── STATUS BAR ───────────────────────────────────────────────────────────────
status_var = tk.StringVar(value="SYSTEM ONLINE  |  READY")
status_bar = tk.Label(root, textvariable=status_var,
                      font=("Consolas", 9), bg=BG, fg=TEXT_DIM, anchor="w")
status_bar.pack(fill="x", padx=24, pady=(4, 0))

# ── INPUT AREA ────────────────────────────────────────────────────────────────
input_frame = tk.Frame(root, bg=BG)
input_frame.pack(fill="x", padx=20, pady=12)

tk.Label(input_frame, text=">>>", font=("Consolas", 13, "bold"),
         bg=BG, fg=ACCENT).pack(side="left", padx=(0, 8))

user_input = tk.Entry(
    input_frame,
    font=("Consolas", 13),
    bg=DIM,
    fg=TEXT_BOT,
    insertbackground=ACCENT,
    relief="flat",
    bd=0,
)
user_input.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

send_btn = tk.Button(
    input_frame,
    text="SEND",
    font=("Consolas", 11, "bold"),
    bg=ACCENT2,
    fg="white",
    activebackground=ACCENT,
    activeforeground=BG,
    relief="flat",
    padx=18,
    pady=6,
    cursor="hand2",
)
send_btn.pack(side="right")

clear_btn = tk.Button(
    input_frame,
    text="CLR",
    font=("Consolas", 11),
    bg=DIM,
    fg=TEXT_DIM,
    activebackground=DIM,
    activeforeground=ACCENT,
    relief="flat",
    padx=10,
    pady=6,
    cursor="hand2",
)
clear_btn.pack(side="right", padx=(0, 6))

# ── ANIMATION ─────────────────────────────────────────────────────────────────
angle      = 0
thinking   = False
rings      = []
CX, CY, R  = 450, 60, 38

for i, (r, dash, color, speed) in enumerate([
    (38, (6, 6),  ACCENT,  1.8),
    (28, (4, 8),  ACCENT2, -2.5),
    (18, (3, 5),  ACCENT,  3.2),
]):
    arc = canvas.create_arc(
        CX - r, CY - r, CX + r, CY + r,
        start=0, extent=270,
        outline=color, width=1.5,
        style="arc", dash=dash,
    )
    rings.append((arc, speed))

dot = canvas.create_oval(CX - 5, CY - 5, CX + 5, CY + 5,
                          fill=ACCENT, outline="")

def animate():
    global angle
    t = time.time()
    for arc, speed in rings:
        a = (angle * speed) % 360
        pulse = 0.6 + 0.4 * math.sin(t * 3) if thinking else 1.0
        canvas.itemconfig(arc, extent=int(220 + 50 * pulse))
        canvas.itemconfig(arc, start=a)
    # dot pulse
    p = 3 + 3 * abs(math.sin(t * 4)) if thinking else 4
    canvas.coords(dot, CX - p, CY - p, CX + p, CY + p)
    col = "#ffffff" if thinking else ACCENT
    canvas.itemconfig(dot, fill=col)
    angle = (angle + 1.2) % 360
    root.after(30, animate)

animate()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def append_chat(text, tag="jarvis"):
    chat_box.config(state="normal")
    chat_box.insert("end", text, tag)
    chat_box.config(state="disabled")
    chat_box.see("end")

def clear_chat():
    chat_box.config(state="normal")
    chat_box.delete("1.0", "end")
    chat_box.config(state="disabled")
    status_var.set("SYSTEM ONLINE  |  CHAT CLEARED")

conversation_history = []

def send_message(event=None):
    global thinking
    question = user_input.get().strip()
    if not question:
        return

    user_input.delete(0, "end")
    send_btn.config(state="disabled")
    thinking = True

    append_chat("\n[ YOU ]\n", "label_u")
    append_chat(f"  {question}\n", "user")
    append_chat("\n[ JARVIS ]\n", "label_j")
    append_chat("  Processing request...\n", "think")
    status_var.set("JARVIS PROCESSING...")

    conversation_history.append({"role": "user", "content": question})

    def run():
        global thinking
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history,
                web_search=False,
            )
            answer = response.choices[0].message.content
            conversation_history.append({"role": "assistant", "content": answer})

            def update():
                global thinking
                # remove "Processing..." line
                chat_box.config(state="normal")
                content = chat_box.get("1.0", "end")
                last_think = content.rfind("  Processing request...")
                if last_think != -1:
                    idx = chat_box.index(f"1.0 + {last_think} chars")
                    chat_box.delete(idx, f"{idx} + {len('  Processing request...')+1} chars")
                chat_box.config(state="disabled")

                append_chat(f"  {answer}\n", "jarvis")
                append_chat("\n" + "─" * 60 + "\n", "divider")
                thinking = False
                send_btn.config(state="normal")
                status_var.set("SYSTEM ONLINE  |  RESPONSE DELIVERED")
                user_input.focus()

            root.after(0, update)

        except Exception as e:
            def show_err():
                global thinking
                chat_box.config(state="normal")
                content = chat_box.get("1.0", "end")
                last_think = content.rfind("  Processing request...")
                if last_think != -1:
                    idx = chat_box.index(f"1.0 + {last_think} chars")
                    chat_box.delete(idx, f"{idx} + {len('  Processing request...')+1} chars")
                chat_box.config(state="disabled")
                append_chat(f"  ERROR: {e}\n", "error")
                thinking = False
                send_btn.config(state="normal")
                status_var.set("SYSTEM ERROR  |  CHECK CONNECTION")
            root.after(0, show_err)

    threading.Thread(target=run, daemon=True).start()

# ── BINDINGS ─────────────────────────────────────────────────────────────────
send_btn.config(command=send_message)
clear_btn.config(command=clear_chat)
user_input.bind("<Return>", send_message)
user_input.focus()

# ── WELCOME MESSAGE ───────────────────────────────────────────────────────────
append_chat("  ╔══════════════════════════════════════╗\n", "label_j")
append_chat("  ║   JARVIS ONLINE — HOW CAN I HELP?   ║\n", "label_j")
append_chat("  ╚══════════════════════════════════════╝\n\n", "label_j")
append_chat("  All systems operational. Type your query below.\n", "think")
append_chat("\n" + "─" * 60 + "\n", "divider")

root.mainloop()
