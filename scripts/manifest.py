import uuid
import json
from dataclasses import dataclass


@dataclass
class WoxManifest:
    ID: str
    ActionKeyword: str
    Name: str
    Description: str
    Author: str
    Version: str
    Language: str
    Website: str
    IcoPath: str
    ExecuteFileName: str

    def generate_id(self):
        return str(uuid.uuid4()).replace('-', '').upper()

    @classmethod
    def from_file(cls, file_path: str = "plugin.json"):
        with open(file_path, 'r') as f:
            return cls(**json.load(f))


@dataclass
class FlowLauncherManifest(WoxManifest):
    pass
