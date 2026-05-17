from pydantic import BaseModel


class ClusterMetadata(BaseModel):
    cluster_id: int
    cluster_name: str
    description: str
    recommended_actions: list[str]
