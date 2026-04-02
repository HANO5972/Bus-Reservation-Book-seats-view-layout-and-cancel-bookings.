import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

DATA_FILE = "bookings.json"
TOTAL_SEATS = 30

# ---------- Colors ----------
BG             = "#1a1a2e"
PANEL          = "#16213e"
ACCENT         = "#e94560"
TEXT           = "#eaeaea"
MUTED          = "#8892a4"
SEAT_AVAILABLE = "#0f9b58"
SEAT_BOOKED    = "#e94560"


# ---------- File Helpers ----------

def load_bookings():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_bookings(bookings):
    with open(DATA_FILE, "w") as f:
        json.dump(bookings, f, indent=4)


# ---------- App ----------

class BusReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bus Reservation System")
        self.root.configure(bg=BG)
        self.root.geometry("700x620")
        self.root.resizable(False, False)

        self.bookings = load_bookings()   # single source of truth
        self.seat_buttons = {}
        self.status_var = tk.StringVar(value="Click a seat to book or cancel.")

        self.build_ui()
        self.refresh_seats()              # called AFTER all widgets exist

    def build_ui(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=ACCENT, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="🚌  Bus Reservation System",
                 font=("Helvetica", 20, "bold"), bg=ACCENT, fg="white").pack()
        tk.Label(header, text="Alliance University — Micro Project",
                 font=("Helvetica", 9), bg=ACCENT, fg="#ffd0d8").pack()

        # --- Legend ---
        legend = tk.Frame(self.root, bg=BG, pady=6)
        legend.pack()
        for color, label in [(SEAT_AVAILABLE, "Available"), (SEAT_BOOKED, "Booked")]:
            tk.Label(legend, text="●", fg=color, bg=BG,
                     font=("Helvetica", 14)).pack(side="left", padx=4)
            tk.Label(legend, text=label, fg=MUTED, bg=BG,
                     font=("Helvetica", 10)).pack(side="left", padx=(0, 14))

        # --- Seat Grid ---
        grid_frame = tk.Frame(self.root, bg=PANEL, padx=20, pady=16)
        grid_frame.pack(padx=20, pady=(0, 8), fill="x")

        tk.Label(grid_frame, text="SELECT A SEAT", font=("Helvetica", 11, "bold"),
                 bg=PANEL, fg=MUTED).grid(row=0, column=0, columnspan=9,
                                           pady=(0, 6), sticky="w")
        tk.Label(grid_frame, text="🚗 DRIVER", font=("Helvetica", 8),
                 bg=PANEL, fg=MUTED).grid(row=1, column=0, columnspan=2,
                                           sticky="w", padx=4)

        # 4 seats per row, aisle gap between column index 1 and 2 (col 2 = spacer)
        for i in range(1, TOTAL_SEATS + 1):
            grid_row = ((i - 1) // 4) + 2
            pos      = (i - 1) % 4
            grid_col = pos if pos < 2 else pos + 1   # cols 0,1 | gap at 2 | cols 3,4

            btn = tk.Button(
                grid_frame,
                text=str(i),
                width=4, height=2,
                font=("Helvetica", 10, "bold"),
                bg=SEAT_AVAILABLE, fg="white",
                relief="flat", cursor="hand2",
                command=lambda s=i: self.on_seat_click(s)
            )
            btn.grid(row=grid_row, column=grid_col, padx=4, pady=4)
            self.seat_buttons[i] = btn

        # Aisle label
        tk.Label(grid_frame, text="│\nA\nI\nS\nL\nE\n│",
                 font=("Helvetica", 7), bg=PANEL, fg=MUTED).grid(
            row=2, column=2, rowspan=8, padx=2)

        # --- Status Bar ---
        tk.Label(self.root, textvariable=self.status_var,
                 bg=PANEL, fg=MUTED, font=("Helvetica", 9),
                 anchor="w", padx=12, pady=6).pack(fill="x", padx=20)

        # --- Bottom Buttons ---
        btn_frame = tk.Frame(self.root, bg=BG, pady=10)
        btn_frame.pack()
        for label, cmd, color in [
            ("📋  View All Bookings", self.view_bookings, "#2d6a8a"),
            ("🔄  Refresh",           self.refresh_seats, "#3a3a5c"),
            ("❌  Exit",              self.root.quit,     "#5a2a2a"),
        ]:
            tk.Button(btn_frame, text=label, command=cmd,
                      bg=color, fg="white", font=("Helvetica", 10, "bold"),
                      padx=16, pady=8, relief="flat", cursor="hand2",
                      activebackground=ACCENT, activeforeground="white"
                      ).pack(side="left", padx=8)

    # ---- update seat colors from self.bookings (no file re-read) ----
    def refresh_seats(self):
        for i in range(1, TOTAL_SEATS + 1):
            if str(i) in self.bookings:
                self.seat_buttons[i].config(bg=SEAT_BOOKED)
            else:
                self.seat_buttons[i].config(bg=SEAT_AVAILABLE)
        booked = len(self.bookings)
        self.status_var.set(
            f"  {booked} seat(s) booked  |  {TOTAL_SEATS - booked} seat(s) available")

    # ---- seat click: book or cancel ----
    def on_seat_click(self, seat_num):
        seat = str(seat_num)

        if seat in self.bookings:
            name = self.bookings[seat]
            if messagebox.askyesno("Cancel Booking",
                                   f"Seat {seat_num} is booked by {name}.\n\nCancel this booking?"):
                del self.bookings[seat]
                save_bookings(self.bookings)
                self.refresh_seats()
                messagebox.showinfo("Cancelled",
                                    f"Booking for seat {seat_num} ({name}) cancelled.")
        else:
            name = simpledialog.askstring(
                "Book Seat", f"Enter passenger name for Seat {seat_num}:",
                parent=self.root)

            if name is None:          # user pressed Cancel
                return
            if not name.strip():
                messagebox.showwarning("Invalid", "Name cannot be empty.")
                return

            self.bookings[seat] = name.strip()
            save_bookings(self.bookings)
            self.refresh_seats()
            messagebox.showinfo("Booked!", f"Seat {seat_num} booked for {name.strip()} ✓")

    # ---- view all bookings popup ----
    def view_bookings(self):
        if not self.bookings:
            messagebox.showinfo("Bookings", "No bookings yet!")
            return

        win = tk.Toplevel(self.root)
        win.title("All Bookings")
        win.configure(bg=BG)
        win.geometry("320x400")
        win.resizable(False, False)

        tk.Label(win, text="ALL BOOKINGS", font=("Helvetica", 13, "bold"),
                 bg=BG, fg=ACCENT).pack(pady=(16, 4))
        tk.Label(win, text=f"{len(self.bookings)} of {TOTAL_SEATS} seats booked",
                 font=("Helvetica", 9), bg=BG, fg=MUTED).pack(pady=(0, 10))

        frame = tk.Frame(win, bg=PANEL, padx=16, pady=12)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=PANEL)

        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # sort by integer seat number (fixes "9" sorting after "30" as string)
        for seat, name in sorted(self.bookings.items(), key=lambda x: int(x[0])):
            row = tk.Frame(scroll_frame, bg=PANEL)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=f"Seat {int(seat):2}", font=("Courier", 10, "bold"),
                     bg=PANEL, fg=ACCENT, width=8).pack(side="left")
            tk.Label(row, text="→", bg=PANEL, fg=MUTED,
                     font=("Helvetica", 10)).pack(side="left", padx=4)
            tk.Label(row, text=name, font=("Helvetica", 10),
                     bg=PANEL, fg=TEXT).pack(side="left")


if __name__ == "__main__":
    root = tk.Tk()
    app = BusReservationApp(root)
    root.mainloop()
