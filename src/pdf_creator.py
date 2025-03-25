import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, 
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from typing import Dict, List, Optional, Union

class PDFInvoiceGenerator:
    @staticmethod
    def generate_invoice_pdf(
        invoice_id: Union[int, str], 
        customer_info: Dict, 
        items: List[Dict], 
        output_dir: str = 'invoices', 
        logo_path: Optional[str] = "images/images.jpeg",
        custom_invoice_number: Optional[str] = None
    ) -> str:
        """
        Generate a PDF invoice with enhanced formatting and consistent margins
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine invoice number
        display_invoice_number = (
            custom_invoice_number if custom_invoice_number 
            else str(invoice_id)
        )
        
        # Generate PDF path
        pdf_path = os.path.join(output_dir, f'invoice_{display_invoice_number}.pdf')
        
        # Set up document with margins
        margin = 0.25 * inch
        doc = SimpleDocTemplate(
            pdf_path, 
            pagesize=letter, 
            leftMargin=margin, 
            rightMargin=margin, 
            topMargin=margin, 
            bottomMargin=margin
        )
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Header Section with Logo, Invoice Number, and Date
        header_table_data = []
        
        # Prepare Logo
        logo = None
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
            except Exception as e:
                print(f"Warning: Could not load logo: {e}")
        
        # Today's Date
        today = datetime.now().strftime("%B %d, %Y")
        
        # Invoice Number and Date Paragraphs
        invoice_header_style = styles['Normal'].clone('InvoiceHeader')
        invoice_header_style.fontSize = 10
        invoice_header_style.alignment = 2  # Right align
        
        invoice_details = [
            Paragraph(f"<b>Invoice #{display_invoice_number}</b>", invoice_header_style),
            Paragraph(f"<b>Date: {today}</b>", invoice_header_style)
        ]
        
        # Create header row
        header_row = [
            logo or '', 
            '', 
            invoice_details
        ]
        
        header_table = Table(
            [header_row], 
            colWidths=[2*inch, 3*inch, 2*inch]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.25*inch))

        sender_info = {
            "name": "InAndOut Graphics",
            "email": "Inandoutgraphics@gmail.com",
            "phone": "786-246-9041",
            "address": "316 East 92nd St"
        }
        
        sender_details = [
            ["Sender:", ""],
            [f"Name: {sender_info['name']}", ""],
            [f"Email: {sender_info['email']}", ""],
            [f"Phone: {sender_info['phone']}", ""],
            [f"Address: {sender_info['address']}", ""]
        ]
        sender_table = Table(sender_details, colWidths=[4*inch, 2*inch])
        sender_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (0,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(sender_table)
        elements.append(Spacer(1, 0.25*inch))

        # (Customer Information, Items Table, etc.)
        
        # Customer Information
        customer_details = [
            ["Bill To:", ""],
            [f"Name: {customer_info['name']}", ""],
            [f"Email: {customer_info['email']}", ""],
            [f"Phone: {customer_info['phone']}", ""],
            [f"Address: {customer_info['address']}", ""]
        ]
        customer_table = Table(customer_details, colWidths=[4*inch, 2*inch])
        customer_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (0,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.25*inch))
        
        # Invoice Items (rest of the method remains the same)
        item_data = [['Product', 'Quantity', 'Price', 'Total', 'Description']]
        total = 0
        for item in items:
            item_total = item['quantity'] * item['price']
            total += item_total
            item_data.append([
                item['product_name'], 
                str(item['quantity']), 
                f"${item['price']:.2f}", 
                f"${item_total:.2f}", 
                item['description']
            ])
        
        # Add total row
        item_data.append(['', '', 'Total:', f'${total:.2f}', ''])
        
        item_table = Table(item_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 2*inch])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        elements.append(item_table)
        
        # Build PDF
        doc.build(elements)
        return pdf_path

# Rest of the code remains the same as in your original implementation