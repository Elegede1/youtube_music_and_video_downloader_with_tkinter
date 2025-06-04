# YouTube Downloader GUI

A simple graphical user interface (GUI) application built with Python and Tkinter to download videos and audio from YouTube and YouTube Music.

## Features

-   Download videos and audio streams.
-   Select preferred video quality or audio bitrate.
-   Choose a custom download location.
-   Dark mode and Light mode toggle.
-   Progress bar for downloads.
-   Welcome page with usage instructions.

## Requirements

-   Python 3.x
-   `yt-dlp` library
-   (Optional but Recommended for audio conversion) FFmpeg:
    -   Ensure FFmpeg is installed and added to your system's PATH if you want to download audio in MP3 format. The application will attempt to convert to MP3 if FFmpeg is found.

## How to Use

1.  **Paste URL**: Enter a YouTube or YouTube Music URL.
2.  **Fetch Streams**: Click "Fetch Streams" to load available formats.
3.  **Select Type**: Choose "Video" or "Audio".
4.  **Select Format**: Pick a format from the list.
5.  **Choose Path**: (Optional) Click "Change Path" to set a download folder.
6.  **Download**: Click "Download Selected Stream".

A welcome screen with more detailed instructions will appear when you first launch the application.

## Running from Source

1.  **Clone the repository (if applicable) or download the script.**
2.  **Install dependencies:**
    