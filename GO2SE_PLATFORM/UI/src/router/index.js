/**
 * GO2SE Vue3 Router Configuration
 * ===============================
 * v2.6 - 14模块完整导航架构
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  // ========== 零级: 入口页 ==========
  { path: '/', name: 'Landing', component: () => import('@/pages/Landing.vue'), meta: { title: '启动页' } },
  { path: '/login', name: 'Login', component: () => import('@/pages/Login.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'Register', component: () => import('@/pages/Register.vue'), meta: { title: '注册' } },

  // ========== A. 注意力板块 ==========
  { path: '/focus', name: 'Focus', component: () => import('@/pages/Focus.vue'), meta: { title: '注意力板块', icon: '🎯' } },

  // ========== B. 宏观微观 ==========
  { path: '/macro-micro', name: 'MacroMicro', component: () => import('@/pages/MacroMicro.vue'), meta: { title: '宏观微观', icon: '🔭' } },

  // ========== C. 资产看板 ==========
  {
    path: '/assets',
    name: 'Assets',
    component: () => import('@/pages/Assets.vue'),
    meta: { title: '资产看板', icon: '💰' },
    children: [
      { path: '', redirect: '/assets/c1' },
      { path: 'c1', name: 'AssetsC1', component: () => import('@/pages/assets/C1.vue') },
      { path: 'c2', name: 'AssetsC2', component: () => import('@/pages/assets/C2.vue') },
      { path: 'c3', name: 'AssetsC3', component: () => import('@/pages/assets/C3.vue') },
      { path: 'c4', name: 'AssetsC4', component: () => import('@/pages/assets/C4.vue') },
      { path: 'c5', name: 'AssetsC5', component: () => import('@/pages/assets/C5.vue') },
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
  { path: '/compute', name: 'Compute', component: () => import('@/pages/Compute.vue'), meta: { title: '算力资源', icon: '🖥️' } },

  // ========== G. 信号输入 ==========
  { path: '/signals', name: 'Signals', component: () => import('@/pages/Signals.vue'), meta: { title: '信号输入', icon: '📡' } },

  // ========== H. 策略为王 ==========
  {
    path: '/strategies',
    name: 'Strategies',
    component: () => import('@/pages/Strategies.vue'),
    meta: { title: '策略为王', icon: '♟️' },
    children: [
      { path: '', redirect: '/strategies/h1' },
      { path: 'h1', name: 'StrategyH1', component: () => import('@/pages/strategies/H1.vue') },
      { path: 'h2', name: 'StrategyH2', component: () => import('@/pages/strategies/H2.vue') },
      { path: 'h3', name: 'StrategyH3', component: () => import('@/pages/strategies/H3.vue') },
      { path: 'h4', name: 'StrategyH4', component: () => import('@/pages/strategies/H4.vue') },
    ],
  },

  // ========== I. 安全机制 ==========
  {
    path: '/security',
    name: 'Security',
    component: () => import('@/pages/Security.vue'),
    meta: { title: '安全机制', icon: '🔒' },
    children: [
      { path: '', redirect: '/security/i1' },
      { path: 'i1', name: 'SecurityI1', component: () => import('@/pages/security/I1.vue') },
      { path: 'i2', name: 'SecurityI2', component: () => import('@/pages/security/I2.vue') },
      { path: 'i3', name: 'SecurityI3', component: () => import('@/pages/security/I3.vue') },
      { path: 'i4', name: 'SecurityI4', component: () => import('@/pages/security/I4.vue') },
      { path: 'i5', name: 'SecurityI5', component: () => import('@/pages/security/I5.vue') },
      { path: 'i6', name: 'SecurityI6', component: () => import('@/pages/security/I6.vue') },
      { path: 'i7', name: 'SecurityI7', component: () => import('@/pages/security/I7.vue') },
    ],
  },

  // ========== J. 机器学习 ==========
  {
    path: '/ml',
    name: 'ML',
    component: () => import('@/pages/ML.vue'),
    meta: { title: '机器学习', icon: '🤖' },
    children: [
      { path: '', redirect: '/ml/j1' },
      { path: 'j1', name: 'MLJ1', component: () => import('@/pages/ml/J1.vue') },
      { path: 'j2', name: 'MLJ2', component: () => import('@/pages/ml/J2.vue') },
    ],
  },

  // ========== K. 私募LP ==========
  {
    path: '/private',
    name: 'Private',
    component: () => import('@/pages/Private.vue'),
    meta: { title: '私募LP', icon: '🏛️' },
    children: [
      { path: '', redirect: '/private/k1' },
      { path: 'k1', name: 'PrivateK1', component: () => import('@/pages/private/K1.vue') },
      { path: 'k2', name: 'PrivateK2', component: () => import('@/pages/private/K2.vue') },
    ],
  },

  // ========== L. 设置 ==========
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/pages/Settings.vue'),
    meta: { title: '设置', icon: '⚙️' },
    children: [
      { path: '', redirect: '/settings/l1' },
      { path: 'l1', name: 'SettingsL1', component: () => import('@/pages/settings/L1.vue') },
      { path: 'l2', name: 'SettingsL2', component: () => import('@/pages/settings/L2.vue') },
      { path: 'l3', name: 'SettingsL3', component: () => import('@/pages/settings/L3.vue') },
      { path: 'l4', name: 'SettingsL4', component: () => import('@/pages/settings/L4.vue') },
    ],
  },

  // ========== M. 脚本日志 ==========
  {
    path: '/scripts',
    name: 'Scripts',
    component: () => import('@/pages/Scripts.vue'),
    meta: { title: '脚本日志', icon: '📝' },
    children: [
      { path: '', redirect: '/scripts/m1' },
      { path: 'm1', name: 'ScriptsM1', component: () => import('@/pages/scripts/M1.vue') },
      { path: 'm2', name: 'ScriptsM2', component: () => import('@/pages/scripts/M2.vue') },
      { path: 'm3', name: 'ScriptsM3', component: () => import('@/pages/scripts/M3.vue') },
    ],
  },

  // ========== N. 工程模式 ==========
  {
    path: '/engineering',
    name: 'Engineering',
    component: () => import('@/pages/Engineering.vue'),
    meta: { title: '工程模式', icon: '🔧' },
    children: [
      { path: '', redirect: '/engineering/n1' },
      { path: 'n1', name: 'EngineeringN1', component: () => import('@/pages/engineering/N1.vue') },
      { path: 'n2', name: 'EngineeringN2', component: () => import('@/pages/engineering/N2.vue') },
      { path: 'n3', name: 'EngineeringN3', component: () => import('@/pages/engineering/N3.vue') },
    ],
  },

  // ========== Legacy Routes ==========
  { path: '/dashboard', redirect: '/assets' },
  { path: '/home', redirect: '/focus' },
  { path: '/hot', redirect: '/focus' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
