import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import subprocess
import threading


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.selected_streams = None
        self.video_info = None
        self.style = ttk.Style(self.root)
        self.download_path = os.getcwd() # Default download path to current working directory

        # Initialize widgets creation
        self.create_widgets()

        # Set initial theme state to start in dark mode.
        # We'll set self.dark_mode to False initially, so the first call to toggle_theme() will set it to True and apply the dark mode styles.
        self.dark_mode = False
        self.toggle_theme() # Apply dark mode styles

        # Show welcome page on startup
        self.show_welcome_page()

    # Show welcome page on startup
    def show_welcome_page(self):
        welcome_window = tk.Toplevel(self.root)
        welcome_window.title("Welcome to YouTube Downloader")
        welcome_window.geometry("500x610") # Adjust size as needed
        welcome_window.transient(self.root) # Keep it on top of main window
        welcome_window.grab_set() # Prevent interaction with the main window

        # Apply theme to welcome window
        bg_color = "#2e2e2e" if self.dark_mode else "SystemButtonFace"
        fg_color = "white" if self.dark_mode else "black"
        welcome_window.configure(bg=bg_color)

        instructions_frame = ttk.Frame(welcome_window, padding="10")
        instructions_frame.pack(expand=True, fill="both")

        instructions_text = """
Welcome to the YouTube Downloader!

How to Use:
1. Paste a YouTube video or YouTube Music link into the 'YouTube URL' field.
2. Click 'Fetch Streams'.
3. Select your desired download option ('Video' or 'Audio').
   The list below will update with available formats.
4. Choose a stream from the 'Available Streams' list.
5. (Optional) Click 'Change Path' to select where the file will be saved.
   The default is your current working directory.
6. Click 'Download Selected Stream'.
7. Wait for the download to complete. A message will confirm success or failure.

Tips:
- Toggle between Dark/Light mode using the ☀️/🌙 button.
- For audio downloads, FFmpeg is required to convert to MP3.
  Ensure FFmpeg is installed and in your system's PATH if you encounter issues.
  You can download it from https://ffmpeg.org/download.html or open command prompt and type 'winget install ffmpeg'.
- For video downloads, FFmpeg is not required.
- If you encounter any issues, please report them on the GitHub page.

Enjoy downloading!
                """

        # Use a Text widget for better formatting and scrollability if needed
        text_widget = tk.Text(instructions_frame, wrap="word", height=15, width=60,
                              background=bg_color, foreground=fg_color,
                              bd=0, highlightthickness=0)  # Remove border
        text_widget.insert(tk.END, instructions_text.strip())
        text_widget.config(state="disabled")  # Make it read-only
        text_widget.pack(pady=10, padx=10, expand=True, fill="both")

        # Styling for Text widget scrollbar if it were enabled
        # scroll = ttk.Scrollbar(instructions_frame, command=text_widget.yview)
        # text_widget['yscrollcommand'] = scroll.set
        # scroll.pack(side="right", fill="y")

        ok_button = ttk.Button(instructions_frame, text="Got it!", command=welcome_window.destroy)
        ok_button.pack(pady=10)

        # Center the welcome window
        self.root.update_idletasks()  # Ensure main window dimensions are up-to-date
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (welcome_window.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (welcome_window.winfo_height() // 2)
        welcome_window.geometry(f"+{x}+{y}")

    def create_widgets(self):
        # Dark mode toggle button in top-left corner
        self.mode_button = ttk.Button(self.root, text="", command=self.toggle_theme, width=3)
        # Using pack with side "right" to keep it small and at the top
        self.mode_button.pack(anchor="nw", padx=10, pady=5)

        # URL entry
        frame_url = ttk.LabelFrame(self.root, text="YouTube URL")
        frame_url.pack(padx=10, pady=10, fill="x")
        self.link_entry = ttk.Entry(frame_url, width=60)
        self.link_entry.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ttk.Button(frame_url, text="Fetch Streams", command=self.fetch_streams).pack(side="left", padx=5)

        # Option for Video vs Audio using radio buttons
        frame_option = ttk.LabelFrame(self.root, text="Download Options")
        frame_option.pack(padx=10, pady=10, fill="x")
        self.type = tk.StringVar(value="Video")
        ttk.Radiobutton(frame_option, text="Video", variable=self.type, value="Video").pack(side="left", padx=5)
        ttk.Radiobutton(frame_option, text="Audio", variable=self.type, value="Audio").pack(side="left", padx=5)

        # Download path selection
        frame_path = ttk.LabelFrame(self.root, text="Download location")
        frame_path.pack(padx=10, pady=10, fill="x")
        self.path_label = ttk.Label(frame_path, text=f"Download Path: {self.download_path}")
        self.path_label.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ttk.Button(frame_path, text="Change Path", command=self.select_download_path).pack(side="left", padx=5)

        # Listbox to display available streams and quality information
        frame_streams = ttk.LabelFrame(self.root, text="Available Streams")
        frame_streams.pack(padx=10, pady=10, fill="both", expand=True)
        self.streams_listbox = tk.Listbox(frame_streams, height=10, width=60)
        self.streams_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(frame_streams, orient="vertical", command=self.streams_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.streams_listbox.config(yscrollcommand=scrollbar.set)

        # Download button
        ttk.Button(self.root, text="Download Selected Stream", command=self.download_selected).pack(pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=5, padx=10, fill="x")

    # Download path selection dialog
    def select_download_path(self):
        '''Opens a dialog to select the download path.'''
        path = filedialog.askdirectory(initialdir=self.download_path, title="Select Download Path")
        if path: # If a path is selected
            self.download_path = path
            self.path_label.config(text=f"Download Path: {self.download_path}")


    # Add dark mode toggle functionality
    def toggle_theme(self):
        """Toggle between light mode and dark mode."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            # Dark mode settings
            dark_bg = "#2e2e2e"
            dark_fg = "white"
            entry_bg = "#3e3e3e"

            self.root.configure(bg=dark_bg)
            self.style.theme_use('clam') # Using 'clam' or 'alt' or 'default' can give more control

            self.style.configure(".", background=dark_bg, foreground=dark_fg) # General style for all ttk widgets
            self.style.configure("TLabel", background=dark_bg, foreground=dark_fg)
            self.style.configure("TButton", background="#555555", foreground=dark_fg) # Slightly different bg for button
            self.style.map("TButton", background=[('active', '#666666')])
            self.style.configure("TEntry", fieldbackground=entry_bg, foreground=dark_fg, insertcolor=dark_fg)
            self.style.configure("TLabelframe", background=dark_bg, foreground=dark_fg, bordercolor=dark_fg)
            self.style.configure("TLabelframe.Label", background=dark_bg, foreground=dark_fg)
            self.style.configure("TRadiobutton", background=dark_bg, foreground=dark_fg)
            self.style.map("TRadiobutton",
                           background=[('active', dark_bg)],
                           indicatorcolor=[('selected', dark_fg), ('!selected', dark_fg)]) # Style indicator too
            self.style.configure("TScrollbar", background=dark_bg, troughcolor=entry_bg)
            self.style.configure("TProgressbar", background=entry_bg, troughcolor=dark_bg)


            # For tk.Listbox (not a ttk widget, so configure directly)
            self.streams_listbox.configure(
                background=entry_bg,
                foreground=dark_fg,
                selectbackground="#004080", # Darker blue for selection
                selectforeground=dark_fg
            )
            # Update path_label color for dark mode
            if hasattr(self, 'path_label'):
                self.path_label.configure(background=dark_bg, foreground=dark_fg)

            self.mode_button.config(text="☀️")

        else:
            # Light mode (default) settings
            light_bg = "SystemButtonFace" # Default system background
            light_fg = "black"
            entry_bg_light = "white"

            self.root.configure(bg=light_bg)
            # Revert to a default theme or configure styles individually
            self.style.theme_use('default') # Or your preferred default theme like 'vista', 'xpnative'

            self.style.configure(".", background=light_bg, foreground=light_fg)
            self.style.configure("TLabel", background=light_bg, foreground=light_fg)
            self.style.configure("TButton", background=light_bg, foreground=light_fg) # Revert to default
            self.style.map("TButton", background=[('active', light_bg)]) # Revert active state
            self.style.configure("TEntry", fieldbackground=entry_bg_light, foreground=light_fg, insertcolor=light_fg)
            self.style.configure("TLabelframe", background=light_bg, foreground=light_fg, bordercolor=light_fg)
            self.style.configure("TLabelframe.Label", background=light_bg, foreground=light_fg)
            self.style.configure("TRadiobutton", background=light_bg, foreground=light_fg)
            self.style.map("TRadiobutton",
                           background=[('active', light_bg)],
                           indicatorcolor=[('selected', light_fg), ('!selected', light_fg)])
            self.style.configure("TScrollbar", background=light_bg, troughcolor=light_bg) # Revert
            self.style.configure("TProgressbar", background=light_bg, troughcolor=light_bg) # Revert

            # For tk.Listbox
            self.streams_listbox.configure(
                background=entry_bg_light,
                foreground=light_fg,
                selectbackground="SystemHighlight", # Default system selection color
                selectforeground="SystemHighlightText"
            )
            # Update path_label color for light mode
            if hasattr(self, 'path_label'): # Check if path_label exists
                self.path_label.configure(background=light_bg, foreground=light_fg)

            self.mode_button.config(text="🌙")



    def fetch_streams(self):
        link = self.link_entry.get().strip()
        if not link:
            messagebox.showerror("Error", "Please enter a YouTube link.")
            return

        self.progress.start()
        threading.Thread(target=self._fetch_streams_thread, args=(link,), daemon=True).start()

    def _fetch_streams_thread(self, link):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                # 'cookiefile': 'path/to/your/cookies.txt',
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.video_info = ydl.extract_info(link, download=False)

            self.root.after(0, self._update_streams_list)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Invalid URL or network error:\n{e}"))
        finally:
            self.root.after(0, self.progress.stop)

    def _update_streams_list(self):
        self.streams_listbox.delete(0, tk.END)

        # Check if video_info was successfully fetched and contains the 'formats' key
        if not self.video_info or 'formats' not in self.video_info or not self.video_info['formats']:
            self.streams_listbox.insert(tk.END, "Could not fetch stream information for this URL.")
            self.selected_streams = None # Reset selected streams
            return # Stop processing if formats are not available

        # Now it's safe to access self.video_info['formats']
        all_formats = self.video_info['formats']

        if self.type.get() == "Video":
            # Filter for video formats (with video and audio codecs, mp4 extension)
            formats = [f for f in all_formats
                       if f.get('vcodec') != 'none' and f.get('acodec') != 'none'
                       and f.get('ext') == 'mp4']
            formats.sort(key=lambda x: x.get('height') or 0, reverse=True)

            for idx, fmt in enumerate(formats):
                height = fmt.get('height') or 'N/A'
                filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                size_mb = round(filesize / (1024 * 1024), 2) if filesize else "N/A"
                fps = fmt.get('fps') or ''
                fps_str = f" {fps}fps" if fps else ""
                resolution_str = f"{height}p" if height != 'N/A' else "Unknown"
                self.streams_listbox.insert(tk.END, f"{idx + 1}. {resolution_str}{fps_str} - {size_mb} MB")
        else: # Audio
            # Filter for audio-only formats
            formats = [f for f in all_formats
                       if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
            formats.sort(key=lambda x: f.get('abr') or 0, reverse=True) # Sort by average bitrate

            for idx, fmt in enumerate(formats):
                abr = fmt.get('abr') or 'N/A'
                filesize = fmt.get('filesize') or fmt.get('filesize_approx') or 0
                size_mb = round(filesize / (1024 * 1024), 2) if filesize else "N/A"
                ext = fmt.get('ext', 'unknown')
                abr_str = f"{abr}kbps" if abr != 'N/A' else "Unknown bitrate"
                self.streams_listbox.insert(tk.END, f"{idx + 1}. Audio {abr_str} ({ext}) - {size_mb} MB")

        self.selected_streams = formats
        if not formats:
            # More specific message if no *suitable* formats were found after filtering
            self.streams_listbox.insert(tk.END, f"No suitable {self.type.get().lower()} formats found.")


    def download_selected(self):
        selection = self.streams_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a stream from the list.")
            return

        if not self.selected_streams:
            messagebox.showerror("Error", "No streams available.")
            return

        index = selection[0]
        if index >= len(self.selected_streams):
            messagebox.showerror("Error", "Invalid selection.")
            return

        selected_format = self.selected_streams[index]

        self.progress.start()
        threading.Thread(target=self._download_thread, args=(selected_format,), daemon=True).start()

    def _download_thread(self, selected_format):
        try:
            # Use the selected download_path
            save_path = self.download_path

            # Clean filename template
            filename_template = '%(title)s.%(ext)s'

            if self.type.get() == "Audio":
                ydl_opts = {
                    'format': str(selected_format['format_id']),
                    'outtmpl': os.path.join(save_path, filename_template),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'postprocessor_args': [
                        '-ar', '44100'
                    ],
                }
            else:
                ydl_opts = {
                    'format': str(selected_format['format_id']),
                    'outtmpl': os.path.join(save_path, filename_template),
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.video_info['webpage_url']])

            file_type = "Audio" if self.type.get() == "Audio" else "Video"
            self.root.after(0, lambda: messagebox.showinfo("Success",
                                                           f"{file_type} downloaded successfully to:\n{save_path}"))

        except Exception as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                error_msg += "\n\nNote: FFmpeg is required for audio conversion. Please install FFmpeg."
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed:\n{error_msg}"))
        finally:
            self.root.after(0, self.progress.stop)


def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
