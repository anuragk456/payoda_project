import logging
import sys
from typing import Dict, Any

from config import LOG_LEVEL

logger = logging.getLogger("fastapi_auth_app")
logger.setLevel(LOG_LEVEL)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(LOG_LEVEL)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def mask_sensitive(data: Dict[str, Any]) -> Dict[str, Any]:
    """Utility to mask sensitive information in logs."""
    masked = {}
    for k, v in data.items():
        if k.lower() in ("password", "authorization", "token", "access_token"):
            masked[k] = "***REDACTED***"
        else:
            masked[k] = v
    return masked
