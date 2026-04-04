/**
 * GO2SE Vue3 Router Configuration
 * ===============================
 * 基于v2.5页面架构
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

  // ========== 一级: 主导航页 (基于v2.5架构) ==========
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/pages/Home.vue'),
    meta: { title: '首页纵览', icon: '🏠' },
  },
  {
    path: '/hot',
    name: 'Hot',
    component: () => import('@/pages/Hot.vue'),
    meta: { title: '热点纵览', icon: '🔥' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { title: '参数仪表盘', icon: '📊' },
  },
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('@/pages/Assets.vue'),
    meta: { title: '资产看板', icon: '💰' },
  },
  {
    path: '/portfolio',
    name: 'Portfolio',
    component: () => import('@/pages/Portfolio.vue'),
    meta: { title: '投资组合', icon: '📈' },
  },
  {
    path: '/sonar',
    name: 'Sonar',
    component: () => import('@/pages/Sonar.vue'),
    meta: { title: '声纳趋势', icon: '📡' },
  },
  {
    path: '/oracle',
    name: 'Oracle',
    component: () => import('@/pages/Oracle.vue'),
    meta: { title: '预言机', icon: '🔮' },
  },
  {
    path: '/ecosystem',
    name: 'Ecosystem',
    component: () => import('@/pages/Ecosystem.vue'),
    meta: { title: '生态工具', icon: '🛠️' },
  },
  {
    path: '/scripts',
    name: 'Scripts',
    component: () => import('@/pages/Scripts.vue'),
    meta: { title: '脚本日志', icon: '📝' },
  },
  {
    path: '/referral',
    name: 'Referral',
    component: () => import('@/pages/Referral.vue'),
    meta: { title: '分享有礼', icon: '🎁' },
  },
  {
    path: '/private',
    name: 'Private',
    component: () => import('@/pages/Private.vue'),
    meta: { title: '私募LP', icon: '💎' },
  },
  {
    path: '/support',
    name: 'Support',
    component: () => import('@/pages/Support.vue'),
    meta: { title: '客服中心', icon: '💬' },
  },

  // ========== 北斗七鑫 (子路由) ==========
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/pages/Market.vue'),
    meta: { title: '北斗七鑫', icon: '🔯' },
    redirect: '/market/top20',
    children: [
      { path: 'top20', name: 'MarketTop20', component: () => import('@/pages/MarketTop20.vue') },
      { path: 'movers', name: 'MarketMovers', component: () => import('@/pages/MarketMovers.vue') },
      { path: 'exchanges', name: 'MarketExchanges', component: () => import('@/pages/MarketExchanges.vue') },
    ],
  },
  {
    path: '/market/kline/:symbol',
    name: 'KlineDetail',
    component: () => import('@/pages/KlineDetail.vue'),
  },

  // ========== 策略 (子路由) ==========
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/pages/Strategies.vue'),
    meta: { title: '策略模型', icon: '♟️' },
    redirect: '/strategies/rabbit',
    children: [
      { path: 'rabbit', name: 'StrategyRabbit', component: () => import('@/pages/StrategyRabbit.vue') },
      { path: 'mole', name: 'StrategyMole', component: () => import('@/pages/StrategyMole.vue') },
      { path: 'oracle', name: 'StrategyOracle', component: () => import('@/pages/StrategyOracle.vue') },
      { path: 'leader', name: 'StrategyLeader', component: () => import('@/pages/StrategyLeader.vue') },
      { path: 'hitchhiker', name: 'StrategyHitchhiker', component: () => import('@/pages/StrategyHitchhiker.vue') },
      { path: 'airdrop', name: 'StrategyAirdrop', component: () => import('@/pages/StrategyAirdrop.vue') },
      { path: 'crowdsource', name: 'StrategyCrowdsource', component: () => import('@/pages/StrategyCrowdsource.vue') },
    ],
  },

  // ========== 信号 (子路由) ==========
  {
    path: '/signals',
    name: 'Signals',
    component: () => import('@/pages/Signals.vue'),
    meta: { title: '信号', icon: '📡' },
    redirect: '/signals/list',
    children: [
      { path: 'list', name: 'SignalsList', component: () => import('@/pages/SignalsList.vue') },
      { path: 'mirofish', name: 'SignalsMirofish', component: () => import('@/pages/SignalsMirofish.vue') },
      { path: 'sonar', name: 'SignalsSonar', component: () => import('@/pages/SignalsSonar.vue') },
    ],
  },

  // ========== 交易 (子路由) ==========
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('@/pages/Trading.vue'),
    meta: { title: '交易', icon: '💹' },
    redirect: '/trading/positions',
    children: [
      { path: 'positions', name: 'TradingPositions', component: () => import('@/pages/TradingPositions.vue') },
      { path: 'history', name: 'TradingHistory', component: () => import('@/pages/TradingHistory.vue') },
      { path: 'paper', name: 'TradingPaper', component: () => import('@/pages/TradingPaper.vue') },
      { path: 'live', name: 'TradingLive', component: () => import('@/pages/TradingLive.vue') },
    ],
  },

  // ========== 钱包 (子路由) ==========
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/pages/Wallet.vue'),
    meta: { title: '钱包', icon: '💰' },
    redirect: '/wallet/assets',
    children: [
      { path: 'assets', name: 'WalletAssets', component: () => import('@/pages/WalletAssets.vue') },
      { path: 'deposit', name: 'WalletDeposit', component: () => import('@/pages/WalletDeposit.vue') },
      { path: 'withdraw', name: 'WalletWithdraw', component: () => import('@/pages/WalletWithdraw.vue') },
      { path: 'history', name: 'WalletHistory', component: () => import('@/pages/WalletHistory.vue') },
    ],
  },

  // ========== 设置 (子路由) ==========
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { title: '设置中心', icon: '⚙️' },
    redirect: '/settings/trading',
    children: [
      { path: 'trading', name: 'SettingsTrading', component: () => import('@/pages/SettingsTrading.vue') },
      { path: 'risk', name: 'SettingsRisk', component: () => import('@/pages/SettingsRisk.vue') },
      { path: 'api', name: 'SettingsAPI', component: () => import('@/pages/SettingsAPI.vue') },
      { path: 'notifications', name: 'SettingsNotifications', component: () => import('@/pages/SettingsNotifications.vue') },
      { path: 'team', name: 'SettingsTeam', component: () => import('@/pages/SettingsTeam.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
