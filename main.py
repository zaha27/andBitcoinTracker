import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to get the current Bitcoin price
def get_bitcoin_price():
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
    data = response.json()
    return float(data['bpi']['USD']['rate'].replace(',', ''))

# Function to update the price in the GUI
def update_price():
    global target_price, initial_price, prices, timestamps
    while True:
        current_price = get_bitcoin_price()
        percent_change = ((current_price - initial_price) / initial_price) * 100 if initial_price else 0
        price_label.config(text=f"Prețul curent al Bitcoin: ${current_price:.2f}")
        percent_label.config(text=f"Schimbare: {percent_change:.2f}%")
        
        if target_price is not None:
            difference_to_target = target_price - current_price
            if difference_to_target > 0:
                target_label.config(text=f"Prețul trebuie să crească cu ${difference_to_target:.2f} ({(difference_to_target / current_price) * 100:.2f}%) pentru a ajunge la ${target_price:.2f}.")
            elif difference_to_target < 0:
                target_label.config(text=f"Prețul trebuie să scadă cu ${-difference_to_target:.2f} ({(-difference_to_target / current_price) * 100:.2f}%) pentru a ajunge la ${target_price:.2f}.")
            else:
                target_label.config(text=f"Prețul este exact la ${target_price:.2f}!")

        # Update the chart data
        prices.append(current_price)
        timestamps.append(time.strftime("%H:%M:%S"))
        update_chart()

        time.sleep(5)  # Update every 5 seconds

# Function to update the chart
def update_chart():
    ax.clear()
    ax.plot(timestamps, prices, label='Preț Bitcoin', color='blue')
    ax.set_xlabel('Timp')
    ax.set_ylabel('Preț (USD)')
    ax.set_title('Bitcoin Price Live Chart')
    ax.legend()
    ax.set_xticklabels(timestamps, rotation=45, ha='right')
    canvas.draw()

# Function to set the target price
def set_target():
    global target_price, initial_price
    try:
        target_price = float(target_entry.get())
        initial_price = get_bitcoin_price()
        messagebox.showinfo("Informație", f"Prețul țintă setat: ${target_price:.2f}\nPrețul inițial al Bitcoin: ${initial_price:.2f}")
    except ValueError:
        messagebox.showerror("Eroare", "Te rog introdu un număr valid pentru prețul țintă.")

# Initialize the main window
root = tk.Tk()
root.title("Bitcoin Tracker")

# Set the application icon
icon_image = tk.PhotoImage(file="icon.png")  # Make sure to have an icon.png in the same directory
root.iconphoto(False, icon_image)

# Create and place the widgets
target_label = tk.Label(root, text="Introdu prețul țintă:")
target_label.pack()

target_entry = tk.Entry(root)
target_entry.pack()

set_button = tk.Button(root, text="Setează Prețul Țintă", command=set_target)
set_button.pack()

price_label = tk.Label(root, text="Prețul curent al Bitcoin: $0.00")
price_label.pack()

percent_label = tk.Label(root, text="Schimbare: 0.00%")
percent_label.pack()

target_label = tk.Label(root, text="")
target_label.pack()

# Initialize global variables
target_price = None
initial_price = None
prices = []
timestamps = []

# Create a figure for the chart
fig, ax = plt.subplots(figsize=(5, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Start the price update thread
price_thread = threading.Thread(target=update_price, daemon=True)
price_thread.start()

# Start the GUI event loop
root.mainloop()
