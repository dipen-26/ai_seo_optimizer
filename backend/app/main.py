from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pathlib import Path
from .api import cro_routes, gmb_routes

app = FastAPI(title='AI SEO Optimizer')

# Middleware to capture raw request body for debugging JSON parse errors
@app.middleware("http")
async def capture_request_body(request: Request, call_next):
    try:
        body = await request.body()
    except Exception:
        body = b""

    # Keep original raw body for debugging
    request.state.raw_body = body

    # If content-type is JSON and body contains literal newlines, attempt to sanitize
    content_type = request.headers.get('content-type', '')
    if 'application/json' in content_type and body:
        import json as _json
        try:
            # If JSON parses fine, nothing to do
            _json.loads(body)
        except Exception:
            # Replace literal CRLF / CR / LF with escaped \n sequence so JSON parser accepts it
            try:
                sanitized = body.replace(b'\r\n', b'\\n').replace(b'\r', b'\\n').replace(b'\n', b'\\n')
                # Cache sanitized body so downstream reads use it
                try:
                    request._body = sanitized
                except Exception:
                    pass
                request.state.raw_body_sanitized = sanitized
            except Exception:
                # If anything goes wrong, leave original body
                request.state.raw_body_sanitized = None

    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw = getattr(request.state, 'raw_body', b'')
    try:
        raw_text = raw.decode('utf-8')
    except Exception:
        raw_text = str(raw)
    return JSONResponse(status_code=422, content={
        "detail": exc.errors(),
        "raw_body_preview": raw_text[:200]
    })

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(cro_routes.router, prefix='/api/cro')
app.include_router(gmb_routes.router, prefix='/api/gmb')

BASE_DIR = Path(__file__).resolve().parents[2]
frontend_dir = BASE_DIR / 'frontend'
if frontend_dir.exists():
    app.mount('/', StaticFiles(directory=str(frontend_dir), html=True), name='frontend')
else:
    @app.get('/')
    async def root():
        return {'message': 'AI SEO Optimizer Backend Running'}
