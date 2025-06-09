"""
This analysis module tracks the mass of the soap bar over time and computes
summary statistics.

Plans:
- Accept mass history data.
- Compute:
    - Total mass lost.
    - Average erosion rate.
    - Time to 50% depletion (half-life equivalent).
- Provide utilities for saving/loading time series.
- Visualize with plots.

Nuclear Engineering Parallel:
This reflects core physics analysis routines that calculate burnup,
depletion rates, or CRUD accumulation/depletion trends in reactor analysis tools.
"""

import numpy as np
import matplotlib.pyplot as plt

class MassTracker:
    def __init__(self, mass_history):
        self.history = np.array(mass_history)

    def compute_summary(self):
        initial = self.history[0]
        final = self.history[-1]
        total_loss = initial - final
        avg_rate = total_loss / len(self.history)
        half_mass = initial / 2.0
        half_time = next((i for i, m in enumerate(self.history) if m <= half_mass), None)

        return {
            'initial_mass': initial,
            'final_mass': final,
            'total_loss': total_loss,
            'avg_erosion_rate': avg_rate,
            'half_mass_time': half_time
        }

    def plot(self):
        plt.plot(self.history)
        plt.xlabel("Time step")
        plt.ylabel("Mass")
        plt.title("Soap Mass vs Time")
        plt.grid(True)
        plt.show()
