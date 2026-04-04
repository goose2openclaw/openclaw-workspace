/**
 * GO2SE Integration Entry Point V11
 * 前后端数据流通 - 统一入口
 * 
 * 使用方式:
 * import GO2SE from './integration';
 * 
 * // 在 main.js 中初始化
 * GO2SE.init vue, pinia, router
 * 
 * // 在组件中使用 hooks
 * const { useMarketData, useSignals, useMirofish } = GO2SE.hooks;
 * 
 * // 在组件中使用 stores
 * const marketStore = GO2SE.stores.market();
 */

import * as apiClient from './api_client.js';
import * as apiHooks from './api_hooks.js';
import * as stores from './stores/index.js';
import * as wsService from './ws_service.js';

// ========== Vue 插件安装函数 ==========
function installVuePlugin(app, options = {}) {
  const { router = null, autoConnect = true } = options;

  // 挂载到全局
  app.config.globalProperties.$go2se = apiClient.GO2SE;
  app.config.globalProperties.$go2seWs = wsService.GO2SE_WS;

  // 提供 inject
  app.provide('go2se', apiClient.GO2SE);
  app.provide('go2seWs', wsService.GO2SE_WS);

  // 自动连接WebSocket
  if (autoConnect && typeof window !== 'undefined') {
    apiClient.GO2SE.healthCheck().then(result => {
      if (result.ok) {
        wsService.GO2SE_WS.connect();
        console.log('🪿 GO2SE WebSocket auto-connected');
      }
    });
  }

  console.log('🪿 GO2SE Integration installed');
}

// ========== Pinia 插件 ==========
function getPiniaStores() {
  return {
    marketStore: stores.useMarketStore,
    signalsStore: stores.useSignalsStore,
    strategiesStore: stores.useStrategiesStore,
    portfolioStore: stores.usePortfolioStore,
    walletStore: stores.useWalletStore,
    mirofishStore: stores.useMirofishStore,
    healthStore: stores.useHealthStore,
  };
}

// ========== 组合式API hooks ==========
function getHooks() {
  return {
    useApi: apiHooks.useApi,
    useMarketData: apiHooks.useMarketData,
    useSignals: apiHooks.useSignals,
    useStrategies: apiHooks.useStrategies,
    usePortfolio: apiHooks.usePortfolio,
    useWallet: apiHooks.useWallet,
    useMirofish: apiHooks.useMirofish,
    useWebSocket: apiHooks.useWebSocket,
    useHealth: apiHooks.useHealth,
  };
}

// ========== 完整导出 ==========
const GO2SEIntegration = {
  // 插件安装
  install: installVuePlugin,

  // API客户端
  client: apiClient.GO2SE,
  apiClient,

  // WebSocket服务
  ws: wsService.GO2SE_WS,
  wsService,

  // Pinia stores
  stores: getPiniaStores(),

  // Vue Composition API hooks
  hooks: getHooks(),

  // 便捷方法
  init(app, pinia, router, options = {}) {
    // 初始化Pinia
    if (pinia) {
      app.use(pinia);
    }

    // 安装插件
    installVuePlugin(app, { router, ...options });

    return this;
  },

  // 连接状态
  isConnected() {
    return wsService.GO2SE_WS.isConnected;
  },

  // 发送消息
  send(type, data) {
    return wsService.GO2SE_WS.send({ type, ...data });
  },

  // 订阅频道
  subscribe(channel) {
    wsService.GO2SE_WS.subscribe(channel);
  },

  // 取消订阅
  unsubscribe(channel) {
    wsService.GO2SE_WS.unsubscribe(channel);
  },
};

export default GO2SEIntegration;
export {
  apiClient,
  apiHooks,
  stores,
  wsService,
  installVuePlugin as install,
};
