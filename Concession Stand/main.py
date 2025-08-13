menu = {
        "pizza": 800,
        "berger": 400,
        "chips": 300,
        "wings": 350,
        "beverage": 150,
        "salad": 600
}

cart = []
total = 0

print("--------MENU--------")
for key, value in menu.items():
    print(f"{key:10}: Rs{value:.2f}")
print("--------------------")

while True:
    food = input("Select an item (q to quit): ").lower()
    if food == "q":
        break
    elif food in menu:
        cart.append(food)
        print(f"added {food} to your order.")
    else:
        print(f"Sorry we don't have {food}. Please choose from the menu.")

print("\n-------YOUR ORDER-------")
for food in cart:
    price = menu[food]
    total += price
    print(f"{food:10}: Rs{price:.2f}")

print("---------------")
print(f"Total is: Rs{total:.2f}")
