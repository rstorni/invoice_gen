import sys
import os
from typing import List, Dict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem, 
    QPushButton, QMessageBox, QDialog, QFormLayout
)
from PyQt6.QtCore import Qt

# Relative import of invoice system
from .invoice_generator import InvoiceSystem

class AddItemDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Invoice Item")
        self.setModal(True)
        
        layout = QFormLayout()
        
        # Item input fields
        self.product_name = QLineEdit()
        self.quantity = QLineEdit()
        self.price = QLineEdit()
        self.description = QLineEdit()
        
        layout.addRow("Product Name:", self.product_name)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Price:", self.price)
        layout.addRow("Description:", self.description)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
    
    def get_item_data(self) -> Dict:
        return {
            'product_name': self.product_name.text(),
            'quantity': float(self.quantity.text()),
            'price': float(self.price.text()),
            'description': self.description.text()
        }

class InvoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Generator")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize invoice system
        self.invoice_system = InvoiceSystem()
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Customer Information Section
        customer_group = QWidget()
        customer_layout = QFormLayout()
        
        self.customer_name = QLineEdit()
        self.customer_email = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_address = QLineEdit()
        
        customer_layout.addRow("Name:", self.customer_name)
        customer_layout.addRow("Email:", self.customer_email)
        customer_layout.addRow("Phone:", self.customer_phone)
        customer_layout.addRow("Address:", self.customer_address)
        
        customer_group.setLayout(customer_layout)
        main_layout.addWidget(customer_group)
        
        # Invoice Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "Product Name", "Quantity", "Price", "Total", "Description"
        ])
        main_layout.addWidget(self.items_table)
        
        # Buttons Layout
        btn_layout = QHBoxLayout()
        
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self.add_item)
        
        remove_item_btn = QPushButton("Remove Item")
        remove_item_btn.clicked.connect(self.remove_item)
        
        generate_invoice_btn = QPushButton("Generate Invoice")
        generate_invoice_btn.clicked.connect(self.generate_invoice)
        
        btn_layout.addWidget(add_item_btn)
        btn_layout.addWidget(remove_item_btn)
        btn_layout.addWidget(generate_invoice_btn)
        
        main_layout.addLayout(btn_layout)
        
        # Set main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def add_item(self):
        dialog = AddItemDialog(self)
        if dialog.exec():
            try:
                item = dialog.get_item_data()
                row = self.items_table.rowCount()
                self.items_table.insertRow(row)
                
                # Calculate total
                total = item['quantity'] * item['price']
                
                self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
                self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
                self.items_table.setItem(row, 2, QTableWidgetItem(f"${item['price']:.2f}"))
                self.items_table.setItem(row, 3, QTableWidgetItem(f"${total:.2f}"))
                self.items_table.setItem(row, 4, QTableWidgetItem(item['description']))
            except ValueError:
                QMessageBox.warning(self, "Input Error", "Please enter valid numeric values for quantity and price.")
    
    def remove_item(self):
        current_row = self.items_table.currentRow()
        if current_row >= 0:
            self.items_table.removeRow(current_row)
    
    def generate_invoice(self):
        # Validate customer information
        customer_info = {
            'name': self.customer_name.text(),
            'email': self.customer_email.text(),
            'phone': self.customer_phone.text(),
            'address': self.customer_address.text()
        }
        
        # Validate customer fields
        if not all(customer_info.values()):
            QMessageBox.warning(self, "Missing Information", "Please fill in all customer details.")
            return
        
        # Collect invoice items
        items = []
        for row in range(self.items_table.rowCount()):
            item = {
                'product_name': self.items_table.item(row, 0).text(),
                'quantity': float(self.items_table.item(row, 1).text()),
                'price': float(self.items_table.item(row, 2).text().replace('$', '')),
                'description': self.items_table.item(row, 4).text()
            }
            items.append(item)
        
        # Validate items
        if not items:
            QMessageBox.warning(self, "No Items", "Please add at least one invoice item.")
            return
        
        try:
            # Generate invoice
            invoice = self.invoice_system.create_invoice(customer_info, items)
            
            # Show success message
            QMessageBox.information(
                self, 
                "Invoice Generated", 
                f"Invoice #{invoice['invoice_id']} created successfully!\n\n"
                f"PDF saved at: {invoice['pdf_path']}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Invoice Generation Error", 
                f"An error occurred: {str(e)}"
            )

def main():
    app = QApplication(sys.argv)
    invoice_app = InvoiceApp()
    invoice_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()