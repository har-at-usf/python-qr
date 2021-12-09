from contextlib import contextmanager
from enum import Enum
from pyqrcode import create
from tempfile import TemporaryFile
from PIL import Image 
from shutil import move
from os import remove
from win32clipboard import OpenClipboard, GetClipboardData, CloseClipboard


class ImageType(Enum):  
    """Only accept PNG or SVG as export filetypes."""
    PNG = 'png'
    SVG = 'svg'


class QRFile:
    """Superclass to write a QR code to a file."""
    
    # When creating a new QR code, temporarily store it in an alternate
    # location, then move to the target location once it finishes.
    TMP = TemporaryFile().name
         
    def export(self, data, img_type=ImageType.PNG):
        """Export data to a valid file extension (defined in the `ImageType`
        class). If `img_type` is not a valid `ImageType`, undefined behavior
        can occur."""
        
        # This is horthand for QR: create(data).filetype(filename, scale)
        getattr(create(data), img_type.value)(self.TMP, scale=8)

    def make_qrcode(self):
        """Abstract method to generate the QR code."""
        return None
    
    def open_file(self):
        """ Open a file in the default image viewer. """
        Image.open(self.TMP).show()
        
    def cleanup_file_data(self, save_to=None):
        """If `save_to` is a valid pathname, moves the newly-generated QR code
        there. Otherwise, it deletes the data."""
        move(self.TMP, save_to) if save_to else remove(self.TMP)


class WindowsQRFile(QRFile):
    """Windows-specific approach to writing a QR code, from the clipboard,
    to a graphic representation."""
    
    def make_qrcode_from_clipboard(self):
        """ Open QR as an image files. (Linux just prints to console.) """        
        self.export(self.clipboard())
        self.open_file()
        self.cleanup()        
    
    @contextmanager
    def clipboard(self):
        """TODO: I forget what this does.  .__. """  
        
        OpenClipboard()
        yield GetClipboardData()
        CloseClipboard()


if __name__ == "__main__":
    """ Later versions might have like: Linux().make_qrcode() """
    WindowsQRFile().make_qrcode_from_clipboard()
            