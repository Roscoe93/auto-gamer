from __future__ import annotations

import platform
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class Window:
    id: str
    title: str

@dataclass
class WindowRect:
    x: int
    y: int
    width: int
    height: int

class WindowService:
    def list_windows(self) -> list[Window]:
        if sys.platform == "darwin":
            return self._list_mac_windows()
        elif sys.platform == "win32":
            return self._list_windows_windows()
        return [Window("unsupported", f"Unsupported platform: {sys.platform}")]

    def get_window_rect(self, window_id: str) -> WindowRect | None:
        """Get the physical coordinates and size of the window."""
        if sys.platform == "darwin":
            return self._get_mac_window_rect(window_id)
        elif sys.platform == "win32":
            return self._get_windows_window_rect(window_id)
        return None

    def bring_to_front(self, window_id: str) -> bool:
        """Bring the specified window to the foreground."""
        if sys.platform == "darwin":
            return self._bring_mac_window_to_front(window_id)
        elif sys.platform == "win32":
            return self._bring_windows_window_to_front(window_id)
        return False

    def _get_windows_window_rect(self, window_id: str) -> WindowRect | None:
        try:
            import ctypes
            import ctypes.wintypes

            # extract hwnd from string like "win_12345"
            hwnd_str = window_id.replace("win_", "")
            if not hwnd_str.isdigit():
                return None

            hwnd = int(hwnd_str)
            user32 = ctypes.windll.user32

            rect = ctypes.wintypes.RECT()
            if user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                # Note: This returns logical pixels. For actual screen capture,
                # we might need to handle DPI scaling.
                return WindowRect(
                    x=rect.left,
                    y=rect.top,
                    width=rect.right - rect.left,
                    height=rect.bottom - rect.top
                )
            return None
        except Exception:
            return None

    def _bring_windows_window_to_front(self, window_id: str) -> bool:
        try:
            import ctypes

            hwnd_str = window_id.replace("win_", "")
            if not hwnd_str.isdigit():
                return False

            hwnd = int(hwnd_str)
            user32 = ctypes.windll.user32

            # SW_RESTORE = 9
            user32.ShowWindow(hwnd, 9)
            return bool(user32.SetForegroundWindow(hwnd))
        except Exception:
            return False

    def _get_mac_window_rect(self, window_id: str) -> WindowRect | None:
        try:
            # We stored the app name in title when listing mac windows
            # Format is "mac_app_0" etc., but we need the actual app name
            # Let's search through all apps to find the rect

            # A more robust way in macOS is using CoreGraphics, but for simplicity
            # in this POC, we use AppleScript to get the bounds of the frontmost window

            # We don't have the title easily accessible here just from the ID,
            # so this is a simplified version that just gets the frontmost window of the app

            # Wait, we need the app name. Let's find it.
            windows = self._list_mac_windows()
            app_name = None
            for w in windows:
                if w.id == window_id:
                    app_name = w.title
                    break

            if not app_name:
                return None

            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set p to position of window 1
                    set s to size of window 1
                    return (item 1 of p) & "," & (item 2 of p) & "," & (item 1 of s) & "," & (item 2 of s)
                end tell
            end tell
            '''
            try:
                output = subprocess.check_output(["osascript", "-e", script], text=True, stderr=subprocess.PIPE).strip()
            except subprocess.CalledProcessError as e:
                print(f"[WindowService] Failed to get rect for {app_name}: {e.stderr}", file=sys.stderr)
                return None

            if output:
                x, y, w, h = map(int, output.split(","))
                return WindowRect(x=x, y=y, width=w, height=h)
            return None
        except Exception:
            return None

    def _bring_mac_window_to_front(self, window_id: str) -> bool:
        try:
            windows = self._list_mac_windows()
            app_name = None
            for w in windows:
                if w.id == window_id:
                    app_name = w.title
                    break

            if not app_name:
                return False

            script = f'''
            tell application "{app_name}" to activate
            '''
            try:
                subprocess.check_output(["osascript", "-e", script], stderr=subprocess.PIPE)
                return True
            except subprocess.CalledProcessError as e:
                print(f"[WindowService] Failed to bring to front {app_name}: {e.stderr}", file=sys.stderr)
                return False
        except Exception as e:
            print(f"[WindowService] Unexpected error: {e}", file=sys.stderr)
            return False

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
