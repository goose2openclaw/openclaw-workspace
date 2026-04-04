"""
策略导入器 - JSON/YAML配置动态加载
=====================================

支持:
1. JSON格式导入
2. YAML格式导入
3. API动态导入
4. 配置验证和合并
"""

import json
import yaml
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import importlib.util

# ==================== 导入源类型 ====================

class ImportSource(Enum):
    """导入源类型"""
    JSON_FILE = "json_file"
    YAML_FILE = "yaml_file"
    API = "api"
    DICT = "dict"
    MODULE = "module"

@dataclass
class ImportResult:
    """导入结果"""
    success: bool
    source: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str = ""
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now().isoformat()
        if self.warnings is None:
            self.warnings = []

# ==================== 策略导入器基类 ====================

class BaseStrategyImporter:
    """策略导入器基类"""
    
    def __init__(self):
        self.imported_strategies: Dict[str, Dict] = {}
        self.import_history: List[ImportResult] = []
    
    def import_strategy(self, source: str, **kwargs) -> ImportResult:
        """导入策略 - 子类实现"""
        raise NotImplementedError
    
    def validate_strategy(self, data: Dict) -> tuple[bool, List[str]]:
        """验证策略数据"""
        errors = []
        warnings = []
        
        # 必须字段检查
        required_fields = ["tool_type", "name", "position_limit", "stop_loss", "take_profit"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # 类型检查
        if "position_limit" in data:
            if not isinstance(data["position_limit"], (int, float)):
                errors.append("position_limit must be a number")
            elif data["position_limit"] > 100 or data["position_limit"] < 0:
                warnings.append("position_limit should be between 0 and 100")
        
        if "stop_loss" in data:
            if not isinstance(data["stop_loss"], (int, float)):
                errors.append("stop_loss must be a number")
        
        if "take_profit" in data:
            if not isinstance(data["take_profit"], (int, float)):
                errors.append("take_profit must be a number")
        
        # 风控检查
        if "stop_loss" in data and "take_profit" in data:
            if data["stop_loss"] >= data["take_profit"]:
                warnings.append("stop_loss >= take_profit may be too aggressive")
        
        return len(errors) == 0, warnings
    
    def merge_strategy(self, existing: Dict, new: Dict) -> Dict:
        """合并策略配置"""
        merged = existing.copy()
        merged.update(new)
        
        # 深度合并条件
        if "conditions" in existing and "conditions" in new:
            merged["conditions"] = {**existing["conditions"], **new["conditions"]}
        
        if "applicable_models" in existing and "applicable_models" in new:
            # 合并模型列表，去重
            merged["applicable_models"] = list(set(
                existing["applicable_models"] + new["applicable_models"]
            ))
        
        merged["_merged_at"] = datetime.now().isoformat()
        merged["_merged_from"] = [existing.get("_source", "unknown"), new.get("_source", "unknown")]
        
        return merged
    
    def get_history(self) -> List[ImportResult]:
        """获取导入历史"""
        return self.import_history

# ==================== JSON导入器 ====================

class JSONStrategyImporter(BaseStrategyImporter):
    """JSON格式策略导入器"""
    
    def import_strategy(self, source: str, **kwargs) -> ImportResult:
        """
        从JSON文件或字符串导入策略
        
        Args:
            source: 文件路径或JSON字符串
            encoding: 文件编码，默认utf-8
        """
        encoding = kwargs.get("encoding", "utf-8")
        
        try:
            # 判断是文件还是字符串
            if os.path.exists(source):
                with open(source, 'r', encoding=encoding) as f:
                    data = json.load(f)
                source_type = "file"
            else:
                data = json.loads(source)
                source_type = "string"
            
            # 验证
            valid, warnings = self.validate_strategy(data)
            
            result = ImportResult(
                success=True,
                source=source,
                data=data,
                warnings=warnings
            )
            
            if not valid:
                result.success = False
                result.error = f"Validation failed: {warnings}"
            
            self.import_history.append(result)
            
            # 存储
            if data.get("tool_type"):
                data["_source"] = source
                data["_imported_at"] = datetime.now().isoformat()
                self.imported_strategies[data["tool_type"]] = data
            
            return result
            
        except json.JSONDecodeError as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"JSON parse error: {str(e)}"
            )
            self.import_history.append(result)
            return result
        except Exception as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"Import error: {str(e)}"
            )
            self.import_history.append(result)
            return result
    
    def import_batch(self, sources: List[str]) -> List[ImportResult]:
        """批量导入JSON文件"""
        return [self.import_strategy(s) for s in sources]

