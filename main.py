import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os

class YouTubeDownloader:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("YouTube Video Downloader")
        self.window.geometry("600x400")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.window, 
            text="YouTube Video Downloader",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # URL Input
        self.url_label = ctk.CTkLabel(self.window, text="Enter YouTube URL:")
        self.url_label.pack(pady=5)
        
        self.url_entry = ctk.CTkEntry(self.window, width=500, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.pack(pady=5)
        
        # Download Path
        self.path_frame = ctk.CTkFrame(self.window, fg_color="transparent")
        self.path_frame.pack(pady=10)
        
        self.path_entry = ctk.CTkEntry(self.path_frame, width=400, placeholder_text="Download location")
        self.path_entry.pack(side="left", padx=5)
        self.path_entry.insert(0, os.path.expanduser("~/Downloads"))
        
        self.browse_btn = ctk.CTkButton(self.path_frame, text="Browse", width=80, command=self.browse_folder)
        self.browse_btn.pack(side="left")
        
        # Quality Selection
        self.quality_label = ctk.CTkLabel(self.window, text="Select Quality:")
        self.quality_label.pack(pady=5)
        
        self.quality_var = ctk.StringVar(value="best")
        self.quality_menu = ctk.CTkOptionMenu(
            self.window, 
            values=["best", "1080p", "720p", "480p", "360p", "audio_only"],
            variable=self.quality_var,
            width=200
        )
        self.quality_menu.pack(pady=5)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            self.window, 
            text="Download", 
            command=self.start_download,
            width=200,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.download_btn.pack(pady=20)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(self.window, width=500)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(self.window, text="Ready to download", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, folder)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0%').strip('%')
                self.progress_bar.set(float(percent) / 100)
                self.status_label.configure(text=f"Downloading: {percent}%")
            except:
                pass
        elif d['status'] == 'finished':
            self.progress_bar.set(1)
            self.status_label.configure(text="Processing... Almost done!")
    
    def download_video(self):
        url = self.url_entry.get().strip()
        download_path = self.path_entry.get().strip()
        quality = self.quality_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not os.path.exists(download_path):
            messagebox.showerror("Error", "Download path does not exist")
            return
        
        try:
            self.download_btn.configure(state="disabled")
            self.status_label.configure(text="Starting download...")
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if quality == "audio_only":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif quality == "best":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                ydl_opts['format'] = f'bestvideo[height<={quality[:-1]}]+bestaudio/best[height<={quality[:-1]}]'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.status_label.configure(text="Download completed!")
            messagebox.showinfo("Success", "Video downloaded successfully!")
            
        except Exception as e:
            self.status_label.configure(text="Download failed")
            messagebox.showerror("Error", f"Download failed: {str(e)}")
        
        finally:
            self.download_btn.configure(state="normal")
            self.progress_bar.set(0)
    
    def start_download(self):
        # Run download in separate thread to prevent UI freezing
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        thread.start()
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.run()