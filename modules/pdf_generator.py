from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
import os

def generate_pdf_from_json(data, filename):
    """
    Generates a professional Certificate of Insurance PDF from JSON data.
    """
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.4*inch, bottomMargin=0.4*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # --- Logo ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "..", "static", "images", "tiarna-logo.png")
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2*inch, height=0.4*inch) # Reduced logo size
        logo.hAlign = 'LEFT'
        story.append(logo)
        story.append(Spacer(1, 0.1*inch)) # Reduced spacer

    # Custom Styles - Optimized for single page
    title_style = ParagraphStyle(
        name='Title',
        fontSize=14, # Reduced font size
        leading=18, # Reduced leading
        alignment=1,
        spaceAfter=10, # Reduced space after
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50")
    )
    
    section_header_style = ParagraphStyle(
        name='SectionHeader',
        fontSize=10, # Reduced font size
        leading=12, # Reduced leading
        spaceBefore=8, # Reduced space before
        spaceAfter=4, # Reduced space after
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#34495E")
    )
    
    field_style = ParagraphStyle(
        name='Field',
        fontSize=7, # Reduced font size
        leading=10, # Reduced leading
        fontName='Helvetica',
        textColor=colors.HexColor("#34495E")
    )
    
    field_bold_style = ParagraphStyle(
        name='FieldBold',
        fontSize=7, # Reduced font size
        leading=10, # Reduced leading
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#2C3E50")
    )
    
    # Title
    story.append(Paragraph("CERTIFICATE OF LIABILITY INSURANCE", title_style))
    story.append(Spacer(1, 0.15*inch))
    
    # Producer, Insured, Certificate Holder Section
    basic_info_data = []
    
    # Row 1: Headers
    basic_info_data.append([
        Paragraph("<b>PRODUCER</b>", field_bold_style),
        Paragraph("<b>INSURED</b>", field_bold_style),
        Paragraph("<b>CERTIFICATE HOLDER</b>", field_bold_style)
    ])
    
    # Row 2: Names
    producer_name = data.get('producer', {}).get('name', '')
    insured_name = data.get('insured', {}).get('name', '')
    cert_holder_name = data.get('certificate_holder', {}).get('name', '')
    
    basic_info_data.append([
        Paragraph(f"<b>Name:</b><br/>{producer_name}", field_style),
        Paragraph(f"<b>Name:</b><br/>{insured_name}", field_style),
        Paragraph(f"<b>Name:</b><br/>{cert_holder_name}", field_style)
    ])
    
    # Row 3: Addresses
    producer_address = data.get('producer', {}).get('address', '')
    insured_address = data.get('insured', {}).get('address', '')
    cert_holder_address = data.get('certificate_holder', {}).get('address', '')
    
    basic_info_data.append([
        Paragraph(f"<b>Address:</b><br/>{producer_address}", field_style),
        Paragraph(f"<b>Address:</b><br/>{insured_address}", field_style),
        Paragraph(f"<b>Address:</b><br/>{cert_holder_address}", field_style)
    ])
    
    basic_info_table = Table(basic_info_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    basic_info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (1, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (1, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#34495E")),
        ('LINEAFTER', (0, 0), (-2, -1), 1, colors.HexColor("#D5D8DC")),
    ]))
    
    story.append(basic_info_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Insurance Coverage Table
    story.append(Paragraph("Insurance Coverage", section_header_style))
    
    coverage_headers = [
        "TYPE OF INSURANCE",
        "INSURER",
        "POLICY NUMBER", 
        "POLICY EFFECTIVE DATE",
        "LIMITS"
    ]
    
    coverage_data = [coverage_headers]
    
    # Helper function to format effective dates
    def format_date_range(effective_date):
        if isinstance(effective_date, dict):
            start = effective_date.get('start', '')
            end = effective_date.get('end', '')
            if start or end:
                return f"{start} to {end}"
            return ""
        return str(effective_date) if effective_date else ""
    
    # Commercial General Liability
    cgl = data.get('commercial_general_liability', {})
    date_range = format_date_range(cgl.get('effective_date', {}))
    
    limits_text = []
    if cgl.get('each_occurrence'):
        limits_text.append(f"Each Occurrence: {cgl.get('each_occurrence')}")
    if cgl.get('damage_to_rented_premises'):
        limits_text.append(f"Damage to Rented Premises: {cgl.get('damage_to_rented_premises')}")
    if cgl.get('med_expense_limit'):
        limits_text.append(f"Med Expense: {cgl.get('med_expense_limit')}")
    if cgl.get('personal_adv_injury_limit'):
        limits_text.append(f"Personal & Adv Injury: {cgl.get('personal_adv_injury_limit')}")
    if cgl.get('general_aggregate_limit'):
        limits_text.append(f"General Aggregate: {cgl.get('general_aggregate_limit')}")
    if cgl.get('products_comp_op_aggregate_limit'):
        limits_text.append(f"Products-Comp/OP Agg: {cgl.get('products_comp_op_aggregate_limit')}")
    
    coverage_data.append([
        "Commercial General Liability",
        cgl.get('insurer_name', ''),
        cgl.get('policy_number', ''),
        date_range,
        '\n'.join(limits_text) if limits_text else ''
    ])
    
    if cgl.get('additional_insured'):
        coverage_data.append([
            "  - Additional Insured",
            "",
            "",
            "",
            cgl.get('additional_insured', '')
        ])
    
    if cgl.get('subrogation'):
        coverage_data.append([
            "  - Subrogation Waived",
            "",
            "",
            "",
            cgl.get('subrogation', '')
        ])
    
    if cgl.get('claims_basis'):
        coverage_data.append([
            "  - Claims Basis",
            "",
            "",
            "",
            cgl.get('claims_basis', '')
        ])
    
    # Automobile Liability
    auto = data.get('automobile_liability', {})
    date_range = format_date_range(auto.get('effective_date', {}))
    
    limits_text = []
    if auto.get('combined_single_limit'):
        limits_text.append(f"Combined Single Limit: {auto.get('combined_single_limit')}")
    
    coverage_data.append([
        "Automobile Liability",
        auto.get('insurer_name', ''),
        auto.get('policy_number', ''),
        date_range,
        '\n'.join(limits_text) if limits_text else ''
    ])
    
    if auto.get('coverage_type'):
        coverage_data.append([
            "  - Coverage Type",
            "",
            "",
            "",
            auto.get('coverage_type', '')
        ])
    
    if auto.get('additional_insured'):
        coverage_data.append([
            "  - Additional Insured",
            "",
            "",
            "",
            auto.get('additional_insured', '')
        ])
    
    if auto.get('subrogation'):
        coverage_data.append([
            "  - Subrogation Waived",
            "",
            "",
            "",
            auto.get('subrogation', '')
        ])
    
    # Umbrella Liability
    umbrella = data.get('umbrella_liability', {})
    date_range = format_date_range(umbrella.get('effective_date', {}))
    
    limits_text = []
    if umbrella.get('each_occurrence_limit'):
        limits_text.append(f"Each Occurrence: {umbrella.get('each_occurrence_limit')}")
    if umbrella.get('aggregate_limit'):
        limits_text.append(f"Aggregate: {umbrella.get('aggregate_limit')}")
    if umbrella.get('retention_amount'):
        limits_text.append(f"Retention: {umbrella.get('retention_amount')}")
    
    coverage_data.append([
        "Umbrella Liability",
        umbrella.get('insurer_name', ''),
        umbrella.get('policy_number', ''),
        date_range,
        '\n'.join(limits_text) if limits_text else ''
    ])
    
    if umbrella.get('claims_basis'):
        coverage_data.append([
            "  - Claims Basis",
            "",
            "",
            "",
            umbrella.get('claims_basis', '')
        ])
    
    # Workers Compensation
    workers_comp = data.get('workers_compensation', {})
    date_range = format_date_range(workers_comp.get('effective_date', {}))
    
    limits_text = []
    if workers_comp.get('each_accident_limit'):
        limits_text.append(f"Each Accident: {workers_comp.get('each_accident_limit')}")
    if workers_comp.get('disease_policy_limit'):
        limits_text.append(f"Disease - Policy Limit: {workers_comp.get('disease_policy_limit')}")
    if workers_comp.get('disease_each_employee_limit'):
        limits_text.append(f"Disease - Each Employee: {workers_comp.get('disease_each_employee_limit')}")
    
    coverage_data.append([
        "Workers Compensation",
        workers_comp.get('insurer_name', ''),
        workers_comp.get('policy_number', ''),
        date_range,
        '\n'.join(limits_text) if limits_text else ''
    ])
    
    if workers_comp.get('compliance'):
        coverage_data.append([
            "  - Compliance",
            "",
            "",
            "",
            workers_comp.get('compliance', '')
        ])
    
    if workers_comp.get('exclusion'):
        coverage_data.append([
            "  - Exclusion",
            "",
            "",
            "",
            workers_comp.get('exclusion', '')
        ])
    
    # Property Insurance
    prop_insurance = data.get('property_insurance', {})
    date_range = format_date_range(prop_insurance.get('effective_date', {}))
    
    coverage_data.append([
        "Property Insurance",
        prop_insurance.get('insurer', ''),
        prop_insurance.get('policy_number', ''),
        date_range,
        prop_insurance.get('limit', '')
    ])
    
    if prop_insurance.get('additional_insured'):
        coverage_data.append([
            "  - Additional Insured",
            "",
            "",
            "",
            prop_insurance.get('additional_insured', '')
        ])
    
    if prop_insurance.get('subrogation'):
        coverage_data.append([
            "  - Subrogation Waived",
            "",
            "",
            "",
            prop_insurance.get('subrogation', '')
        ])
    
    # Convert data to Paragraphs for better formatting
    formatted_coverage_data = []
    for i, row in enumerate(coverage_data):
        formatted_row = []
        for cell in row:
            if i == 0:  # Header row
                formatted_row.append(Paragraph(f"<b>{cell}</b>", field_bold_style))
            else:
                formatted_row.append(Paragraph(str(cell), field_style))
        formatted_coverage_data.append(formatted_row)
    
    coverage_table = Table(formatted_coverage_data, 
                          colWidths=[1.6*inch, 1.3*inch, 1.3*inch, 1.4*inch, 2.1*inch])
    coverage_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#34495E")),
        ('LINEABOVE', (0, 1), (-1, -1), 0.5, colors.HexColor("#D5D8DC")),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    
    story.append(coverage_table)
    story.append(Spacer(1, 0.1*inch))
    
    # Description of Operations
    story.append(Paragraph("DESCRIPTION OF OPERATIONS / LOCATIONS / VEHICLES", section_header_style))
    
    description = data.get('description_of_operations', {})
    full_text = description.get('full_text', '')
    addresses = description.get('addresses', '')
    entitlement = description.get('entitlement', '')
    
    if full_text:
        story.append(Paragraph(full_text, field_style))
        story.append(Spacer(1, 0.05*inch))
    
    if addresses:
        story.append(Paragraph(f"<b>Location Address:</b> {addresses}", field_style))
        story.append(Spacer(1, 0.05*inch))
    
    if entitlement:
        story.append(Paragraph(f"<b>Certificate Holder Entitlement:</b> {entitlement}", field_style))
        story.append(Spacer(1, 0.05*inch))
    
    if not (full_text or addresses or entitlement):
        story.append(Paragraph("No description provided", field_style))
        story.append(Spacer(1, 0.1*inch))
    
    # Notice of Cancellation
    story.append(Paragraph("CANCELLATION", section_header_style))
    notice = data.get('notice_of_cancellation', '')
    if notice:
        story.append(Paragraph(notice, field_style))
    else:
        story.append(Paragraph("No cancellation notice provided", field_style))
    
    story.append(Spacer(1, 0.15*inch))
    
    # Footer/Signature Section - Compact for single page
    signature_data = [
        [
            Paragraph("<b>CERTIFICATE HOLDER</b>", field_bold_style),
            Paragraph("<b>AUTHORIZED REPRESENTATIVE</b>", field_bold_style)
        ],
        [
            Paragraph(f"{cert_holder_name}<br/>{cert_holder_address}", field_style),
            Paragraph("Signature: ________________________<br/>Date: _______________", field_style)
        ]
    ]
    
    signature_table = Table(signature_data, colWidths=[4*inch, 3.5*inch])
    signature_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#EAECEE")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (1, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (1, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor("#34495E")),
        ('LINEAFTER', (0, 0), (0, -1), 1, colors.HexColor("#D5D8DC")),
    ]))

    story.append(signature_table)

    # --- Footer ---
    def footer(canvas, doc):
        canvas.saveState()
        footer_style = ParagraphStyle(
            name='Footer',
            fontSize=7,
            leading=10,
            textColor=colors.grey,
            alignment=1
        )
        footer_text = "Generated by Real Estate Company | Page %d" % doc.page
        p = Paragraph(footer_text, footer_style)
        w, h = p.wrap(doc.width, doc.bottomMargin)
        p.drawOn(canvas, doc.leftMargin, h)
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
