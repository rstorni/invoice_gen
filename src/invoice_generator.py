import logging
from typing import Dict, List
from .database import DatabaseManager
from .pdf_creator import PDFInvoiceGenerator

class InvoiceSystem:
    def __init__(self, database_path: str = 'data/invoices.db'):
        """
        Initialize invoice system with database connection
        
        Args:
            database_path (str): Path to SQLite database
        """
        logging.basicConfig(
            filename='logs/invoice_system.log', 
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )
        
        self.db_manager = DatabaseManager(database_path)
    
    def create_invoice(self, customer_info: Dict, items: List[Dict]) -> Dict:
        """
        Create a new invoice
        
        Args:
            customer_info (dict): Customer details
            items (list): List of invoice items
        
        Returns:
            dict: Invoice details including ID and PDF path
        """
        try:
            # Validate input data
            self._validate_input(customer_info, items)
            
            # Insert invoice to database
            invoice_id = self.db_manager.insert_invoice(customer_info, items)
            
            # Generate PDF
            pdf_path = PDFInvoiceGenerator.generate_invoice_pdf(
                invoice_id, 
                customer_info, 
                items
            )
            
            # Log invoice creation
            logging.info(f"Invoice {invoice_id} created successfully")
            
            return {
                'invoice_id': invoice_id,
                'pdf_path': pdf_path
            }
        
        except Exception as e:
            logging.error(f"Invoice creation failed: {e}")
            raise
    
    def _validate_input(self, customer_info: Dict, items: List[Dict]):
        """
        Validate input data before invoice creation
        
        Args:
            customer_info (dict): Customer details
            items (list): List of invoice items
        
        Raises:
            ValueError: If input data is invalid
        """
        # Check customer info
        required_customer_fields = ['name', 'email', 'phone', 'address']
        for field in required_customer_fields:
            if not customer_info.get(field):
                raise ValueError(f"Missing required customer field: {field}")
        
        # Check items
        if not items:
            raise ValueError("Invoice must contain at least one item")
        
        for item in items:
            required_item_fields = ['product_name', 'quantity', 'price', 'description']
            for field in required_item_fields:
                if field not in item:
                    raise ValueError(f"Missing required item field: {field}")
            
            if item['quantity'] <= 0 or item['price'] < 0:
                raise ValueError("Invalid quantity or price")
    
    def get_invoice(self, invoice_id: int):
        """
        Retrieve an existing invoice
        
        Args:
            invoice_id (int): Invoice identifier
        
        Returns:
            tuple: Invoice details and items
        """
        return self.db_manager.get_invoice(invoice_id)
    
    def __del__(self):
        """Close database connection when object is destroyed"""
        self.db_manager.close()

# # Example usage script
# def main():
#     invoice_system = InvoiceSystem()
    
#     customer_info = {
#         'name': 'Jane Doe',
#         'email': 'jane.doe@example.com',
#         'phone': '(555) 123-4567',
#         'address': '123 Business Street, Anytown, USA'
#     }
    
#     items = [
#         {
#             'product_name': 'Consulting Services',
#             'quantity': 5,
#             'price': 200.00,
#             'description': 'Strategic business consultation'
#         },
#         {
#             'product_name': 'Report Generation',
#             'quantity': 1,
#             'price': 750.00,
#             'description': 'Comprehensive market analysis'
#         }
#     ]
    
#     try:
#         invoice = invoice_system.create_invoice(customer_info, items)
#         print(f"Invoice created: {invoice['invoice_id']}")
#         print(f"PDF saved at: {invoice['pdf_path']}")
#     except Exception as e:
#         print(f"Error creating invoice: {e}")

# if __name__ == '__main__':
#     main()