# ==================== YAML导入器 ====================

class YAMLStrategyImporter(BaseStrategyImporter):
    """YAML格式策略导入器"""
    
    def import_strategy(self, source: str, **kwargs) -> ImportResult:
        """
        从YAML文件或字符串导入策略
        """
        try:
            # 判断PyYAML是否可用
            try:
                import yaml
            except ImportError:
                return ImportResult(
                    success=False,
                    source=source,
                    error="PyYAML not installed. Run: pip install pyyaml"
                )
            
            # 判断是文件还是字符串
            if os.path.exists(source):
                with open(source, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                source_type = "file"
            else:
                data = yaml.safe_load(source)
                source_type = "string"
            
            # 如果是完整配置文件，提取tools部分
            if "tools" in data and isinstance(data["tools"], dict):
                # 批量导入多个工具
                results = []
                for tool_type, tool_data in data["tools"].items():
                    tool_data["tool_type"] = tool_type
                    valid, warnings = self.validate_strategy(tool_data)
                    
                    result = ImportResult(
                        success=valid,
                        source=f"{source}:{tool_type}",
                        data=tool_data,
                        warnings=warnings
                    )
                    
                    if not valid:
                        result.error = f"Validation failed for {tool_type}"
                    
                    self.import_history.append(result)
                    
                    # 存储
                    tool_data["_source"] = source
                    tool_data["_imported_at"] = datetime.now().isoformat()
                    self.imported_strategies[tool_type] = tool_data
                    
                    results.append(result)
                
                # 返回第一个作为代表
                return results[0] if results else ImportResult(
                    success=False,
                    source=source,
                    error="No tools found in YAML"
                )
            else:
                # 单个策略
                valid, warnings = self.validate_strategy(data)
                
                result = ImportResult(
                    success=valid,
                    source=source,
                    data=data,
                    warnings=warnings
                )
                
                if not valid:
                    result.error = f"Validation failed: {warnings}"
                
                self.import_history.append(result)
                
                if data.get("tool_type"):
                    data["_source"] = source
                    data["_imported_at"] = datetime.now().isoformat()
                    self.imported_strategies[data["tool_type"]] = data
                
                return result
                
        except yaml.YAMLError as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"YAML parse error: {str(e)}"
            )
            self.import_history.append(result)
            return result
        except Exception as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"Import error: {str(e)}"
            )
            self.import_history.append(result)
            return result
    
    def import_batch(self, sources: List[str]) -> List[ImportResult]:
        """批量导入YAML文件"""
        return [self.import_strategy(s) for s in sources]

# ==================== API导入器 ====================

