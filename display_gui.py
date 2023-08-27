import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import queue
import playerClass as pc

class DiceStatisticsApp(tk.Tk):
    def __init__(self, q, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = q
        self.after(100, self.check_queue)
        self.players = {}

        self.title("DnD Dice Statistics")

        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.subplot = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Setup choice between player and general statistics
        self.player_var = tk.StringVar(self)
        self.dropdown = ttk.Combobox(self, textvariable=self.player_var)
        self.populate_dropdown()
        self.dropdown.pack(pady=20)

        # Last roll slider
        self.last_slider = tk.Scale(self, from_=1, to=10, orient=tk.HORIZONTAL, command=self.slider_changed)
        self.last_slider.pack(pady=20)
        self.last_slider.pack_forget()  # Hide the slider by default
        self.dropdown.bind("<<ComboboxSelected>>", self.handle_dropdown_change) # Bind the dropdown to the handler

    def plot_data(self, dice, outcome):
        # find out what we are plotting
        if self.dropdown.get() == "Last roll":
            pmf = self.compute_pmf(dice)
            self.setup_subplots(pmf, outcome, dice)
        else:
            player_name = self.dropdown.get()
            player = self.get_player_by_name(player_name)
            # get the amount of rolls
            n_rolls = int(self.last_slider.get()) if\
                      int(self.last_slider.get()) < int(len(player.rolls)/2) else int(len(player.rolls)/2)
            # Get the rolls and results
            rolls = []
            results = []
            modifiers = 0
            for i in range(n_rolls):
                roll = player.rolls[-(i * 2 + 2)]
                res = player.rolls[-(i * 2 + 1)]
                dice, modifier = pc.ret_dice(roll)
                [rolls.append(int(die)) for die in dice]
                results.append(res - modifier)
                modifiers = modifiers + modifier
            # Compute the PMF
            pmf = self.compute_pmf(rolls)
            # Set up the subplots
            self.setup_subplots(pmf, sum(results), rolls)
        self.canvas.draw()

    def populate_dropdown(self):
        """Populate the dropdown menu with player names."""
        player_names = [player.name for player in self.players]
        self.dropdown['values'] = ["Last roll"] + player_names
        if player_names:
            self.dropdown.current(0)

    def handle_dropdown_change(self, event):
        if self.dropdown.get() == "Last roll":
            self.last_slider.pack_forget()
        else:
            self.last_slider.pack()

    def slider_changed(self, event):
        self.plot_data(None, None)

    def setup_subplots(self, pmf, outcome, dice_sides):
        fig = self.canvas.figure
        fig.clear()
        ax1, ax2 = fig.subplots(1, 2)

        cdf = np.cumsum(pmf)
        labels = [str(i+len(dice_sides)) for i in range(len(pmf))]

        # Modify the outcome to be the index of the list
        list_outcome = outcome - len(dice_sides)

        # Update the label with the required text
        cdf_chance = np.cumsum(pmf)[list_outcome]
        pmf_chance = pmf[list_outcome]

        # Plot the CDF
        ax1.bar(labels, cdf, color=['blue' if int(lbl) <= outcome else 'gray' for lbl in labels])
        ax1.axvline(x=str(outcome), color='red', linestyle='--')
        ax1.set_ylabel('Probability')
        ax1.set_xlabel('Sum of Dice Rolls')
        ax1.set_title(f'CDF for Dice with Sides: {", ".join(map(str, dice_sides))}\n Chance: {cdf_chance*100:.2f}%')
        ax1.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        # Plot the PMF
        ax2.bar(labels, pmf, color=['blue' if int(lbl) <= outcome else 'gray' for lbl in labels])
        ax2.axvline(x=str(outcome), color='red', linestyle='--')
        ax2.set_ylabel('Probability')
        ax2.set_xlabel('Sum of Dice Rolls')
        ax2.set_title(f'PMF for Dice with Sides: {", ".join(map(str, dice_sides))}\n Chance: {pmf_chance*100:.2f}%')
        ax2.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=.25)

        fig.tight_layout()
        return ax1, ax2

    def check_queue(self):
        try:
            package = self.queue.get_nowait()
            if package[0] == "players":
                self.players = package[1]
                self.populate_dropdown()
            elif package[0] == "rolls":
                dice_list = package[1]
                outcome = package[2]
                self.update_data_from_queue(dice_list, outcome)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

    def update_data_from_queue(self, dice, outcome):
        self.plot_data(dice, outcome)

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None

    @staticmethod
    def compute_pmf(dice_sides):
        pmf = np.ones(dice_sides[0]) / dice_sides[0]
        for sides in dice_sides[1:]:
            tpmf = np.zeros(len(pmf) + sides - 1)
            for j, p in enumerate(pmf):
                tpmf[j:j + sides] += p / sides
            pmf = tpmf
        return pmf



def run_gui(q):
    app = DiceStatisticsApp(q)
    app.mainloop()


# Debugging
if __name__ == "__main__":
    q = queue.Queue()

    gui_thread = threading.Thread(target=run_gui, args=(q,))
    gui_thread.start()

    # Example: Pretend this is your Selenium part.
    import time

    for _ in range(10):
        time.sleep(2)
        q.put(([6, 6], np.random.randint(2, 13)))  # Simulating dice rolls