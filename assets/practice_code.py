import sys
PRODUCTS = [["Adele", "135", "6", "0"], ["Gruel", "6.9", "3", "5"]]
PASSWORD = "w"
user_input = None

while user_input is not PASSWORD:
    user_input = input("Enter Password >:( ")

choice = None
choices = ["1", "2", "3", "4"]
while choice not in choices:
    choice = input("""1. make a sale
2. change the price of an item
3. create list of products to be ordered
4. exit

Choice: """)

if choice == "1":
    column = int(input("Column: "))
    row = int(input("Row: "))
    choice = PRODUCTS[row][column]
    print(f"""Product name      Qty      Price
{choice}                 1        PRICE

Total                             TOTAL""")
elif choice == "4":
    sys.exit()
