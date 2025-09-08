from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import Request
from fastapi.responses import Response
import json
import time

from utils.logger import logger, mask_sensitive

class LoggingMiddleware:
    """ASGI middleware that logs incoming requests and responses (excludes sensitive fields)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        start = time.time()
        headers = dict(request.headers)
        logged_headers = mask_sensitive(headers)
        logger.info(f"Request -> {request.method} {request.url.path} headers={logged_headers}")

        # Use a small inner send wrapper to capture the response status and length
        response_body = b""
        response_status = None

        async def send_wrapper(message):
            nonlocal response_body, response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            if message["type"] == "http.response.body":
                response_body += message.get("body", b"")
            await send(message)

        await self.app(scope, receive, send_wrapper)

        elapsed_ms = (time.time() - start) * 1000
        body_text = None
        try:
            body_text = response_body.decode("utf-8")
            parsed = json.loads(body_text) if body_text else None
            if isinstance(parsed, dict):
                parsed = mask_sensitive(parsed)
            logger.info(f"Response <- status={response_status} body={parsed} time_ms={elapsed_ms:.2f}")
        except Exception:
            logger.info(f"Response <- status={response_status} (non-json or large body) time_ms={elapsed_ms:.2f}")
