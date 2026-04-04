/**
 * GO2SE Integration - 使用示例
 * ==============================
 * 
 * 本目录包含前后端数据流通的完整实现
 */

// ========== 1. 初始化 (在 main.js 中) ==========
/*
import GO2SE from './integration/index.js';

const app = createApp(App);
GO2SE.init(app, pinia, router);
*/

// ========== 2. 组件中使用 Hooks ==========
/*
<template>
  <div>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">错误: {{ error.message }}</div>
    <div v-else>
      <div v-for="item in signals" :key="item.id">
        {{ item.strategy }} - {{ item.signal }}
      </div>
    </div>
    <button @click="refresh">刷新</button>
  </div>
</template>

<script>
import { useSignals } from '@/integration/hooks.js';

export default {
  setup() {
    // 方式1: 自动获取数据
    const { signals, loading, error, fetchSignals, runSignal } = useSignals();
    
    // 方式2: 手动获取
    const { execute: fetchMarket } = useApi(() => window.GO2SE.getMarketData());
    
    const refresh = async () => {
      await fetchSignals({ limit: 100 });
    };
    
    return {
      signals,
      loading,
      error,
      refresh,
    };
  },
};
</script>
*/

// ========== 3. 组件中使用 Stores ==========
/*
<template>
  <div>
    <h3>资产看板</h3>
    <p>总资产: ${{ totalAsset }}</p>
    <div v-for="tool in investmentTools" :key="tool.id">
      {{ tool.name }}: {{ tool.allocation }}
    </div>
    <button @click="portfolioStore.fetchAll()">刷新</button>
  </div>
</template>

<script>
import { usePortfolioStore } from '@/integration/stores.js';
import { onMounted } from 'vue';

export default {
  setup() {
    const portfolioStore = usePortfolioStore();
    
    onMounted(() => {
      portfolioStore.fetchAll();
    });
    
    return {
      totalAsset: portfolioStore.totalAsset,
      investmentTools: portfolioStore.investmentTools,
      portfolioStore,
    };
  },
};
</script>
*/

// ========== 4. WebSocket 实时数据 ==========
/*
<template>
  <div>
    <span :class="{ connected: wsConnected }">
      {{ wsConnected ? '🟢 已连接' : '🔴 未连接' }}
    </span>
    <div v-if="lastMarketUpdate">
      最新价格: {{ lastMarketUpdate.price }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import { useWebSocket } from '@/integration/hooks.js';

export default {
  setup() {
    const lastMarketUpdate = ref(null);
    const wsConnected = ref(false);
    
    const { connected, lastMessage } = useWebSocket({
      onMessage: (data) => {
        if (data.type === 'market') {
          lastMarketUpdate.value = data.data;
        }
      },
    });
    
    wsConnected.value = connected.value;
    
    return {
      wsConnected,
      lastMarketUpdate,
    };
  },
};
</script>
*/

// ========== 5. MiroFish 预测 ==========
/*
<template>
  <div>
    <input v-model="question" placeholder="输入问题..." />
    <button @click="doPredict" :disabled="loading">
      {{ loading ? '预测中...' : '预测' }}
    </button>
    <div v-if="prediction">
      <pre>{{ JSON.stringify(prediction, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useMirofish } from '@/integration/hooks.js';

export default {
  setup() {
    const question = ref('');
    const { loading, predict, latestPrediction } = useMirofish();
    
    const doPredict = async () => {
      if (!question.value) return;
      await predict(question.value, 'default');
    };
    
    return {
      question,
      loading,
      prediction: latestPrediction,
      doPredict,
    };
  },
};
</script>
*/

// ========== 6. 健康检查 ==========
/*
<template>
  <div>
    <span :class="healthStore.isHealthy ? 'text-success' : 'text-danger'">
      {{ healthStore.isHealthy ? '✅ 健康' : '⚠️ 异常' }}
    </span>
    <div v-if="healthStore.hasAlerts">
      <span class="text-warning">⚠️ 有告警</span>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useHealthStore } from '@/integration/stores.js';

export default {
  setup() {
    const healthStore = useHealthStore();
    
    onMounted(() => {
      healthStore.check();
      healthStore.startAutoCheck(30000); // 每30秒检查
    });
    
    return {
      healthStore,
    };
  },
};
</script>
*/
