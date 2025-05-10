import json
import os
import datetime
import mysql.connector
import customtkinter as ctk

class Medicine:
    def __init__(self, med_id, name, category, price, quantity, expiry_date):
        self.med_id = med_id
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity
        self.expiry_date = expiry_date  # YYYY-MM-DD format

    def to_dict(self):
        return {
            'med_id': self.med_id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'quantity': self.quantity,
            'expiry_date': self.expiry_date,
        }

    @staticmethod
    def from_dict(data):
        return Medicine(
            data['med_id'],
            data['name'],
            data['category'],
            data['price'],
            data['quantity'],
            data['expiry_date']
        )


class Customer:
    def __init__(self, cust_id, name, phone):
        self.cust_id = cust_id
        self.name = name
        self.phone = phone

    def to_dict(self):
        return {
            'cust_id': self.cust_id,
            'name': self.name,
            'phone': self.phone,
        }

    @staticmethod
    def from_dict(data):
        return Customer(data['cust_id'], data['name'], data['phone'])


class Order:
    def __init__(self, order_id, cust_id, items, order_date):
        self.order_id = order_id
        self.cust_id = cust_id
        self.items = items  # list of dicts {med_id, quantity, price}
        self.order_date = order_date

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'cust_id': self.cust_id,
            'items': self.items,
            'order_date': self.order_date,
        }

    @staticmethod
    def from_dict(data):
        return Order(
            data['order_id'],
            data['cust_id'],
            data['items'],
            data['order_date']
        )


