import logging
import mimetypes
from pathlib import Path
from typing import Optional, Set

from fastapi import HTTPException, Request, Response
from fastapi.responses import FileResponse

_log = logging.getLogger(__name__)


class LocalizedStaticFiles(Response):
    def __init__(self, base_dir: str, default_locale: str = "en", supported_locales: Optional[Set[str]] = None):
        self.base_dir = Path(base_dir).resolve()
        self.default_locale = default_locale
        if supported_locales:
            self.supported_locales = supported_locales
        else:
            self.supported_locales = set()
            for d in self.base_dir.iterdir():
                if not d.is_dir():
                    continue
                if d.name not in self.supported_locales:
                    self.supported_locales.add(d.name)
            _log.info("Detected supported locales: %s", self.supported_locales)

    def get_static_page(self, request: Request) -> Response:
        uri_path = request.url.path
        if uri_path.startswith("/api/"):
            _log.warning("Not found: %s", uri_path)
            raise HTTPException(status_code=404, detail="Not found")

        language = self._get_language(request)
        resolved_path = self._resolve_path(uri_path, language)

        file_path = self.base_dir / resolved_path
        file_path = file_path.resolve()

        if not str(file_path).startswith(str(self.base_dir)):
            raise HTTPException(status_code=404, detail="Not found")

        if file_path.is_dir():
            file_path = file_path / "index.html"

        if not file_path.is_file():
            # Fallback to language root index.html
            fallback = self.base_dir / language / "index.html"
            if fallback.is_file():
                file_path = fallback
            else:
                _log.warning("Static page not found: %s", file_path)
                raise HTTPException(status_code=404, detail="Page not found")
        return FileResponse(
            path=file_path,
            media_type=mimetypes.guess_type(str(file_path))[0] or "application/octet-stream",
            filename=file_path.name if file_path.suffix != ".html" else None,
        )

    def _get_language(self, request: Request) -> str:
        header = request.headers.get("accept-language", "")
        _log.debug("Accept-Language: %s", header)
        # Parse languages with q-values (simple version)
        languages = []
        for part in header.split(","):
            if ";" in part:
                lang, q = part.split(";", 1)
                q = float(q.split("=")[1]) if "=" in q else 1.0
            else:
                lang, q = part.strip(), 1.0
            languages.append((lang.split("-")[0], q))  # Use base language (pl-PL -> pl)

        # Sort by quality descending
        languages.sort(key=lambda x: x[1], reverse=True)

        # Find first supported
        locale = self.default_locale
        for lang, _ in languages:
            if lang in self.supported_locales:
                locale = lang
                break
        _log.debug("Resolved language: %s", locale)
        return locale

    def _resolve_path(self, uri_path: str, language: str) -> str:
        path = uri_path if uri_path != "/" else "/index.html"
        path = path.lstrip("/")

        if not any(path.startswith(f"{lang}/") for lang in self.supported_locales):
            path = f"{language}/{path}"
        _log.debug("URI path: %s", uri_path)
        _log.debug("Resolved path: %s", path)
        # Normalize: remove double slashes, etc.
        return Path(path).as_posix()
