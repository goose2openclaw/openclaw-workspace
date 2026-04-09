#!/usr/bin/env python3
"""
北斗七鑫 - 会员体系核心系统
"""

import json
import time
from dataclasses import dataclass
from typing import Dict, List

# ==================== 会员等级 ====================

@dataclass
class MembershipLevel:
    name: str
    level: int
    monthly_fee: float
    yearly_fee: float
    simulated_funds: float
    max_simulated_transfer: float
    tools_access: List[str]
    priority_level: int
    has_expert: bool
    has_lp: bool

MEMBERSHIP_LEVELS = {
    'guest': MembershipLevel(
        name='游客', level=0,
        monthly_fee=0, yearly_fee=0,
        simulated_funds=1000,
        max_simulated_transfer=0,
        tools_access=['airdrop_basic'],
        priority_level=1,
        has_expert=False, has_lp=False, can_withdraw_airdrop=True
    ),
    'subscriber': MembershipLevel(
        name='订阅', level=1,
        monthly_fee=49, yearly_fee=49*12*0.9,
        simulated_funds=3000,
        max_simulated_transfer=3000,
        tools_access=['rabbit', 'mole', 'prediction', 'follow', 'hitchhike', 'airdrop', 'crowdsource'],
        priority_level=2,
        has_expert=False, has_lp=False, can_withdraw_airdrop=True
    ),
    'member': MembershipLevel(
        name='会员', level=2,
        monthly_fee=99, yearly_fee=89*12,
        simulated_funds=5000,
        max_simulated_transfer=5000,
        tools_access=['rabbit', 'mole', 'prediction', 'follow', 'hitchhike', 'airdrop', 'crowdsource'],
        priority_level=3,
        has_expert=False, has_lp=False, can_withdraw_airdrop=True
    ),
    'lp': MembershipLevel(
        name='私募LP', level=3,
        monthly_fee=0, yearly_fee=0,
        simulated_funds=10000,
        max_simulated_transfer=10000,
        tools_access=['rabbit', 'mole', 'prediction', 'follow', 'hitchhike', 'airdrop', 'crowdsource'],
        priority_level=4,
        has_expert=True, has_lp=True
    ),
    'expert': MembershipLevel(
        name='专家', level=4,
        monthly_fee=199, yearly_fee=169*12,
        simulated_funds=15000,
        max_simulated_transfer=15000,
        tools_access=['rabbit', 'mole', 'prediction', 'follow', 'hitchhike', 'airdrop', 'crowdsource', 'expert_mode'],
        priority_level=5,
        has_expert=True, has_lp=True
    ),
}

# ==================== 用户系统 ====================

class User:
    def __init__(self, user_id: str, level: str = 'guest'):
        self.user_id = user_id
        self.level = level
        self.created_at = int(time.time())
        self.expires_at = None
        
        # 资产
        self.simulated_balance = MEMBERSHIP_LEVELS[level].simulated_funds
        self.simulated_profits = 0
        self.earnings_withdrawable = 0  # 可提现收益
        
        # 统计
        self.stats = {
            'total_trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0
        }
    
    def upgrade(self, new_level: str) -> bool:
        """升级"""
        old = MEMBERSHIP_LEVELS[self.level]
        new = MEMBERSHIP_LEVELS[new_level]
        
        if new.level <= old.level:
            return False
        
        self.level = new_level
        self.simulated_balance = new.simulated_funds
        
        return True
    
    def can_use_tool(self, tool: str) -> bool:
        """检查工具权限"""
        level = MEMBERSHIP_LEVELS[self.level]
        return tool in level.tools_access
    
    def get_priority(self) -> int:
        """获取优先级"""
        return MEMBERSHIP_LEVELS[self.level].priority_level
    
    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'level': self.level,
            'level_name': MEMBERSHIP_LEVELS[self.level].name,
            'simulated_balance': self.simulated_balance,
            'simulated_profits': self.simulated_profits,
            'earnings_withdrawable': self.earnings_withdrawable,
            'priority': self.get_priority(),
            'stats': self.stats
        }

# ==================== 会员系统 ====================

class MembershipSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.guest_counter = 0
    
    def create_guest(self) -> User:
        """创建游客"""
        self.guest_counter += 1
        user_id = f"guest_{self.guest_counter:06d}"
        user = User(user_id, 'guest')
        self.users[user_id] = user
        return user
    
    def get_user(self, user_id: str) -> User:
        """获取用户"""
        return self.users.get(user_id)
    
    def upgrade_user(self, user_id: str, new_level: str) -> bool:
        """升级用户"""
        user = self.get_user(user_id)
        if not user:
            return False
        return user.upgrade(new_level)
    
    def add_simulated_profit(self, user_id: str, profit: float):
        """添加模拟收益"""
        user = self.get_user(user_id)
        if user:
            user.simulated_profits += profit
            user.stats['total_trades'] += 1
            if profit > 0:
                user.stats['wins'] += 1
            else:
                user.stats['losses'] += 1
            user.stats['total_pnl'] += profit
    
    def transfer_to_real(self, user_id: str, amount: float) -> Dict:
        """转存模拟收益"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'reason': 'user_not_found'}
        
        level = MEMBERSHIP_LEVELS[user.level]
        
        # 检查是否可转存
        if level.level < 1:
            return {'success': False, 'reason': 'need_subscribe'}
        
        # 检查金额
        if amount > level.max_simulated_transfer:
            amount = level.max_simulated_transfer
        
        if amount > user.simulated_profits:
            amount = user.simulated_profits
        
        if amount <= 0:
            return {'success': False, 'reason': 'no_profits'}
        
        # 执行转存
        user.simulated_balance -= amount
        user.simulated_profits -= amount
        user.earnings_withdrawable += amount
        
        return {
            'success': True,
            'amount': amount,
            'new_balance': user.simulated_balance,
            'withdrawable': user.earnings_withdrawable
        }
    
    def withdraw_earnings(self, user_id: str) -> Dict:
        """提现收益"""
        user = self.get_user(user_id)
        if not user:
            return {'success': False, 'reason': 'user_not_found'}
        
        level = MEMBERSHIP_LEVELS[user.level]
        
        if level.level < 1:
            return {'success': False, 'reason': 'need_subscribe'}
        
        amount = user.earnings_withdrawable
        
        if amount <= 0:
            return {'success': False, 'reason': 'no_earnings'}
        
        # 模拟提现
        user.earnings_withdrawable = 0
        
        return {
            'success': True,
            'amount': amount,
            'message': f'提现 ${amount:.2f} 成功'
        }
    
    def get_membership_benefits(self, level_name: str) -> Dict:
        """获取会员权益"""
        level = MEMBERSHIP_LEVELS.get(level_name)
        if not level:
            return {}
        
        return {
            'name': level.name,
            'monthly_fee': level.monthly_fee,
            'yearly_fee': level.yearly_fee,
            'simulated_funds': level.simulated_funds,
            'max_transfer': level.max_simulated_transfer,
            'tools': level.tools_access,
            'priority': level.priority_level,
            'expert': level.has_expert,
            'lp': level.has_lp
        }

# ==================== 测试 ====================

def test():
    """测试"""
    print("🧪 会员系统测试")
    print("="*50)
    
    system = MembershipSystem()
    
    # 创建游客
    guest = system.create_guest()
    print(f"\n📝 创建游客: {guest.user_id}")
    print(f"   等级: {guest.level}")
    print(f"   模拟金: ${guest.simulated_balance}")
    
    # 升级为订阅
    system.upgrade_user(guest.user_id, 'subscriber')
    print(f"\n📈 升级为订阅")
    print(f"   等级: {guest.level}")
    print(f"   模拟金: ${guest.simulated_balance}")
    
    # 添加收益
    system.add_simulated_profit(guest.user_id, 150)
    print(f"\n💰 添加收益: $150")
    print(f"   总收益: ${guest.simulated_profits}")
    print(f"   可转存: ${MEMBERSHIP_LEVELS[guest.level].max_simulated_transfer}")
    
    # 转存
    result = system.transfer_to_real(guest.user_id, 100)
    print(f"\n🔄 转存: ${result.get('amount', 0)}")
    print(f"   状态: {'成功' if result.get('success') else '失败'}")
    
    # 查看权益
    print(f"\n📋 订阅权益:")
    benefits = system.get_membership_benefits('subscriber')
    print(f"   月费: ${benefits.get('monthly_fee')}")
    print(f"   工具: {', '.join(benefits.get('tools', []))}")
    
    print("\n✅ 测试完成")
    
    return system

if __name__ == '__main__':
    test()
