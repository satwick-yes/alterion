import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor

def create_report(parameters: dict, player=None) -> str:
    """
    Creates a professional PDF report.
    """
    title = parameters.get("title", "Report")
    sections = parameters.get("sections", [])
    
    if not sections:
        return "Error: No sections provided for the report."

    if player:
        player.write_log(f"SYS: Creating report '{title}'...")

    import re
    target_dir = parameters.get("directory")
    if not target_dir or not os.path.isdir(target_dir):
        target_dir = os.getcwd()

    safe_title = re.sub(r'[\\/*?:"<>|]', "", title[:30]).strip()
    filename = f"{safe_title.replace(' ', '_')}_Report.pdf"
    save_path = os.path.join(target_dir, filename)

    try:
        doc = SimpleDocTemplate(save_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
                                
        styles = getSampleStyleSheet()
        
        # Enhanced Styles
        styles.add(ParagraphStyle(
            name='CoverTitle', 
            alignment=TA_CENTER, 
            fontSize=28, 
            spaceAfter=30,
            textColor=HexColor('#2c3e50'),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CoverSubtitle', 
            alignment=TA_CENTER, 
            fontSize=16, 
            textColor=HexColor('#7f8c8d'),
            fontName='Helvetica-Oblique'
        ))
        
        styles.add(ParagraphStyle(
            name='EnhancedHeader',
            fontSize=16,
            spaceBefore=15,
            spaceAfter=15,
            textColor=HexColor('#ffffff'),
            backColor=HexColor('#34495e'),
            borderPadding=(10, 10, 10, 10),
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='EnhancedBody',
            alignment=TA_JUSTIFY,
            fontSize=11,
            leading=16,
            spaceAfter=10,
            textColor=HexColor('#333333'),
            fontName='Helvetica'
        ))
        
        Story = []
        
        # Cover Page
        Story.append(Spacer(1, 150))
        Story.append(Paragraph(title, styles["CoverTitle"]))
        Story.append(Paragraph("Comprehensive Analysis Report", styles["CoverSubtitle"]))
        Story.append(PageBreak())
        
        # Sections
        for section in sections:
            header = section.get("header", "")
            content = section.get("content", "")
            
            if header:
                Story.append(Paragraph(header.upper(), styles["EnhancedHeader"]))
                Story.append(Spacer(1, 10))
                
            if content:
                for paragraph in content.split('\n\n'):
                    if paragraph.strip():
                        Story.append(Paragraph(paragraph.strip(), styles["EnhancedBody"]))
                        Story.append(Spacer(1, 12))
        
        doc.build(Story)

        if player:
            player.write_log(f"SYS: Report saved to {save_path}")
            
        try:
            os.startfile(save_path)
        except Exception as open_err:
            if player:
                player.write_log(f"SYS: Could not automatically open report: {open_err}")
        
        return f"Report successfully created and saved to {save_path}."
    except Exception as e:
        return f"Error creating report: {e}"
