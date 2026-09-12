import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (Only on page 2+)
        if self._pageNumber > 1:
            self.drawString(36, 762, "Dhvani Rakshak — Technologies & Architecture Guide")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(36, 756, 576, 756)

        # Footer (All pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(36, 36, 576, 36)
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 24, page_text)
        self.drawString(36, 24, "Dhvani Rakshak • Real-Time AI Voice Clone & Fraud Defense System")
        self.restoreState()


def build_pdf():
    pdf_filename = r"c:\Users\golag\New folder\Dhvani Rakshak\Dhvani_Rakshak_Technologies_Used.pdf"
    
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    primary_color = colors.HexColor("#1A365D")   # Deep navy
    secondary_color = colors.HexColor("#2B6CB0") # Slate blue
    dark_gray = colors.HexColor("#2D3748")       # Charcoal body text
    light_bg = colors.HexColor("#F7FAFC")        # Table alternate row
    border_color = colors.HexColor("#CBD5E0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_gray,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_gray,
        leftIndent=12,
        spaceAfter=3
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white
    )

    table_body_bold = ParagraphStyle(
        'TableBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_color
    )

    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=dark_gray
    )

    story = []

    # Title & Subtitle Header
    story.append(Paragraph("🛡️ Dhvani Rakshak — Technologies Used", title_style))
    story.append(Paragraph("A Simple & Clear Guide to All Tools, Frameworks, and AI Models in the Project", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # Section 1: Simple Overview
    story.append(Paragraph("1. What is Dhvani Rakshak? (Simple Overview)", h1_style))
    overview_text = (
        "<b>Dhvani Rakshak</b> (<i>Voice Defender</i>) is an AI-powered security application created to protect "
        "users from fake voice scam calls. When someone receives a call, Dhvani Rakshak listens in real time, "
        "detects if the caller's voice is computer-generated (AI Voice Clone), scans for fraud intent, and instantly "
        "displays a simple pop-up alert on the phone screen: <b>RED</b> for dangerous scam calls, <b>YELLOW</b> for suspicious calls, "
        "and <b>GREEN</b> for genuine human calls."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 4))

    # Section 2: Detailed Breakdown
    story.append(Paragraph("2. Project Technologies & Simple Explanations", h1_style))

    # Backend
    story.append(Paragraph("A. Backend & Server Technologies (The Brain of the System)", h2_style))
    backend_techs = [
        ("Python", "The primary programming language used for all server operations, audio processing, and AI workflows."),
        ("FastAPI", "A high-performance Python web framework used to handle live voice streaming and REST API requests."),
        ("Uvicorn", "An ultra-fast server engine that runs the FastAPI application smoothly under high traffic."),
        ("WebSockets", "A real-time 2-way communication link streaming live voice audio chunks and alerts in under 250 milliseconds."),
        ("Pydantic", "A data verification tool ensuring all incoming audio data and client requests are valid and error-free."),
        ("NumPy & SciPy", "Mathematical libraries used to compute sound wave math, pitch frequencies, and signal spectrums.")
    ]
    for name, desc in backend_techs:
        story.append(Paragraph(f"• <b>{name}</b>: {desc}", bullet_style))
    story.append(Spacer(1, 4))

    # AI & ML
    story.append(Paragraph("B. AI, Machine Learning & Voice Security (The Fake Voice & Scam Detectors)", h2_style))
    ai_techs = [
        ("WavLM / AASIST AI Models", "Neural network models trained to spot artificial speech patterns and detect AI voice clones."),
        ("Whisper STT (Speech-to-Text)", "OpenAI's AI speech recognizer converting live phone call audio into written text."),
        ("Gemini NLU (Natural Language Understanding)", "Google's AI model that reads call text to detect scam attempts (asking for OTPs, urgent bank transfers, threats)."),
        ("Librosa", "An audio processing package that cleans up background noise and standardizes audio format (16kHz mono)."),
        ("Prosody & Acoustic Analyzers", "Custom engines checking speech rhythm, pitch variance, stress patterns, and unnatural pauses."),
        ("Speaker Verification & Biometrics", "Matches the caller's voice fingerprint against trusted contacts or known safe human profiles."),
        ("Score Fusion Engine", "Calculates a single risk score (0-100) by weighting synthetic voice score (60%), scam text score (25%), and fraud keywords (15%).")
    ]
    for name, desc in ai_techs:
        story.append(Paragraph(f"• <b>{name}</b>: {desc}", bullet_style))
    story.append(Spacer(1, 4))

    # Mobile & Frontend
    story.append(Paragraph("C. Mobile App & Web Interface (What the User Sees)", h2_style))
    frontend_techs = [
        ("Android (Kotlin & Java)", "Native mobile programming languages used to build the Android phone app."),
        ("Foreground Service (CallAudioService)", "A continuous Android background worker ensuring call scanning stays active without being closed by the OS."),
        ("Floating Risk Overlay (SYSTEM_ALERT_WINDOW)", "A pop-up alert window appearing directly over active phone calls with RED/YELLOW/GREEN safety badges."),
        ("WebRTC & AudioRecord", "High-performance phone audio tools capturing clear sound from speakerphone and VoIP apps like WhatsApp."),
        ("React (v19)", "A modern web framework used to build the live monitoring and administration dashboard."),
        ("Vite (v8)", "A modern frontend build tool that ensures instant page loading and smooth dashboard performance."),
        ("Capacitor", "A cross-platform tool that packages the React web dashboard directly into the native Android application."),
        ("Chart.js & React-Chartjs-2", "Data visualization packages rendering real-time risk graphs and call analytics."),
        ("Lucide Icons", "A visual graphics collection providing clean UI icons for alerts, phone calls, and security badges.")
    ]
    for name, desc in frontend_techs:
        story.append(Paragraph(f"• <b>{name}</b>: {desc}", bullet_style))
    story.append(Spacer(1, 4))

    # DevOps
    story.append(Paragraph("D. DevOps & Deployment Tools (Building & Hosting)", h2_style))
    devops_techs = [
        ("Docker & Docker Compose", "Bundles the server and AI tools into isolated virtual containers for easy deployment on any computer."),
        ("Render & Vercel", "Cloud platforms used to deploy and host the backend server APIs and frontend web app on the internet."),
        ("Postman", "An API testing environment used to verify that server endpoints function correctly under all test conditions.")
    ]
    for name, desc in devops_techs:
        story.append(Paragraph(f"• <b>{name}</b>: {desc}", bullet_style))
    story.append(Spacer(1, 8))

    # Summary Table
    story.append(Paragraph("3. Technology Quick Reference Summary Table", h1_style))

    table_data = [
        [
            Paragraph("Technology", table_header_style),
            Paragraph("Category", table_header_style),
            Paragraph("Simple Role in Dhvani Rakshak", table_header_style)
        ]
    ]

    all_tech_summary = [
        ("Python", "Backend", "Core programming language for server and AI logic"),
        ("FastAPI", "Backend", "High-speed API server handling real-time audio & response"),
        ("WebSockets", "Backend", "Live 2-way streaming connector for instant audio analysis"),
        ("WavLM / AASIST", "AI & ML", "Deepfake detector spotting computer-generated fake voices"),
        ("Whisper STT", "AI & ML", "Converts live call voice into written text transcriptions"),
        ("Gemini NLU", "AI & ML", "Analyzes call text to detect scam tactics and urgency"),
        ("Librosa / NumPy", "AI & ML", "Cleans audio and calculates voice frequencies and pitch curves"),
        ("Score Fusion", "AI & ML", "Merges voice clone, scam text, and keyword scores into 0-100 risk score"),
        ("Android (Kotlin)", "Mobile App", "Native app capturing call audio and running mobile security features"),
        ("CallAudioService", "Mobile App", "Background service keeping microphone listening active during calls"),
        ("Floating Overlay", "Mobile App", "On-screen floating alert box (Red/Yellow/Green) shown during calls"),
        ("React + Vite", "Web Frontend", "Web control panel for live monitoring and administrative management"),
        ("Capacitor", "Mobile Bridge", "Converts web interface into native Android mobile screens"),
        ("Chart.js", "Web Frontend", "Draws visual risk graphs and live telemetry charts"),
        ("Docker", "DevOps", "Packs the application into isolated containers for fast deployment"),
        ("Render / Vercel", "DevOps", "Cloud servers hosting the backend API and frontend web app")
    ]

    for tech, cat, role in all_tech_summary:
        table_data.append([
            Paragraph(tech, table_body_bold),
            Paragraph(cat, table_body_style),
            Paragraph(role, table_body_style)
        ])

    col_widths = [110, 85, 345]
    summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(summary_table)

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated formatted PDF at: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
