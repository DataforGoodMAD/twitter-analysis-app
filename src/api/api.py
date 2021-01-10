from fastapi.routing import APIRouter

from .timeline import timeline
from .users import users


api = APIRouter(prefix='/api')

api.include_router(timeline)
api.include_router(users)
