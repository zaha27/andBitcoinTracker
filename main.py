import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
import time
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Function to get the current Bitcoin price
def get_bitcoin_price():
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
    data = response.json()
    return round(float(data['bpi']['USD']['rate'].replace(',', '')), 1)  # Round to 1 decimal place

# Function to update the price in the GUI
def update_price():
    global target_prices, initial_price, prices, timestamps
    while True:
        current_price = get_bitcoin_price()
        percent_change = ((current_price - initial_price) / initial_price) * 100 if initial_price else 0
        price_label.config(text=f"Prețul curent al Bitcoin: ${current_price:.1f}", fg='lime')
        percent_label.config(text=f"Schimbare: {percent_change:.2f}%", fg='lime')

        # Check each target price
        for target_price, details in target_prices.items():
            if current_price > target_price and not details['alerted_above']:
                messagebox.showinfo("Informație", f"Prețul '{details['name']}' a trecut peste prețul țintă: ${target_price:.1f}!")
                details['alerted_above'] = True  # Set the flag to indicate the alert has been triggered
                details['alerted_below'] = False  # Reset the below alert flag
                details['has_exceeded'] = True  # Mark that the target has been exceeded
            elif current_price < target_price and not details['alerted_below']:
                # Only notify if the target has been exceeded
                if details.get('has_exceeded', False):
                    messagebox.showinfo("Informație", f"Prețul '{details['name']}' a scăzut sub prețul țintă: ${target_price:.1f}!")
                    details['alerted_below'] = True  # Set the flag to indicate the alert has been triggered
                    details['alerted_above'] = False  # Reset the above alert flag
            
            # Calculate the difference to target price
            difference_to_target = target_price - current_price
            if difference_to_target > 0:
                target_change_label.config(text=f"Prețul '{details['name']}' trebuie să crească cu ${difference_to_target:.1f} pentru a ajunge la ${target_price:.1f}.", fg='lime')
            elif difference_to_target < 0:
                target_change_label.config(text=f"Prețul '{details['name']}' trebuie să scadă cu ${-difference_to_target:.1f} pentru a ajunge la ${target_price:.1f}.", fg='lime')
            else:
                target_change_label.config(text=f"Prețul '{details['name']}' este exact la prețul țintă!", fg='lime')

            # Update the table
            update_alert_table()

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
    global initial_price, first_notification
    try:
        target_price = round(float(target_entry.get()), 1)  # Round target price to 1 decimal place
        alert_name = alert_name_entry.get()  # Get the alert name
        if alert_name == "":
            messagebox.showerror("Eroare", "Te rog introdu un nume valid pentru alertă.")
            return
        initial_price = get_bitcoin_price()
        target_prices[target_price] = {'name': alert_name, 'alerted_above': False, 'alerted_below': False, 'has_exceeded': False}  # Add new target price with alert status
        
        # Skip the first notification
        if not first_notification:
            first_notification = True
        else:
            messagebox.showinfo("Informație", f"Prețul țintă '{alert_name}' setat: ${target_price:.1f}\nPrețul inițial al Bitcoin: ${initial_price:.1f}")
        
        target_change_label.config(text="")  # Clear previous messages
        update_alert_table()  # Update the alert table
    except ValueError:
        messagebox.showerror("Eroare", "Te rog introdu un număr valid pentru prețul țintă.")

# Function to update the alert table
def update_alert_table():
    for row in alert_table.get_children():
        alert_table.delete(row)  # Clear existing rows

    # Display alerts in the order they were added
    for target_price, details in target_prices.items():
        current_price = get_bitcoin_price()
        difference_to_target = target_price - current_price
        percent_change = (difference_to_target / target_price) * 100 if target_price != 0 else 0
        alert_table.insert("", "end", values=(details['name'], f"${target_price:.1f}", f"{percent_change:.2f}%"))

# Function to delete the selected alert
def delete_alert():
    selected_item = alert_table.selection()
    if not selected_item:
        messagebox.showwarning("Atenție", "Te rog selectează o alertă pentru a o șterge.")
        return

    # Get the selected alert's name
    item = selected_item[0]
    alert_name = alert_table.item(item, 'values')[0]

    # Find and delete the corresponding target price from the dictionary
    for target_price in list(target_prices.keys()):
        if target_prices[target_price]['name'] == alert_name:
            del target_prices[target_price]
            break

    alert_table.delete(item)  # Remove the selected item from the Treeview
    messagebox.showinfo("Informație", f"Alertele '{alert_name}' au fost șterse.")

# Initialize global variables
target_prices = {}  # Dictionary to hold target prices and their alert statuses
initial_price = None
prices = []
timestamps = []
first_notification = False  # Flag to skip the first notification

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

# New entry for alert name
alert_name_label = tk.Label(root, text="Introdu numele alertei:", bg='black', fg='lime')
alert_name_label.pack(pady=(10, 0))  # Add padding for spacing

alert_name_entry = tk.Entry(root, bg='black', fg='lime', insertbackground='lime')  # Set entry field background and text color
alert_name_entry.pack(pady=(5, 10))  # Add padding for spacing

# Create a button with a black background and black text
set_button = tk.Button(root, text="Setează Prețul Țintă", command=set_target, bg='black', fg='lime', borderwidth=2, relief='solid', highlightbackground='black')
set_button.pack(pady=(5, 10))  # Add padding for spacing

# Create a button to delete the selected alert
delete_button = tk.Button(root, text="Șterge Alerte", command=delete_alert, bg='black', fg='lime', borderwidth=2, relief='solid', highlightbackground='black')
delete_button.pack(pady=(5, 10))  # Add padding for spacing

price_label = tk.Label(root, text="Prețul curent al Bitcoin: $0.0", bg='black', fg='lime')
price_label.pack(pady=(5, 0))

percent_label = tk.Label(root, text="Schimbare: 0.00%", bg='black', fg='lime')
percent_label.pack(pady=(5, 0))

# Create a label for displaying target change messages
target_change_label = tk.Label(root, text="", bg='black', fg='lime')
target_change_label.pack(pady=(5, 0))

# Create a frame for the alert table
alert_frame = tk.Frame(root)
alert_frame.pack(pady=(10, 0))

# Create a Treeview for alerts
alert_table = ttk.Treeview(alert_frame, columns=("Nume", "Preț", "Schimbare"), show='headings', height=5)
alert_table.heading("Nume", text="Nume")
alert_table.heading("Preț", text="Preț")
alert_table.heading("Schimbare", text="Schimbare (%)")
alert_table.pack()

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