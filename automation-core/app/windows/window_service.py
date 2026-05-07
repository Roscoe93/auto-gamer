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
        return [Window("mock_win_1", "Mock Game Window (Windows)"), Window("mock_win_2", "Mock App Window (Windows)")]

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
