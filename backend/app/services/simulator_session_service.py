"""
Simulator Session Manager

Quản lý các phiên mô phỏng (Session Manager) lưu trong system_settings.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy.orm import Session

from ..models.system import SystemSetting

SETTING_KEY = "simulator_sessions"


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def get_sessions(db: Session) -> List[Dict[str, Any]]:
    setting = (
        db.query(SystemSetting).filter(SystemSetting.key == SETTING_KEY).first()
    )
    if setting and setting.value:
        return setting.value
    return []


def get_session(session_id: str, db: Session) -> Optional[Dict[str, Any]]:
    sessions = get_sessions(db)
    for item in sessions:
        if item.get("id") == session_id:
            return item
    return None


def save_sessions(sessions: List[Dict[str, Any]], db: Session) -> List[Dict[str, Any]]:
    setting = (
        db.query(SystemSetting).filter(SystemSetting.key == SETTING_KEY).first()
    )
    if setting:
        setting.value = sessions
        setting.is_public = False
    else:
        setting = SystemSetting(
            key=SETTING_KEY,
            value=sessions,
            description="Simulator sessions (Session Manager)",
            is_public=False,
        )
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting.value


def start_session(
    name: str,
    note: Optional[str],
    db: Session,
    scenarios_snapshot: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    sessions = get_sessions(db)
    session = {
        "id": str(uuid4()),
        "name": name or f"Session-{len(sessions) + 1}",
        "note": note,
        "status": "running",
        "started_at": _now_iso(),
        "ended_at": None,
        "scenarios_snapshot": scenarios_snapshot or [],
    }
    sessions.insert(0, session)
    saved = save_sessions(sessions, db)
    return session, saved


def stop_session(
    session_id: str, db: Session, result: Optional[Dict[str, Any]] = None
) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    sessions = get_sessions(db)
    found = None
    for item in sessions:
        if item.get("id") == session_id:
            item["status"] = "stopped"
            item["ended_at"] = _now_iso()
            if result:
                item["result"] = result
            found = item
            break
    saved = save_sessions(sessions, db)
    return found, saved


def replay_session(session_id: str, db: Session) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Đánh dấu session đã replay và trả về snapshot kịch bản để apply simulator.
    """
    sessions = get_sessions(db)
    found = None
    for item in sessions:
        if item.get("id") == session_id:
            item["last_replayed_at"] = _now_iso()
            found = item
            break
    saved = save_sessions(sessions, db)
    return found, saved


def reset_sessions(db: Session) -> List[Dict[str, Any]]:
    return save_sessions([], db)


