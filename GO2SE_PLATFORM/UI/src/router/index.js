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
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
  },

  // ========== 一级: 主导航页 ==========
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { title: '总览' },
  },
  {
    path: '/market',
    name: 'Market',
    component: () => import('@/pages/Market.vue'),
    meta: { title: '市场', children: [
      { path: 'top20', title: '主流币' },
      { path: 'movers', title: '异动币' },
      { path: 'exchanges', title: '交易所' },
    ]},
  },
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/pages/Strategies.vue'),
    meta: { title: '策略', children: [
      { path: 'rabbit', title: '打兔子' },
      { path: 'mole', title: '打地鼠' },
      { path: 'oracle', title: '走着瞧' },
      { path: 'leader', title: '跟大哥' },
      { path: 'hitchhiker', title: '搭便车' },
      { path: 'airdrop', title: '薅羊毛' },
      { path: 'crowdsource', title: '穷孩子' },
    ]},
  },
  {
    path: '/signals',
    name: 'Signals',
    component: () => import('@/pages/Signals.vue'),
    meta: { title: '信号', children: [
      { path: 'list', title: '信号列表' },
      { path: 'mirofish', title: 'MiroFish' },
      { path: 'sonar', title: '声纳库' },
    ]},
  },
  {
    path: '/trading',
    name: 'Trading',
    component: () => import('@/pages/Trading.vue'),
    meta: { title: '交易', children: [
      { path: 'positions', title: '持仓' },
      { path: 'history', title: '历史' },
      { path: 'paper', title: '模拟交易' },
      { path: 'live', title: '实盘交易' },
    ]},
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/pages/Wallet.vue'),
    meta: { title: '钱包', children: [
      { path: 'assets', title: '资产管理' },
      { path: 'deposit', title: '充值' },
      { path: 'withdraw', title: '提现' },
      { path: 'history', title: '记录' },
    ]},
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { title: '设置', children: [
      { path: 'trading', title: '交易配置' },
      { path: 'risk', title: '风控规则' },
      { path: 'api', title: 'API管理' },
      { path: 'notifications', title: '通知' },
      { path: 'team', title: '团队' },
    ]},
  },

  // ========== 二级: 功能模块页 ==========
  {
    path: '/market/kline/:symbol',
    name: 'KlineDetail',
    component: () => import('@/pages/KlineDetail.vue'),
    meta: { title: 'K线详情', parent: 'Market' },
  },
  {
    path: '/signals/:id',
    name: 'SignalDetail',
    component: () => import('@/pages/SignalDetail.vue'),
    meta: { title: '信号详情', parent: 'Signals' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
