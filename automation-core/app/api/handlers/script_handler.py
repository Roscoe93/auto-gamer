import json
from typing import Any, Dict
from websockets.asyncio.server import ServerConnection

from app.api.message_router import MessageRouter
from app.scripts.registry import ScriptRegistry
from app.scripts.profile_manager import ProfileManager

def create_script_router(script_registry: ScriptRegistry, profile_manager: ProfileManager) -> MessageRouter:
    router = MessageRouter()

    async def handle_scripts_list(connection: ServerConnection, message: Dict[str, Any]) -> None:
        script_registry.reload()
        scripts = script_registry.list_scripts()
        await connection.send(json.dumps({
            "type": "scripts/listed",
            "payload": [s.to_payload() for s in scripts]
        }))

    async def handle_profiles_list(connection: ServerConnection, message: Dict[str, Any]) -> None:
        profile_manager.reload()
        profiles = profile_manager.list_profiles()
        await connection.send(json.dumps({
            "type": "profiles/listed",
            "payload": [p.to_payload() for p in profiles]
        }))

    async def handle_profiles_save(connection: ServerConnection, message: Dict[str, Any]) -> None:
        payload = message.get("payload", {})
        try:
            profile = profile_manager.save_profile(
                script_id=payload.get("scriptId"),
                name=payload.get("name"),
                parameters=payload.get("parameters", {}),
                profile_id=payload.get("id")
            )
            await connection.send(json.dumps({
                "type": "profiles/saved",
                "payload": profile.to_payload()
            }))
        except Exception as e:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "PROFILE_SAVE_FAILED", "message": str(e)}}))

    async def handle_profiles_delete(connection: ServerConnection, message: Dict[str, Any]) -> None:
        payload = message.get("payload", {})
        profile_id = payload.get("id")
        success = profile_manager.delete_profile(profile_id)
        if success:
            await connection.send(json.dumps({
                "type": "profiles/deleted",
                "payload": {"id": profile_id}
            }))
        else:
            await connection.send(json.dumps({"type": "error", "payload": {"code": "PROFILE_DELETE_FAILED", "message": "Profile not found"}}))

    router.register("scripts/list", handle_scripts_list)
    router.register("profiles/list", handle_profiles_list)
    router.register("profiles/save", handle_profiles_save)
    router.register("profiles/delete", handle_profiles_delete)
    
    return router
