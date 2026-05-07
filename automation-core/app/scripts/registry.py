import json
import os
import glob
from typing import Dict, List, Optional
from app.scripts.models import ScriptManifest

class ScriptRegistry:
    def __init__(self, scripts_dir: str = None):
        if scripts_dir is None:
            # Default to the data/scripts directory relative to the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.scripts_dir = os.path.join(base_dir, "data", "scripts")
        else:
            self.scripts_dir = scripts_dir
            
        self._scripts: Dict[str, ScriptManifest] = {}
        self.reload()

    def load_script(self, file_path: str) -> Optional[ScriptManifest]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Simple validation
            required_keys = ["id", "name", "version"]
            if not all(k in data for k in required_keys):
                print(f"Failed to load {file_path}: missing required keys")
                return None
                
            manifest = ScriptManifest(
                id=data["id"],
                name=data["name"],
                version=data["version"],
                description=data.get("description", ""),
                author=data.get("author", "Unknown"),
                schema=data.get("schema", {})
            )
            return manifest
        except Exception as e:
            print(f"Error loading script manifest {file_path}: {e}")
            return None

    def reload(self) -> None:
        self._scripts.clear()
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir, exist_ok=True)
            
        pattern = os.path.join(self.scripts_dir, "*.json")
        for file_path in glob.glob(pattern):
            manifest = self.load_script(file_path)
            if manifest:
                self._scripts[manifest.id] = manifest

    def get_script(self, script_id: str) -> Optional[ScriptManifest]:
        return self._scripts.get(script_id)

    def list_scripts(self) -> List[ScriptManifest]:
        return list(self._scripts.values())
