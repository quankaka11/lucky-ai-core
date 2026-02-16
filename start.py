"""Railway entry point – reads PORT from environment."""
import os
import uvicorn

port = int(os.environ.get("PORT", 8080))
print(f">>> Starting on port {port} (from $PORT env)")
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
