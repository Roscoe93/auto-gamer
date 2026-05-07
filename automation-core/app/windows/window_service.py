from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Window:
    id: str
    title: str


class WindowService:
    def list_windows(self) -> list[Window]:
        if sys.platform == "darwin":
            return self._list_mac_windows()
        elif sys.platform == "win32":
            return self._list_windows_windows()
        return [Window("unsupported", f"Unsupported platform: {sys.platform}")]

    def _list_windows_windows(self) -> list[Window]:
        try:
            import ctypes
            import ctypes.wintypes
            
            # Use ctypes to call Windows API user32.dll
            user32 = ctypes.windll.user32
            
            # Define the callback function type for EnumWindows
            WNDENUMPROC = ctypes.WINFUNCTYPE(
                ctypes.wintypes.BOOL,
                ctypes.wintypes.HWND,
                ctypes.wintypes.LPARAM
            )
            
            windows = []
            
            def enum_windows_callback(hwnd, lParam):
                # Check if window is visible
                if user32.IsWindowVisible(hwnd):
                    # Get window title length
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        # Create buffer for window title
                        buff = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buff, length + 1)
                        title = buff.value
                        
                        # Filter out some common Windows system processes
                        ignore_list = ["Program Manager", "Settings", "Microsoft Text Input Application"]
                        if title and title not in ignore_list:
                            windows.append(Window(f"win_{hwnd}", title))
                
                return True # Continue enumeration
                
            # Call EnumWindows
            user32.EnumWindows(WNDENUMPROC(enum_windows_callback), 0)
            
            if not windows:
                windows.append(Window("mock_win_1", "No visible windows found"))
                
            return windows
        except Exception as e:
            return [Window("error_win", f"Error listing windows on Windows: {e}")]

    def _list_mac_windows(self) -> list[Window]:
        try:
            # Using AppleScript to get names of applications that have a UI
            script = 'tell application "System Events" to get name of every process whose background only is false'
            output = subprocess.check_output(["osascript", "-e", script], text=True)
            apps = [name.strip() for name in output.split(",") if name.strip()]
            
            # Filter out some common non-game apps for a cleaner list
            ignore_list = ["Finder", "System Settings", "Terminal", "Code", "Cursor", "Activity Monitor"]
            windows = []
            
            for i, name in enumerate(apps):
                if name not in ignore_list:
                    windows.append(Window(f"mac_app_{i}", name))
                    
            if not windows:
                windows.append(Window("mock_mac_1", "No other visible apps found"))
                
            return windows
        except Exception as e:
            return [Window("error_win", f"Error listing windows: {e}")]
