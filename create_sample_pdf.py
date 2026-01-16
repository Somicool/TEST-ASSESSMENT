"""
Create a sample PDF for testing the RAG system
Run: python create_sample_pdf.py
"""

def create_sample_pdf():
    """Create a sample PDF with test content"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        
        filename = "sample_document.pdf"
        
        # Create PDF
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Page 1
        story.append(Paragraph("<b>Annual Report 2023</b>", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Company Overview", styles['Heading1']))
        story.append(Paragraph(
            "TechCorp Inc. is a leading provider of cloud computing services. "
            "Founded in 2010 by John Smith, the company has grown to serve over "
            "10,000 customers worldwide.", 
            styles['Normal']
        ))
        story.append(Spacer(1, 12))
        
        # Page 2
        story.append(Paragraph("Financial Performance", styles['Heading1']))
        story.append(Paragraph(
            "Q4 2023 revenue reached $2.4 billion, representing a 15% year-over-year increase. "
            "The revenue growth was driven primarily by increased demand in the enterprise segment. "
            "Operating income for the quarter was $450 million with a margin of 18.75%.",
            styles['Normal']
        ))
        story.append(Spacer(1, 12))
        
        story.append(Paragraph("Product Developments", styles['Heading1']))
        story.append(Paragraph(
            "We launched three major products in 2023: CloudStore Pro, DataPipeline Enterprise, "
            "and AI Analytics Suite. CloudStore Pro achieved 50,000 users within the first quarter "
            "of launch. Customer satisfaction scores increased to 4.8 out of 5.",
            styles['Normal']
        ))
        story.append(Spacer(1, 12))
        
        # Page 3
        story.append(Paragraph("Strategic Initiatives", styles['Heading1']))
        story.append(Paragraph(
            "Our strategic focus for 2024 includes expanding into the Asia-Pacific region, "
            "investing $100 million in AI research, and launching a new sustainability program "
            "targeting carbon neutrality by 2025. We have also partnered with three major "
            "universities for research collaboration.",
            styles['Normal']
        ))
        
        doc.build(story)
        print(f"✓ Created {filename}")
        return filename
        
    except ImportError:
        # Fallback: Create using pypdf and basic text
        print("reportlab not installed. Creating basic PDF using PyPDF2...")
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            
            # Page 1
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, "Annual Report 2023", ln=True, align='C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Company Overview", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5, 
                "TechCorp Inc. is a leading provider of cloud computing services. "
                "Founded in 2010 by John Smith, the company has grown to serve over "
                "10,000 customers worldwide.")
            pdf.ln(5)
            
            # Page 2
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Financial Performance", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5,
                "Q4 2023 revenue reached $2.4 billion, representing a 15% year-over-year increase. "
                "The revenue growth was driven primarily by increased demand in the enterprise segment. "
                "Operating income for the quarter was $450 million with a margin of 18.75%.")
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Product Developments", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5,
                "We launched three major products in 2023: CloudStore Pro, DataPipeline Enterprise, "
                "and AI Analytics Suite. CloudStore Pro achieved 50,000 users within the first quarter "
                "of launch. Customer satisfaction scores increased to 4.8 out of 5.")
            
            # Page 3
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Strategic Initiatives", ln=True)
            pdf.set_font("Arial", '', 11)
            pdf.multi_cell(0, 5,
                "Our strategic focus for 2024 includes expanding into the Asia-Pacific region, "
                "investing $100 million in AI research, and launching a new sustainability program "
                "targeting carbon neutrality by 2025. We have also partnered with three major "
                "universities for research collaboration.")
            
            filename = "sample_document.pdf"
            pdf.output(filename)
            print(f"✓ Created {filename}")
            return filename
            
        except ImportError:
            print("✗ Neither reportlab nor fpdf is installed")
            print("Please install one of them:")
            print("  pip install reportlab")
            print("  OR")
            print("  pip install fpdf2")
            return None


if __name__ == "__main__":
    print("Creating sample PDF for testing...")
    result = create_sample_pdf()
    
    if result:
        print("\n" + "="*60)
        print("✅ Sample PDF created successfully!")
        print("="*60)
        print("\nYou can now test the RAG system:")
        print(f"  python main.py {result}")
        print("\nSample questions to try:")
        print("  - What was the revenue in Q4 2023?")
        print("  - Who founded the company?")
        print("  - What products were launched in 2023?")
        print("  - What is the strategic focus for 2024?")
        print("  - Tell me about flying cars (should return 'Not found')")
        print("="*60)
    else:
        print("\n❌ Failed to create sample PDF")
