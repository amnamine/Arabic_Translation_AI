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

class ModificationWindow:
    def __init__(self, parent, text, callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Modify Translation")
        self.top.geometry("800x600")
        self.callback = callback
        
        # Text area for modification
        self.text_area = scrolledtext.ScrolledText(
            self.top,
            width=70,
            height=20,
            font=('Segoe UI', 11),
            bg='#EDF2F7',
            fg='#2C3E50',
            padx=10,
            pady=5
        )
        self.text_area.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.text_area.insert("1.0", text)
        
        # Validate button
        self.validate_btn = tk.Button(
            self.top,
            text="Validate Translation",
            command=self.validate,
            bg='#3498DB',
            fg='#FFFFFF',
            font=('Segoe UI', 10),
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.validate_btn.pack(pady=10)
        
        # Center the window
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')
        
    def validate(self):
        modified_text = self.text_area.get("1.0", tk.END).strip()
        self.callback(modified_text)
        self.top.destroy()

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
                                            values=['Arabic', 'English', 'French', 'Latin', 'Spanish'])
        self.source_lang_combo.pack(side=tk.LEFT, padx=5)

        # Target language selection
        self.target_lang_var = tk.StringVar(value='English')
        self.target_lang_label = tk.Label(lang_frame, text="To:", bg=self.style['bg'])
        self.target_lang_label.pack(side=tk.LEFT, padx=5)
        self.target_lang_combo = ttk.Combobox(lang_frame, textvariable=self.target_lang_var, 
                                            values=['Arabic', 'English', 'French', 'Latin', 'Spanish'])
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
        self.modify_btn = self.create_styled_button(button_frame, "Modify Translation", self.modify_translation)
        self.modify_btn.configure(state='disabled')  # Initially disabled

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

        # Audio control variables
        self.current_audio_file = None
        self.is_playing = False
        self.volume = 0.5
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)

        # Audio controls frame
        audio_frame = tk.Frame(main_frame, bg=self.style['bg'])
        audio_frame.pack(pady=5)

        # Audio control buttons
        self.play_btn = self.create_styled_button(audio_frame, "▶", self.toggle_play)
        self.save_audio_btn = self.create_styled_button(audio_frame, "Save MP3", self.save_audio)
        
        # Volume controls
        vol_frame = tk.Frame(audio_frame, bg=self.style['bg'])
        vol_frame.pack(side=tk.LEFT, padx=5)
        
        self.vol_down_btn = self.create_styled_button(vol_frame, "−", self.volume_down)
        self.vol_up_btn = self.create_styled_button(vol_frame, "+", self.volume_up)
        
        # Volume label
        self.vol_label = tk.Label(vol_frame, 
                                text=f"Volume: {int(self.volume * 100)}%",
                                bg=self.style['bg'],
                                fg=self.style['fg'])
        self.vol_label.pack(side=tk.LEFT, padx=5)

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
                'Latin': 'la',
                'Spanish': 'es'
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
            self.modify_btn.configure(state='normal')  # Enable modify button after translation
            
        except Exception as e:
            self.status_bar['text'] = "Translation error"
            self.output_area.delete("1.0", tk.END)
            self.output_area.insert("1.0", f"An error occurred: {str(e)}")
            self.modify_btn.configure(state='disabled')

    def toggle_play(self):
        if self.current_audio_file:
            if self.is_playing:
                pygame.mixer.music.pause()
                self.play_btn.configure(text="▶")
            else:
                pygame.mixer.music.unpause()
                self.play_btn.configure(text="⏸")
            self.is_playing = not self.is_playing

    def volume_up(self):
        if self.volume < 1.0:
            self.volume = min(1.0, self.volume + 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self.vol_label.configure(text=f"Volume: {int(self.volume * 100)}%")

    def volume_down(self):
        if self.volume > 0.0:
            self.volume = max(0.0, self.volume - 0.1)
            pygame.mixer.music.set_volume(self.volume)
            self.vol_label.configure(text=f"Volume: {int(self.volume * 100)}%")

    def save_audio(self):
        try:
            text = self.output_area.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Warning", "No text to save as audio")
                return
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3")],
                initialfile="translation.mp3"
            )
            
            if file_path:
                self.status_bar['text'] = "Generating audio file..."
                self.root.update()
                
                lang_map = {
                    'Arabic': 'ar',
                    'English': 'en',
                    'French': 'fr',
                    'Latin': 'la',
                    'Spanish': 'es'
                }
                
                lang = lang_map[self.target_lang_var.get()]
                tts = gTTS(text=text, lang=lang)
                tts.save(file_path)
                
                self.status_bar['text'] = "Audio saved successfully"
                messagebox.showinfo("Success", "Audio file saved successfully!")
        
        except Exception as e:
            self.status_bar['text'] = "Error saving audio"
            messagebox.showerror("Error", f"Failed to save audio: {str(e)}")

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
                'Latin': 'la',
                'Spanish': 'es'
            }
            
            lang = lang_map[self.target_lang_var.get()]
            
            # Generate speech
            tts = gTTS(text=text, lang=lang)
            tts.save(temp_path)
            
            # Update current audio file
            self.current_audio_file = temp_path
            self.is_playing = True
            self.play_btn.configure(text="⏸")
            
            # Play the audio
            self.status_bar['text'] = "Reading text..."
            self.root.update()
            
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Don't wait for playback to finish anymore
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

    def modify_translation(self):
        current_text = self.output_area.get("1.0", tk.END).strip()
        if current_text:
            ModificationWindow(self.root, current_text, self.update_translation)

    def update_translation(self, modified_text):
        self.output_area.delete("1.0", tk.END)
        self.output_area.insert("1.0", modified_text)
        self.status_bar['text'] = "Translation modified"

    def reset(self):
        self.text_area.delete("1.0", tk.END)
        self.output_area.delete("1.0", tk.END)
        self.current_file = None
        self.progress['value'] = 0
        self.status_bar['text'] = "Ready"
        self.modify_btn.configure(state='disabled')  # Disable modify button on reset
        if self.current_audio_file:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()  # Unload the music file first
            self.is_playing = False
            self.play_btn.configure(text="▶")
            try:
                if os.path.exists(self.current_audio_file):
                    os.unlink(self.current_audio_file)
            except PermissionError:
                # If file is still locked, we'll just ignore the error
                pass
            self.current_audio_file = None

if __name__ == "__main__":
    # sys.stdout.reconfigure(encoding='utf-8')  # Not needed for .exe
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
