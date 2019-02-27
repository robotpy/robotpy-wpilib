#
# Utilities for compiling things that link against HAL or need the HAL
# headers
#
# Note: this file must not depend on anything else in the library, so we
# can import it from setup.py. Also used by the wpilib tests
#


hal_version = "2019.4.1"
wpiutil_version = "2019.4.1"

frc_site = "http://first.wpi.edu/FRC/roborio/maven/release"
frc_site_dev = "http://first.wpi.edu/FRC/roborio/maven/development"

hal_site = "%s/edu/wpi/first/hal/hal-cpp" % frc_site
wpiutil_site = "%s/edu/wpi/first/wpiutil/wpiutil-cpp" % frc_site

hal_libs = "hal-cpp-%s-linuxathena.zip" % hal_version
hal_headers = "hal-cpp-%s-headers.zip" % hal_version
wpiutil_libs = "wpiutil-cpp-%s-linuxathena.zip" % wpiutil_version


def _download(url):
    """
        Downloads the HAL zipfile to a temporary directory
    """

    import atexit
    import posixpath
    from urllib.request import urlretrieve, urlcleanup
    import sys

    print("Downloading", posixpath.basename(url))

    def _reporthook(count, blocksize, totalsize):
        percent = int(count * blocksize * 100 / totalsize)
        sys.stdout.write("\r%02d%%" % percent)
        sys.stdout.flush()

    filename, _ = urlretrieve(url, reporthook=_reporthook)
    atexit.register(urlcleanup)
    return filename


def extract_hal_headers(to=None):
    """
        Downloads the HAL headers and extracts them to a specified location
        
        :param to: is either a string or a dict of {src: dst}
    """
    url = "%s/%s/%s" % (hal_site, hal_version, hal_headers)
    return download_and_extract_zip(url, to=to)


def extract_hal_libs(to=None):
    """
        Downloads the HAL library zipfile and extracts it to a specified location
    
        :param to: is either a string or a dict of {src: dst}
    """
    url = "%s/%s/%s" % (hal_site, hal_version, hal_libs)
    return download_and_extract_zip(url, to=to)


def extract_wpiutil_libs(to=None):
    """
        Downloads the WPIUtil library zipfile and extracts it to a specified location
    
        :param to: is either a string or a dict of {src: dst}
    """
    url = "%s/%s/%s" % (wpiutil_site, wpiutil_version, wpiutil_libs)
    return download_and_extract_zip(url, to=to)


def download_and_extract_zip(url, to=None):
    """
        Utility method intended to be useful for downloading/extracting
        third party source zipfiles
    """

    import atexit
    import shutil
    import tempfile
    import zipfile

    if to is None:
        # generate temporary directory
        tod = tempfile.TemporaryDirectory()
        to = tod.name
        atexit.register(tod.cleanup)

    zip_fname = _download(url)
    with zipfile.ZipFile(zip_fname) as z:
        if isinstance(to, str):
            z.extractall(to)
            return to
        else:
            for src, dst in to.items():
                with z.open(src, "r") as zfp:
                    with open(dst, "wb") as fp:
                        shutil.copyfileobj(zfp, fp)
