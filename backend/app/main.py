from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import cro_routes, gmb_routes

app = FastAPI(title='AI SEO Optimizer')

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
