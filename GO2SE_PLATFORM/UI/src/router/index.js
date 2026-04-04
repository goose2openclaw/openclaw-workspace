/**
 * GO2SE Vue3 Router Configuration
 * ===============================
 * 三级页面路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ========== 零级: 入口页 ==========
  {
    path: '/',
    name: 'Landing',
    component: () => import('@/pages/Landing.vue'),
    meta: { title: '启动页' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { title: '注册' },
  },

  // ========== 一级: 主导航页 ==========
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { title: '总览', icon: '📊' },
  },
  {
    path: '/market',
    name: 'Market',
    redirect: '/market/top20',
    component: () => import('@/pages/Market.vue'),
    meta: { title: '市场', icon: '📈' },
    children: [
      { path: '', redirect: '/market/top20' },
      { path: 'top20', name: 'MarketTop20', component: () => import('@/pages/MarketTop20.vue'), meta: { title: '前20主流币', parent: 'Market' } },
      { path: 'movers', name: 'MarketMovers', component: () => import('@/pages/MarketMovers.vue'), meta: { title: '异动币', parent: 'Market' } },
      { path: 'exchanges', name: 'MarketExchanges', component: () => import('@/pages/MarketExchanges.vue'), meta: { title: '交易所', parent: 'Market' } },
    ],
  },
  {
    path: '/market/kline/:symbol',
    name: 'KlineDetail',
    component: () => import('@/pages/KlineDetail.vue'),
    meta: { title: 'K线详情', parent: 'Market' },
  },
  {
    path: '/strategies',
    name: 'Strategies',
    redirect: '/strategies/rabbit',
    component: () => import('@/pages/Strategies.vue'),
    meta: { title: '策略', icon: '⚙️' },
    children: [
      { path: '', redirect: '/strategies/rabbit' },
      { path: 'rabbit', name: 'StrategyRabbit', component: () => import('@/pages/StrategyRabbit.vue'), meta: { title: '🐰 打兔子', parent: 'Strategies' } },
      { path: 'mole', name: 'StrategyMole', component: () => import('@/pages/StrategyMole.vue'), meta: { title: '🐹 打地鼠', parent: 'Strategies' } },
      { path: 'oracle', name: 'StrategyOracle', component: () => import('@/pages/StrategyOracle.vue'), meta: { title: '🔮 走着瞧', parent: 'Strategies' } },
      { path: 'leader', name: 'StrategyLeader', component: () => import('@/pages/StrategyLeader.vue'), meta: { title: '👑 跟大哥', parent: 'Strategies' } },
      { path: 'hitchhiker', name: 'StrategyHitchhiker', component: () => import('@/pages/StrategyHitchhiker.vue'), meta: { title: '🍀 搭便车', parent: 'Strategies' } },
      { path: 'airdrop', name: 'StrategyAirdrop', component: () => import('@/pages/StrategyAirdrop.vue'), meta: { title: '💰 薅羊毛', parent: 'Strategies' } },
      { path: 'crowdsource', name: 'StrategyCrowdsource', component: () => import('@/pages/StrategyCrowdsource.vue'), meta: { title: '👶 穷孩子', parent: 'Strategies' } },
    ],
  },
  {
    path: '/signals',
    name: 'Signals',
    redirect: '/signals/list',
    component: () => import('@/pages/Signals.vue'),
    meta: { title: '信号', icon: '📡' },
    children: [
      { path: '', redirect: '/signals/list' },
      { path: 'list', name: 'SignalsList', component: () => import('@/pages/SignalsList.vue'), meta: { title: '信号列表', parent: 'Signals' } },
      { path: 'mirofish', name: 'SignalsMirofish', component: () => import('@/pages/SignalsMirofish.vue'), meta: { title: 'MiroFish决策', parent: 'Signals' } },
      { path: 'sonar', name: 'SignalsSonar', component: () => import('@/pages/SignalsSonar.vue'), meta: { title: '声纳库', parent: 'Signals' } },
    ],
  },
  {
    path: '/signals/:id',
    name: 'SignalDetail',
    component: () => import('@/pages/SignalDetail.vue'),
    meta: { title: '信号详情', parent: 'Signals' },
  },
  {
    path: '/trading',
    name: 'Trading',
    redirect: '/trading/positions',
    component: () => import('@/pages/Trading.vue'),
    meta: { title: '交易', icon: '💹' },
    children: [
      { path: '', redirect: '/trading/positions' },
      { path: 'positions', name: 'TradingPositions', component: () => import('@/pages/TradingPositions.vue'), meta: { title: '持仓', parent: 'Trading' } },
      { path: 'history', name: 'TradingHistory', component: () => import('@/pages/TradingHistory.vue'), meta: { title: '历史', parent: 'Trading' } },
      { path: 'paper', name: 'TradingPaper', component: () => import('@/pages/TradingPaper.vue'), meta: { title: '模拟交易', parent: 'Trading' } },
      { path: 'live', name: 'TradingLive', component: () => import('@/pages/TradingLive.vue'), meta: { title: '实盘交易', parent: 'Trading' } },
    ],
  },
  {
    path: '/wallet',
    name: 'Wallet',
    redirect: '/wallet/assets',
    component: () => import('@/pages/Wallet.vue'),
    meta: { title: '钱包', icon: '💰' },
    children: [
      { path: '', redirect: '/wallet/assets' },
      { path: 'assets', name: 'WalletAssets', component: () => import('@/pages/WalletAssets.vue'), meta: { title: '资产管理', parent: 'Wallet' } },
      { path: 'deposit', name: 'WalletDeposit', component: () => import('@/pages/WalletDeposit.vue'), meta: { title: '充值', parent: 'Wallet' } },
      { path: 'withdraw', name: 'WalletWithdraw', component: () => import('@/pages/WalletWithdraw.vue'), meta: { title: '提现', parent: 'Wallet' } },
      { path: 'history', name: 'WalletHistory', component: () => import('@/pages/WalletHistory.vue'), meta: { title: '记录', parent: 'Wallet' } },
    ],
  },
  {
    path: '/settings',
    name: 'Settings',
    redirect: '/settings/trading',
    component: () => import('@/pages/Settings.vue'),
    meta: { title: '设置', icon: '⚡' },
    children: [
      { path: '', redirect: '/settings/trading' },
      { path: 'trading', name: 'SettingsTrading', component: () => import('@/pages/SettingsTrading.vue'), meta: { title: '交易配置', parent: 'Settings' } },
      { path: 'risk', name: 'SettingsRisk', component: () => import('@/pages/SettingsRisk.vue'), meta: { title: '风控规则', parent: 'Settings' } },
      { path: 'api', name: 'SettingsAPI', component: () => import('@/pages/SettingsAPI.vue'), meta: { title: 'API管理', parent: 'Settings' } },
      { path: 'notifications', name: 'SettingsNotifications', component: () => import('@/pages/SettingsNotifications.vue'), meta: { title: '通知', parent: 'Settings' } },
      { path: 'team', name: 'SettingsTeam', component: () => import('@/pages/SettingsTeam.vue'), meta: { title: '团队', parent: 'Settings' } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
