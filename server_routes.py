import os
import sys

try:
    from aiohttp import web
    from server import PromptServer

    @PromptServer.instance.routes.get('/iterator_suite/browse')
    async def browse_directory(request):
        path = request.query.get('path', '').strip()

        if not path:
            if sys.platform == 'win32':
                return web.json_response({
                    "path": "", "parent": None, "dirs": _windows_drives()
                })
            path = '/'

        path = os.path.normpath(path)
        if not os.path.isdir(path):
            return web.json_response({"error": f"Not a directory: {path}"}, status=400)

        try:
            raw = [
                {"name": e.name, "path": os.path.join(path, e.name)}
                for e in os.scandir(path)
                if e.is_dir() and not e.name.startswith('.')
            ]
            dirs   = sorted(raw, key=lambda d: d["name"].lower())
            parent = os.path.dirname(path)
            if parent == path:
                # at filesystem root
                parent = "" if sys.platform == 'win32' else None
            return web.json_response({"path": path, "parent": parent, "dirs": dirs})
        except OSError as exc:
            return web.json_response({"error": str(exc)}, status=403)

except Exception:
    pass  # not running inside ComfyUI


def _windows_drives():
    import ctypes
    import string
    drives  = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drive = f"{letter}:\\"
            drives.append({"name": drive, "path": drive})
        bitmask >>= 1
    return drives
