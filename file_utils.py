import time
import os
from pathlib import Path
from selenium.webdriver.support.ui import WebDriverWait
import glob

def download_wait(connection, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        connection.driver.implicitly_wait(1)
        dl_wait = False
        files = os.listdir(Path(connection.downloadPath))
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds

#todo: finish save
def save_pdf(directory):
    folder_path = Path(directory)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


def is_downloaded(connection,name):
    # returns the name of the file if it is already downloaded and False otherwise
    glb = glob.glob(connection.downloadPath+name+'*.mp4')
    if(len(glb) != 0):
        return glb[0]
    else:
        return False