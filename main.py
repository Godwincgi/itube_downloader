import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pytubefix import YouTube
import threading
import re

# Initialize main window
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("500x400")
root.config(bg="#2E2E2E")

# YouTube URL Entry
tk.Label(root, text="Enter YouTube URL:", bg="#2E2E2E", fg="white").pack(pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Resolution Dropdown
tk.Label(root, text="Select Resolution:", bg="#2E2E2E", fg="white").pack(pady=10)
resolution_var = tk.StringVar(value="Highest")
resolution_dropdown = ttk.Combobox(root, textvariable=resolution_var)
resolution_dropdown['values'] = ["Highest", "720p", "480p", "360p", "Audio Only"]
resolution_dropdown.pack(pady=5)

# Progress Bar
progress = ttk.Progressbar(root, length=400, mode="determinate")
progress.pack(pady=20)

# Percentage Label
percentage_label = tk.Label(root, text="0%", bg="#2E2E2E", fg="white")
percentage_label.pack()

# Folder Selection
def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

folder_path = tk.StringVar()
tk.Button(root, text="Choose Download Folder", command=choose_folder).pack(pady=10)
tk.Label(root, textvariable=folder_path, bg="#2E2E2E", fg="white").pack()

# Function to normalize YouTube URLs
def normalize_youtube_url(url):
    short_url_pattern = r"https?://youtu\.be/([a-zA-Z0-9_-]+)"
    full_url_pattern = r"https?://(www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)"
    
    # Check if URL is a shortened URL
    short_match = re.match(short_url_pattern, url)
    if short_match:
        video_id = short_match.group(1)
        return f"https://www.youtube.com/watch?v={video_id}"
    
    # Check if URL is already in full format
    full_match = re.match(full_url_pattern, url)
    if full_match:
        return url
    
    # Return None if URL is invalid
    return None

# Download function with progress updates
def download_video():
    url = url_entry.get()
    normalized_url = normalize_youtube_url(url)
    download_location = folder_path.get() if folder_path.get() else None  # Default to current directory if not set
    
    if not normalized_url:
        messagebox.showerror("Error", "Please enter a valid YouTube URL")
        return
    
    try:
        yt = YouTube(normalized_url, on_progress_callback=on_progress)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        return
    
    # Select the appropriate stream based on resolution
    stream = None
    if resolution_var.get() == "Audio Only":
        stream = yt.streams.filter(only_audio=True).first()
    elif resolution_var.get() == "Highest":
        stream = yt.streams.get_highest_resolution()
    else:
        stream = yt.streams.filter(res=resolution_var.get()).first()
    
    if stream:
        download_thread = threading.Thread(target=stream.download, kwargs={"output_path": download_location})
        download_thread.start()
    else:
        messagebox.showerror("Error", "Resolution not available")

# Update progress bar during download
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress["value"] = (bytes_downloaded / total_size) * 100
    percentage_label.config(text=f"{int((bytes_downloaded / total_size) * 100)}%")  # Update percentage label
    root.update_idletasks()

# Download Button
download_button = tk.Button(root, text="Download", command=download_video, bg="#4CAF50", fg="white")
download_button.pack(pady=20)

root.mainloop()