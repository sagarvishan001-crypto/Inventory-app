import psycopg
import repository

def main():
    while True:
        print("\n1. Add product 2.List 3. Update stock 4. Low stock 5. Delete 6. Quit")
        choice = input("Choose: ")
        
        if choice == "1":
            try:
                name = input("Name: ")
                price = float(input("Price: "))
                stock = int(input("Stock: "))
                new_id = repository.add_product(name, price, stock)
                print(f"Added with id {new_id}")

            except ValueError:
                print("Price must be a number and Stock a Whole number.")
            except psycopg.errors.UniqueViolation:
                print("That product already exists.")
            except psycopg.errors.CheckViolation:
                print("Price and Stock cannot be negative.")

        elif choice =="2":
            for row in repository.list_products():
                print(row)

        elif choice == "3":
            try:
                # for row in repository.list_products():
                #     print(row)
                product_id = int(input("Product id: "))
                new_stock = int(input("New stock: "))

                if repository.update_stock(product_id, new_stock) == 0:
                    print("No product with that id.")
                else:
                    print("Updated.")

            except ValueError:
                print("Please enter Whole Numbers.")
            except psycopg.errors.CheckViolation:
                print("Stock cannot be negative.")

        elif choice == "4":
            try:
                threshold = int(input("Show products with stock below: "))
                for row in repository.low_stock(threshold):
                    print(row[1],": Only",row[3]," left.")

            except ValueError:
                print("Please enter a Whole Number.")

        elif choice == "5":
            try:

                for row in repository.list_products():
                    print(row)

                product_id = int(input("Please enter product id which you want to delete: "))

                if repository.delete_product(product_id) == 0:
                    print("No product with that id.")
                else:
                    print("Deleted.")
            except ValueError:
                print("Please enter a Whole Number.")

        elif choice == "6":
            break

        else:
            print("Invalid Choice.")

if __name__ == "__main__":
    try:    
        main()
    except KeyboardInterrupt:
        print("\nGoodBye!")