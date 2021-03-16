

class DownloadException(IOError):
    msg = "Not able to download the requested file.\n"

    def __init__(self, msg, file):
        self.msg += msg
        self.msg += f"\nThe error ocurred with file: {file}"
