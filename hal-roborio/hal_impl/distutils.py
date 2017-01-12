#
# Utilities for compiling things that link against HAL or need the HAL
# headers
#
# Note: this file must not depend on anything else in the library, so we
# can import it from setup.py. Also used by the wpilib tests
#


hal_version = '2017.1.1'

hal_site = 'http://first.wpi.edu/FRC/roborio/maven/release/edu/wpi/first/wpilib/athena-runtime'
hal_zip = 'athena-runtime-%s.zip' % hal_version


def _download(url):
    '''
        Downloads the HAL zipfile to a temporary directory
    '''
    
    import atexit
    import posixpath
    from urllib.request import urlretrieve, urlcleanup
    import sys
    
    print("Downloading", posixpath.basename(url))
    
    def _reporthook(count, blocksize, totalsize):
        percent = int(count*blocksize*100/totalsize)
        sys.stdout.write("\r%02d%%" % percent)
        sys.stdout.flush()

    filename, _ = urlretrieve(url, reporthook=_reporthook)
    atexit.register(urlcleanup)
    return filename
    
def extract_halzip(to=None):
    '''
        Downloads the HAL zipfile and extracts it to a specified location
    
        :param to: is either a string or a dict of {src: dst}
    '''
    url = "%s/%s/%s" % (hal_site, hal_version, hal_zip)
    return download_and_extract_zip(url, to=to)
    
def download_and_extract_zip(url, to=None):
    '''
        Utility method intended to be useful for downloading/extracting
        third party source zipfiles
    '''
    
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
                with z.open(src, 'r') as zfp:
                    with open(dst, 'wb') as fp:
                        shutil.copyfileobj(zfp, fp)
