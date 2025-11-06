from fastapi import APIRouter

router = APIRouter(
    prefix='/utils',
    tags=['utils'],
)

@router.get('/health_check')
def health_check() -> bool:
    return True
