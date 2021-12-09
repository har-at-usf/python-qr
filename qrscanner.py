"""qrscanner.py

Utility to scan data from a webcam and set that data to the clipboard. The
current solution works for Windows, but it can be ported to other OSes
(testers welcome).

To use the scanner, run this script and hold the QR code in front of the
lens. You may need to move the QR code closer or further from the webcam.
When the scanner finishes, the console will close automatically. Any scanned
data is set to the clipboard.

One shortcoming of this project is the lack of program feedback. The UI is
just a console prompt. A better version of this application might display
the capture stream as the user is trying to scan. This would show the user
what the webcam can (or cannot) see. This is not currently an interest
because 1) it works, and 2) there are minor privacy concerns with displaying
the QR graphic, which may contain sensitive data, on the monitor; this 
could leak such data to a shoulder-surfer. An even *better* implementation
might display the bare-minimum information about the QR code within the
webcam's target, but this would require a lot of work.
"""
from cv2 import VideoCapture
from os import path
from pathlib import Path
from pyzbar import pyzbar
from win32clipboard import (
    OpenClipboard,
    EmptyClipboard,
    SetClipboardText,
    CloseClipboard,
    CF_UNICODETEXT,
)


class WebcamCapture:
    """Superclass to capture webcam data."""

    # Data is defined in subclasses.
    data: any

    # Filepath should exist on the system.
    filepath: str

    def __init__(self, filepath=None):
        """By default, set the output filepath to the current user's
        `Downloads` folder."""

        self.filepath = (
            filepath if filepath else path.join(Path.home(), "Downloads")
        )

    def set_data(self):
        """Update captured data from the webcam."""
        return None

    def write_to_file(self):
        """Optional: Use this along with/in place of the clipboard."""

        with open(self.filepath, "w+") as file:

            for line in self.data:
                file.write(line)


class ZbarWebcam(WebcamCapture):
    """Uses the pyzbar library to capture QR data from the webcam."""

    # The capture device is represented as an index: 0, ..., <num devices>.
    capture_device: int

    def set_capture_device(self, capture_device: int):
        """Sets the integer representation of the capture device. In most
        cases, this value is `0`: the first webcam in the device list."""
        self.capture_device = capture_device

    def capture_data(self):
        """Runs until data is captured (or forever if no data captured)."""

        stream = VideoCapture(self.capture_device)
        obj = []

        # Runs until at least one object (data) is in the list of objects.
        while not len(obj):

            _, frame = stream.read()

            obj = [o.data.decode("utf-8") for o in pyzbar.decode(frame)]

        # The first element contains the QR data.
        self.data = obj[0]


class WindowsClipboard:
    """Manage the windows clipboard for data capture. Uses the `win32clipboard
    module to handle the clipboard."""

    def set_clipboard(self, data: str):
        """Writes data to the Windows clipboard."""
        OpenClipboard()
        EmptyClipboard()
        SetClipboardText(data, CF_UNICODETEXT)
        CloseClipboard()


class WindowsQrScanner(ZbarWebcam, WindowsClipboard):
    """Capture QR data on a Windows machine."""

    def __init__(self, capture_device=0, filepath=None):
        """Scan a QR code and write its data to the clipboard. The default
        capture device is usually at index 0, if one exists at all. The
        filepath's default follows the superclass and sets to the user's
        Downloads directory."""

        self.set_capture_device(capture_device)
        super().__init__(filepath)

        self.capture_data()

        # If data was captured, set it to the clipboard.
        if self.data:
            self.set_data_to_clipboard(self.data)

    def set_clipboard(self):
        """Write QR data captured by the webcam to the clipboard."""
        super().set_data_to_clipboard(self.data)


if __name__ == "__main__":
    """Demo to scan a QR code on a Windows system."""

    print(
        """QR Scanner:
    
        Hold your QR code in front of the webcam. It may take a few 
        seconds to load. If it doesn't scan at first, try moving it 
        closer and further away, slowly.
        
        Once data is captured, this window will close automatically.
        This program will send the captured data to your clipboard.
        """
    )

    try:
        WindowsQrScanner()

    except KeyboardInterrupt:
        print("Exiting scanner...")
