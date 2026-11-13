"""Moves the window whose title contains <text> to a display and keeps it on top, without the mouse.

Usage: python -I -X utf8 place_window.py <text> [\\\\.\\DISPLAY4]
"""
import ctypes
import ctypes.wintypes as wt
import sys
import time

user32 = ctypes.windll.user32
user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))


class MonitorInfo(ctypes.Structure):
    _fields_ = [("cbSize", wt.DWORD), ("rcMonitor", wt.RECT), ("rcWork", wt.RECT), ("dwFlags", wt.DWORD), ("szDevice", wt.WCHAR * 32)]


def monitor_bounds(name):
    found = []
    callback_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HMONITOR, wt.HDC, ctypes.POINTER(wt.RECT), wt.LPARAM)

    def callback(handle, _hdc, _rect, _data):
        info = MonitorInfo()
        info.cbSize = ctypes.sizeof(MonitorInfo)
        user32.GetMonitorInfoW(handle, ctypes.byref(info))
        if info.szDevice == name:
            found.append(info.rcMonitor)
        return True

    user32.EnumDisplayMonitors(None, None, callback_type(callback), 0)
    if not found:
        raise SystemExit(f"Display {name} not found")
    return found[0]


def window_with_title(text):
    found = []
    callback_type = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    def callback(hwnd, _data):
        length = user32.GetWindowTextLengthW(hwnd)
        if length and user32.IsWindowVisible(hwnd):
            buffer = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buffer, length + 1)
            if text in buffer.value:
                found.append(hwnd)
        return True

    user32.EnumWindows(callback_type(callback), 0)
    return found[0] if found else None


def place_window(text, display=r"\\.\DISPLAY4"):
    hwnd = None
    for _ in range(40):
        hwnd = window_with_title(text)
        if hwnd:
            break
        time.sleep(0.25)
    if not hwnd:
        raise SystemExit("The test window did not appear")
    bounds = monitor_bounds(display)
    user32.MoveWindow(hwnd, bounds.left + 80, bounds.top + 80, 2300, 1500, True)
    # Topmost without taking the focus: a covered window gets almost no animation frames.
    user32.SetWindowPos(hwnd, wt.HWND(-1), 0, 0, 0, 0, 0x0013)


if __name__ == "__main__":
    place_window(sys.argv[1], *sys.argv[2:3])
