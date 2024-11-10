import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ToolTip:
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.text = None

    def show(self, text, x, y):
        self.text = text
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("Arial", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def calculate():
    try:
        name = entry_name.get().strip()
        if not name:
            output_label.config(text="Please enter a name.")
            return
        S = float(entry_spot_price.get())
        K = float(entry_strike_price.get())
        T = float(entry_time_to_maturity.get())
        r = float(entry_risk_free_rate.get()) / 100
        sigma = float(entry_volatility.get()) / 100
        call_price = black_scholes(S, K, T, r, sigma, "call")
        put_price = black_scholes(S, K, T, r, sigma, "put")
        values = (name, f"{call_price:.2f}", f"{put_price:.2f}")
        results_tree.insert("", "end", values=values)
        entry_details[name] = f"Spot Price (S): {S}\nStrike Price (K): {K}\nTime to Maturity (T): {T}\nRisk-Free Rate (r): {r * 100}%\nVolatility (sigma): {sigma * 100}%"
        output_label.config(text="Calculation successful.")
    except ValueError:
        output_label.config(text="Error: Please fill all fields correctly.")

def update_heatmap():
    try:
        min_spot = float(entry_min_spot_price.get())
        max_spot = float(entry_max_spot_price.get())
        min_vol = float(entry_min_volatility.get()) / 100
        max_vol = float(entry_max_volatility.get()) / 100
        spot_prices = np.linspace(min_spot, max_spot, 10)
        volatilities = np.linspace(min_vol, max_vol, 10)
        call_prices = np.zeros((len(volatilities), len(spot_prices)))
        put_prices = np.zeros((len(volatilities), len(spot_prices)))
        K, T, r = 100, 1, 0.05
        for i, sigma in enumerate(volatilities):
            for j, S in enumerate(spot_prices):
                call_prices[i, j] = black_scholes(S, K, T, r, sigma, "call")
                put_prices[i, j] = black_scholes(S, K, T, r, sigma, "put")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)
        c1 = ax1.imshow(call_prices, aspect='auto', origin='lower',
                        extent=[min_spot, max_spot, min_vol * 100, max_vol * 100])
        ax1.set_title("Call Option Price Heatmap")
        ax1.set_xlabel("Spot Price")
        ax1.set_ylabel("Volatility (%)")
        fig.colorbar(c1, ax=ax1)
        c2 = ax2.imshow(put_prices, aspect='auto', origin='lower',
                        extent=[min_spot, max_spot, min_vol * 100, max_vol * 100])
        ax2.set_title("Put Option Price Heatmap")
        ax2.set_xlabel("Spot Price")
        ax2.set_ylabel("Volatility (%)")
        fig.colorbar(c2, ax=ax2)
        for widget in heatmap_frame.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=heatmap_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    except ValueError:
        output_label.config(text="Error: Please fill all fields correctly.")