class APIStrategyImporter(BaseStrategyImporter):
    """API动态策略导入器"""
    
    def __init__(self, api_endpoint: str = None):
        super().__init__()
        self.api_endpoint = api_endpoint
        self.custom_loaders: Dict[str, Callable] = {}
    
    def register_loader(self, strategy_type: str, loader: Callable):
        """
        注册自定义加载器
        
        Args:
            strategy_type: 策略类型标识
            loader: 加载函数，接受source参数，返回Dict
        """
        self.custom_loaders[strategy_type] = loader
    
    def import_strategy(self, source: str, **kwargs) -> ImportResult:
        """
        从API导入策略
        
        Args:
            source: API端点或策略标识
            method: HTTP方法，默认GET
            headers: 请求头
            params: 查询参数
        """
        import requests
        
        method = kwargs.get("method", "GET")
        headers = kwargs.get("headers", {})
        params = kwargs.get("params", {})
        timeout = kwargs.get("timeout", 30)
        
        try:
            response = requests.request(
                method=method,
                url=source if source.startswith("http") else f"{self.api_endpoint}/{source}",
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            if response.status_code != 200:
                return ImportResult(
                    success=False,
                    source=source,
                    error=f"API returned status {response.status_code}"
                )
            
            data = response.json()
            
            # 如果是列表，导入第一个
            if isinstance(data, list):
                if len(data) == 0:
                    return ImportResult(
                        success=False,
                        source=source,
                        error="Empty response"
                    )
                data = data[0]
            
            valid, warnings = self.validate_strategy(data)
            
            result = ImportResult(
                success=valid,
                source=source,
                data=data,
                warnings=warnings
            )
            
            if not valid:
                result.error = f"Validation failed: {warnings}"
            
            self.import_history.append(result)
            
            if data.get("tool_type"):
                data["_source"] = source
                data["_imported_at"] = datetime.now().isoformat()
                self.imported_strategies[data["tool_type"]] = data
            
            return result
            
        except requests.RequestException as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"API request error: {str(e)}"
            )
            self.import_history.append(result)
            return result
        except Exception as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"Import error: {str(e)}"
            )
            self.import_history.append(result)
            return result

# ==================== 模块导入器 ====================

class ModuleStrategyImporter(BaseStrategyImporter):
    """Python模块导入器"""
    
    def import_strategy(self, source: str, **kwargs) -> ImportResult:
        """
        从Python模块导入策略
        
        Args:
            source: 模块路径，如 /path/to/strategies/rabbit.py
            class_name: 类名，默认StrategyConfig
        """
        class_name = kwargs.get("class_name", "StrategyConfig")
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location("strategy_module", source)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取类
            if not hasattr(module, class_name):
                return ImportResult(
                    success=False,
                    source=source,
                    error=f"Module {source} does not have class {class_name}"
                )
            
            strategy_class = getattr(module, class_name)
            
            # 获取配置
            if hasattr(strategy_class, "TOOLS"):
                tools_data = strategy_class.TOOLS
                
                for tool_type, strategy in tools_data.items():
                    if hasattr(strategy, "to_dict"):
                        data = strategy.to_dict()
                    else:
                        data = asdict(strategy) if hasattr(strategy, "__dataclass_fields__") else dict(strategy)
                    
                    valid, warnings = self.validate_strategy(data)
                    
                    result = ImportResult(
                        success=valid,
                        source=f"{source}:{tool_type}",
                        data=data,
                        warnings=warnings
                    )
                    
                    self.import_history.append(result)
                    
                    data["_source"] = source
                    data["_imported_at"] = datetime.now().isoformat()
                    self.imported_strategies[tool_type] = data
                
                return ImportResult(
                    success=True,
                    source=source,
                    data={"imported_count": len(tools_data)},
                    warnings=[f"Imported {len(tools_data)} strategies from {source}"]
                )
            else:
                return ImportResult(
                    success=False,
                    source=source,
                    error=f"Strategy class has no TOOLS attribute"
                )
                
        except Exception as e:
            result = ImportResult(
                success=False,
                source=source,
                error=f"Module import error: {str(e)}"
            )
            self.import_history.append(result)
            return result

# ==================== 统一导入器 ====================

