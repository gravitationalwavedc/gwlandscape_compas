import os
import re
from pathlib import Path


def get_compas_version():
    """Get the COMPAS version string from the changelog file in the local COMPAS repo,
    which is located using the COMPAS_ROOT_DIR environment variable

    Returns
    -------
    str or None
        COMPAS version string
    """    
    compas_dir = os.environ.get("COMPAS_ROOT_DIR", None)
    if not compas_dir:
        return None

    compas_changelog_file = Path(compas_dir) / "src" / "changelog.h"
    compas_changelog = compas_changelog_file.read_text()
    version_match = re.search(
        r"VERSION_STRING = ['\"]([^'\"]*)['\"]", compas_changelog, re.M
    )
    if not version_match:
        return None

    return version_match.group(1)
