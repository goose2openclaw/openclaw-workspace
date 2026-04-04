"""Model Loader - Load and manage 123 trend models"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_importer import BaseImporter


class ModelLoader(BaseImporter):
    """Loader for 123 trend models"""
    
    MODEL_REGISTRY_FILE = "models/model_registry.json"
    
    CATEGORIES = {
        "trend": "trend",
        "momentum": "momentum",
        "volatility": "volatility",
        "volume": "volume",
        "reversal": "reversal",
        "breakout": "breakout",
        "specialized": "specialized",
    }
    
    def __init__(self, base_path: str = "strategies"):
        super().__init__(base_path)
        self._models: Dict[str, Dict] = {}
        self._categories: Dict[str, List[Dict]] = {cat: [] for cat in self.CATEGORIES.keys()}
        self._registry: Optional[Dict] = None
        
    def load(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Load a single model by ID"""
        if model_id in self._models:
            return self._models[model_id]
            
        # Load from registry if not loaded
        if not self._registry:
            self._load_registry()
            
        for model in self._registry.get("models", []):
            if model.get("id") == model_id:
                self._models[model_id] = model
                self.on_load(model_id, model)
                return model
                
        return None
        
    def load_all(self) -> Dict[str, List[Dict]]:
        """Load all models by category"""
        if not self._registry:
            self._load_registry()
            
        for category in self._categories.keys():
            self.load_category(category)
            
        return self._categories
        
    def load_category(self, category: str) -> List[Dict]:
        """Load models by category"""
        if category in self._categories and self._categories[category]:
            return self._categories[category]
            
        if not self._registry:
            self._load_registry()
            
        models = [
            m for m in self._registry.get("models", [])
            if m.get("category") == category
        ]
        
        self._categories[category] = models
        return models
        
    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get model by ID (alias for load)"""
        return self.load(model_id)
        
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get model by name"""
        if not self._registry:
            self._load_registry()
            
        for model in self._registry.get("models", []):
            if model.get("name") == name:
                return model
        return None
        
    def search(self, query: str) -> List[Dict]:
        """Search models by name or description"""
        if not self._registry:
            self._load_registry()
            
        results = []
        query_lower = query.lower()
        
        for model in self._registry.get("models", []):
            if (query_lower in model.get("name", "").lower() or
                query_lower in model.get("description", "").lower()):
                results.append(model)
                
        return results
        
    def _load_registry(self) -> None:
        """Load model registry"""
        try:
            self._registry = self.load_json(self.MODEL_REGISTRY_FILE)
        except FileNotFoundError:
            # Create empty registry if not found
            self._registry = {
                "version": "11.0.0",
                "total_models": 0,
                "categories": {cat: 0 for cat in self.CATEGORIES.keys()},
                "models": []
            }
            
    def reload(self) -> None:
        """Reload all models"""
        self._models.clear()
        for cat in self._categories.keys():
            self._categories[cat] = []
        self._registry = None
        self.load_all()
