"""Base Importer for Strategy System"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseImporter(ABC):
    """Base class for all importers"""
    
    def __init__(self, base_path: str = "strategies"):
        self.base_path = Path(base_path)
        self._loaded_data: Dict[str, Any] = {}
        
    @abstractmethod
    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Load specific item by name"""
        pass
    
    def load_all(self) -> Dict[str, Any]:
        """Load all items"""
        raise NotImplementedError
        
    def load_json(self, relative_path: str) -> Dict[str, Any]:
        """Load JSON file"""
        file_path = self.base_path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    def save_json(self, relative_path: str, data: Dict[str, Any]) -> None:
        """Save JSON file"""
        file_path = self.base_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def validate(self, data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate data against schema, return list of errors"""
        errors = []
        
        for field, field_type in schema.items():
            if field_type.get("required", False) and field not in data:
                errors.append(f"Missing required field: {field}")
                
        return errors
        
    def on_load(self, name: str, data: Dict[str, Any]) -> None:
        """Hook called after loading"""
        pass
        
    def on_error(self, name: str, error: Exception) -> None:
        """Hook called on error"""
        print(f"Error loading {name}: {error}")
