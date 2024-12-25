import requests
import time
import curses

# Function to get the current Bitcoin price
def get_bitcoin_price():
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json')
    data = response.json()
    return float(data['bpi']['USD']['rate'].replace(',', ''))

# Function to calculate relative difference
def relative_difference(current_price, initial_price):
    return ((current_price - initial_price) / initial_price) * 100

# Main function to run the application
def main(stdscr):
    # Initialize color support
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text for current price
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Red text for negative change
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Cyan text for positive change

    stdscr.clear()
    stdscr.addstr("Apasă 'q' pentru a ieși din aplicație.\n")
    
    target_price = None
    initial_price = None

    while True:
        stdscr.addstr("Introdu prețul țintă (sau 'q' pentru a ieși): ")
        stdscr.refresh()

        input_str = stdscr.getstr().decode('utf-8').strip()

        if input_str.lower() == 'q':
            break  # Exit the loop if 'q' is pressed

        try:
            target_price = float(input_str)  # Convert input to float
            initial_price = get_bitcoin_price()  # Get the current Bitcoin price
            stdscr.addstr(f"Prețul țintă setat: ${target_price}\n", curses.color_pair(1))
            stdscr.addstr(f"Prețul inițial al Bitcoin: ${initial_price:.2f}\n", curses.color_pair(1))
        except ValueError:
            stdscr.addstr("Input invalid! Te rog introdu un număr valid.\n", curses.color_pair(1))
            stdscr.refresh()
            time.sleep(2)  # Wait for 2 seconds to allow the user to read the message
            continue  # Go back to the start of the loop

        while True:
            current_price = get_bitcoin_price()
            percent_change = relative_difference(current_price, initial_price)

            # Clear the previous price line
            stdscr.addstr(3, 0, " " * 50)  # Clear the line for the current price
            stdscr.addstr(3, 0, f"Prețul curent al Bitcoin: ${current_price:.2f} ", curses.color_pair(1))  # Green text

            # Display percentage change
            if percent_change > 0:
                stdscr.addstr(f" (+{percent_change:.2f}%)\n", curses.color_pair(3))  # Positive change in cyan
            else:
                stdscr.addstr(f" ({percent_change:.2f}%)\n", curses.color_pair(2))  # Negative change in red

            stdscr.refresh()
            time.sleep(5)  # Wait for 5 seconds before updating

            # Check if 'q' is pressed to exit the inner loop
            if stdscr.getch() == ord('q'):
                break  # Exit the inner loop

    stdscr.addstr("Ieșire din aplicație...\n")
    stdscr.refresh()
    time.sleep(1)  # Wait a moment to allow the user to see the exit message

if __name__ == "__main__":
    curses.wrapper(main)
