CREATE DATABASE PharmacyDB;
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE, -- Ensures unique usernames
    password VARCHAR(255) NOT NULL, -- Stores hashed passwords
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'pharmacist', 'customer')) -- Validates role values
);
CREATE TABLE medicines (
    med_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- Ensures medicine names are unique
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL CHECK (price > 0), -- Ensures price is positive
    quantity INT NOT NULL CHECK (quantity >= 0), -- Ensures quantity is non-negative
    expiry_date DATE NOT NULL CHECK (expiry_date > CURRENT_DATE) -- Ensures expiry date is in the future
);
CREATE TABLE customers (
    cust_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE
);
CREATE TABLE orders (
    order_id INT IDENTITY(1,1) PRIMARY KEY,
    cust_id INT,
    order_date DATETIME NOT NULL,
    FOREIGN KEY (cust_id) REFERENCES customers(cust_id) ON DELETE CASCADE
);
CREATE TABLE order_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    med_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (med_id) REFERENCES medicines(med_id) ON DELETE CASCADE
);