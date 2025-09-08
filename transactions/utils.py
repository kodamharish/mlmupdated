
from django.conf import settings

from uuid import uuid4
from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient
from phonepe.sdk.pg.payments.v2.models.request.standard_checkout_pay_request import StandardCheckoutPayRequest
from phonepe.sdk.pg.common.models.request.meta_info import MetaInfo
from phonepe.sdk.pg.env import Env

#pdf
from io import BytesIO
from datetime import datetime
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from django.conf import settings



def get_phonepe_client():
    env_map = {
        "SANDBOX": Env.SANDBOX,
        "PRODUCTION": Env.PRODUCTION
    }
    return StandardCheckoutClient.get_instance(
        client_id=settings.PHONEPE_CLIENT_ID,
        client_secret=settings.PHONEPE_CLIENT_SECRET,
        client_version=settings.PHONEPE_CLIENT_VERSION,
        env=env_map.get(settings.PHONEPE_ENVIRONMENT, Env.SANDBOX),
        should_publish_events=False
    )


def initiate_payment(amount, redirect_url):
    client = get_phonepe_client()
    unique_order_id = str(uuid4())
    meta_info = MetaInfo(udf1="udf1", udf2="udf2", udf3="udf3")

    pay_request = StandardCheckoutPayRequest.build_request(
        merchant_order_id=unique_order_id,
        amount=amount,
        redirect_url=redirect_url,
        meta_info=meta_info
    )

    response = client.pay(pay_request)
    return {
        "order_id": unique_order_id,
        "merchant_order_id": unique_order_id,
        "redirect_url": response.redirect_url,
    }


# def check_payment_status(merchant_order_id):
#     client = get_phonepe_client()
#     response = client.get_order_status(merchant_order_id, details=False)
#     return response.state  # PENDING, COMPLETED, FAILED, etc.

def check_payment_status(merchant_order_id):
    client = get_phonepe_client()
    response = client.get_order_status(merchant_order_id, details=False)

    # Serialize the payment details
    payment_details = [
        {
            "payment_mode": getattr(detail, "payment_mode", None),
            "amount": getattr(detail, "amount", None),
            "transaction_id": getattr(detail, "transaction_id", None),
            "state": getattr(detail, "state", None),
            "error_code": getattr(detail, "error_code", None),
            "detailed_error_code": getattr(detail, "detailed_error_code", None),
            "instrument_type": getattr(detail, "instrumentType", None),
        }
        for detail in response.payment_details or []
    ]

    return {
        "merchant_order_id": merchant_order_id,
        "status": response.state,
        "payment_details": payment_details,
        "amount": response.amount,
        "order_id": response.order_id,
    }





#PDF 


