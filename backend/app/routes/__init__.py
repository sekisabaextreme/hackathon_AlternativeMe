"""役割: 分割した各ルーターをまとめて FastAPI に公開する。"""

from fastapi import APIRouter

from .simulation import router as simulation_router
from .story import router as story_router
from .tree import router as tree_router


router = APIRouter()
router.include_router(simulation_router)
router.include_router(tree_router)
router.include_router(story_router)
