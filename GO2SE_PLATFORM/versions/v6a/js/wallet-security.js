// ========== 钱包安全架构 ==========
const WalletSecurity = {
    wallets: {
        main: { address: '0x****.main', balance: 45000, label: '💼 主钱包', type: 'main', exposure: 'high' },
        backup: { address: '0x****.backup', balance: 50000, label: '🔐 备用钱包', type: 'backup', exposure: 'none' },
        transit: { address: '0x****.transit', balance: 10000, label: '🔄 中转钱包', type: 'transit', exposure: 'medium' },
        tools: {
            rabbit: { address: '0x****.rabbit', balance: 2500, label: '🐰 打兔子', gas: 0.001 },
            mole: { address: '0x****.mole', balance: 2000, label: '🐹 打地鼠', gas: 0.001 },
            oracle: { address: '0x****.oracle', balance: 1500, label: '🔮 走着瞧', gas: 0.002 },
            leader: { address: '0x****.leader', balance: 1500, label: '👑 跟大哥', gas: 0.001 },
            hitchhiker: { address: '0x****.hitchhiker', balance: 1000, label: '🍀 搭便车', gas: 0.001 },
            airdrop: { address: '0x****.airdrop', balance: 3000, label: '💰 薅羊毛', gas: 0.003 },
            crowdsource: { address: '0x****.crowdsource', balance: 2000, label: '👶 穷孩子', gas: 0.002 }
        }
    },
    gasConfig: { internal: 0.0001, external: 0.002, airdrop: 0.003, claim: 0.005 },
    rules: {
        antiMarking: { maxTxPerDay: 5, minInterval: 300, mixWithTransit: true, randomizeGas: true },
        airdropProtection: { checkContract: true, isolateAirdrop: true, smallFirst: true, revokeAfter: 24 }
    },
    init() { this.loadConfig(); this.renderWalletArchitecture(); this.renderSecurityPanel(); console.log('🔐 WalletSecurity initialized'); },
    loadConfig() { try { const saved = localStorage.getItem('WalletSecurityConfig'); if (saved) this.config = JSON.parse(saved); } catch(e) {} },
    saveConfig() { try { localStorage.setItem('WalletSecurityConfig', JSON.stringify(this.config)); } catch(e) {} },
    renderWalletArchitecture() {
        const c = document.getElementById('walletArchitecturePanel');
        if (!c) return;
        c.innerHTML = `<div style="padding:15px;">
            <h4 style="margin:0 0 15px 0; color:#00d4aa;">🔐 钱包安全架构</h4>
            <div style="background:rgba(0,0,0,0.3); border-radius:10px; padding:12px; margin-bottom:15px;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><span style="color:#ef4444;">🔴</span><span style="color:#888; font-size:11px;">高暴露 - 主钱包, 不直接参与日常操作</span></div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><span style="color:#f59e0b;">🟡</span><span style="color:#888; font-size:11px;">中暴露 - 中转钱包, 汇集/分发资金</span></div>
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><span style="color:#00d4aa;">🟢</span><span style="color:#888; font-size:11px;">零暴露 - 备用钱包, 冷存储隔离</span></div>
                <div style="display:flex; align-items:center; gap:8px;"><span style="color:#3b82f6;">🔵</span><span style="color:#888; font-size:11px;">工具钱包 - 各工具独立, 无关联</span></div>
            </div>
            <div style="text-align:center; margin-bottom:15px;">
                <div style="display:inline-block; padding:8px 15px; background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.4); border-radius:8px; margin-bottom:10px;">
                    <div style="font-size:20px;">💼</div><div style="font-size:11px; color:#ef4444;">主钱包</div><div style="font-size:10px; color:#888;">$45,000</div>
                </div>
            </div>
            <div style="text-align:center; margin-bottom:5px; color:#888; font-size:10px;">↓ 授权转账(Gas优化)</div>
            <div style="text-align:center; margin-bottom:15px;">
                <div style="display:inline-flex; gap:15px;">
                    <div style="padding:8px 12px; background:rgba(245,158,11,0.2); border:1px solid rgba(245,158,11,0.4); border-radius:8px;"><div style="font-size:16px;">🔄</div><div style="font-size:10px; color:#f59e0b;">中转</div><div style="font-size:10px; color:#888;">$10,000</div></div>
                    <div style="padding:8px 12px; background:rgba(0,212,170,0.2); border:1px solid rgba(0,212,170,0.4); border-radius:8px;"><div style="font-size:16px;">🔐</div><div style="font-size:10px; color:#00d4aa;">备用</div><div style="font-size:10px; color:#888;">$50,000</div></div>
                </div>
            </div>
            <div style="text-align:center; margin-bottom:5px; color:#888; font-size:10px;">↓ 工具钱包(独立隔绝)</div>
            <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px;">
                ${Object.entries(this.wallets.tools).map(([id, w]) => `<div style="padding:6px; background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); border-radius:6px; text-align:center;"><div style="font-size:14px;">${w.label.split(' ')[0]}</div><div style="font-size:9px; color:#3b82f6;">Gas: ${w.gas}</div></div>`).join('')}
            </div>
            <div style="margin-top:15px; padding:10px; background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.2); border-radius:8px;">
                <div style="font-size:11px; color:#ef4444; margin-bottom:5px;">⚠️ 安全规则</div>
                <div style="font-size:10px; color:#888; line-height:1.5;">• 每日最多5笔/钱包<br>• 空投钱包完全隔离<br>• 小额测试后再操作<br>• 24小时后自动撤销授权</div>
            </div>
        </div>`;
    },
    renderSecurityPanel() {
        const c = document.getElementById('walletSecurityPanel');
        if (!c) return;
        c.innerHTML = `<div style="padding:15px;">
            <h4 style="margin:0 0 15px 0; color:#ef4444;">🛡️ 安全设置</h4>
            <div style="margin-bottom:15px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="font-size:12px; color:#888;">防标记转账</span><label style="position:relative; width:40px; height:20px;"><input type="checkbox" checked onchange="WalletSecurity.toggleRule('antiMarking')" style="display:none;"><span style="position:absolute; width:36px; height:18px; background:#00d4aa; border-radius:9px; cursor:pointer; left:2px; top:1px; transition:all 0.3s;"></span></label></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="font-size:12px; color:#888;">空投隔离</span><label style="position:relative; width:40px; height:20px;"><input type="checkbox" checked onchange="WalletSecurity.toggleRule('isolateAirdrop')" style="display:none;"><span style="position:absolute; width:36px; height:18px; background:#00d4aa; border-radius:9px; cursor:pointer; left:2px; top:1px; transition:all 0.3s;"></span></label></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;"><span style="font-size:12px; color:#888;">Gas优化</span><label style="position:relative; width:40px; height:20px;"><input type="checkbox" checked onchange="WalletSecurity.toggleRule('gasOptimization')" style="display:none;"><span style="position:absolute; width:36px; height:18px; background:#00d4aa; border-radius:9px; cursor:pointer; left:2px; top:1px; transition:all 0.3s;"></span></label></div>
                <div style="display:flex; justify-content:space-between;"><span style="font-size:12px; color:#888;">小额测试</span><label style="position:relative; width:40px; height:20px;"><input type="checkbox" checked onchange="WalletSecurity.toggleRule('smallFirst')" style="display:none;"><span style="position:absolute; width:36px; height:18px; background:#00d4aa; border-radius:9px; cursor:pointer; left:2px; top:1px; transition:all 0.3s;"></span></label></div>
            </div>
            <div style="background:rgba(0,0,0,0.3); border-radius:8px; padding:12px;">
                <div style="font-size:11px; color:#888; margin-bottom:8px;">Gas配置</div>
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="font-size:11px;">内部转账</span><span style="font-size:11px; color:#00d4aa;">${this.gasConfig.internal} ETH</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:5px;"><span style="font-size:11px;">外部转账</span><span style="font-size:11px; color:#f59e0b;">${this.gasConfig.external} ETH</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="font-size:11px;">合约交互</span><span style="font-size:11px; color:#ef4444;">${this.gasConfig.claim} ETH</span></div>
            </div>
        </div>`;
    },
    toggleRule(rule) { if (!this.config) this.config = {}; this.config[rule] = !this.config[rule]; this.saveConfig(); awShowToast('安全规则已更新'); },
    calculateOptimalPath(fromTool, toTool, amount) {
        const gas = fromTool === toTool ? this.gasConfig.internal : this.gasConfig.external;
        const netAmount = amount - gas;
        return { from: this.wallets.tools[fromTool].label, to: this.wallets.tools[toTool].label, grossAmount: amount, gas: gas, netAmount: netAmount > 0 ? netAmount : 0, totalCost: amount + gas, path: fromTool === toTool ? 'direct' : 'via-transit', recommendation: netAmount > 0 ? '可行' : '余额不足' };
    }
};
document.addEventListener('DOMContentLoaded', function() { WalletSecurity.init(); });
