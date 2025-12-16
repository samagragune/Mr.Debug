import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    # When run as a module (uvicorn Backend.main:app)
    from Backend.error_handling import interpret_error  # type: ignore
except ImportError:
    # When run from inside the Backend folder (python main.py / uvicorn main:app)
    from error_handling import interpret_error


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_INDEX = BASE_DIR.parent / "Frontend" / "index.html"


app = FastAPI(
    title="Code Execution Service",
    description="Execute Python code safely with timeout protection",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str = Field(..., min_length=1)
    stdin: Optional[str] = Field("", description="Optional standard input for the program")
    timeout: Optional[int] = Field(10, ge=1, le=60)


class CodeResponse(BaseModel):
    status: str
    output: Optional[str] = None
    error: Optional[str] = None
    explanation: Optional[dict] = None   
    execution_time: Optional[float] = None


@app.get("/")
async def serve_frontend():
    """
    Serve the bundled frontend so localhost shows the app instead of a directory listing.
    """
    if FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    # Fallback: keep a simple JSON response if the frontend is missing.
    return {
        "service": "Code Execution Service",
        "status": "running",
        "endpoint": "/run",
    }


@app.get("/health")
async def health():
    return {
        "service": "Code Execution Service",
        "status": "running",
        "endpoint": "/run",
    }


@app.post("/run", response_model=CodeResponse)
async def run_code(request: CodeRequest):
    start_time = time.time()
    expects_input = ("input(" in request.code) or ("raw_input(" in request.code)
    has_stdin = bool((request.stdin or "").strip())
    
    try:
        result = subprocess.run(
            [sys.executable, "-c", request.code],
            capture_output=True,
            text=True,
            input=request.stdin or "",
            timeout=request.timeout,
        )

        execution_time = time.time() - start_time

        if result.returncode == 0:
            return CodeResponse(
                status="success",
                output=result.stdout or "(no output)",
                execution_time=execution_time
            )

    
        explanation = interpret_error(
            code=request.code,
            error=result.stderr
        )

        return CodeResponse(
            status="error",
            error=result.stderr,
            explanation=explanation,
            execution_time=execution_time
        )

    except subprocess.TimeoutExpired:
        if expects_input and not has_stdin:
            return CodeResponse(
                status="error",
                error="Your code is waiting for input, but no input was provided.",
                explanation={
                    "summary": "Your code is waiting for user input.",
                    "why_it_happened": "The script calls input() but the API call did not supply stdin data.",
                    "how_to_fix": [
                        "Add the expected input in the 'Program input' field before running",
                        "Or remove input() calls if they are not required"
                    ],
                    "confidence": 0.95
                },
                execution_time=time.time() - start_time
            )

        return CodeResponse(
            status="error",
            error=f"Execution timed out after {request.timeout} seconds",
            execution_time=time.time() - start_time
        )

    except Exception as e:
        return CodeResponse(
            status="error",
            error=str(e),
            execution_time=time.time() - start_time
        )


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=os.getenv("RELOAD", "true").lower() == "true",
    )
