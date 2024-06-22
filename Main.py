import pdfplumber
import re
import json
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def split_into_sections(text):
    sections = defaultdict(list)
    lines = text.split('\n')
    current_title = None
    for line in lines:
        if re.match(r'^\s*[A-Z0-9][A-Za-z0-9\s,]*$', line):  # Basit bir başlık tespiti
            current_title = line.strip()
        elif current_title:
            sections[current_title].append(line.strip())
    return sections

def clean_sections(sections):
    clean_data = {}
    for title, paragraphs in sections.items():
        paragraphs = [p for p in paragraphs if p]  # Boş paragrafları temizle
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
        messagebox.showerror("ERR", "Please select PDF and JSON path.")
        return
    try:
        main(pdf_path, json_path)
        messagebox.showinfo("JSON file saved.")
    except Exception as e:
        messagebox.showerror("ERR", f"code: {str(e)}")

app = tk.Tk()
app.title("PDF To Json")

tk.Label(app, text="PDF Path:").grid(row=0, column=0, padx=10, pady=10)
pdf_entry = tk.Entry(app, width=50)
pdf_entry.grid(row=0, column=1, padx=10, pady=10)
tk.Button(app, text="Select", command=select_pdf).grid(row=0, column=2, padx=10, pady=10)

tk.Label(app, text="Json Save Path:").grid(row=1, column=0, padx=10, pady=10)
json_entry = tk.Entry(app, width=50)
json_entry.grid(row=1, column=1, padx=10, pady=10)
tk.Button(app, text="Select", command=select_json).grid(row=1, column=2, padx=10, pady=10)

tk.Button(app, text="Convert", command=convert).grid(row=2, column=0, columnspan=3, padx=10, pady=10)

app.mainloop()
