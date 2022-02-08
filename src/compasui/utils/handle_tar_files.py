import os
import shutil
import tarfile


def compress_files_into_tarball(filespath, tarfilepath):
    """
    Compress the contents of a directory into a tarball
    params:
    filespath: path to the directory to be compressed
    tarfilepath: tarfile path
    """

    if os.path.exists(tarfilepath):
        return tarfilepath

    with tarfile.open(tarfilepath, "w:gz") as tar:
        tar.add(filespath, arcname=os.path.basename(filespath))