from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from datetime import datetime

def generate_pdf_report(prediction_history, results, shap_image_path, lime_image_path=None):
    if os.environ.get('VERCEL'):
        reports_dir = os.path.join('/tmp', 'reports')
    else:
        reports_dir = os.path.join('static', 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"report_{prediction_history.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    
    elements = []
    
    # Header
    elements.append(Paragraph("Disease Prediction System Report", title_style))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", subtitle_style))
    patient_info = [
        ['Name:', prediction_history.patient_info.name, 'Age:', str(prediction_history.patient_info.age)],
        ['Gender:', prediction_history.patient_info.gender, 'Date:', prediction_history.date_predicted.strftime('%Y-%m-%d')]
    ]
    t1 = Table(patient_info, colWidths=[100, 150, 100, 150])
    t1.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t1)
    elements.append(Spacer(1, 20))
    
    # Medical Report & Clinical Notes (if available)
    if hasattr(prediction_history, 'medical_report_notes') and prediction_history.medical_report_notes:
        elements.append(Paragraph("Clinical Medical Report & Observations", subtitle_style))
        report_meta = []
        if hasattr(prediction_history, 'medical_report_type') and prediction_history.medical_report_type:
            report_meta.append(['Report Type:', str(prediction_history.medical_report_type)])
        if hasattr(prediction_history, 'medical_report_file') and prediction_history.medical_report_file:
            report_meta.append(['Attached File:', os.path.basename(str(prediction_history.medical_report_file))])
        
        if report_meta:
            t_meta = Table(report_meta, colWidths=[120, 280])
            t_meta.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t_meta)
            elements.append(Spacer(1, 10))
            
        elements.append(Paragraph(str(prediction_history.medical_report_notes), normal_style))
        elements.append(Spacer(1, 20))
    
    # Prediction Results
    elements.append(Paragraph("Prediction Results", subtitle_style))
    results_data = [['Disease', 'Probability']]
    for disease, prob in results.items():
        results_data.append([disease, f"{prob}%"])
        
    t2 = Table(results_data, colWidths=[250, 150])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f2f2f2')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 20))
    
    # SHAP Feature Importance
    if shap_image_path and os.path.exists(shap_image_path):
        elements.append(Paragraph("Explainable AI: SHAP Global Feature Contribution", subtitle_style))
        elements.append(Paragraph("SHAP (SHapley Additive exPlanations) computes game-theoretic contribution values for each vital sign and clinical symptom.", normal_style))
        elements.append(Spacer(1, 8))
        img = Image(shap_image_path, width=420, height=224)
        elements.append(img)
        elements.append(Spacer(1, 20))

    # LIME Local Explanations
    if lime_image_path and os.path.exists(lime_image_path):
        elements.append(Paragraph("Explainable AI: LIME Local Decision Rules", subtitle_style))
        elements.append(Paragraph("LIME (Local Interpretable Model-agnostic Explanations) builds a local surrogate linear model around this patient to identify the exact biometric thresholds driving the diagnosis.", normal_style))
        elements.append(Spacer(1, 8))
        img_lime = Image(lime_image_path, width=420, height=224)
        elements.append(img_lime)
        elements.append(Spacer(1, 20))
        
    doc.build(elements)
    
    return filepath
