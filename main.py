from crawl import aprocess_url, adownload_file
from tkinter import filedialog
from tkinter import ttk
import tkinter as tk
from tkinter import ttk
import asyncio
import os
import asyncio

current_path = os.getcwd()
path = "assets"

class App:
    async def exec(self):
        self.window = Window(asyncio.get_event_loop())
        await self.window.show()

class Window(tk.Tk):
    def __init__(self, loop):
        os.makedirs(path, exist_ok=True)
        
        self.loop = loop
        self.root = tk.Tk()
        self.root.title("AssessmentQ Crawler")
        # self.root.geometry("298x170")
        
        # Label and Entry for URL input
        self.url_label = tk.Label(text="URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.url_entry = tk.Entry(width=30)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.button_explore = tk.Button(text = "Browse Files", command = self.browseFiles)
        self.button_explore.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.label_file_explorer = tk.Label(text = "No File Selected", fg = "blue")
        self.label_file_explorer.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.download_button = tk.Button(text="Download", width=10, command=lambda: self.loop.create_task(self.download()))
        self.download_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.progressbar = ttk.Progressbar(length = 300)
        self.progressbar.grid(row=3, columnspan=2, padx=(8, 8), pady=(16, 0))
        
        # Bind the close event to self.on_close method
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set minimum size
        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight() + 10)
        
        self.root.resizable(0,0)

    
    async def show(self):
        while True:
            self.root.update()
            await asyncio.sleep(.1)
    
    def on_close(self):
        # When window is closed, cancel any running tasks and close the loop
        self.loop.stop()
        self.root.destroy()
    
    def browseFiles(self):
        filename = filedialog.askopenfilename(
            initialdir = "/",
            title = "Select a File",
            filetypes = (
                ("Text files", "*.txt*"),
            )
        )

        if filename:
            # Change label contents
            self.label_file_explorer.configure(text=filename)
        else:
            # No file selected
            self.label_file_explorer.configure(text="No File Selected")
        

    async def download(self):
        self.progressbar["value"] = 0
        
        urls = []
        if self.url_entry.get():
            urls.append(self.url_entry.get())
        
        if self.label_file_explorer.cget("text") != "No File Selected":
            with open(self.label_file_explorer.cget("text"), "r") as f:
                lines = f.read().split("\n")
                urls.extend([line.strip() for line in lines if line.strip() != ""])
        
        if urls == []:
            tk.messagebox.showerror("Error", "Please enter a URL or select a file containing URLs seperated by endline.")
            return
        
        self.download_button.config(state=tk.DISABLED)

        datas = []
        for idx, url in enumerate(urls, start = 1):
            data, save_path = await self.loop.create_task(aprocess_url(url, path))
            
            os.makedirs(save_path, exist_ok=True)
            datas.extend(data)
            self.progressbar["value"] = idx / len(urls) * 100

        agree = tk.messagebox.askyesno("Confirm", f"Found {len(datas)} files! Do you want to download?")

        if not agree:
            self.download_button.config(state=tk.NORMAL)
            self.progressbar["value"] = 0
            return
        
        self.progressbar["value"] = 0
        for idx, file in enumerate(datas, start = 1):
            self.progressbar["value"] = idx / len(datas) * 100
            await self.loop.create_task(adownload_file(file))
        
        self.download_button.config(state=tk.NORMAL)
        
        tk.messagebox.showinfo("Success", f"Downloaded {len(datas)} files to {os.path.join(current_path, path)}!")

asyncio.run(App().exec())