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
from gtts import gTTS
import tempfile
import pygame

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Historical Documents Translator")
        self.root.geometry("900x700")  # Reduced window size
        self.root.configure(bg='#FFFFFF')  # Clean white background

        # Configure modern styles
        self.style = {
            'bg': '#FFFFFF',  # Main background stays white
            'fg': '#2C3E50',
            'button_bg': '#3498DB',
            'button_fg': '#FFFFFF',
            'button_hover': '#2980B9',
            'text_bg': '#EDF2F7',  # Light blue-grey for text areas
            'text_fg': '#2C3E50',
            'border_color': '#CBD5E0',  # Darker border for better visibility
            'font': ('Segoe UI', 11),
            'heading_font': ('Segoe UI', 20, 'bold'),
            'label_font': ('Segoe UI', 12),
            'accent_color': '#E74C3C'
        }

        # Configure ttk styles
        style = ttk.Style()
        style.configure('TCombobox', 
                       fieldbackground=self.style['text_bg'],
                       background=self.style['text_bg'])
        style.configure('TProgressbar', 
                       thickness=8,
                       troughcolor=self.style['text_bg'],
                       background=self.style['button_bg'])

        # Main container with smaller padding
        main_frame = tk.Frame(root, bg=self.style['bg'])
        main_frame.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)

        # Header with accent line
        header_frame = tk.Frame(main_frame, bg=self.style['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        self.title_label = tk.Label(header_frame, 
                                  text="Smart Historical Documents Translator", 
                                  font=self.style['heading_font'],
                                  bg=self.style['bg'],
                                  fg=self.style['fg'])
        self.title_label.pack()
        
        # Accent line under title
        accent_line = tk.Frame(header_frame, 
                             height=3, 
                             bg=self.style['accent_color'])
        accent_line.pack(fill=tk.X, pady=(10, 0))

        # Language selection with better spacing and labels
        lang_frame = tk.Frame(main_frame, bg=self.style['bg'])
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        # Source language selection
        self.source_lang_var = tk.StringVar(value='Arabic')
        self.source_lang_label = tk.Label(lang_frame, text="From:", bg=self.style['bg'])
        self.source_lang_label.pack(side=tk.LEFT, padx=5)
        self.source_lang_combo = ttk.Combobox(lang_frame, textvariable=self.source_lang_var, 
                                            values=['Arabic', 'English', 'French', 'Latin'])
        self.source_lang_combo.pack(side=tk.LEFT, padx=5)

        # Target language selection
        self.target_lang_var = tk.StringVar(value='English')
        self.target_lang_label = tk.Label(lang_frame, text="To:", bg=self.style['bg'])
        self.target_lang_label.pack(side=tk.LEFT, padx=5)
        self.target_lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang_var, 
                                            values=['Arabic', 'English', 'French', 'Latin'])
        self.target_lang_combo.pack(side=tk.LEFT, padx=5)

        for combo in [self.source_lang_combo, self.target_lang_combo]:
            combo.configure(
                width=15,
                font=self.style['font'],
                state='readonly'  # Prevents manual editing
            )

        # Input section
        input_frame = tk.Frame(main_frame, bg=self.style['bg'])
        input_frame.pack(fill=tk.X, pady=10)

        self.input_label = tk.Label(input_frame, 
                                  text="Enter Text:", 
                                  font=self.style['label_font'],
                                  bg=self.style['bg'],
                                  fg=self.style['fg'])
        self.input_label.pack(anchor=tk.W)

        self.text_area = scrolledtext.ScrolledText(
            input_frame, 
            width=70,
            height=8,
            font=self.style['font'],
            bg=self.style['text_bg'],
            fg=self.style['text_fg'],
            padx=10,
            pady=5,
            selectbackground=self.style['button_bg'],
            selectforeground='white',
            relief=tk.SOLID,  # Changed to SOLID for better visibility
            borderwidth=1,
            border=1
        )
        self.text_area.pack(pady=3)  # Reduced padding

        # Translation output section
        output_frame = tk.Frame(main_frame, bg=self.style['bg'])
        output_frame.pack(fill=tk.X, pady=10)

        self.output_label = tk.Label(output_frame, 
                                   text="Translation:", 
                                   font=self.style['label_font'],
                                   bg=self.style['bg'],
                                   fg=self.style['fg'])
        self.output_label.pack(anchor=tk.W)

        self.output_area = scrolledtext.ScrolledText(
            output_frame, 
            width=70,
            height=8,
            font=self.style['font'],
            bg=self.style['text_bg'],
            fg=self.style['text_fg'],
            padx=10,
            pady=5,
            selectbackground=self.style['button_bg'],
            selectforeground='white',
            relief=tk.SOLID,  # Changed to SOLID for better visibility
            borderwidth=1,
            border=1
        )
        self.output_area.pack(pady=3)  # Reduced padding

        # Buttons frame with reduced padding
        button_frame = tk.Frame(main_frame, bg=self.style['bg'])
        button_frame.pack(pady=10)  # Reduced padding

        # Create styled buttons
        self.create_styled_button(button_frame, "Translate", self.translate_text)
        self.create_styled_button(button_frame, "Read Text", self.speak_text)
        self.create_styled_button(button_frame, "Load PDF", self.load_pdf)
        self.create_styled_button(button_frame, "Save as PDF", self.save_as_pdf)
        self.create_styled_button(button_frame, "Reset", self.reset)

        self.translator = Translator()

        # Initialize pygame mixer for TTS
        pygame.mixer.init()

        # Add status bar
        self.status_bar = tk.Label(main_frame, 
                                 text="Ready", 
                                 bd=1, 
                                 relief=tk.SUNKEN, 
                                 anchor=tk.W,
                                 bg=self.style['bg'],
                                 fg=self.style['fg'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Add progress bar with reduced length
        self.progress = ttk.Progressbar(main_frame, 
                                      orient="horizontal", 
                                      length=250,  # Reduced length
                                      mode="determinate")
        self.progress.pack(side=tk.BOTTOM, pady=3)  # Reduced padding
        
        # Store current file name
        self.current_file = None

    def create_styled_button(self, parent, text, command):
        btn = tk.Button(parent, 
                       text=text,
                       command=command,
                       font=('Segoe UI', 10),  # Smaller font
                       bg=self.style['button_bg'],
                       fg=self.style['button_fg'],
                       relief=tk.FLAT,
                       borderwidth=0,
                       padx=15,  # Reduced padding
                       pady=8,   # Reduced padding
                       cursor='hand2')  # Hand cursor on hover
        btn.pack(side=tk.LEFT, padx=5)  # Reduced padding
        
        # Smoother hover effect
        def on_enter(e):
            e.widget['background'] = self.style['button_hover']
        def on_leave(e):
            e.widget['background'] = self.style['button_bg']
            
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        return btn

    def translate_text(self, *args):
        try:
            # Add language mapping
            lang_map = {
                'Arabic': 'ar',
                'English': 'en',
                'French': 'fr',
                'Latin': 'la'
            }
            
            self.status_bar['text'] = "Translating..."
            self.progress['value'] = 0
            self.root.update()

            text = self.text_area.get("1.0", tk.END).strip()
            if not text:
                self.output_area.delete("1.0", tk.END)
                self.output_area.insert("1.0", "Please enter some text to translate")
                return

            source_lang = lang_map[self.source_lang_var.get()]
            target_lang = lang_map[self.target_lang_var.get()]
            
            # If source language is auto, let Google detect it
            if source_lang == 'auto':
                source_lang = None

            chunks = text.split('\n')
            total_chunks = len(chunks)
            translated_text = ""

            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    translation = self.translator.translate(chunk, 
                                                         dest=target_lang,
                                                         src=source_lang)
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

    def speak_text(self):
        try:
            text = self.output_area.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Warning", "No text to read")
                return
                
            self.status_bar['text'] = "Preparing speech..."
            self.root.update()
            
            # Create temporary file for the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Detect language from the target language combobox
            lang_map = {
                'Arabic': 'ar',
                'English': 'en',
                'French': 'fr',
                'Latin': 'la'  # Note: Latin might not be supported by gTTS
            }
            
            lang = lang_map[self.target_lang_var.get()]
            
            # Generate speech
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_path)
            
            # Play the audio
            self.status_bar['text'] = "Reading text..."
            self.root.update()
            
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Cleanup
            pygame.mixer.music.unload()
            os.unlink(temp_path)
            
            self.status_bar['text'] = "Ready"
            
        except Exception as e:
            self.status_bar['text'] = "Error reading text"
            messagebox.showerror("Error", f"Failed to read text: {str(e)}")

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
