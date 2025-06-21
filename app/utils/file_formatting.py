def get_mime_type(name):
    ext = name.lower().split(".")[-1]
    return {
        "pdf": "application/pdf",
        "tif": "image/tiff",
        "tiff": "image/tiff",
        "jpeg": "image/jpeg",
        "jpg": "image/jpeg",
        "png": "image/png",
    }.get(ext, "application/octet-stream")
