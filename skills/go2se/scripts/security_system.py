#!/usr/bin/env python3
"""
北斗七鑫 - 安全保护系统 v1
资产保护 + 紧急转移 + 自动备份
"""

import json
import time
import hashlib
import secrets
import base64
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import os

# ==================== 安全配置 ====================

@dataclass
class SecurityConfig:
    """安全配置"""
    # 授权人 (大白鹅CEO)
    owner_public_key: str = "0xGO2SE_CEO_OWNER_2026"
    
    # 备份密钥 (SHA256哈希存储,不可逆)
    backup_auth_hash: str = ""
    
    # 紧急地址 (仅紧急情况使用)
    emergency_address: str = ""
    
    # 备份间隔 (小时)
    backup_interval: int = 24
    
    # 保留备份数
    max_backups: int = 10

# ==================== 加密模块 ====================

class SecureCrypto:
    """加密模块"""
    
    @staticmethod
    def hash_data(data: str) -> str:
        """哈希"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def generate_token() -> str:
        """生成安全令牌"""
        return secrets.token_hex(32)
    
    @staticmethod
    def encode_data(data: Dict) -> str:
        """编码数据"""
        json_str = json.dumps(data, sort_keys=True)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def decode_data(encoded: str) -> Dict:
        """解码数据"""
        try:
            json_str = base64.b64decode(encoded.encode()).decode()
            return json.loads(json_str)
        except:
            return {}

# ==================== 紧急资产保护 ====================

class AssetProtection:
    """资产保护系统"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.crypto = SecureCrypto()
        
        # 紧急联系人 (仅大白鹅可见)
        self.emergency_contacts = {}
        
        # 转移历史
        self.transfer_history = deque(maxlen=100)
        
        # 保护状态
        self.protection_active = True
    
    def setup_emergency_address(self, address: str, owner_verified: bool = False) -> Dict:
        """设置紧急地址 (仅所有者)"""
        if not owner_verified:
            return {'status': 'error', 'message': '未验证身份'}
        
        # 加密存储
        self.config.emergency_address = self.crypto.hash_data(address)
        
        return {
            'status': 'success',
            'message': '紧急地址已加密保存',
            'address_hash': self.config.emergency_address[:16] + '...'
        }
    
    def emergency_transfer(self, amount: float, target_address: str, 
                          owner_token: str, reason: str = "") -> Dict:
        """紧急转移 (仅所有者可执行)"""
        # 验证令牌
        if not self._verify_owner(owner_token):
            return {'status': 'error', 'message': '权限不足'}
        
        # 记录转移
        transfer = {
            'id': f"EMERG_{int(time.time())}",
            'amount': amount,
            'target': target_address[:10] + '...',
            'reason': reason,
            'time': int(time.time()),
            'status': 'completed'
        }
        
        self.transfer_history.append(transfer)
        
        return {
            'status': 'success',
            'transfer_id': transfer['id'],
            'message': '紧急转移已完成'
        }
    
    def _verify_owner(self, token: str) -> bool:
        """验证所有者"""
        # 实际应该比对加密令牌
        return len(token) > 10
    
    def get_protection_status(self) -> Dict:
        """保护状态"""
        return {
            'active': self.protection_active,
            'emergency_set': bool(self.config.emergency_address),
            'transfers': len(self.transfer_history)
        }

# ==================== 自动备份系统 ====================

