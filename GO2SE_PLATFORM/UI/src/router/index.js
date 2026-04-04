/**
 * GO2SE Vue3 Router Configuration
 * ===============================
 * 基于v2.5 UX完整架构
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

  // ========== A. 注意力板块 ==========
  {
    path: '/focus',
    name: 'Focus',
    component: () => import('@/pages/Focus.vue'),
    meta: { title: '注意力板块', icon: '🎯' },
  },

  // ========== B. 宏观微观 ==========
  {
    path: '/macro-micro',
    name: 'MacroMicro',
    component: () => import('@/pages/MacroMicro.vue'),
    meta: { title: '宏观微观', icon: '🔭' },
  },

  // ========== C. 资产看板 ==========
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('@/pages/Assets.vue'),
    meta: { title: '资产看板', icon: '💰' },
    children: [
      { path: '', redirect: '/assets/overview' },
      { path: 'overview', name: 'AssetsOverview', component: () => import('@/pages/assets/Overview.vue') },
      { path: 'investment', name: 'AssetsInvestment', component: () => import('@/pages/assets/Investment.vue') },
      { path: 'work', name: 'AssetsWork', component: () => import('@/pages/assets/Work.vue') },
      { path: 'simulator', name: 'AssetsSimulator', component: () => import('@/pages/assets/Simulator.vue') },
    ],
  },

  // ========== D. 投资配置 ==========
  {
    path: '/invest',
    name: 'Invest',
    component: () => import('@/pages/Invest.vue'),
    meta: { title: '投资配置', icon: '📊' },
    children: [
      { path: '', redirect: '/invest/rabbit' },
      { path: 'rabbit', name: 'InvestRabbit', component: () => import('@/pages/invest/Rabbit.vue') },
      { path: 'mole', name: 'InvestMole', component: () => import('@/pages/invest/Mole.vue') },
      { path: 'oracle', name: 'InvestOracle', component: () => import('@/pages/invest/Oracle.vue') },
      { path: 'leader', name: 'InvestLeader', component: () => import('@/pages/invest/Leader.vue') },
      { path: 'hitchhiker', name: 'InvestHitchhiker', component: () => import('@/pages/invest/Hitchhiker.vue') },
    ],
  },

  // ========== E. 打工配置 ==========
  {
    path: '/work',
    name: 'Work',
    component: () => import('@/pages/Work.vue'),
    meta: { title: '打工配置', icon: '💼' },
    children: [
      { path: '', redirect: '/work/wool' },
      { path: 'wool', name: 'WorkWool', component: () => import('@/pages/work/Wool.vue') },
      { path: 'poor', name: 'WorkPoor', component: () => import('@/pages/work/Poor.vue') },
    ],
  },

  // ========== F. 算力资源 ==========
  {
    path: '/compute',
    name: 'Compute',
    component: () => import('@/pages/Compute.vue'),
    meta: { title: '算力资源', icon: '🖥️' },
  },

  // ========== G. 信号输入 ==========
  {
    path: '/signals',
    name: 'Signals',
    component: () => import('@/pages/Signals.vue'),
    meta: { title: '信号输入', icon: '📡' },
  },

  // ========== H. 策略为王 ==========
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/pages/Strategies.vue'),
    meta: { title: '策略为王', icon: '♟️' },
  },

  // ========== I. 安全机制 ==========
  {
    path: '/security',
    name: 'Security',
    component: () => import('@/pages/Security.vue'),
    meta: { title: '安全机制', icon: '🔒' },
  },

  // ========== J. 机器学习 ==========
  {
    path: '/ml',
    name: 'ML',
    component: () => import('@/pages/ML.vue'),
    meta: { title: '机器学习', icon: '🤖' },
  },

  // ========== Legacy Routes (兼容) ==========
  {
    path: '/dashboard',
    redirect: '/assets'
  },
  {
    path: '/home',
    redirect: '/focus'
  },
  {
    path: '/hot',
    redirect: '/focus'
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
