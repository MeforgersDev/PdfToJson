import pdfplumber
import re
import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            text += page.extract_text()
            progress_var.set((i + 1) / total_pages * 100)
            app.update_idletasks()
    return text

def clean_text(text):
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Remove special characters
    text = re.sub(r'[^A-Za-z0-9\s,.\-]', '', text)
    return text

def split_into_sections(text):
    sections = defaultdict(list)
    lines = text.split('\n')
    current_title = None
    for line in lines:
        line = clean_text(line)  # Apply cleaning here
        if re.match(r'^\s*[A-Z0-9][A-Za-z0-9\s,]*$', line):  # Simple title detection
            current_title = line.strip()
        elif current_title:
            sections[current_title].append(line.strip())
    return sections

def clean_sections(sections):
    clean_data = {}
    for title, paragraphs in sections.items():
        paragraphs = [p for p in paragraphs if p]  # Remove empty paragraphs
        if paragraphs:
            clean_data[title] = ' '.join(paragraphs)
    return clean_data

def save_to_json(data, json_path):
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

def main(pdf_path, json_path):
    text = extract_text_from_pdf(pdf_path)
    sections = split_into_sections(text)
    clean_data = clean_sections(sections)
    save_to_json(clean_data, json_path)

def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, file_path)
    if file_path:
        json_default_path = file_path.replace(".pdf", ".json")
        json_entry.delete(0, tk.END)
        json_entry.insert(0, json_default_path)

def select_json():
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    json_entry.delete(0, tk.END)
    json_entry.insert(0, file_path)

def convert():
    pdf_path = pdf_entry.get()
    json_path = json_entry.get()
    if not pdf_path or not json_path:
        messagebox.showerror("Error", "Please select both PDF and JSON files.")
        return
    try:
        progress_var.set(0)
        main(pdf_path, json_path)
        progress_var.set(100)
        messagebox.showinfo("Success", "PDF successfully converted to JSON.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during conversion: {str(e)}")

app = tk.Tk()
app.title("PDF to JSON Converter")

tk.Label(app, text="PDF File:").grid(row=0, column=0, padx=10, pady=10)
pdf_entry = tk.Entry(app, width=50)
pdf_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Select", command=select_pdf).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="JSON File:").grid(row=1, column=0, padx=10, pady=10)
json_entry = tk.Entry(app, width=50)
json_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(app, text="Select", command=select_json).grid(row=1, column=2, padx=10, pady=10)

tk.Button(app, text="Convert", command=convert).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, variable=progress_var, maximum=100)
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky='ew')

app.mainloop()
