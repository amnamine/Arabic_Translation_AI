import tkinter as tk
from tkinter import scrolledtext
from googletrans import Translator
import arabic_reshaper
from bidi.algorithm import get_display
import sys

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arabic Text Translator")
        self.root.geometry("800x600")

        # Text area for Arabic input
        self.input_label = tk.Label(root, text="Enter Arabic Text:")
        self.input_label.pack(pady=5)

        self.text_area = scrolledtext.ScrolledText(root, width=70, height=10)
        self.text_area.pack(pady=10)

        # Translation output area
        self.output_label = tk.Label(root, text="Translation:")
        self.output_label.pack(pady=5)

        self.output_area = scrolledtext.ScrolledText(root, width=70, height=10)
        self.output_area.pack(pady=10)

        # Buttons frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # Translation buttons
        self.to_english_btn = tk.Button(button_frame, text="Translate to English", 
                                      command=lambda: self.translate_text('en'))
        self.to_english_btn.pack(side=tk.LEFT, padx=5)

        self.to_french_btn = tk.Button(button_frame, text="Translate to French", 
                                     command=lambda: self.translate_text('fr'))
        self.to_french_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(button_frame, text="Reset", command=self.reset)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.translator = Translator()

    def translate_text(self, target_lang):
        try:
            arabic_text = self.text_area.get("1.0", tk.END).strip()
            if not arabic_text:
                self.output_area.delete("1.0", tk.END)
                self.output_area.insert("1.0", "Please enter some text to translate")
                return

            # Reshape Arabic text for display
            reshaped_text = arabic_reshaper.reshape(arabic_text)
            bidi_text = get_display(reshaped_text)

            # Translate
            translation = self.translator.translate(arabic_text, src='ar', dest=target_lang)
            self.output_area.delete("1.0", tk.END)
            self.output_area.insert("1.0", translation.text)

        except Exception as e:
            self.output_area.delete("1.0", tk.END)
            self.output_area.insert("1.0", f"An error occurred: {str(e)}")

    def reset(self):
        self.text_area.delete("1.0", tk.END)
        self.output_area.delete("1.0", tk.END)

if __name__ == "__main__":
    # sys.stdout.reconfigure(encoding='utf-8')  # Comment out or remove this line
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