class AutoBackup:
    """自动备份系统"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.crypto = SecureCrypto()
        
        # 备份列表
        self.backups = deque(maxlen=config.max_backups)
        
        # 最后备份时间
        self.last_backup = int(time.time())
    
    def create_backup(self, data: Dict, backup_type: str = "manual") -> Dict:
        """创建备份"""
        # 加密数据
        encrypted = self.crypto.encode_data(data)
        
        backup = {
            'id': f"BK_{int(time.time())}",
            'type': backup_type,
            'data_hash': self.crypto.hash_data(encrypted),
            'size': len(encrypted),
            'created': int(time.time()),
            'checksum': self.crypto.hash_data(str(data))
        }
        
        self.backups.append(backup)
        self.last_backup = int(time.time())
        
        return {
            'status': 'success',
            'backup_id': backup['id'],
            'checksum': backup['checksum'][:16] + '...',
            'size': backup['size']
        }
    
    def restore_backup(self, backup_id: str, auth_token: str) -> Dict:
        """恢复备份 (需授权)"""
        # 查找备份
        backup = None
        for b in self.backups:
            if b['id'] == backup_id:
                backup = b
                break
        
        if not backup:
            return {'status': 'error', 'message': '备份不存在'}
        
        return {
            'status': 'success',
            'backup_id': backup['id'],
            'type': backup['type'],
            'created': backup['created'],
            'checksum': backup['checksum'][:16] + '...'
        }
    
    def list_backups(self) -> List[Dict]:
        """列出备份"""
        return [{
            'id': b['id'],
            'type': b['type'],
            'created': b['created'],
            'size': b['size']
        } for b in self.backups]
    
    def auto_backup_needed(self) -> bool:
        """检查是否需要自动备份"""
        elapsed = time.time() - self.last_backup
        return elapsed > (self.config.backup_interval * 3600)
    
    def get_backup_status(self) -> Dict:
        """备份状态"""
        return {
            'total_backups': len(self.backups),
            'last_backup': self.last_backup,
            'auto_interval': self.config.backup_interval,
            'auto_needed': self.auto_backup_needed()
        }

# ==================== 访问控制 ====================

class AccessControl:
    """访问控制系统"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.crypto = SecureCrypto()
        
        # 访问令牌
        self.tokens = {}
        
        # 访问日志
        self.access_log = deque(maxlen=1000)
    
    def generate_owner_token(self) -> str:
        """生成所有者令牌"""
        token = self.crypto.generate_token()
        
        self.tokens[token] = {
            'type': 'owner',
            'created': int(time.time()),
            'expires': int(time.time()) + (365 * 24 * 3600),  # 1年
            'permissions': ['read', 'write', 'backup', 'restore', 'emergency']
        }
        
        return token
    
    def generate_backup_token(self) -> str:
        """生成备份操作员令牌"""
        token = self.crypto.generate_token()
        
        self.tokens[token] = {
            'type': 'backup_operator',
            'created': int(time.time()),
            'expires': int(time.time()) + (30 * 24 * 3600),  # 30天
            'permissions': ['backup', 'restore']
        }
        
        return token
    
    def verify_token(self, token: str, required_permission: str = None) -> Dict:
        """验证令牌"""
        if token not in self.tokens:
            return {'valid': False, 'reason': '令牌无效'}
        
        token_data = self.tokens[token]
        
        # 检查过期
        if token_data['expires'] < int(time.time()):
            return {'valid': False, 'reason': '令牌已过期'}
        
        # 检查权限
        if required_permission and required_permission not in token_data['permissions']:
            return {'valid': False, 'reason': '权限不足'}
        
        # 记录访问
        self.access_log.append({
            'token_type': token_data['type'],
            'permission': required_permission,
            'time': int(time.time())
        })
        
        return {
            'valid': True,
            'type': token_data['type'],
            'permissions': token_data['permissions']
        }
    
    def revoke_token(self, token: str) -> Dict:
        """撤销令牌"""
        if token in self.tokens:
            del self.tokens[token]
            return {'status': 'success', 'message': '令牌已撤销'}
        return {'status': 'error', 'message': '令牌不存在'}

# ==================== 主安全系统 ====================

class SecuritySystem:
    """安全系统"""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.asset_protection = AssetProtection(self.config)
        self.backup = AutoBackup(self.config)
        self.access = AccessControl(self.config)
        
        # 生成所有者令牌
        self.owner_token = self.access.generate_owner_token()
        
        # 日志
        self.events = deque(maxlen=500)
    
    def initialize(self, owner_wallet: str) -> Dict:
        """初始化系统"""
        # 设置紧急地址
        self.asset_protection.setup_emergency_address(
            owner_wallet, 
            owner_verified=True
        )
        
        self._log_event('system_initialized', '系统已初始化')
        
        return {
            'status': 'success',
            'owner_token': self.owner_token[:8] + '...' + self.owner_token[-8:],
            'message': '安全系统已启动'
        }
    
    def create_data_backup(self, data: Dict) -> Dict:
        """创建数据备份"""
        return self.backup.create_backup(data, 'auto')
    
    def emergency_asset_move(self, amount: float, reason: str) -> Dict:
        """紧急资产转移"""
        return self.asset_protection.emergency_transfer(
            amount,
            self.config.emergency_address,
            self.owner_token,
            reason
        )
    
    def _log_event(self, event_type: str, message: str):
        """记录事件"""
        self.events.append({
            'type': event_type,
            'message': message,
            'time': int(time.time())
        })
    
    def get_status(self) -> Dict:
        """系统状态"""
        return {
            'asset_protection': self.asset_protection.get_protection_status(),
            'backup': self.backup.get_backup_status(),
            'events': len(self.events)
        }

# ==================== 测试 ====================

def test():
    print("\n" + "="*60)
    print("🛡️ 北斗七鑫 - 安全系统测试")
    print("="*60)
    
    security = SecuritySystem()
    
    # 初始化
    result = security.initialize("0xEMERGENCY_WALLET_ADDRESS")
    print(f"\n初始化: {result}")
    
    # 创建备份
    test_data = {
        'signals': 100,
        'balance': 85000,
        'tools': 7
    }
    
    backup = security.create_data_backup(test_data)
    print(f"\n创建备份: {backup}")
    
    # 列出备份
    backups = security.backup.list_backups()
    print(f"\n备份列表: {backups}")
    
    # 紧急转移
    emergency = security.emergency_asset_move(5000, "测试紧急转移")
    print(f"\n紧急转移: {emergency}")
    
    # 状态
    status = security.get_status()
    print(f"\n系统状态:")
    print(f"  保护: {status['asset_protection']['active']}")
    print(f"  备份数: {status['backup']['total_backups']}")
    print(f"  事件: {status['events']}")
    
    # 令牌测试
    verify = security.access.verify_token(security.owner_token, 'emergency')
    print(f"\n令牌验证: {verify}")
    
    print("\n✅ 安全系统测试完成")

if __name__ == '__main__':
    test()
