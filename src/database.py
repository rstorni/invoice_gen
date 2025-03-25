import sqlite3
from typing import Dict, List, Tuple
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, database_path: str = 'data/invoices.db'):
        """
        Initialize database connection and create tables if not exists
        
        Args:
            database_path (str): Path to SQLite database file
        """
        try:
            self.conn = sqlite3.connect(database_path)
            self.cursor = self.conn.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                customer_email TEXT,
                customer_phone TEXT,
                customer_address TEXT,
                invoice_date TEXT,
                total_amount REAL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                description TEXT,
                FOREIGN KEY(invoice_id) REFERENCES invoices(invoice_id)
            )
        ''')
        self.conn.commit()
    
    def insert_invoice(self, customer_info: Dict, items: List[Dict]) -> int:
        """
        Insert a new invoice and its associated items
        
        Args:
            customer_info (dict): Customer details
            items (list): List of invoice items
        
        Returns:
            int: Generated invoice ID
        """
        total_amount = sum(item['quantity'] * item['price'] for item in items)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Insert invoice
            self.cursor.execute('''
                INSERT INTO invoices 
                (customer_name, customer_email, customer_phone, customer_address, invoice_date, total_amount)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                customer_info['name'], 
                customer_info['email'], 
                customer_info['phone'], 
                customer_info['address'],
                current_date,
                total_amount
            ))
            
            invoice_id = self.cursor.lastrowid
            
            # Insert invoice items
            for item in items:
                self.cursor.execute('''
                    INSERT INTO invoice_items 
                    (invoice_id, product_name, quantity, price, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    invoice_id, 
                    item['product_name'], 
                    item['quantity'], 
                    item['price'], 
                    item['description']
                ))
            
            self.conn.commit()
            return invoice_id
        
        except sqlite3.Error as e:
            self.conn.rollback()
            logging.error(f"Error inserting invoice: {e}")
            raise
    
    def get_invoice(self, invoice_id: int) -> Tuple:
        """
        Retrieve a specific invoice and its items
        
        Args:
            invoice_id (int): Invoice identifier
        
        Returns:
            tuple: Invoice details and associated items
        """
        try:
            self.cursor.execute('SELECT * FROM invoices WHERE invoice_id = ?', (invoice_id,))
            invoice = self.cursor.fetchone()
            
            self.cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
            items = self.cursor.fetchall()
            
            return invoice, items
        except sqlite3.Error as e:
            logging.error(f"Error retrieving invoice: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        self.conn.close()