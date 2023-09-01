from pathlib import Path
from django.http import Http404, FileResponse
from django.core.exceptions import ValidationError
from .models import FileDownloadToken


def file_download(request):
    # Get the file token from the request and make sure it's real
    token = request.GET.get("fileId", None)
    if not token:
        raise Http404

    try:
        # First try the token as a file download token
        fdl = FileDownloadToken.get_by_token(token)

        # Was a file found with this token?
        if fdl:
            file_path = Path(fdl.path)
            return FileResponse(
                open(file_path, "rb"),
                as_attachment="forceDownload" in request.GET,
                filename=file_path.name,
                content_type="application/octet-stream",
            )

        raise Http404
    except ValidationError:
        raise Http404
