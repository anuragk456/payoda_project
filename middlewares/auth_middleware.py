from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

from config import SECRET_KEY, ALGORITHM, HARDCODED_USERNAME

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
        self.public_paths = (
            "/auth/login",
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/static",
        )

    def _is_public_path(self, path: str) -> bool:
        for p in self.public_paths:
            if path == p or path.startswith(p):
                return True
        return False

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        path = request.url.path

        if self._is_public_path(path):
            await self.app(scope, receive, send)
            return

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = JSONResponse({"detail": "Not authenticated"}, status_code=401)
            await response(scope, receive, send)
            return

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if not username or username != HARDCODED_USERNAME:
                raise JWTError()
            scope["authenticated_user"] = username
        except JWTError:
            response = JSONResponse({"detail": "Invalid or expired token"}, status_code=401)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
