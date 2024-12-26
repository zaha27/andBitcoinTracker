import requests
import tkinter as tk
from tkinter import messagebox
import threading
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio

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
        price_label.config(text=f"Prețul curent al Bitcoin: ${current_price:.2f}", fg='lime')
        percent_label.config(text=f"Schimbare: {percent_change:.2f}%", fg='lime')
        
        if target_price is not None:
            difference_to_target = target_price - current_price
            if difference_to_target > 0:
                target_label.config(text=f"Prețul trebuie să crească cu ${difference_to_target:.2f} ({(difference_to_target / current_price) * 100:.2f}%) pentru a ajunge la ${target_price:.2f}.", fg='lime')
            elif difference_to_target < 0:
                target_label.config(text=f"Prețul trebuie să scadă cu ${-difference_to_target:.2f} ({(-difference_to_target / current_price) * 100:.2f}%) pentru a ajunge la ${target_price:.2f}.", fg='lime')
            else:
                target_label.config(text=f"Prețul este exact la ${target_price:.2f}!", fg='lime')

        # Update the chart data
        prices.append(current_price)
        timestamps.append(time.strftime("%H:%M:%S"))
        update_chart()

        time.sleep(5)  # Update every 5 seconds

# Function to update the chart
def update_chart():
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=timestamps, y=prices, mode='lines+markers', name='Preț Bitcoin', line=dict(color='lime')))
    
    fig.update_layout(
        title='Bitcoin Price Live Chart',
        xaxis_title='Timp',
        yaxis_title='Preț (USD)',
        plot_bgcolor='black',  # Set chart background to black
        paper_bgcolor='black',  # Set paper background to black
        font=dict(color='lime'),
        xaxis=dict(showgrid=True, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridcolor='gray')
    )
    
    # Render the plot in the Tkinter window
    pio.write_image(fig, 'chart.png')  # Save the figure as an image
    img = tk.PhotoImage(file='chart.png')  # Load the image
    chart_label.config(image=img)
    chart_label.image = img  # Keep a reference to avoid garbage collection

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
root.configure(bg='black')  # Set the background color of the application to black

# Set the application icon
icon_image = tk.PhotoImage(file="icon.png")  # Make sure to have an icon.png in the same directory
root.iconphoto(False, icon_image)

# Create and place the widgets
target_label = tk.Label(root, text="Introdu prețul țintă:", bg='black', fg='lime')
target_label.pack(pady=(10, 0))  # Add padding for spacing

target_entry = tk.Entry(root, bg='black', fg='lime', insertbackground='lime')  # Set entry field background and text color
target_entry.pack(pady=(5, 10))  # Add padding for spacing

# Create a button with a black background and neon green text
set_button = tk.Button(root, text="Setează Prețul Țintă", command=set_target, bg='black', fg='lime', borderwidth=2, relief='solid')
set_button.pack(pady=(5, 10))  # Add padding for spacing

# Set the button's highlight properties to simulate a black border
set_button.config(highlightbackground='black', highlightcolor='black', highlightthickness=2)

price_label = tk.Label(root, text="Prețul curent al Bitcoin: $0.00", bg='black', fg='lime')
price_label.pack(pady=(5, 0))

percent_label = tk.Label(root, text="Schimbare: 0.00%", bg='black', fg='lime')
percent_label.pack(pady=(5, 0))

target_label = tk.Label(root, text="", bg='black', fg='lime')
target_label.pack(pady=(5, 0))

# Initialize global variables
target_price = None
initial_price = None
prices = []
timestamps = []

# Create a frame for the chart
chart_frame = tk.Frame(root)
chart_frame.pack()

# Create a label for the chart
chart_label = tk.Label(chart_frame, bg='black')
chart_label.pack()

# Start the price update thread
price_thread = threading.Thread(target=update_price, daemon=True)
price_thread.start()

# Start the GUI event loop
root.mainloop()
