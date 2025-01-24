import tkinter as tk
from tkinter import ttk
import markdown2
from tkhtmlview import HTMLLabel
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.units import inch
from io import BytesIO
from bs4 import BeautifulSoup

class MarkdownToPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scribe")

        # Create main layout
        self.root.geometry("800x600")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)

        # Markdown editor (left)
        self.text_editor = tk.Text(root, wrap="word", font=("Arial", 12))
        self.text_editor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.text_editor.bind("<<Modified>>", self.update_preview)

        # Preview panel (right)
        self.preview_frame = ttk.Frame(root)
        self.preview_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.html_preview = HTMLLabel(self.preview_frame, html="<h1>Live Preview</h1>")
        self.html_preview.pack(fill="both", expand=True)

        # Bottom frame for buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="se")

        # Export to PDF button
        self.export_button = ttk.Button(self.button_frame, text="Export to PDF", command=self.export_to_pdf)
        self.export_button.pack(side="right", padx=5)

        # Markdown cheat sheet button
        self.cheat_sheet_button = ttk.Button(self.button_frame, text="Markdown Cheat Sheet", command=self.open_cheat_sheet)
        self.cheat_sheet_button.pack(side="right")

    def update_preview(self, event=None):
        # Check if text was modified
        if self.text_editor.edit_modified():
            # Convert Markdown to HTML
            markdown_text = self.text_editor.get("1.0", "end-1c")
            rendered_html = markdown2.markdown(markdown_text, extras=["break-on-newline"])
            self.html_preview.set_html(rendered_html)
            # Reset the modified flag
            self.text_editor.edit_modified(False)

    def export_to_pdf(self):
        markdown_text = self.text_editor.get("1.0", "end-1c")
        rendered_html = markdown2.markdown(markdown_text)
        html_content = BeautifulSoup(rendered_html, "html.parser")

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Define custom styles for different Markdown elements
        header1_style = ParagraphStyle(
            'Header1Style',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceAfter=12
        )

        header2_style = ParagraphStyle(
            'Header2Style',
            parent=styles['Heading2'],
            fontSize=16,
            leading=20,
            spaceAfter=10
        )

        header3_style = ParagraphStyle(
            'Header3Style',
            parent=styles['Heading3'],
            fontSize=14,
            leading=18,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['BodyText'],
            spaceAfter=12
        )

        blockquote_style = ParagraphStyle(
            'BlockquoteStyle',
            parent=styles['BodyText'],
            spaceAfter=12,
            leftIndent=20,
            textColor='grey',
            italic=True
        )

        code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Code'],
            fontSize=10,
            leading=12,
            backColor='lightgrey'
        )

        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=styles['BodyText'],
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )

        italic_style = ParagraphStyle(
            'ItalicStyle',
            parent=styles['BodyText'],
            spaceAfter=12,
            fontName='Helvetica-Oblique'
        )

        story = []
        for element in html_content:
            if element.name == 'h1':
                story.append(Paragraph(element.get_text(), header1_style))
            elif element.name == 'h2':
                story.append(Paragraph(element.get_text(), header2_style))
            elif element.name == 'h3':
                story.append(Paragraph(element.get_text(), header3_style))
            elif element.name == 'p':
                if element.find('strong'):
                    story.append(Paragraph(element.get_text(), bold_style))
                elif element.find('em'):
                    story.append(Paragraph(element.get_text(), italic_style))
                else:
                    story.append(Paragraph(element.get_text(), body_style))
            elif element.name == 'blockquote':
                story.append(Paragraph(element.get_text(), blockquote_style))
            elif element.name == 'code':
                story.append(Paragraph(element.get_text(), code_style))
            elif element.name == 'ul':
                list_items = []
                for li in element.find_all('li'):
                    list_items.append(ListItem(Paragraph(li.get_text(), body_style)))
                story.append(ListFlowable(list_items, bulletType='bullet'))
            elif element.name == 'ol':
                list_items = []
                for li in element.find_all('li'):
                    list_items.append(ListItem(Paragraph(li.get_text(), body_style)))
                story.append(ListFlowable(list_items, bulletType='I'))
            elif element.name == 'br':
                story.append(Spacer(1, 0.2 * inch))

        doc.build(story)

        with open("output.pdf", "wb") as pdf_file:
            pdf_file.write(pdf_buffer.getvalue())

    def open_cheat_sheet(self):
        cheat_sheet_window = tk.Toplevel(self.root)
        cheat_sheet_window.title("Markdown Cheat Sheet")
        cheat_sheet_window.geometry("600x400")

        cheat_sheet_frame = tk.Frame(cheat_sheet_window)
        cheat_sheet_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(cheat_sheet_frame)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(cheat_sheet_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Cheat sheet content
        cheat_sheet_content = [
            {"style": "Headers", "symbol": "# H1\n## H2\n### H3"},
            {"style": "Emphasis", "symbol": "*Italic* or _Italic_\n**Bold** or __Bold__\n***Bold Italic*** or ___Bold Italic___"},
            {"style": "Blockquotes", "symbol": "> This is a blockquote"},
            {"style": "Lists", "symbol": "- Item 1\n- Item 2\n  - Subitem 1\n  - Subitem 2\n\n1. First item\n2. Second item"},
            {"style": "Code", "symbol": "`inline code`\n\n```\nCode block\n```"},
            {"style": "Links", "symbol": "[Link text](https://example.com)"}
        ]

        for item in cheat_sheet_content:
            style_label = ttk.Label(scrollable_frame, text=item["style"], font=("Arial", 12, "bold"))
            style_label.pack(anchor="w", padx=10, pady=5)

            symbol_label = ttk.Label(scrollable_frame, text=item["symbol"], font=("Arial", 10), background="#f0f0f0")
            symbol_label.pack(fill="x", padx=10, pady=5)

        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownToPDFApp(root)
    root.mainloop()
