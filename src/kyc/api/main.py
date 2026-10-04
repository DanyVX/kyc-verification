from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from kyc.api.rate_limit import FixedWindowRateLimiter
from kyc.api.uploads import UploadRejected, validate_image_upload
from kyc.audit import AuditLedger
from kyc.decision import DecisionEngine
from kyc.domain import KycSession, SignalBundle
from kyc.session_repository import SessionRepository
from kyc.settings import settings
from kyc.storage import EncryptedStore
from kyc.workflow import InvalidTransition, apply_event

app = FastAPI(title="Synthetic KYC Verification Demo", version="0.1.0")
sessions: dict[UUID, KycSession] = {}
ledger = AuditLedger()
engine = DecisionEngine(Path(__file__).parents[3] / "config" / "decision-rules.yaml")
store = EncryptedStore(settings.encryption_key)
repository = SessionRepository(settings.database_url)
rate_limiter = FixedWindowRateLimiter(settings.requests_per_minute)


def find_session(session_id: UUID) -> KycSession | None:
    return sessions.get(session_id) or repository.get(session_id)


def client_auth(x_api_key: str = Header()) -> None:
    if x_api_key != settings.client_api_key:
        raise HTTPException(status_code=401, detail="invalid credentials")


def admin_auth(x_api_key: str = Header()) -> None:
    if x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="invalid credentials")


@app.middleware("http")
async def request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
    client_key = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(client_key):
        raise HTTPException(status_code=429, detail="request rate limited")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "generated-local")
    return response


class EventBody(BaseModel):
    event: str
    idempotency_key: str


class DecideBody(BaseModel):
    signals: SignalBundle


@app.post("/sessions", dependencies=[Depends(client_auth)])
def create_session() -> KycSession:
    session = KycSession()
    sessions[session.id] = session
    repository.save(session)
    ledger.append(session.id, "client", "create")
    return session


@app.post("/sessions/{session_id}/events", dependencies=[Depends(client_auth)])
def transition(session_id: UUID, body: EventBody) -> KycSession:
    session = find_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="not found")
    try:
        updated = apply_event(session, body.event, body.idempotency_key)
    except InvalidTransition as exc:
        ledger.append(session_id, "client", "invalid_transition", str(exc).split(":")[0])
        raise HTTPException(status_code=409, detail="event cannot be applied") from exc
    ledger.append(session_id, "client", body.event)
    repository.save(updated)
    return updated


@app.put("/sessions/{session_id}/uploads/{kind}", dependencies=[Depends(client_auth)])
async def upload(session_id: UUID, kind: str, request: Request) -> dict[str, str]:
    """Raw image upload with magic-byte/dimension checks; stores ciphertext only."""
    if kind not in {"front", "back", "selfie"}:
        raise HTTPException(status_code=404, detail="not found")
    if find_session(session_id) is None:
        raise HTTPException(status_code=404, detail="not found")
    payload = await request.body()
    try:
        validate_image_upload(payload, settings.max_upload_bytes)
    except UploadRejected:
        raise HTTPException(status_code=422, detail="upload rejected") from None
    key = f"session/{session_id}/{kind}"
    store.put(key, payload)
    ledger.append(session_id, "client", f"upload_{kind}")
    return {"status": "stored", "kind": kind}


@app.post("/sessions/{session_id}/decision", dependencies=[Depends(client_auth)])
def decide(session_id: UUID, body: DecideBody) -> object:
    if find_session(session_id) is None:
        raise HTTPException(status_code=404, detail="not found")
    decision = engine.decide(body.signals)
    ledger.append(session_id, "system", "decision", decision.verdict.value)
    return decision


@app.get("/admin/sessions", dependencies=[Depends(admin_auth)])
def list_sessions() -> list[dict[str, str]]:
    return [
        {"id": str(item.id), "state": item.state.value, "expires_at": item.expires_at.isoformat()}
        for item in repository.list_recent()
    ]


@app.post("/admin/sessions/{session_id}/review", dependencies=[Depends(admin_auth)])
def review_session(session_id: UUID, idempotency_key: str = Header()) -> KycSession:
    session = find_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="not found")
    try:
        updated = apply_event(session, "review", idempotency_key)
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail="event cannot be applied") from exc
    repository.save(updated)
    ledger.append(session_id, "admin", "review")
    return updated


@app.delete("/sessions/{session_id}", dependencies=[Depends(client_auth)])
def erase_session(session_id: UUID) -> dict[str, int]:
    """DSAR-style erase for raw encrypted demo artifacts."""
    deleted = store.erase_prefix(f"session/{session_id}/")
    sessions.pop(session_id, None)
    ledger.append(session_id, "client", "erase")
    return {"erased_artifacts": deleted}


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
