import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QCheckBox, QTabWidget, QScrollArea,
                            QGroupBox, QFileDialog, QSpinBox, QToolTip,
                            QPlainTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QFile, QTextStream
from PyQt6.QtGui import QIcon, QFont
import yt_dlp
import resources  # Will contain our icons/styles

class DownloadWorker(QThread):
    progress = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, url, options):
        super().__init__()
        self.url = url
        self.options = options
        
    def run(self):
        try:
            def progress_hook(d):
                self.progress.emit(d)
                
            self.options['progress_hooks'] = [progress_hook]
            with yt_dlp.YoutubeDL(self.options) as ydl:
                ydl.download([self.url])
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("yt-dlp GUI")
        self.setMinimumSize(800, 600)
        QToolTip.setFont(QFont("SansSerif", 10))
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Basic tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        tabs.addTab(basic_tab, "Basic")
        
        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_input = QLineEdit()
        self.url_input.setToolTip("Enter the URL of the video you want to download.")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        basic_layout.addLayout(url_layout)
        
        # Format selection
        format_group = QGroupBox("Format Selection")
        format_layout = QVBoxLayout()
        
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Best quality (video + audio)",
            "Audio only (best quality)",
            "Custom format"
        ])
        self.format_combo.setToolTip("Select the desired download format.")
        format_layout.addWidget(self.format_combo)
        
        # Custom format options (initially hidden)
        self.custom_format_widget = QWidget()
        custom_format_layout = QVBoxLayout(self.custom_format_widget)
        self.custom_format_input = QLineEdit()
        self.custom_format_input.setToolTip("Enter custom format details if 'Custom format' is selected.")
        custom_format_layout.addWidget(self.custom_format_input)
        format_layout.addWidget(self.custom_format_widget)
        self.custom_format_widget.hide()
        
        format_group.setLayout(format_layout)
        basic_layout.addWidget(format_group)
        
        # Output directory
        output_group = QGroupBox("Output Options")
        output_layout = QHBoxLayout()
        self.output_path = QLineEdit()
        self.output_path.setToolTip("Enter or select the download directory.")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(browse_btn)
        output_group.setLayout(output_layout)
        basic_layout.addWidget(output_group)
        
        # Dynamic Format Preview in Basic tab
        dynamic_group = QGroupBox("Dynamic Format Preview")
        dynamic_layout = QVBoxLayout()
        self.load_formats_btn = QPushButton("Load Available Formats")
        self.load_formats_btn.setToolTip("Click to fetch available formats for the entered URL.")
        self.load_formats_btn.clicked.connect(self.load_available_formats)
        dynamic_layout.addWidget(self.load_formats_btn)
        self.format_preview_text = QPlainTextEdit()
        self.format_preview_text.setReadOnly(True)
        self.format_preview_text.setToolTip("Displays a list of available formats for the video.")
        dynamic_layout.addWidget(self.format_preview_text)
        lbl_selected_format = QLabel("Selected Format ID:")
        dynamic_layout.addWidget(lbl_selected_format)
        self.selected_format_id = QLineEdit()
        self.selected_format_id.setToolTip("Enter the specific format ID from the preview, if desired.")
        dynamic_layout.addWidget(self.selected_format_id)
        dynamic_group.setLayout(dynamic_layout)
        basic_layout.addWidget(dynamic_group)
        
        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setToolTip("Click to start download with current settings.")
        self.download_btn.clicked.connect(self.start_download)
        basic_layout.addWidget(self.download_btn)
        
        # Progress bar and status
        self.progress_label = QLabel()
        basic_layout.addWidget(self.progress_label)
        
        # Advanced tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        tabs.addTab(advanced_tab, "Advanced")
        
        # Add advanced options in scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        advanced_layout.addWidget(scroll)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Add various advanced option groups
        self.add_advanced_options(scroll_layout)
        
        scroll.setWidget(scroll_content)
        
        # User Guide tab
        guide_tab = QWidget()
        guide_layout = QVBoxLayout(guide_tab)
        tabs.addTab(guide_tab, "User Guide")
        
        guide_scroll = QScrollArea()
        guide_scroll.setWidgetResizable(True)
        guide_layout.addWidget(guide_scroll)
        
        guide_content = QWidget()
        guide_content_layout = QVBoxLayout(guide_content)
        guide_scroll.setWidget(guide_content)
        
        guide_text = QLabel()
        guide_text.setTextFormat(Qt.TextFormat.RichText)
        guide_text.setOpenExternalLinks(True)
        guide_text.setWordWrap(True)
        guide_text.setText("""
<style>
  body { font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }
  h1 { color: #2E86C1; margin-bottom: 20px; }
  h2 { color: #2874A6; border-bottom: 2px solid #D5D8DC; padding-bottom: 5px; margin-top: 30px; }
  h3 { font-size: 16px; color: #2E86C1; margin-top: 20px; }
  p, li { font-size: 14px; margin: 10px 0; }
  ul { margin-left: 20px; }
  a { color: #2874A6; text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>

<body>
<h1>Welcome to yt-dlp GUI</h1>
<p>Welcome to yt-dlp GUI – a professional-grade, user-friendly front-end for the powerful yt-dlp video downloader. Whether you're a seasoned developer or a content creator, our application offers robust functionality combined with a polished, intuitive design.</p>

<h2>Getting Started</h2>
<p>In the <strong>Basic</strong> tab, you can quickly set up your download:</p>
<ul>
  <li><strong>Video URL:</strong> Enter or paste the URL of the video or playlist you wish to download.</li>
  <li><strong>Format Selection:</strong> Choose from best quality (video &amp; audio), audio only, or a custom format tailored to your needs.</li>
  <li><strong>Output Directory:</strong> Select where your files will be saved.</li>
  <li><strong>Dynamic Format Preview:</strong> Click "Load Available Formats" to view detailed information such as resolution, file format, and codec. You can then specify a particular format ID if desired.</li>
</ul>
<p>Once configured, simply hit the <strong>Download</strong> button to start downloading.</p>

<h2>Advanced Options</h2>
<p>If you need more control, the <strong>Advanced</strong> tab provides a range of powerful settings:</p>

<h3>1. Video, Audio, and Subtitle Settings</h3>
<ul>
  <li><strong>Video Options:</strong> Choose your desired video quality and container format.</li>
  <li><strong>Audio Options:</strong> Enable audio extraction and pick your preferred audio format.</li>
  <li><strong>Subtitle Options:</strong> Opt to download and embed subtitles.</li>
  <li><strong>Playlist Options:</strong> Select between downloading a single video or processing an entire playlist/channel.</li>
  <li><strong>Miscellaneous Options:</strong> Toggle verbose logging or simulate downloads for testing purposes.</li>
</ul>

<h3>2. Post-Processing Features</h3>
<ul>
  <li><strong>Embed Thumbnails:</strong> Automatically include a thumbnail image in your downloaded file.</li>
  <li><strong>Embed Metadata:</strong> Insert details like title and description directly into your file.</li>
  <li><strong>Format Conversion:</strong> Convert your download to another format (e.g., MP4 or MKV) after completion.</li>
</ul>

<h3>3. Network &amp; Authentication</h3>
<ul>
  <li><strong>Proxy:</strong> Enter proxy details if needed (e.g., http://proxy:port).</li>
  <li><strong>Cookies:</strong> Provide a cookies file path to access geo-restricted content.</li>
  <li><strong>User Credentials:</strong> Supply your username and password when authentication is required.</li>
</ul>

<h3>4. Playlist Filtering</h3>
<ul>
  <li><strong>After Date:</strong> Specify a date (YYYYMMDD) to filter videos uploaded after a certain day.</li>
  <li><strong>Max Videos:</strong> Set a limit on the number of videos to download.</li>
  <li><strong>Title Regex:</strong> Use regex filters to select videos by title.</li>
</ul>

<h3>5. Logging &amp; Debugging</h3>
<ul>
  <li><strong>Log Level:</strong> Choose from quiet to debug modes for logging details.</li>
  <li><strong>Log File:</strong> Specify a file path to save logs for troubleshooting.</li>
</ul>

<h3>6. Content Export Options</h3>
<p>This feature lets you log detailed information about each download – including media type, title, description, uploader, upload date, date of capture, and timestamp – to an export file. Choose your preferred format (CSV, JSON, TSV, Excel, or XML) for effective record-keeping and analysis.</p>

<h2>Usage Tips</h2>
<p>Hover over any control to view a brief description of its function. Our context-aware help makes it easy to fine-tune your settings with confidence.</p>

<h2>Frequently Asked Questions (FAQ)</h2>
<ul>
  <li><strong>Q:</strong> Can I download a full channel or playlist?<br><strong>A:</strong> Yes, provide a channel URL and use the Playlist Filtering Options to control the download.</li>
  <li><strong>Q:</strong> What does Dynamic Format Preview do?<br><strong>A:</strong> It displays all available formats for a video, allowing you to select a specific option if desired.</li>
  <li><strong>Q:</strong> How do I use the Network/Authentication settings?<br><strong>A:</strong> Enter the necessary proxy, cookies, and credentials to access restricted content.</li>
  <li><strong>Q:</strong> What is Content Export Logging?<br><strong>A:</strong> When enabled, it logs detailed information about your downloads in your chosen format.</li>
  <li><strong>Q:</strong> How does simulation mode work?<br><strong>A:</strong> It runs a trial download without saving any files, ideal for testing your configuration.</li>
</ul>

<h2>Support &amp; Resources</h2>
<p>For further assistance, comprehensive documentation, or to contribute, please visit our <a href=\"https://github.com/yt-dlp/yt-dlp\" target=\"_blank\">official GitHub repository</a>. Thank you for choosing yt-dlp GUI!</p>
</body>
""")
        guide_content_layout.addWidget(guide_text)
        
        self.load_styles()
        
    def load_styles(self):
        try:
            # Try to load from resources first
            style_file = QFile(":/styles/style.qss")
            if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                stream = QTextStream(style_file)
                self.setStyleSheet(stream.readAll())
                style_file.close()
        except Exception as e:
            print(f"Could not load style from resources: {e}")
            # Fallback to direct file
            try:
                with open("styles/style.qss", "r") as f:
                    self.setStyleSheet(f.read())
            except Exception as e:
                print(f"Could not load style from file: {e}")
        
    def add_advanced_options(self, layout):
        # Video Options
        video_group = QGroupBox("Video Options")
        video_layout = QVBoxLayout()
        
        self.video_quality = QComboBox()
        self.video_quality.addItems(["1080p", "720p", "480p", "360p", "240p"])
        self.video_quality.setToolTip("Select the preferred video quality.")
        video_layout.addWidget(QLabel("Preferred Quality:"))
        video_layout.addWidget(self.video_quality)
        
        self.video_format = QComboBox()
        self.video_format.addItems(["mp4", "webm", "mkv"])
        self.video_format.setToolTip("Select the container format for the video.")
        video_layout.addWidget(QLabel("Container Format:"))
        video_layout.addWidget(self.video_format)
        
        video_group.setLayout(video_layout)
        layout.addWidget(video_group)
        
        # Audio Options
        audio_group = QGroupBox("Audio Options")
        audio_layout = QVBoxLayout()
        
        self.extract_audio = QCheckBox("Extract Audio")
        self.extract_audio.setToolTip("Enable this to extract audio from the downloaded video.")
        self.audio_format = QComboBox()
        self.audio_format.addItems(["mp3", "m4a", "wav", "opus"])
        self.audio_format.setToolTip("Select the audio format for extraction.")
        
        audio_layout.addWidget(self.extract_audio)
        audio_layout.addWidget(QLabel("Audio Format:"))
        audio_layout.addWidget(self.audio_format)
        
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # Subtitle Options
        subtitle_group = QGroupBox("Subtitle Options")
        subtitle_layout = QVBoxLayout()
        
        self.download_subs = QCheckBox("Download Subtitles")
        self.download_subs.setToolTip("Check to download available subtitles for the video.")
        self.embed_subs = QCheckBox("Embed Subtitles")
        self.embed_subs.setToolTip("Check to embed subtitles into the video file after download, if available.")
        
        subtitle_layout.addWidget(self.download_subs)
        subtitle_layout.addWidget(self.embed_subs)
        
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        # Playlist Options
        playlist_group = QGroupBox("Playlist Options")
        playlist_layout = QVBoxLayout()
        self.single_video_only = QCheckBox("Download single video only (ignore playlist)")
        self.single_video_only.setToolTip("If selected, only the individual video is downloaded even if the URL points to a playlist.")
        playlist_layout.addWidget(self.single_video_only)
        playlist_group.setLayout(playlist_layout)
        layout.addWidget(playlist_group)
        
        # Miscellaneous Options
        misc_group = QGroupBox("Miscellaneous Options")
        misc_layout = QVBoxLayout()
        self.verbose_logging = QCheckBox("Verbose logging")
        self.verbose_logging.setToolTip("Enable detailed logging for debugging purposes.")
        misc_layout.addWidget(self.verbose_logging)
        
        self.simulate_download = QCheckBox("Simulate download (dry run)")
        self.simulate_download.setToolTip("Perform a dry run without actual downloading.")
        misc_layout.addWidget(self.simulate_download)
        
        misc_group.setLayout(misc_layout)
        layout.addWidget(misc_group)

        # Post-Processing Options
        postproc_group = QGroupBox("Post-Processing Options")
        postproc_layout = QVBoxLayout()
        self.embed_thumbnails = QCheckBox("Embed Thumbnails")
        self.embed_thumbnails.setToolTip("Embed video thumbnails into the output file, if available.")
        postproc_layout.addWidget(self.embed_thumbnails)
        self.embed_metadata = QCheckBox("Embed Metadata")
        self.embed_metadata.setToolTip("Embed metadata (title, description, etc.) into the output file.")
        postproc_layout.addWidget(self.embed_metadata)
        lbl_convert = QLabel("Convert Format:")
        postproc_layout.addWidget(lbl_convert)
        self.convert_format = QComboBox()
        self.convert_format.addItems(["No Conversion", "mp4", "mkv", "webm"])
        self.convert_format.setToolTip("Select a format to convert the video post-download.")
        postproc_layout.addWidget(self.convert_format)
        postproc_group.setLayout(postproc_layout)
        layout.addWidget(postproc_group)

        # Network / Authentication Options
        network_group = QGroupBox("Network / Authentication Options")
        network_layout = QVBoxLayout()
        lbl_proxy = QLabel("Proxy:")
        network_layout.addWidget(lbl_proxy)
        self.proxy_input = QLineEdit()
        self.proxy_input.setToolTip("Enter proxy (e.g. http://proxy:port) if needed.")
        network_layout.addWidget(self.proxy_input)
        lbl_cookies = QLabel("Cookies File:")
        network_layout.addWidget(lbl_cookies)
        self.cookies_input = QLineEdit()
        self.cookies_input.setToolTip("Enter path to a cookies file if needed.")
        network_layout.addWidget(self.cookies_input)
        lbl_username = QLabel("Username:")
        network_layout.addWidget(lbl_username)
        self.username_input = QLineEdit()
        self.username_input.setToolTip("Enter username for authentication if required.")
        network_layout.addWidget(self.username_input)
        lbl_password = QLabel("Password:")
        network_layout.addWidget(lbl_password)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setToolTip("Enter password for authentication if required.")
        network_layout.addWidget(self.password_input)
        network_group.setLayout(network_layout)
        layout.addWidget(network_group)

        # Playlist Filtering Options
        playlist_filter_group = QGroupBox("Playlist Filtering Options")
        playlist_filter_layout = QVBoxLayout()
        lbl_after_date = QLabel("After Date (YYYYMMDD):")
        playlist_filter_layout.addWidget(lbl_after_date)
        self.after_date_input = QLineEdit()
        self.after_date_input.setToolTip("Only download videos uploaded after this date.")
        playlist_filter_layout.addWidget(self.after_date_input)
        lbl_max_videos = QLabel("Max Videos:")
        playlist_filter_layout.addWidget(lbl_max_videos)
        self.max_videos_input = QSpinBox()
        self.max_videos_input.setRange(0, 10000)
        self.max_videos_input.setValue(0)
        self.max_videos_input.setToolTip("Maximum number of videos to download (0 for no limit).")
        playlist_filter_layout.addWidget(self.max_videos_input)
        lbl_title_regex = QLabel("Title Regex Filter:")
        playlist_filter_layout.addWidget(lbl_title_regex)
        self.title_regex_input = QLineEdit()
        self.title_regex_input.setToolTip("Regex pattern to filter videos by title.")
        playlist_filter_layout.addWidget(self.title_regex_input)
        playlist_filter_group.setLayout(playlist_filter_layout)
        layout.addWidget(playlist_filter_group)

        # Logging and Debugging Options
        logging_group = QGroupBox("Logging and Debugging Options")
        logging_layout = QVBoxLayout()
        lbl_log_level = QLabel("Log Level:")
        logging_layout.addWidget(lbl_log_level)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["quiet", "debug", "info", "warning", "error"])
        self.log_level_combo.setToolTip("Select the desired log level.")
        logging_layout.addWidget(self.log_level_combo)
        lbl_log_file = QLabel("Log File:")
        logging_layout.addWidget(lbl_log_file)
        self.log_file_input = QLineEdit()
        self.log_file_input.setToolTip("Specify a file path to save logs.")
        logging_layout.addWidget(self.log_file_input)
        logging_group.setLayout(logging_layout)
        layout.addWidget(logging_group)
        
        # Content Export Options
        export_group = QGroupBox("Content Export Options")
        export_layout = QVBoxLayout()

        self.enable_export = QCheckBox("Enable Content Export Logging")
        self.enable_export.setToolTip("Log downloaded content details (Media Type, Title, Description, Uploader, Upload Date, Date of Capture, Timestamp) to an export file.")
        export_layout.addWidget(self.enable_export)

        export_format_label = QLabel("Export Format:")
        export_layout.addWidget(export_format_label)
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "JSON", "TSV", "Excel", "XML"])
        self.export_format_combo.setToolTip("Select the format for exporting the download log.")
        export_layout.addWidget(self.export_format_combo)

        export_file_label = QLabel("Export File Path:")
        export_layout.addWidget(export_file_label)
        h_layout_export = QHBoxLayout()
        self.export_file_input = QLineEdit()
        self.export_file_input.setToolTip("Specify the file path to save the export log.")
        h_layout_export.addWidget(self.export_file_input)
        self.export_browse_btn = QPushButton("Browse")
        self.export_browse_btn.setToolTip("Click to select the export file path.")
        self.export_browse_btn.clicked.connect(self.browse_export)
        h_layout_export.addWidget(self.export_browse_btn)
        export_layout.addLayout(h_layout_export)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
    def browse_output(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_path.setText(directory)
            
    def start_download(self):
        url = self.url_input.text()
        if not url:
            return
            
        options = self.get_download_options()
        
        self.download_worker = DownloadWorker(url, options)
        self.download_worker.progress.connect(self.update_progress)
        self.download_worker.finished.connect(self.download_finished)
        self.download_worker.error.connect(self.download_error)
        self.download_worker.start()
        
        self.download_btn.setEnabled(False)
        
    def get_download_options(self):
        options = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.output_path.text(), '%(title)s.%(ext)s'),
        }
        
        # Add more options based on UI selections
        if self.format_combo.currentText() == "Audio only (best quality)":
            options['format'] = 'bestaudio/best'
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format.currentText(),
            }]
        
        if self.selected_format_id.text():
            options['format'] = self.selected_format_id.text()
        if self.embed_thumbnails.isChecked():
            options['writethumbnail'] = True
        if self.embed_metadata.isChecked():
            options['addmetadata'] = True
        if self.convert_format.currentText() != "No Conversion":
            if 'postprocessors' in options:
                options['postprocessors'].append({
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': self.convert_format.currentText()
                })
            else:
                options['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': self.convert_format.currentText()
                }]
        if self.proxy_input.text():
            options['proxy'] = self.proxy_input.text()
        if self.cookies_input.text():
            options['cookiefile'] = self.cookies_input.text()
        if self.username_input.text():
            options['username'] = self.username_input.text()
        if self.password_input.text():
            options['password'] = self.password_input.text()
        if self.after_date_input.text():
            options['dateafter'] = self.after_date_input.text()
        if self.max_videos_input.value() > 0:
            options['playlistend'] = self.max_videos_input.value()
        if self.title_regex_input.text():
            import re
            options['match_filter'] = lambda info: re.search(self.title_regex_input.text(), info.get('title', '')) is not None
        options['log_level'] = self.log_level_combo.currentText()
        if self.log_file_input.text():
            options['logger'] = self.log_file_input.text()  # Placeholder for actual logger integration
        if self.verbose_logging.isChecked():
            options['verbose'] = True
        if self.simulate_download.isChecked():
            options['simulate'] = True
        if self.enable_export.isChecked():
            options['export_enabled'] = True
            options['export_format'] = self.export_format_combo.currentText()
            options['export_file'] = self.export_file_input.text()
        return options
        
    def update_progress(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d['_percent_str']
                speed = d['_speed_str']
                self.progress_label.setText(f"Downloading... {percent} at {speed}")
            except KeyError:
                pass
                
    def download_finished(self):
        self.progress_label.setText("Download completed!")
        self.download_btn.setEnabled(True)
        
    def download_error(self, error):
        self.progress_label.setText(f"Error: {error}")
        self.download_btn.setEnabled(True)

    def load_available_formats(self):
        url = self.url_input.text()
        if not url:
            self.format_preview_text.setPlainText("Please enter a valid URL.")
            return
        ydl_opts = {'skip_download': True, 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                output = ""
                for f in formats:
                    output += f"ID: {f.get('format_id', 'N/A')} - Resolution: {f.get('resolution', 'N/A')}, Ext: {f.get('ext', 'N/A')}, Note: {f.get('format_note', 'N/A')}\n"
                self.format_preview_text.setPlainText(output)
        except Exception as e:
            self.format_preview_text.setPlainText("Error fetching formats: " + str(e))

    def browse_export(self):
        # Use QFileDialog.getSaveFileName to allow the user to choose a file for export logging
        filename, _ = QFileDialog.getSaveFileName(self, "Select Export File", "", "All Files (*)")
        if filename:
            self.export_file_input.setText(filename)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 