def update_inputs(event):
    selected_tab = notebook.tab(notebook.select(), "text")
    for widget in input_frame.winfo_children():
        widget.destroy()
    global entry_name, entry_spot_price, entry_strike_price, entry_time_to_maturity, entry_risk_free_rate, entry_volatility
    global entry_min_spot_price, entry_max_spot_price, entry_min_volatility, entry_max_volatility
    global calc_button, heatmap_button
    if selected_tab == "Calculation":
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = ttk.Entry(input_frame)
        entry_name.grid(row=0, column=1)
        ttk.Label(input_frame, text="Spot Price (S):").grid(row=1, column=0, sticky="w", pady=5)
        entry_spot_price = ttk.Entry(input_frame)
        entry_spot_price.grid(row=1, column=1)
        ttk.Label(input_frame, text="Strike Price (K):").grid(row=2, column=0, sticky="w", pady=5)
        entry_strike_price = ttk.Entry(input_frame)
        entry_strike_price.grid(row=2, column=1)
        ttk.Label(input_frame, text="Time to Maturity (T):").grid(row=3, column=0, sticky="w", pady=5)
        entry_time_to_maturity = ttk.Entry(input_frame)
        entry_time_to_maturity.grid(row=3, column=1)
        ttk.Label(input_frame, text="Risk-Free Rate (r %):").grid(row=4, column=0, sticky="w", pady=5)
        entry_risk_free_rate = ttk.Entry(input_frame)
        entry_risk_free_rate.grid(row=4, column=1)
        ttk.Label(input_frame, text="Volatility (sigma %):").grid(row=5, column=0, sticky="w", pady=5)
        entry_volatility = ttk.Entry(input_frame)
        entry_volatility.grid(row=5, column=1)
        calc_button = ttk.Button(input_frame, text="Calculate", command=calculate)
        calc_button.grid(row=6, column=0, columnspan=2, pady=10)
    elif selected_tab == "Heatmap":
        ttk.Label(input_frame, text="Min Spot Price:").grid(row=0, column=0, sticky="w", pady=5)
        entry_min_spot_price = ttk.Entry(input_frame)
        entry_min_spot_price.insert(0, "50")
        entry_min_spot_price.grid(row=0, column=1)
        ttk.Label(input_frame, text="Max Spot Price:").grid(row=1, column=0, sticky="w", pady=5)
        entry_max_spot_price = ttk.Entry(input_frame)
        entry_max_spot_price.insert(0, "150")
        entry_max_spot_price.grid(row=1, column=1)
        ttk.Label(input_frame, text="Min Volatility (%):").grid(row=2, column=0, sticky="w", pady=5)
        entry_min_volatility = ttk.Entry(input_frame)
        entry_min_volatility.insert(0, "10")
        entry_min_volatility.grid(row=2, column=1)
        ttk.Label(input_frame, text="Max Volatility (%):").grid(row=3, column=0, sticky="w", pady=5)
        entry_max_volatility = ttk.Entry(input_frame)
        entry_max_volatility.insert(0, "50")
        entry_max_volatility.grid(row=3, column=1)
        heatmap_button = ttk.Button(input_frame, text="Update Heatmap", command=update_heatmap)
        heatmap_button.grid(row=4, column=0, columnspan=2, pady=10)

def on_treeview_hover(event):
    item_id = results_tree.identify_row(event.y)
    column = results_tree.identify_column(event.x)
    if item_id and column == "#1":
        name = results_tree.item(item_id, "values")[0]
        details = entry_details.get(name, "")
        tooltip.show(details, event.x_root + 20, event.y_root + 10)
    else:
        tooltip.hide()

root = tk.Tk()
root.title("Black-Scholes Calculator")
root.configure(bg="#2d2d2d")

style = ttk.Style()
style.theme_use('clam')
style.configure("TLabel", background="#2d2d2d", foreground="white", font=("Arial", 10))
style.configure("TEntry", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10))
style.configure("TFrame", background="#2d2d2d")

entry_details = {}
tooltip = ToolTip(root)

input_frame = ttk.Frame(root, padding="10")
input_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

notebook = ttk.Notebook(root)
notebook.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

table_frame = ttk.Frame(notebook)
notebook.add(table_frame, text="Calculation")

columns = ("Name", "Call Price", "Put Price")
results_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
results_tree.heading("Name", text="Name")
results_tree.heading("Call Price", text="Call Price")
results_tree.heading("Put Price", text="Put Price")
results_tree.pack(fill="both", expand=True)
results_tree.bind("<Motion>", on_treeview_hover)

heatmap_frame = ttk.Frame(notebook)
notebook.add(heatmap_frame, text="Heatmap")

output_label = ttk.Label(root, text="Please enter values and press 'Calculate'.", font=("Arial", 12), background="#2d2d2d", foreground="white")
output_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

notebook.bind("<<NotebookTabChanged>>", update_inputs)

entry_name = entry_spot_price = entry_strike_price = entry_time_to_maturity = entry_risk_free_rate = entry_volatility = None
entry_min_spot_price = entry_max_spot_price = entry_min_volatility = entry_max_volatility = None
calc_button = heatmap_button = None

update_inputs(None)

root.mainloop()