class UnifiedStrategyImporter:
    """统一策略导入器"""
    
    def __init__(self):
        self.json_importer = JSONStrategyImporter()
        self.yaml_importer = YAMLStrategyImporter()
        self.api_importer = APIStrategyImporter()
        self.module_importer = ModuleStrategyImporter()
    
    def import_from_file(self, file_path: str, **kwargs) -> ImportResult:
        """从文件导入，自动识别格式"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".json":
            return self.json_importer.import_strategy(file_path, **kwargs)
        elif ext in [".yaml", ".yml"]:
            return self.yaml_importer.import_strategy(file_path, **kwargs)
        elif ext == ".py":
            return self.module_importer.import_strategy(file_path, **kwargs)
        else:
            return ImportResult(
                success=False,
                source=file_path,
                error=f"Unknown file format: {ext}"
            )
    
    def import_from_string(self, content: str, format: str = "auto", **kwargs) -> ImportResult:
        """从字符串导入"""
        if format == "json":
            return self.json_importer.import_strategy(content, **kwargs)
        elif format == "yaml":
            return self.yaml_importer.import_strategy(content, **kwargs)
        else:
            # 尝试自动识别
            content = content.strip()
            if content.startswith("{"):
                return self.json_importer.import_strategy(content, **kwargs)
            elif content.startswith("---") or content.startswith("tools:"):
                return self.yaml_importer.import_strategy(content, **kwargs)
            else:
                return ImportResult(
                    success=False,
                    source="string",
                    error="Cannot auto-detect format. Please specify 'json' or 'yaml'"
                )
    
    def import_from_api(self, endpoint: str, **kwargs) -> ImportResult:
        """从API导入"""
        return self.api_importer.import_strategy(endpoint, **kwargs)
    
    def get_all_strategies(self) -> Dict[str, Dict]:
        """获取所有已导入的策略"""
        all_strategies = {}
        all_strategies.update(self.json_importer.imported_strategies)
        all_strategies.update(self.yaml_importer.imported_strategies)
        all_strategies.update(self.api_importer.imported_strategies)
        all_strategies.update(self.module_importer.imported_strategies)
        return all_strategies
    
    def get_import_history(self) -> List[ImportResult]:
        """获取所有导入历史"""
        history = []
        history.extend(self.json_importer.get_history())
        history.extend(self.yaml_importer.get_history())
        history.extend(self.api_importer.get_history())
        history.extend(self.module_importer.get_history())
        return sorted(history, key=lambda x: x.timestamp)

# ==================== 配置目录自动导入 ====================

class ConfigDirectoryLoader:
    """配置目录自动加载器"""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.importer = UnifiedStrategyImporter()
    
    def auto_load(self) -> Dict[str, Dict]:
        """
        自动加载配置目录下的所有策略文件
        
        Returns:
            所有已导入的策略字典
        """
        if not os.path.exists(self.config_dir):
            return {}
        
        for filename in os.listdir(self.config_dir):
            file_path = os.path.join(self.config_dir, filename)
            
            if os.path.isfile(file_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in [".json", ".yaml", ".yml", ".py"]:
                    try:
                        self.importer.import_from_file(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to import {file_path}: {e}")
        
        return self.importer.get_all_strategies()
    
    def watch_for_changes(self, callback: Callable[[str, Dict], None]):
        """
        监听配置目录变化
        
        Args:
            callback: 变化时的回调函数 (filename, strategy_data)
        """
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class ConfigChangeHandler(FileSystemEventHandler):
            def __init__(self, loader, callback):
                self.loader = loader
                self.callback = callback
            
            def on_modified(self, event):
                if not event.is_directory:
                    ext = os.path.splitext(event.src_path)[1].lower()
                    if ext in [".json", ".yaml", ".yml"]:
                        result = self.loader.importer.import_from_file(event.src_path)
                        if result.success and result.data:
                            self.callback(event.src_path, result.data)
        
        observer = Observer()
        handler = ConfigChangeHandler(self, callback)
        observer.schedule(handler, self.config_dir, recursive=False)
        observer.start()
        
        return observer

# ==================== 主入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("策略导入器测试")
    print("=" * 60)
    
    importer = UnifiedStrategyImporter()
    
    # 测试JSON导入
    json_config = '{
        "tool_type": "TEST",
        "name": "Test Strategy",
        "position_limit": 10.0,
        "stop_loss": 5.0,
        "take_profit": 15.0
    }'
    
    result = importer.import_from_string(json_config, format="json")
    print(f"\nJSON导入结果: {result.success}")
    if result.success:
        print(f"  数据: {result.data}")
    
    # 测试YAML导入
    yaml_config = """
    tool_type: "TEST2"
    name: "Test Strategy 2"
    position_limit: 20.0
    stop_loss: 3.0
    take_profit: 10.0
    """
    
    result = importer.import_from_string(yaml_config, format="yaml")
    print(f"\nYAML导入结果: {result.success}")
    if result.success:
        print(f"  数据: {result.data}")
    
    print("\n✅ 导入器测试完成")
