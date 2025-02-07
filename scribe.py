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
from PIL import Image, ImageTk

class Scribe:
    def __init__(self, root):
        self.root = root
        self.root.title("Scribe")
        self.root.geometry("800x600")
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create a PanedWindow
        self.paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Markdown editor
        self.text_editor = tk.Text(self.paned_window, wrap="word", font=("Arial", 12))
        self.paned_window.add(self.text_editor)
        self.text_editor.bind("<<Modified>>", self.update_preview)

        # Preview panel
        self.preview_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.preview_frame)
        self.html_preview = HTMLLabel(self.preview_frame, html="<h1></h1>")
        self.html_preview.pack(fill="both", expand=True)

        # Add this line to make the two panels even initially
        self.paned_window.paneconfig(self.text_editor, minsize=400)
        self.paned_window.paneconfig(self.preview_frame, minsize=400)

        # Bottom buttons
        self.button_frame = ttk.Frame(root)
        self.button_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="se")
        
        # Load images for buttons and resize them
        self.export_image = Image.open("export.png").resize((50, 50), Image.LANCZOS) 
        self.export_photo = ImageTk.PhotoImage(self.export_image)

        self.cheat_sheet_image = Image.open("cheatsheet.png").resize((50, 50), Image.LANCZOS) 
        self.cheat_sheet_photo = ImageTk.PhotoImage(self.cheat_sheet_image)
        
        # Create buttons with images instead of text
        ttk.Button(self.button_frame, image=self.export_photo, command=self.export_to_pdf).pack(side="right", padx=5)
        ttk.Button(self.button_frame, image=self.cheat_sheet_photo, command=self.open_cheat_sheet).pack(side="right")

    def update_preview(self, event=None):
        if self.text_editor.edit_modified():
            markdown_text = self.text_editor.get("1.0", "end-1c")
            rendered_html = markdown2.markdown(markdown_text, extras=["break-on-newline"])
            self.html_preview.set_html(rendered_html)
            self.text_editor.edit_modified(False)

    def export_to_pdf(self):
        markdown_text = self.text_editor.get("1.0", "end-1c")
        rendered_html = markdown2.markdown(markdown_text)
        html_content = BeautifulSoup(rendered_html, "html.parser")

        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        # Define custom styles
        header_styles = {
            'h1': ParagraphStyle('Header1', parent=styles['Heading1'], fontSize=18, spaceAfter=12),
            'h2': ParagraphStyle('Header2', parent=styles['Heading2'], fontSize=16, spaceAfter=10),
            'h3': ParagraphStyle('Header3', parent=styles['Heading3'], fontSize=14, spaceAfter=8),
        }
        body_style = styles['BodyText']
        blockquote_style = ParagraphStyle('Blockquote', parent=body_style, leftIndent=20, textColor='grey', italic=True)
        code_style = ParagraphStyle('Code', fontSize=10, backColor='lightgrey')

        story = []

        def process_list(element, bullet_type):
            """Helper to process ordered and unordered lists."""
            items = [ListItem(Paragraph(li.get_text(), body_style)) for li in element.find_all('li')]
            return ListFlowable(items, bulletType=bullet_type)

        for element in html_content:
            if element.name in header_styles:
                story.append(Paragraph(element.get_text(), header_styles[element.name]))
            elif element.name == 'p':
                story.append(Paragraph(element.get_text(), body_style))
            elif element.name == 'blockquote':
                story.append(Paragraph(element.get_text(), blockquote_style))
            elif element.name == 'code':
                story.append(Paragraph(element.get_text(), code_style))
            elif element.name == 'ul':
                story.append(process_list(element, 'bullet'))
            elif element.name == 'ol':
                story.append(process_list(element, '1'))
            elif element.name == 'br':
                story.append(Spacer(1, 0.2 * inch))

        try:
            doc.build(story)
            with open("output.pdf", "wb") as pdf_file:
                pdf_file.write(pdf_buffer.getvalue())
            print("PDF saved as 'output.pdf'")
        except Exception as e:
            print(f"Error exporting PDF: {e}")

    def open_cheat_sheet(self):
        cheat_sheet_window = tk.Toplevel(self.root)
        cheat_sheet_window.title("Markdown Cheat Sheet")
        cheat_sheet_window.geometry("600x400")

        cheat_sheet_content = [
            {"style": "Headers", "symbol": "# H1\n## H2\n### H3"},
            {"style": "Emphasis", "symbol": "*Italic* or _Italic_\n**Bold** or __Bold__"},
            {"style": "Lists", "symbol": "- Item 1\n- Item 2\n1. Ordered Item"},
            {"style": "Blockquote", "symbol": "> Quote text"},
            {"style": "Code", "symbol": "`Inline code`\n\n```\nBlock code\n```"},
        ]

        frame = tk.Frame(cheat_sheet_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Enable scrolling
        cheat_sheet_canvas = tk.Canvas(frame)
        cheat_sheet_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=cheat_sheet_canvas.yview)
        cheat_sheet_scrollable_frame = ttk.Frame(cheat_sheet_canvas)

        cheat_sheet_scrollable_frame.bind(
            "<Configure>",
            lambda e: cheat_sheet_canvas.configure(
                scrollregion=cheat_sheet_canvas.bbox("all")
            )
        )

        cheat_sheet_canvas.create_window((0, 0), window=cheat_sheet_scrollable_frame, anchor="nw")
        cheat_sheet_canvas.configure(yscrollcommand=cheat_sheet_scrollbar.set)

        cheat_sheet_canvas.bind_all("<MouseWheel>", lambda e: cheat_sheet_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        cheat_sheet_canvas.pack(side="left", fill="both", expand=True)
        cheat_sheet_scrollbar.pack(side="right", fill="y")

        for item in cheat_sheet_content:
            ttk.Label(cheat_sheet_scrollable_frame, text=item["style"], font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
            ttk.Label(cheat_sheet_scrollable_frame, text=item["symbol"], font=("Arial", 10), background="#f0f0f0").pack(fill="x", pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = Scribe(root)
    root.mainloop()
