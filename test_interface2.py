import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
from googletrans import Translator
import arabic_reshaper
from bidi.algorithm import get_display
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from PyPDF2 import PdfReader
import os.path

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arabic Text Translator")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f2f5')

        # Configure styles
        self.style = {
            'bg': '#f0f2f5',
            'fg': '#1a1a1a',
            'button_bg': '#4a90e2',
            'button_fg': 'white',
            'button_hover': '#357abd',
            'text_bg': 'white',
            'font': ('Segoe UI', 10),
            'heading_font': ('Segoe UI', 12, 'bold')
        }

        # Main container
        main_frame = tk.Frame(root, bg=self.style['bg'])
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame, bg=self.style['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = tk.Label(header_frame, 
                                  text="Arabic Text Translator", 
                                  font=self.style['heading_font'],
                                  bg=self.style['bg'],
                                  fg=self.style['fg'])
        self.title_label.pack()

        # Input section
        input_frame = tk.Frame(main_frame, bg=self.style['bg'])
        input_frame.pack(fill=tk.X, pady=10)

        self.input_label = tk.Label(input_frame, 
                                  text="Enter Arabic Text:", 
                                  font=self.style['font'],
                                  bg=self.style['bg'],
                                  fg=self.style['fg'])
        self.input_label.pack(anchor=tk.W)

        self.text_area = scrolledtext.ScrolledText(input_frame, 
                                                 width=80, 
                                                 height=10,
                                                 font=self.style['font'],
                                                 bg=self.style['text_bg'],
                                                 relief=tk.SOLID,
                                                 borderwidth=1)
        self.text_area.pack(pady=5)

        # Translation output section
        output_frame = tk.Frame(main_frame, bg=self.style['bg'])
        output_frame.pack(fill=tk.X, pady=10)

        self.output_label = tk.Label(output_frame, 
                                   text="Translation:", 
                                   font=self.style['font'],
                                   bg=self.style['bg'],
                                   fg=self.style['fg'])
        self.output_label.pack(anchor=tk.W)

        self.output_area = scrolledtext.ScrolledText(output_frame, 
                                                   width=80, 
                                                   height=10,
                                                   font=self.style['font'],
                                                   bg=self.style['text_bg'],
                                                   relief=tk.SOLID,
                                                   borderwidth=1)
        self.output_area.pack(pady=5)

        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=self.style['bg'])
        button_frame.pack(pady=20)

        # Create styled buttons
        self.create_styled_button(button_frame, "Translate to English", 
                                lambda: self.translate_text('en'))
        self.create_styled_button(button_frame, "Translate to French", 
                                lambda: self.translate_text('fr'))
        self.create_styled_button(button_frame, "Load PDF", 
                                self.load_pdf)
        self.create_styled_button(button_frame, "Save as PDF", 
                                self.save_as_pdf)
        self.create_styled_button(button_frame, "Reset", 
                                self.reset)

        self.translator = Translator()

        # Add status bar
        self.status_bar = tk.Label(main_frame, 
                                 text="Ready", 
                                 bd=1, 
                                 relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg=self.style['bg'],
                                 fg=self.style['fg'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add progress bar
        self.progress = ttk.Progressbar(main_frame, 
                                      orient="horizontal", 
                                      length=300, 
                                      mode="determinate")
        self.progress.pack(side=tk.BOTTOM, pady=5)
        
        # Store current file name
        self.current_file = None

    def create_styled_button(self, parent, text, command):
        btn = tk.Button(parent, 
                       text=text,
                       command=command,
                       font=self.style['font'],
                       bg=self.style['button_bg'],
                       fg=self.style['button_fg'],
                       relief=tk.RAISED,
                       borderwidth=2,
                       padx=15,
                       pady=8)
        btn.pack(side=tk.LEFT, padx=5)
        btn.bind('<Enter>', lambda e: btn.configure(bg=self.style['button_hover']))
        btn.bind('<Leave>', lambda e: btn.configure(bg=self.style['button_bg']))
        return btn

    def translate_text(self, target_lang):
        try:
            self.status_bar['text'] = "Translating..."
            self.progress['value'] = 0
            self.root.update()

            text = self.text_area.get("1.0", tk.END).strip()
            if not text:
                self.output_area.delete("1.0", tk.END)
                self.output_area.insert("1.0", "Please enter some text to translate")
                return

            # Split text into chunks for progress indication
            chunks = text.split('\n')
            total_chunks = len(chunks)
            translated_text = ""

            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    translation = self.translator.translate(chunk, dest=target_lang)
                    translated_text += translation.text + "\n"
                    self.progress['value'] = ((i + 1) / total_chunks) * 100
                    self.root.update()

            self.output_area.delete("1.0", tk.END)
            self.output_area.insert("1.0", translated_text)
            
            self.status_bar['text'] = f"Translation completed"
            
        except Exception as e:
            self.status_bar['text'] = "Translation error"
            self.output_area.delete("1.0", tk.END)
            self.output_area.insert("1.0", f"An error occurred: {str(e)}")

    def load_pdf(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            if file_path:
                self.current_file = os.path.basename(file_path)
                self.progress['value'] = 0
                self.status_bar['text'] = f"Loading {self.current_file}..."
                self.root.update()

                # Extract text from PDF
                reader = PdfReader(file_path)
                text = ""
                total_pages = len(reader.pages)
                
                for i, page in enumerate(reader.pages):
                    text += page.extract_text() + "\n"
                    self.progress['value'] = ((i + 1) / total_pages) * 100
                    self.root.update()

                # Display extracted text
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", text)
                
                self.status_bar['text'] = f"Successfully loaded {self.current_file}"
                messagebox.showinfo("Success", f"PDF '{self.current_file}' loaded successfully!")
                
        except Exception as e:
            self.status_bar['text'] = "Error loading PDF"
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")

    def save_as_pdf(self):
        try:
            translation = self.output_area.get("1.0", tk.END).strip()
            if not translation:
                messagebox.showwarning("Warning", "No translation to save")
                return

            suggested_name = ""
            if self.current_file:
                base_name = os.path.splitext(self.current_file)[0]
                suggested_name = f"{base_name}_translated.pdf"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialfile=suggested_name
            )
            
            if file_path:
                self.status_bar['text'] = "Saving PDF..."
                self.progress['value'] = 0
                self.root.update()

                # Create PDF using reportlab
                pdf_canvas = canvas.Canvas(file_path, pagesize=letter)
                pdf_canvas.setFont("Helvetica", 12)
                width, height = letter
                y_position = height - 50

                lines = translation.splitlines()
                total_lines = len(lines)

                for i, line in enumerate(lines):
                    pdf_canvas.drawString(50, y_position, line)
                    y_position -= 15

                    if y_position < 50:
                        pdf_canvas.showPage()
                        pdf_canvas.setFont("Helvetica", 12)
                        y_position = height - 50

                    self.progress['value'] = ((i + 1) / total_lines) * 100
                    self.root.update()

                pdf_canvas.save()
                self.status_bar['text'] = "PDF saved successfully"
                messagebox.showinfo("Success", f"PDF saved successfully as {os.path.basename(file_path)}")
                
        except Exception as e:
            self.status_bar['text'] = "Error saving PDF"
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")

    def reset(self):
        self.text_area.delete("1.0", tk.END)
        self.output_area.delete("1.0", tk.END)
        self.current_file = None
        self.progress['value'] = 0
        self.status_bar['text'] = "Ready"

if __name__ == "__main__":
    # sys.stdout.reconfigure(encoding='utf-8')  # Not needed for .exe
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
