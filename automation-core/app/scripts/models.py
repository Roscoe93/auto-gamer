from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class ScriptManifest:
    id: str
    name: str
    version: str
    description: str
    author: str
    # JSON schema for parameter validation and form generation
    schema: Dict[str, Any] = field(default_factory=dict)
    
    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "schema": self.schema,
        }

@dataclass
class Profile:
    id: str
    script_id: str
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scriptId": self.script_id,
            "name": self.name,
            "parameters": self.parameters,
        }
