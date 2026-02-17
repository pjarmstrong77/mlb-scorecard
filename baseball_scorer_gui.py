import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os

class BaseballScorerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MLB Baseball Scorekeeper - 2026 Projected")
        self.root.geometry("1100x800")

        # Projected lineups (add more teams as needed)
        self.projected_lineups = {
            "New York Yankees": [
                "1. Trent Grisham (CF)", "2. Aaron Judge (RF)", "3. Cody Bellinger (LF)",
                "4. Ben Rice (1B)", "5. Giancarlo Stanton (DH)", "6. Jazz Chisholm Jr. (3B)",
                "7. Anthony Volpe (SS)", "8. Austin Wells (C)", "9. Oswaldo Cabrera (2B/INF)"
            ],
            "Boston Red Sox": [
                "1. Roman Anthony (OF)", "2. Trevor Story (SS)", "3. Jarren Duran (DH/CF)",
                "4. Willson Contreras (1B/C)", "5. Triston Casas (1B)", "6. Masataka Yoshida (LF)",
                "7. Ceddanne Rafaela (CF)", "8. Connor Wong (C)", "9. Kristian Campbell (2B/INF)"
            ],
            "Los Angeles Dodgers": [
                "1. Shohei Ohtani (DH)", "2. Mookie Betts (RF/SS)", "3. Freddie Freeman (1B)",
                "4. Teoscar Hernández (LF)", "5. Will Smith (C)", "6. Max Muncy (3B)",
                "7. Andy Pages (CF)", "8. Tommy Edman (UTIL)", "9. Miguel Rojas (SS/2B)"
            ],
        }

        self.away_team = tk.StringVar(value=list(self.projected_lineups.keys())[0])
        self.home_team = tk.StringVar(value=list(self.projected_lineups.keys())[1])

        # Game state
        self.inning = 1
        self.half_inning = "Top"
        self.outs = 0
        self.bases = [False, False, False]  # 0:1st, 1:2nd, 2:3rd
        self.max_innings = 12
        self.away_runs = [0] * self.max_innings
        self.home_runs = [0] * self.max_innings
        self.away_hits = 0
        self.home_hits = 0
        self.away_errors = 0
        self.home_errors = 0
        self.away_batter = 0
        self.home_batter = 0
        self.events = []

        self.away_lineup = []
        self.home_lineup = []

        self.current_batter_label = None
        self.diamond_canvas = None

        self.setup_ui()

    def setup_ui(self):
        self.team_frame = ttk.Frame(self.root, padding=10)
        self.team_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self.team_frame, text="Select Away Team:").grid(row=0, column=0, pady=5)
        ttk.Combobox(self.team_frame, textvariable=self.away_team, values=list(self.projected_lineups.keys())).grid(row=0, column=1, pady=5)

        ttk.Label(self.team_frame, text="Select Home Team:").grid(row=1, column=0, pady=5)
        ttk.Combobox(self.team_frame, textvariable=self.home_team, values=list(self.projected_lineups.keys())).grid(row=1, column=1, pady=5)

        ttk.Button(self.team_frame, text="Start Scoring", command=self.start_game).grid(row=2, column=0, columnspan=2, pady=20)

        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=10)

        # Now Batting
        self.batter_frame = ttk.LabelFrame(self.main_frame, text="Now Batting")
        self.batter_frame.pack(fill=tk.X, pady=5)
        self.current_batter_label = ttk.Label(self.batter_frame, text="Select teams to start", font=("Arial", 14, "bold"))
        self.current_batter_label.pack(pady=5)

        # Box Score
        box_frame = ttk.LabelFrame(self.main_frame, text="Box Score")
        box_frame.pack(fill=tk.X, pady=5)

        ttk.Label(box_frame, text="Team", width=12, anchor="center").grid(row=0, column=0, padx=2)
        for col in range(1, 10):
            ttk.Label(box_frame, text=str(col), width=4, anchor="center").grid(row=0, column=col, padx=2)
        ttk.Label(box_frame, text="R", width=4, anchor="center").grid(row=0, column=10, padx=2)
        ttk.Label(box_frame, text="H", width=4, anchor="center").grid(row=0, column=11, padx=2)
        ttk.Label(box_frame, text="E", width=4, anchor="center").grid(row=0, column=12, padx=2)

        self.away_inning_labels = []
        ttk.Label(box_frame, textvariable=self.away_team, width=12).grid(row=1, column=0, padx=2, pady=2)
        for col in range(1, 10):
            lbl = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
            lbl.grid(row=1, column=col, padx=2)
            self.away_inning_labels.append(lbl)
        self.away_r_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.away_r_label.grid(row=1, column=10, padx=2)
        self.away_h_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.away_h_label.grid(row=1, column=11, padx=2)
        self.away_e_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.away_e_label.grid(row=1, column=12, padx=2)

        self.home_inning_labels = []
        ttk.Label(box_frame, textvariable=self.home_team, width=12).grid(row=2, column=0, padx=2, pady=2)
        for col in range(1, 10):
            lbl = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
            lbl.grid(row=2, column=col, padx=2)
            self.home_inning_labels.append(lbl)
        self.home_r_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.home_r_label.grid(row=2, column=10, padx=2)
        self.home_h_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.home_h_label.grid(row=2, column=11, padx=2)
        self.home_e_label = ttk.Label(box_frame, text="0", width=4, relief="sunken", anchor="center")
        self.home_e_label.grid(row=2, column=12, padx=2)

        # Diamond + Info
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=10)

        diamond_f = ttk.LabelFrame(top_frame, text="Diamond View")
        diamond_f.pack(side=tk.LEFT, padx=10)
        self.diamond_canvas = tk.Canvas(diamond_f, width=220, height=220, bg="lightgreen")
        self.diamond_canvas.pack()
        self.draw_diamond_base()

        info_f = ttk.Frame(top_frame)
        info_f.pack(side=tk.LEFT, padx=20)
        self.inning_label = ttk.Label(info_f, text="", font=("Arial", 14))
        self.inning_label.pack(pady=5)
        self.outs_label = ttk.Label(info_f, text="Outs: 0/3", font=("Arial", 14))
        self.outs_label.pack(pady=5)
        self.bases_label = ttk.Label(info_f, text="Bases: --- --- ---", font=("Arial", 12))
        self.bases_label.pack(pady=5)

        # Lineups
        lineups_frame = ttk.Frame(self.main_frame)
        lineups_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        away_f = ttk.LabelFrame(lineups_frame, text="Away Lineup")
        away_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.away_text = tk.Text(away_f, height=15, width=45, font=("Courier", 10))
        self.away_text.pack(fill=tk.BOTH, expand=True)

        home_f = ttk.LabelFrame(lineups_frame, text="Home Lineup")
        home_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.home_text = tk.Text(home_f, height=15, width=45, font=("Courier", 10))
        self.home_text.pack(fill=tk.BOTH, expand=True)

        # Buttons
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=10)

        actions = [
            ("Out", self.record_out),
            ("Single", lambda: self.record_hit(1)),
            ("Double", lambda: self.record_hit(2)),
            ("Triple", lambda: self.record_hit(3)),
            ("HR", lambda: self.record_hit(4)),
            ("Walk", self.record_walk),
            ("Steal", self.record_steal),
            ("+ Hit", self.add_hit),
            ("+ Error", self.add_error),
            ("Next Batter", self.next_batter)
        ]
        for text, cmd in actions:
            ttk.Button(btn_frame, text=text, command=cmd).pack(side=tk.LEFT, padx=4)

        extra_frame = ttk.Frame(self.main_frame)
        extra_frame.pack(pady=5)
        ttk.Button(extra_frame, text="End Half", command=self.next_half).pack(side=tk.LEFT, padx=10)
        ttk.Button(extra_frame, text="Save", command=self.save_game).pack(side=tk.LEFT, padx=10)
        ttk.Button(extra_frame, text="Load", command=self.load_game).pack(side=tk.LEFT, padx=10)
        ttk.Button(extra_frame, text="Quit", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        self.log_text = scrolledtext.ScrolledText(self.main_frame, height=8, width=100, font=("Arial", 10))
        self.log_text.pack(pady=10, fill=tk.X)

    def draw_diamond_base(self):
        c = self.diamond_canvas
        c.delete("all")
        # Diamond
        c.create_polygon(110, 20, 200, 110, 110, 200, 20, 110, fill="", outline="white", width=3)
        self.base_coords = {
            0: (200, 110),  # 1st base
            1: (110, 20),   # 2nd base
            2: (20, 110)    # 3rd base
        }
        # Home plate
        c.create_polygon(105, 195, 115, 195, 115, 205, 110, 215, 105, 205, fill="white", outline="black")
        # Pitcher mound
        c.create_oval(105, 105, 115, 115, fill="brown")
        # Bases
        for base in [0,1,2]:
            x, y = self.base_coords[base]
            c.create_rectangle(x-8, y-8, x+8, y+8, fill="white", outline="black", tags=f"base{base}")

    def update_diamond(self):
        if not self.diamond_canvas:
            return
        c = self.diamond_canvas
        for base_idx, tag in enumerate(["base0", "base1", "base2"]):
            fill_color = "red" if self.bases[base_idx] else "white"
            outline_color = "yellow" if self.bases[base_idx] else "black"
            c.itemconfig(tag, fill=fill_color, outline=outline_color)

    def start_game(self):
        self.away_lineup = self.projected_lineups.get(self.away_team.get(), [])
        self.home_lineup = self.projected_lineups.get(self.home_team.get(), [])
        if not self.away_lineup or not self.home_lineup:
            messagebox.showerror("Error", "Selected teams not found.")
            return

        self.team_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.log(f"Game started: {self.away_team.get()} @ {self.home_team.get()}")
        self.update_display()

    def update_display(self):
        if not self.away_lineup:
            return

        # Box score
        for i in range(min(9, self.max_innings)):
            self.away_inning_labels[i].config(text=str(self.away_runs[i]))
            self.home_inning_labels[i].config(text=str(self.home_runs[i]))
        self.away_r_label.config(text=str(sum(self.away_runs)))
        self.home_r_label.config(text=str(sum(self.home_runs)))
        self.away_h_label.config(text=str(self.away_hits))
        self.home_h_label.config(text=str(self.home_hits))
        self.away_e_label.config(text=str(self.away_errors))
        self.home_e_label.config(text=str(self.home_errors))

        # Now batting
        if self.half_inning == "Top":
            batter_idx = self.away_batter
            lineup = self.away_lineup
            team = self.away_team.get()
        else:
            batter_idx = self.home_batter
            lineup = self.home_lineup
            team = self.home_team.get()
        if lineup:
            batter_str = lineup[batter_idx]
            self.current_batter_label.config(text=f"{team} - {batter_str}")

        # Inning / Outs / Bases text
        self.inning_label.config(text=f"Inning {self.inning} ({self.half_inning})")
        self.outs_label.config(text=f"Outs: {self.outs}/3")
        bases_str = f"1st: {'Runner' if self.bases[0] else '---'} | 2nd: {'Runner' if self.bases[1] else '---'} | 3rd: {'Runner' if self.bases[2] else '---'}"
        self.bases_label.config(text=bases_str)

        # Lineups with current batter arrow
        self.away_text.delete(1.0, tk.END)
        for i, player in enumerate(self.away_lineup):
            marker = " ←" if i == self.away_batter and self.half_inning == "Top" else ""
            self.away_text.insert(tk.END, player + marker + "\n")

        self.home_text.delete(1.0, tk.END)
        for i, player in enumerate(self.home_lineup):
            marker = " ←" if i == self.home_batter and self.half_inning == "Bottom" else ""
            self.home_text.insert(tk.END, player + marker + "\n")

        self.update_diamond()

    def log(self, msg):
        self.events.append(msg)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def record_out(self):
        self.outs += 1
        self.log(f"Out recorded. Outs: {self.outs}/3")
        if self.outs >= 3:
            self.next_half()
        else:
            self.next_batter()
        self.update_display()

    def record_hit(self, bases):
        runs = 0

        # Score runners who advance enough
        if self.bases[2]:
            runs += 1
            self.bases[2] = False

        if self.bases[1] and bases >= 2:
            runs += 1
            self.bases[1] = False

        if self.bases[0] and bases >= 3:
            runs += 1
            self.bases[0] = False

        if bases == 4:
            runs += 1

        current_runs_list = self.away_runs if self.half_inning == "Top" else self.home_runs
        if self.inning - 1 < len(current_runs_list):
            current_runs_list[self.inning - 1] += runs

        # Place batter on base (not for HR)
        if bases < 4:
            self.bases[bases - 1] = True

        hit_type = {1:"Single", 2:"Double", 3:"Triple", 4:"Home Run"}[bases]
        self.log(f"{hit_type}! {runs} run(s) scored. Bases now: {self.bases}")
        self.next_batter()
        self.update_display()

    def record_walk(self):
        runs = 0

        # Bases loaded walk forces run
        if all(self.bases):
            runs += 1
            # In force situation, runner from 3rd scores, others advance
            self.bases[2] = True   # was already true
            self.bases[1] = True
            self.bases[0] = True
        else:
            # Normal force
            if self.bases[0] and self.bases[1]:
                self.bases[2] = self.bases[2] or True
            if self.bases[0]:
                self.bases[1] = self.bases[1] or True
            self.bases[0] = True

        current_runs_list = self.away_runs if self.half_inning == "Top" else self.home_runs
        if self.inning - 1 < len(current_runs_list):
            current_runs_list[self.inning - 1] += runs

        self.log(f"Walk. {runs} run(s) scored. Bases now: {self.bases}")
        self.next_batter()
        self.update_display()

    def record_steal(self):
        if self.bases[0]:
            self.bases[1] = True
            self.bases[0] = False
            self.log("Runner steals 2nd. Bases now: {self.bases}")
        elif self.bases[1]:
            self.bases[2] = True
            self.bases[1] = False
            self.log("Runner steals 3rd. Bases now: {self.bases}")
        elif self.bases[2]:
            self.log("Runner on 3rd - steal not modeled (would score)")
        self.update_display()

    def add_hit(self):
        if self.half_inning == "Top":
            self.away_hits += 1
        else:
            self.home_hits += 1
        self.log("Manual +1 Hit added")
        self.update_display()

    def add_error(self):
        if self.half_inning == "Top":
            self.away_errors += 1
        else:
            self.home_errors += 1
        self.log("Manual +1 Error added")
        self.update_display()

    def next_batter(self):
        if self.half_inning == "Top":
            self.away_batter = (self.away_batter + 1) % len(self.away_lineup)
        else:
            self.home_batter = (self.home_batter + 1) % len(self.home_lineup)
        self.update_display()

    def next_half(self):
        self.outs = 0
        self.bases = [False, False, False]
        if self.half_inning == "Top":
            self.half_inning = "Bottom"
        else:
            self.half_inning = "Top"
            self.inning += 1
            if self.inning > self.max_innings:
                self.log("Game extended beyond 12 innings")
        self.log(f"New half-inning: {self.half_inning} of {self.inning} — bases cleared")
        self.update_display()

    def save_game(self):
        data = {
            "away_team": self.away_team.get(), "home_team": self.home_team.get(),
            "inning": self.inning, "half_inning": self.half_inning, "outs": self.outs,
            "bases": self.bases, "away_runs": self.away_runs, "home_runs": self.home_runs,
            "away_hits": self.away_hits, "home_hits": self.home_hits,
            "away_errors": self.away_errors, "home_errors": self.home_errors,
            "away_batter": self.away_batter, "home_batter": self.home_batter,
            "events": self.events
        }
        filename = tk.simpledialog.askstring("Save", "Filename (no .json):")
        if filename:
            with open(f"{filename}.json", "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Saved", "Game saved!")

    def load_game(self):
        filename = tk.simpledialog.askstring("Load", "Filename (no .json):")
        if filename and os.path.exists(f"{filename}.json"):
            with open(f"{filename}.json", "r") as f:
                data = json.load(f)
            self.away_team.set(data["away_team"])
            self.home_team.set(data["home_team"])
            self.inning = data["inning"]
            self.half_inning = data["half_inning"]
            self.outs = data["outs"]
            self.bases = data["bases"]
            self.away_runs = data["away_runs"]
            self.home_runs = data["home_runs"]
            self.away_hits = data.get("away_hits", 0)
            self.home_hits = data.get("home_hits", 0)
            self.away_errors = data.get("away_errors", 0)
            self.home_errors = data.get("home_errors", 0)
            self.away_batter = data["away_batter"]
            self.home_batter = data["home_batter"]
            self.events = data["events"]
            self.log_text.delete(1.0, tk.END)
            for e in self.events:
                self.log_text.insert(tk.END, e + "\n")
            self.log_text.see(tk.END)
            self.team_frame.pack_forget()
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            self.update_display()
            messagebox.showinfo("Loaded", "Game loaded!")
        else:
            messagebox.showerror("Error", "File not found.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseballScorerGUI(root)
    root.mainloop()