interface SettingsProps {
  appVersion: string;
}

export function Settings({ appVersion }: SettingsProps) {
  return (
    <div className="settings-section">
      <h2>⚙️ 系统设置</h2>
      <div className="settings-grid">
        <div className="card setting-card">
          <h4>🛡️ 风控规则</h4>
          <div className="setting-row"><span>总仓位上限</span><span>80%</span></div>
          <div className="setting-row"><span>单笔风险</span><span>5%</span></div>
          <div className="setting-row"><span>日亏损熔断</span><span>15%</span></div>
        </div>
        <div className="card setting-card">
          <h4>🔧 平台配置</h4>
          <div className="setting-row"><span>交易模式</span><span>Dry Run</span></div>
          <div className="setting-row"><span>API延迟</span><span>7ms</span></div>
          <div className="setting-row"><span>版本</span><span>{appVersion}</span></div>
        </div>
      </div>
    </div>
  );
}
