import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import queue


class DiceStatisticsApp(tk.Tk):
    def __init__(self, q, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = q
        self.after(100, self.check_queue)

        self.title("DnD Dice Statistics")

        self.figure = Figure(figsize=(10, 5), dpi=100)
        self.subplot = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(pady=20)

    def plot_data(self, dice, outcome):
        pmf = self.compute_pmf(dice)
        self.setup_subplots(pmf, outcome, dice)

        self.canvas.draw()

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
            dice_list, outcome = self.queue.get_nowait()
            self.update_data_from_queue(dice_list, outcome)
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

    def update_data_from_queue(self, dice, outcome):
        self.plot_data(dice, outcome)

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