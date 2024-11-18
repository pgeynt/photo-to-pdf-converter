import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import os
import io
import re

# Log handler to redirect logs to Tkinter Text widget
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.configure(state='disabled')
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)

class PDFCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fotoğrafları PDF'e Dönüştürme Aracı")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.photo_paths = []
        self.pdf_path = None

        self.create_widgets()
        self.setup_logging()

    def create_widgets(self):
        # Butonlar Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.load_button = tk.Button(button_frame, text="Fotoğrafları Yükle", command=self.load_photos, width=20)
        self.load_button.grid(row=0, column=0, padx=5)

        self.process_button = tk.Button(button_frame, text="İşle", command=self.process_photos, state='disabled', width=20)
        self.process_button.grid(row=0, column=1, padx=5)

        self.save_button = tk.Button(button_frame, text="PDF'i Al", command=self.save_pdf, state='disabled', width=20)
        self.save_button.grid(row=0, column=2, padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal', length=680, mode='determinate')
        self.progress.pack(pady=20)

        # Log Bölümü
        log_label = tk.Label(self.root, text="Log:")
        log_label.pack(anchor='w', padx=10)

        log_frame = tk.Frame(self.root)
        log_frame.pack(padx=10, pady=5, fill='both', expand=True)

        self.log_text = tk.Text(log_frame, height=15, state='disabled')
        self.log_text.pack(side='left', fill='both', expand=True)

        # Scrollbar for log
        scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text['yscrollcommand'] = scrollbar.set
        scrollbar.pack(side='right', fill='y')

    def setup_logging(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Handler for the Text widget
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        text_handler.setFormatter(formatter)
        self.logger.addHandler(text_handler)

    def load_photos(self):
        file_types = [("Image Files", "*.jpeg;*.jpg;*.png")]
        paths = filedialog.askopenfilenames(title="Fotoğrafları Seç", filetypes=file_types)
        if paths:
            # Sıralama işlemi
            self.photo_paths = sorted(list(paths), key=self.extract_number)
            self.logger.info(f"{len(self.photo_paths)} fotoğraf yüklendi ve sıralandı.")
            self.process_button.config(state='normal')
            self.save_button.config(state='disabled')
        else:
            self.logger.warning("Hiç fotoğraf seçilmedi.")

    def extract_number(self, file_path):
        """
        Dosya adından sayısal kısmı çıkarır ve bu sayıya göre sıralama yapar.
        Örneğin, "Screenshot_160.png" için 160 döner.
        """
        filename = os.path.basename(file_path)
        # Sayı kısmını çekmek için regex kullanıyoruz
        match = re.search(r'(\d+)', filename)
        if match:
            return int(match.group(1))
        else:
            return 0  # Sayı bulunamazsa başa al

    def process_photos(self):
        if not self.photo_paths:
            messagebox.showwarning("Uyarı", "İşlenecek fotoğraf yok.")
            return
        self.process_button.config(state='disabled')
        self.load_button.config(state='disabled')
        self.save_button.config(state='disabled')
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.photo_paths)
        threading.Thread(target=self.create_pdf, daemon=True).start()

    def create_pdf(self):
        try:
            self.logger.info("PDF oluşturma işlemi başladı.")
            c = canvas.Canvas("temp_output.pdf", pagesize=A4)
            page_width, page_height = A4  # Sabit A4 boyutu

            for idx, img_path in enumerate(self.photo_paths, start=1):
                self.logger.info(f"İşleniyor ({idx}/{len(self.photo_paths)}): {os.path.basename(img_path)}")
                img = Image.open(img_path)

                # Eğer görüntü RGBA modunda ise RGB moduna dönüştür
                if img.mode == 'RGBA':
                    img = img.convert('RGB')

                img_width, img_height = img.size

                # Görüntüyü sayfaya sığdırmak için ölçeklendirme
                ratio = min(page_width / img_width, page_height / img_height)
                new_width = img_width * ratio
                new_height = img_height * ratio

                x = (page_width - new_width) / 2
                y = (page_height - new_height) / 2

                # In-memory görüntü kullanarak ImageReader oluştur
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)
                img_reader = ImageReader(img_byte_arr)

                # PDF'e ekle
                c.drawImage(img_reader, x, y, width=new_width, height=new_height)
                c.showPage()

                # Progress bar güncelle
                self.progress['value'] += 1

            c.save()

            # PDF dosyasını taşımak
            self.pdf_path = os.path.abspath("temp_output.pdf")
            self.logger.info("PDF oluşturma işlemi tamamlandı.")
            self.save_button.config(state='normal')
        except Exception as e:
            self.logger.error(f"PDF oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"PDF oluşturma sırasında bir hata oluştu:\n{e}")
        finally:
            self.process_button.config(state='normal')
            self.load_button.config(state='normal')

    def save_pdf(self):
        if not self.pdf_path:
            messagebox.showwarning("Uyarı", "Kaydedilecek PDF yok.")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf")],
                                                 title="PDF'i Kaydet",
                                                 initialfile="output.pdf")
        if save_path:
            try:
                os.replace(self.pdf_path, save_path)
                self.logger.info(f"PDF başarıyla kaydedildi: {save_path}")
                messagebox.showinfo("Başarılı", f"PDF başarıyla kaydedildi:\n{save_path}")
                self.pdf_path = None
                self.save_button.config(state='disabled')
            except Exception as e:
                self.logger.error(f"PDF kaydetme hatası: {e}")
                messagebox.showerror("Hata", f"PDF kaydetme sırasında bir hata oluştu:\n{e}")
        else:
            self.logger.info("PDF kaydetme işlemi iptal edildi.")

def main():
    root = tk.Tk()
    app = PDFCreatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