class PharmacyApp:
    def __init__(self):
        self.medicines_file = 'medicines.json'
        self.customers_file = 'customers.json'
        self.orders_file = 'orders.json'
        self.medicines = self.load_medicines()
        self.customers = self.load_customers()
        self.orders = self.load_orders()
        self.next_med_id = self.get_next_med_id()
        self.next_cust_id = self.get_next_cust_id()
        self.next_order_id = self.get_next_order_id()
    
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="pharmacy_inventory"
        )
        self.cursor = self.db.cursor(dictionary=True)

    # --- Load and Save Data ---

    def load_medicines(self):
        try:
            self.cursor.execute("SELECT * FROM medicines")
            rows = self.cursor.fetchall()
            return [Medicine(*row) for row in rows]  # Assuming row order matches constructor
        except Exception as e:
            print(f"Error loading medicines from database: {e}")
            return []

    def save_medicines(self):
        with open(self.medicines_file, 'w') as f:
            json.dump([m.to_dict() for m in self.medicines], f, indent=4)

    def load_customers(self):
        if not os.path.exists(self.customers_file):
            return []
        with open(self.customers_file, 'r') as f:
            data = json.load(f)
            return [Customer.from_dict(c) for c in data]

    def save_customers(self):
        with open(self.customers_file, 'w') as f:
            json.dump([c.to_dict() for c in self.customers], f, indent=4)

    def load_orders(self):
        if not os.path.exists(self.orders_file):
            return []
        with open(self.orders_file, 'r') as f:
            data = json.load(f)
            return [Order.from_dict(o) for o in data]

    def save_orders(self):
        with open(self.orders_file, 'w') as f:
            json.dump([o.to_dict() for o in self.orders], f, indent=4)

    # --- ID Generators ---

    def get_next_med_id(self):
        if not self.medicines:
            return 1
        return max(m.med_id for m in self.medicines) + 1

    def get_next_cust_id(self):
        if not self.customers:
            return 1
        return max(c.cust_id for c in self.customers) + 1

    def get_next_order_id(self):
        if not self.orders:
            return 1
        return max(o.order_id for o in self.orders) + 1

    # --- Medicine Management ---

    def add_medicine(self, name, category, price, quantity, expiry_date):

        try:
            query = """
            INSERT INTO medicines (name, category, price, quantity, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
        """
            self.cursor.execute(query, (name, category, price, quantity, expiry_date))
            self.db.commit()
            print("Medicine added successfully.")
        except Exception as e:
            self.db.rollback()  # Important to rollback on failure
            print(f"Error adding medicine: {e}")

        # print("\n--- Add New Medicine ---")
        # name = input("Medicine name: ").strip()
        # category = input("Category: ").strip()
        # price = self.input_float("Price per unit: ")
        # quantity = self.input_int("Quantity in stock: ")
        # expiry_date = self.input_date("Expiry date (YYYY-MM-DD): ")

        # med = Medicine(self.next_med_id, name, category, price, quantity, expiry_date)
        # self.medicines.append(med)
        # self.next_med_id += 1
        # self.save_medicines()
        # print(f"Medicine'{name}'added with ID{med.med_id}.")

    def update_medicine(self):
        print("\n--- Update Medicine ---")
        med_id = self.input_int("Enter medicine ID to update: ")
        med = self.find_medicine_by_id(med_id)
        if not med:
            print("Medicine not found.")
            return

        print(f"Updating medicine: {med.name} (ID: {med.med_id})")
        print("Leave input blank to keep current value.")

        name = input(f"Name [{med.name}]: ").strip()
        if name:
            med.name = name
        category = input(f"Category [{med.category}]: ").strip()
        if category:
            med.category = category
        price = input(f"Price [{med.price}]: ").strip()
        if price:
            try:
                med.price = float(price)
            except ValueError:
                print("Invalid price input. Skipping update.")
        quantity = input(f"Quantity [{med.quantity}]: ").strip()
        if quantity:
            try:
                med.quantity = int(quantity)
            except ValueError:
                print("Invalid quantity input. Skipping update.")
        expiry_date = input(f"Expiry date [{med.expiry_date}]: ").strip()
        if expiry_date:
            try:
                datetime.datetime.strptime(expiry_date, '%Y-%m-%d')
                med.expiry_date = expiry_date
            except ValueError:
                print("Invalid date format. Skipping update.")

        self.save_medicines()
        print(f"Medicine ID {med.med_id} updated.")

    def delete_medicine(self):
        print("\n--- Delete Medicine ---")
        med_id = self.input_int("Enter medicine ID to delete: ")
        med = self.find_medicine_by_id(med_id)
        if not med:
            print("Medicine not found.")
            return
        confirm = input(f"Are you sure you want to delete {med.name}? (y/n): ").lower()
        if confirm == 'y':
            self.medicines = [m for m in self.medicines if m.med_id != med_id]
            self.save_medicines()
            print("Medicine deleted.")
        else:
            print("Deletion canceled.")

    def list_medicines(self):
        print("\n--- Medicine Inventory ---")
        if not self.medicines:
            print("No medicines in inventory.")
            return
        print(f"{'ID':<4} {'Name':<20} {'Category':<15} {'Price':<10} {'Qty':<6} {'Expiry':<12}")
        print("-"*70)
        for med in self.medicines:
            print(f"{med.med_id:<4} {med.name:<20} {med.category:<15} ${med.price:<9.2f} {med.quantity:<6} {med.expiry_date:<12}")

    def search_medicines(self):
        print("\n--- Search Medicines ---")
        search_term = input("Enter name or category keyword to search: ").strip().lower()
        results = [m for m in self.medicines if search_term in m.name.lower() or search_term in m.category.lower()]
        if not results:
            print("No medicines found matching the search term.")
            return
        print(f"Found {len(results)} medicine(s):")
        print(f"{'ID':<4} {'Name':<20} {'Category':<15} {'Price':<10} {'Qty':<6} {'Expiry':<12}")
        print("-"*70)
        for med in results:
            print(f"{med.med_id:<4} {med.name:<20} {med.category:<15} ${med.price:<9.2f} {med.quantity:<6} {med.expiry_date:<12}")

    def find_medicine_by_id(self, med_id):
        for med in self.medicines:
            if med.med_id == med_id:
                return med
        return None

    # --- Customer Management ---

    def add_customer(self):
        print("\n--- Add New Customer ---")
        name = input("Customer name: ").strip()
        phone = input("Phone number: ").strip()
        cust = Customer(self.next_cust_id, name, phone)
        self.customers.append(cust)
        self.next_cust_id += 1
        self.save_customers()
        print(f"Customer '{name}' added with ID {cust.cust_id}.")

    def list_customers(self):
        print("\n--- Customer List ---")
        if not self.customers:
            print("No customers found.")
            return
        print(f"{'ID':<4} {'Name':<20} {'Phone':<15}")
        print("-"*40)
        for c in self.customers:
            print(f"{c.cust_id:<4} {c.name:<20} {c.phone:<15}")

    def find_customer_by_id(self, cust_id):
        for cust in self.customers:
            if cust.cust_id == cust_id:
                return cust
        return None

    # --- Order Management ---

    def create_order(self):
        print("\n--- Create New Order ---")
        self.list_customers()
        cust_id = self.input_int("Enter customer ID for the order: ")
        customer = self.find_customer_by_id(cust_id)
        if not customer:
            print("Customer not found.")
            return
        order_items = []
        while True:
            self.list_medicines()
            med_id = self.input_int("Enter medicine ID to add to order (0 to finish): ")
            if med_id == 0:
                break
            med = self.find_medicine_by_id(med_id)
            if not med:
                print("Medicine not found.")
                continue
            quantity = self.input_int(f"Enter quantity for {med.name}: ")
            if quantity > med.quantity:
                print(f"Insufficient stock. Available quantity: {med.quantity}")
                continue
            # Add item to order and reduce stock
            order_items.append({'med_id': med.med_id, 'name': med.name, 'quantity': quantity, 'price': med.price})
            med.quantity -= quantity
            print(f"Added {quantity} x {med.name} to order.")
        if not order_items:
            print("Order is empty. Cancelling.")
            return

        order_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order = Order(self.next_order_id, cust_id, order_items, order_date)
        self.orders.append(order)
        self.next_order_id += 1
        self.save_orders()
        self.save_medicines()
        print(f"Order ID {order.order_id} created successfully.")
        self.print_invoice(order)

    def list_orders(self):
        print("\n--- Orders List ---")
        if not self.orders:
            print("No orders found.")
            return
        print(f"{'ID':<4} {'Customer':<20} {'Date':<20} {'Items Count':<12}")
        print("-"*60)
        for o in self.orders:
            customer = self.find_customer_by_id(o.cust_id)
            cust_name = customer.name if customer else "Unknown"
            print(f"{o.order_id:<4} {cust_name:<20} {o.order_date:<20} {len(o.items):<12}")

    def print_invoice(self, order):
        print("\n--- Invoice ---")
        customer = self.find_customer_by_id(order.cust_id)
        print(f"Order ID: {order.order_id}")
        print(f"Customer: {customer.name if customer else 'Unknown'}")
        print(f"Date: {order.order_date}")
        print("-"*40)
        total = 0
        print(f"{'Medicine':<20} {'Qty':<6} {'Unit Price':<12} {'Subtotal':<10}")
        for item in order.items:
            subtotal = item['quantity'] * item['price']
            total += subtotal
            print(f"{item['name']:<20} {item['quantity']:<6} ${item['price']:<11.2f} ${subtotal:<9.2f}")
        print("-"*40)
        print(f"{'Total':<38} ${total:.2f}")
        print("-"*40)

    # --- Utility Inputs ---

    def input_int(self, prompt):
        while True:
            try:
                val = int(input(prompt))
                return val
            except ValueError:
                print("Invalid input. Please enter an integer.")

    def input_float(self, prompt):
        while True:
            try:
                val = float(input(prompt))
                return val
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def input_date(self, prompt):
        while True:
            date_str = input(prompt).strip()
            try:
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                print("Invalid date format. Please enter date in YYYY-MM-DD format.")

    # --- Stock alerts ---

    def low_stock_alert(self):
        low_stock = [m for m in self.medicines if m.quantity <= 5]
        if low_stock:
            print("\n*** Low Stock Alert ***")
            for med in low_stock:
                print(f"Medicine '{med.name}' (ID: {med.med_id}) has low stock: {med.quantity} left.")
            print("*** Please reorder soon ***\n")

    def expired_stock_alert(self):
        today = datetime.datetime.today()
        expired = []
        for m in self.medicines:
            exp_date = datetime.datetime.strptime(m.expiry_date, '%Y-%m-%d')
            if exp_date < today:
                expired.append(m)
        if expired:
            print("\n*** Expired Medicines Alert ***")
            for med in expired:
                print(f"Medicine '{med.name}' (ID: {med.med_id}) expired on {med.expiry_date}.")
            print("*** Please remove expired stock immediately ***\n")

    # --- Main Menu ---

    def main_menu(self):
        while True:
            print("\n===== Pharmacy Management System =====")
            print("1. Manage Medicines")
            print("2. Manage Customers")
            print("3. Create Order")
            print("4. View Orders")
            print("5. Stock Alerts")
            print("6. Exit")
            choice = input("Choose an option (1-6): ")
            if choice == '1':
                self.medicines_menu()
            elif choice == '2':
                self.customers_menu()
            elif choice == '3':
                self.create_order()
            elif choice == '4':
                self.list_orders()
            elif choice == '5':
                self.low_stock_alert()
                self.expired_stock_alert()
            elif choice == '6':
                print("Exiting the Pharmacy Management System. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def medicines_menu(self):
        while True:
            print("\n--- Medicines Menu ---")
            print("1. List Medicines")
            print("2. Add Medicine")
            print("3. Update Medicine")
            print("4. Delete Medicine")
            print("5. Search Medicines")
            print("6. Back to Main Menu")
            choice = input("Choose an option (1-6): ")
            if choice == '1':
                self.list_medicines()
            elif choice == '2':
                self.add_medicine()
            elif choice == '3':
                self.update_medicine()
            elif choice == '4':
                self.delete_medicine()
            elif choice == '5':
                self.search_medicines()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Please try again.")

    def customers_menu(self):
        while True:
            print("\n--- Customers Menu ---")
            print("1. List Customers")
            print("2. Add Customer")
            print("3. Back to Main Menu")
            choice = input("Choose an option (1-3): ")
            if choice == '1':
                self.list_customers()
            elif choice == '2':
                self.add_customer()
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")


if __name__ == '__main__':
    app = PharmacyApp()
    app.low_stock_alert()
    app.expired_stock_alert()
    app.main_menu()