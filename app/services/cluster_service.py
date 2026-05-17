from app.ml.mappings import CLUSTER_DETAILS
from app.schemas.cluster import ClusterMetadata


class ClusterService:
    def list_clusters(self) -> list[ClusterMetadata]:
        return [
            ClusterMetadata(
                cluster_id=cluster_id,
                cluster_name=str(details["cluster_name"]),
                description=str(details["business_summary"]),
                recommended_actions=list(details["recommended_actions"]),
            )
            for cluster_id, details in sorted(CLUSTER_DETAILS.items())
        ]