def generate_invoice_pdf(transaction, user, property_obj, doc_number, doc_type):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    table_width = width - 2 * margin  # Fixed width for both tables

    # === Company Name at Top ===
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 50, "SHRIRAJ PROPERTY SOLUTIONS PRIVATE LIMITED")

    # === Header Section ===
    pdf.setFont("Helvetica", 9)
    
    # Address Left
    left_texts = [
        "50/4,",
        "Atal Chowk, Main Road Boria Khurd, ",
        "Near Durga Mandir,Raipur, ",
        "Chhattisgarh, 492017,",
        "India"
    ]
    for i, line in enumerate(left_texts):
        pdf.drawString(margin, height - 120 - i*12, line)
    
    # Logo in Center
    logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
    if os.path.exists(logo_path):
        logo_width = 90
        logo_height = 90
        pdf.drawImage(logo_path, (width - logo_width) / 2 - 30, height - 190, 
                     width=logo_width, height=logo_height, mask='auto')

    # GST Right
    right_texts = [
        "GSTN 22ABDCS6806R2ZV",
        "9074307248",
        "shrirajproperty00@gmail.com",
        "shrirajteam.com"
    ]
    for i, line in enumerate(right_texts):
        pdf.drawRightString(width - margin, height - 120 - i*12, line)

    # === TAX INVOICE ===
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(width - margin, height - 180, f"Tax {doc_type.title()}")

    # === Invoice Info Table ===
    pdf.setFont("Helvetica", 9)
    info_data = [
        ["REC / INV No", f"{doc_number}", "Name", f"{user.username}"],
        ["Invoice Date", f"{datetime.today().strftime('%d/%m/%Y')}", "Email", f"{user.email}"],
        ["Due Date", f"{datetime.today().strftime('%d/%m/%Y')}", "Phone", f"{user.phone_number}"],
    ]
    
    # Calculate column widths proportionally
    info_col_widths = [
        table_width * 0.20,  # Left label column (20%)
        table_width * 0.30,  # Left value column (30%)
        table_width * 0.15,  # Right label column (15%)
        table_width * 0.35   # Right value column (35%)
    ]
    
    info_table = Table(info_data, colWidths=info_col_widths)
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
    ]))
    info_table.wrapOn(pdf, width, height)
    info_table.drawOn(pdf, margin, height - 300)

    # === Property Table ===
    styles = getSampleStyleSheet()
    cell_style = styles["Normal"]
    cell_style.fontName = "Helvetica"
    cell_style.fontSize = 9
    cell_style.leading = 10
    cell_style.alignment = 1  # Center alignment

    # Create data with proper spacing for headers
    # === Property Table ===
    receipt_property_data = [
        ["S NO", "Property Title", "Property Value", "Balance Amount", "Booking Amount", "Total"],
        ["1", property_obj.property_title, f"{property_obj.total_property_value:.2f}",
         f"{transaction.remaining_amount:.2f}", f"{property_obj.booking_amount:.2f}",
         f"{property_obj.booking_amount:.2f}"]
    ]

    invoice_property_data = [
        ["S NO", "Property Title", "Property Value", "Balance", "Amount", "Total"],
        ["1", property_obj.property_title, f"{property_obj.total_property_value:.2f}",
         f"{transaction.remaining_amount:.2f}", f"{property_obj.property_value_without_booking_amount:.2f}",
         f"{property_obj.property_value_without_booking_amount:.2f}"]
    ]

    
    # Calculate column widths proportionally (same total width as info table)
    prop_col_widths = [
        table_width * 0.07,  # S NO (7%)
        table_width * 0.33,  # Property Title (33%)
        table_width * 0.15,  # Property Value (15%)
        table_width * 0.15,  # Remaining Amount (15%)
        table_width * 0.15,  # Amount (15%)
        table_width * 0.15   # Total (15%)
    ]


    if doc_type == 'receipt':
        prop_table = Table(receipt_property_data, colWidths=prop_col_widths)
    else:
        prop_table = Table(invoice_property_data, colWidths=prop_col_widths)

    
    #prop_table = Table(property_data, colWidths=prop_col_widths)
    prop_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("WORDWRAP", (1, 1), (1, 1), True),  # Wrap property title
    ]))
    
    # Position property table with consistent spacing
    prop_table.wrapOn(pdf, width, height)
    prop_table.drawOn(pdf, margin, height - 360)  # 60px below info table

    # === Footer ===
    footer_y = height - 400  # 40px below property table
    pdf.setFont("Helvetica", 9)
    footer_lines = [
        "Thank you for Trusting Us! Your support inspires us to",
        "Consistently Deliver Quality and Innovation. We Look",
        "Forward to Serving You Again.",
        "",
        "Payment Options",
        "Bank Name - State Bank of India",
        "Account no - 1234",
        "IFSC Code - 1234",
        "Branch - Bangalore",
        "",
        "Terms & Conditions",
        "1. Payment must be made within the due date from the invoice date.",
        "2. Accepted payment methods include Bank Transfer, UPI, Demand Draft (DD), and Cheque",
        "3. Cash payments are not accepted.",
        "4. Prices are exclusive of applicable taxes.",
        "5. Orders cannot be canceled once they have been processed.",
        "6. Refund or exchange of goods will be done only for defective or damaged goods upon inspection by the company.",
        "7. Responsibility ceases regarding the weight of the goods once the box tape is Tampered.",
        "",
        "For any queries, please contact",
        "Email - shrirajproperty00@gmail.com",
        "Contact - 9074307248"
    ]
    for i, line in enumerate(footer_lines):
        pdf.drawString(margin, footer_y - (i * 12), line)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    transaction.document_file.save(f"{doc_number}.pdf", ContentFile(buffer.read()))
