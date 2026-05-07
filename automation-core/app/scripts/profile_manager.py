import json
import os
import glob
import uuid
from typing import Dict, List, Optional
from app.scripts.models import Profile

class ProfileManager:
    def __init__(self, profiles_dir: str = None):
        if profiles_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.profiles_dir = os.path.join(base_dir, "data", "profiles")
        else:
            self.profiles_dir = profiles_dir
            
        self._profiles: Dict[str, Profile] = {}
        self.reload()

    def reload(self) -> None:
        self._profiles.clear()
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            
        pattern = os.path.join(self.profiles_dir, "*.json")
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                profile = Profile(
                    id=data.get("id"),
                    script_id=data.get("script_id") or data.get("scriptId"),
                    name=data.get("name"),
                    parameters=data.get("parameters", {})
                )
                if profile.id and profile.script_id:
                    self._profiles[profile.id] = profile
            except Exception as e:
                print(f"Error loading profile {file_path}: {e}")

    def list_profiles(self) -> List[Profile]:
        return list(self._profiles.values())

    def get_profile(self, profile_id: str) -> Optional[Profile]:
        return self._profiles.get(profile_id)

    def get_profiles_for_script(self, script_id: str) -> List[Profile]:
        return [p for p in self._profiles.values() if p.script_id == script_id]

    def save_profile(self, script_id: str, name: str, parameters: Dict[str, dict], profile_id: Optional[str] = None) -> Profile:
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            
        if not profile_id:
            profile_id = str(uuid.uuid4())
            
        profile = Profile(
            id=profile_id,
            script_id=script_id,
            name=name,
            parameters=parameters
        )
        
        file_path = os.path.join(self.profiles_dir, f"{profile_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({
                "id": profile.id,
                "scriptId": profile.script_id,
                "name": profile.name,
                "parameters": profile.parameters
            }, f, indent=2, ensure_ascii=False)
            
        self._profiles[profile_id] = profile
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            file_path = os.path.join(self.profiles_dir, f"{profile_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        return False
