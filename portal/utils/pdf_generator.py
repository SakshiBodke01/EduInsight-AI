from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_student_report_pdf(student_profile, results):
    """
    Generates a beautifully styled ReportLab PDF result card for a student.
    Returns a BytesIO buffer containing the PDF binary.
    """
    buffer = BytesIO()
    
    # Establish page layout and settings
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Palette - Rich Deep Indigo and Accents
    PRIMARY_COLOR = colors.HexColor("#1A365D")   # Deep Slate/Navy
    SECONDARY_COLOR = colors.HexColor("#2B6CB0") # Academic Blue
    ACCENT_COLOR = colors.HexColor("#319795")    # Teal Accent
    DARK_TEXT = colors.HexColor("#2D3748")       # Charcoal
    LIGHT_BG = colors.HexColor("#F7FAFC")        # Off-white
    BORDER_COLOR = colors.HexColor("#E2E8F0")    # Grey
    
    # Define custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY_COLOR,
        alignment=0, # Left-aligned
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=SECONDARY_COLOR,
        alignment=0,
        spaceAfter=15
    )
    
    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=10,
        spaceAfter=8
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=DARK_TEXT
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=DARK_TEXT
    )
    
    center_bold = ParagraphStyle(
        'CenterBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=PRIMARY_COLOR,
        alignment=1
    )
    
    right_text = ParagraphStyle(
        'RightText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#718096"),
        alignment=2
    )

    # Header / Title Block
    story.append(Paragraph("AI-POWERED STUDENT PORTAL", title_style))
    story.append(Paragraph("Academic Performance & Prediction Report Card", subtitle_style))
    
    # Divider Rule
    header_rule = Table([['']], colWidths=[532])
    header_rule.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 2, PRIMARY_COLOR),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_rule)
    story.append(Spacer(1, 15))
    
    # Student Info Grid
    full_name = student_profile.user.get_full_name() or student_profile.user.username
    roll_no = student_profile.roll_number or "N/A"
    dept = student_profile.department
    cls = student_profile.class_name
    email = student_profile.user.email or "N/A"
    
    info_data = [
        [
            Paragraph("Student Name:", body_bold), Paragraph(full_name, body_style),
            Paragraph("Roll Number:", body_bold), Paragraph(roll_no, body_style)
        ],
        [
            Paragraph("Department:", body_bold), Paragraph(dept, body_style),
            Paragraph("Class / Semester:", body_bold), Paragraph(cls, body_style)
        ],
        [
            Paragraph("Email Address:", body_bold), Paragraph(email, body_style),
            Paragraph("Report Date:", body_bold), Paragraph("June 2026", body_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[90, 176, 90, 176])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Results Section Header
    story.append(Paragraph("Subject-Wise Grade Breakdown & Predictive Insights", header_style))
    story.append(Spacer(1, 5))
    
    # Table of Results
    # Headers
    results_data = [[
        Paragraph("Subject Code & Name", center_bold),
        Paragraph("Attendance", center_bold),
        Paragraph("Study Hrs/Wk", center_bold),
        Paragraph("Mid-Term (100)", center_bold),
        Paragraph("Assignment (100)", center_bold),
        Paragraph("Predicted Grade", center_bold),
        Paragraph("AI Prediction", center_bold)
    ]]
    
    total_attendance = 0
    total_mid = 0
    total_assign = 0
    pass_count = 0
    fail_count = 0
    
    for r in results:
        total_attendance += r.attendance_percentage
        total_mid += r.mid_term_marks
        total_assign += r.assignment_marks
        if r.predicted_status == 'Pass':
            pass_count += 1
        else:
            fail_count += 1
            
        status_color = "#319795" if r.predicted_status == 'Pass' else "#E53E3E"
        status_para = f"<font color='{status_color}'><b>{r.predicted_status}</b></font>"
        
        results_data.append([
            Paragraph(f"<b>{r.subject.code}</b> - {r.subject.name}", body_style),
            Paragraph(f"{r.attendance_percentage}%", body_style),
            Paragraph(f"{r.study_hours} hrs", body_style),
            Paragraph(f"{r.mid_term_marks}", body_style),
            Paragraph(f"{r.assignment_marks}", body_style),
            Paragraph(f"<b>{r.predicted_grade}</b>", body_style),
            Paragraph(status_para, body_style)
        ])
    
    num_results = len(results)
    avg_attendance = round(total_attendance / num_results, 1) if num_results > 0 else 0
    avg_mid = round(total_mid / num_results, 1) if num_results > 0 else 0
    avg_assign = round(total_assign / num_results, 1) if num_results > 0 else 0
    
    # Add summary row
    results_data.append([
        Paragraph("<b>Average / Summary</b>", body_bold),
        Paragraph(f"<b>{avg_attendance}%</b>", body_bold),
        Paragraph("-", body_bold),
        Paragraph(f"<b>{avg_mid}</b>", body_bold),
        Paragraph(f"<b>{avg_assign}</b>", body_bold),
        Paragraph("-", body_bold),
        Paragraph(f"<b>{pass_count} Pass / {fail_count} Fail</b>", body_bold)
    ])
    
    # Column widths summing to 532 pt
    results_table = Table(results_data, colWidths=[140, 65, 75, 75, 75, 52, 50])
    results_table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_COLOR),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('BACKGROUND', (0,-1), (-1,-1), LIGHT_BG), # summary row bg
    ])
    
    # Fix the text color for table headers in ReportLab (since styles default to black)
    # We can override with table styles or by using paragraph format. Let's adjust table styles:
    for col_idx in range(len(results_data[0])):
        results_table_style.add('TEXTCOLOR', (col_idx, 0), (col_idx, 0), colors.white)
        
    results_table.setStyle(results_table_style)
    story.append(results_table)
    story.append(Spacer(1, 20))
    
    # ML Recommendation / Insight Box
    story.append(Paragraph("AI-Generated Recommendations", header_style))
    story.append(Spacer(1, 5))
    
    # Compile text recommendation based on student marks
    rec_text = ""
    if avg_attendance < 75.0:
        rec_text += "• <b>Attendance Alert</b>: The student's average attendance is currently below 75%. Prioritizing lecture attendance is highly critical to avoid falling behind. <br/>"
    else:
        rec_text += "• <b>Attendance Strength</b>: Excellent class attendance consistency. Keep it up! <br/>"
        
    if avg_mid < 60.0 or avg_assign < 60.0:
        rec_text += "• <b>Targeted Academic Support</b>: Performance in assignments or mid-terms indicates areas of concepts that require reinforcement. We recommend attending extra-help tutorials or study group sessions. <br/>"
    else:
        rec_text += "• <b>Satisfactory Marks</b>: Solid mid-semester and assignment performance. Maintaining this rhythm will secure strong final outcomes. <br/>"
        
    if fail_count > 0:
        rec_text += "• <b>Risk Warning</b>: The ML engine has flagged one or more subjects with a predicted 'Fail' risk. An early academic intervention is recommended."
    else:
        rec_text += "• <b>Performance Prediction</b>: The predictive engine projects a successful pass across all subjects. Continue with the current study routine."
        
    rec_para = Paragraph(rec_text, body_style)
    
    rec_box = Table([[rec_para]], colWidths=[532])
    rec_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")), # Light Blue
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#BEE3F8")),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    
    story.append(rec_box)
    story.append(Spacer(1, 30))
    
    # Footer and Signature Block
    footer_text = [
        [
            Paragraph("_____________________________<br/><b>Class Teacher / Registrar</b>", body_style),
            Paragraph("_____________________________<br/><b>Head of Department</b>", body_style)
        ]
    ]
    footer_table = Table(footer_text, colWidths=[266, 266])
    footer_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 20),
    ]))
    
    story.append(KeepTogether([footer_table]))
    story.append(Spacer(1, 15))
    story.append(Paragraph("This is an AI-generated report containing predictive performance analytics. Issued by Student Portal Services.", right_text))
    
    # Build Document
    doc.build(story)
    
    buffer.seek(0)
    return buffer
