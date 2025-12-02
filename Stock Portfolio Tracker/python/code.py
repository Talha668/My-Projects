#                             Stock Portfolio Tracker
# Hardcoded dictionary of stock prices (in USD)
stock_prices = {
    "AAPL": 180,
    "TSLA": 250,
    "GOOG": 140,
    "MSFT": 330,
    "AMZN": 120
}

portfolio = {}  # To store user input (stock name → quantity)
total_value = 0.0

print("=== STOCK PORTFOLIO TRACKER ===")
print("Available stocks and prices:")
for stock, price in stock_prices.items():
    print(f"{stock}: ${price}")
print("\nEnter your stocks (type 'done' when finished):")

# --- Step 1: Take user input ---
while True:
    stock_name = input("Enter stock symbol (or 'done' to finish): ").upper()
    
    if stock_name == "DONE":
        break
    
    if stock_name not in stock_prices:
        print("❌ Stock not found in price list. Try again.\n")
        continue
    
    try:
        quantity = int(input(f"Enter quantity of {stock_name}: "))
        if quantity < 0:
            print("❌ Quantity cannot be negative.\n")
            continue
    except ValueError:
        print("❌ Please enter a valid number.\n")
        continue
    
    # Save to portfolio
    portfolio[stock_name] = portfolio.get(stock_name, 0) + quantity
    print(f"✅ Added {quantity} shares of {stock_name}.\n")

# --- Step 2: Calculate total investment ---
print("\n=== YOUR PORTFOLIO SUMMARY ===")
for stock, quantity in portfolio.items():
    price = stock_prices[stock]
    value = price * quantity
    total_value += value
    print(f"{stock}: {quantity} shares × ${price} = ${value:.2f}")

print(f"\n💰 Total Investment Value: ${total_value:.2f}")

# --- Step 3 (Optional): Save to file ---
save_choice = input("\nWould you like to save this report to a file? (y/n): ").lower()
if save_choice == "y":
    with open("portfolio_summary.txt", "w") as file:
        file.write("Stock Portfolio Summary\n")
        file.write("=========================\n")
        for stock, quantity in portfolio.items():
            price = stock_prices[stock]
            value = price * quantity
            file.write(f"{stock}: {quantity} × ${price} = ${value:.2f}\n")
        file.write(f"\nTotal Investment Value: ${total_value:.2f}\n")
    print("✅ Portfolio saved to 'portfolio_summary.txt'.")

print("\nThank you for using the Stock Portfolio Tracker!")
