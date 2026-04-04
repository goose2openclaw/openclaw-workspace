"""Config Importer - Parse and validate JSON configurations"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_importer import BaseImporter


class ConfigImporter(BaseImporter):
    """Importer for JSON configuration files"""
    
    def __init__(self, base_path: str = "strategies"):
        super().__init__(base_path)
        
    def load_config(self, relative_path: str) -> Optional[Dict[str, Any]]:
        """Load a configuration file"""
        try:
            return self.load_json(relative_path)
        except Exception as e:
            self.on_error(relative_path, e)
            return None
            
    def parse(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and normalize configuration"""
        parsed = {
            "id": config.get("id"),
            "name": config.get("name"),
            "version": config.get("version", "1.0.0"),
            "enabled": config.get("enabled", True),
            "priority": config.get("priority", 999),
        }
        
        # Parse allocation
        if "allocation" in config:
            parsed["allocation"] = self._parse_allocation(config["allocation"])
            
        # Parse risk
        if "risk" in config:
            parsed["risk"] = self._parse_risk(config["risk"])
            
        # Parse indicators
        if "indicators" in config:
            parsed["indicators"] = self._parse_indicators(config["indicators"])
            
        return parsed
        
    def _parse_allocation(self, alloc: Dict[str, Any]) -> Dict[str, float]:
        """Parse allocation config"""
        return {
            "target": float(alloc.get("target", 0)),
            "min": float(alloc.get("min", 0)),
            "max": float(alloc.get("max", 0)),
        }
        
    def _parse_risk(self, risk: Dict[str, Any]) -> Dict[str, float]:
        """Parse risk config"""
        return {
            "stop_loss": float(risk.get("stop_loss", 0)),
            "take_profit": float(risk.get("take_profit", 0)),
            "max_position_size": float(risk.get("max_position_size", 0)),
            "daily_loss_limit": float(risk.get("daily_loss_limit", 0)),
        }
        
    def _parse_indicators(self, indicators: Dict[str, Any]) -> Dict[str, List[str]]:
        """Parse indicators config"""
        return {
            "primary": indicators.get("primary", []),
            "secondary": indicators.get("secondary", []),
            "filters": indicators.get("filters", []),
        }
        
    def validate(self, config: Dict[str, Any]) -> List[str]:
        """Validate configuration structure"""
        errors = []
        
        if "id" not in config:
            errors.append("Missing 'id' field")
            
        if "name" not in config:
            errors.append("Missing 'name' field")
            
        return errors
        
    def merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Merge two configurations, override takes precedence"""
        merged = base.copy()
        for key, value in override.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value
        return merged
