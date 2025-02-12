from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "yt_dlp", "PyQt6"],
    "excludes": [],
    "include_files": ["resources.py"]
}

setup(
    name="yt-dlp-gui",
    version="1.0",
    description="GUI for yt-dlp",
    options={"build_exe": build_exe_options},
    executables=[Executable("yt_dlp_gui.py", base="Win32GUI")]
) 