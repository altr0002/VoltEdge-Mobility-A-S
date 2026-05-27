from fastapi import APIRouter, Request

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health(request: Request) -> dict[str, str]:
    service_name = getattr(
        request.app.state,
        "service_name",
        "voltedge-operational-monitoring",
    )

    return {"status": "ok", "service": service_name}
