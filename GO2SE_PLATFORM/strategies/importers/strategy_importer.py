"""Strategy Importer - Load and manage tool strategies"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_importer import BaseImporter


class StrategyImporter(BaseImporter):
    """Importer for 7 tool strategies"""
    
    STRATEGY_FILES = {
        "rabbit": "config/rabbit.json",
        "mole": "config/mole.json",
        "oracle": "config/oracle.json",
        "follow": "config/follow.json",
        "hitchhike": "config/hitchhike.json",
        "airdrop": "config/airdrop.json",
        "crowdsource": "config/crowdsource.json",
    }
    
    REQUIRED_FIELDS = [
        "id", "name", "version", "enabled", "priority",
        "allocation", "risk", "symbols", "indicators"
    ]
    
    def __init__(self, base_path: str = "strategies"):
        super().__init__(base_path)
        self._strategies: Dict[str, Dict] = {}
        
    def load(self, name: str) -> Optional[Dict[str, Any]]:
        """Load a single strategy by name"""
        if name in self._strategies:
            return self._strategies[name]
            
        file_path = self.STRATEGY_FILES.get(name)
        if not file_path:
            return None
            
        try:
            data = self.load_json(file_path)
            self._strategies[name] = data
            self.on_load(name, data)
            return data
        except Exception as e:
            self.on_error(name, e)
            return None
            
    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """Load all 7 tool strategies"""
        strategies = {}
        for name in self.STRATEGY_FILES.keys():
            strategy = self.load(name)
            if strategy:
                strategies[name] = strategy
        return strategies
        
    def get_enabled(self) -> List[Dict[str, Any]]:
        """Get list of enabled strategies"""
        enabled = []
        for strategy in self._strategies.values():
            if strategy.get("enabled", False):
                enabled.append(strategy)
        return sorted(enabled, key=lambda x: x.get("priority", 999))
        
    def get_by_id(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get strategy by ID"""
        for strategy in self._strategies.values():
            if strategy.get("id") == strategy_id:
                return strategy
        return None
        
    def validate(self, strategy: Dict[str, Any]) -> List[str]:
        """Validate strategy configuration"""
        errors = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in strategy:
                errors.append(f"Missing required field: {field}")
                
        # Validate allocation
        if "allocation" in strategy:
            alloc = strategy["allocation"]
            for key in ["target", "min", "max"]:
                if key not in alloc:
                    errors.append(f"Missing allocation.{key}")
                    
        # Validate risk
        if "risk" in strategy:
            risk = strategy["risk"]
            for key in ["stop_loss", "take_profit"]:
                if key not in risk:
                    errors.append(f"Missing risk.{key}")
                    
        return errors
        
    def reload(self, name: str) -> Optional[Dict[str, Any]]:
        """Reload a strategy"""
        if name in self._strategies:
            del self._strategies[name]
        return self.load(name)
