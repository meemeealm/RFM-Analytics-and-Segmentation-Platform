from fastapi import APIRouter, Depends

from app.core.security import require_api_key_placeholder
from app.schemas.cluster import ClusterMetadata
from app.services.cluster_service import ClusterService

router = APIRouter(
    prefix="/clusters",
    tags=["clusters"],
    dependencies=[Depends(require_api_key_placeholder)],
)

cluster_service = ClusterService()


@router.get("", response_model=list[ClusterMetadata], summary="List cluster metadata")
async def list_clusters() -> list[ClusterMetadata]:
    return cluster_service.list_clusters()
