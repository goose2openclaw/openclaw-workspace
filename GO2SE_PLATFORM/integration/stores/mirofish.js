/**
 * Mirofish Store - MiroFish预测集成状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useMirofishStore = defineStore('mirofish', () => {
  const markets = ref([]);
  const predictions = ref([]);
  const simulationResults = ref(null);
  const dimensions = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const lastPrediction = ref(null);

  // 最新预测
  const latestPrediction = computed(() => {
    return predictions.value[0] || null;
  });

  // 预测历史
  const predictionHistory = computed(() => {
    return [...predictions.value].slice(0, 20);
  });

  // 仿真状态
  const simulationStatus = computed(() => {
    if (!simulationResults.value) return 'idle';
    if (simulationResults.value.running) return 'running';
    if (simulationResults.value.error) return 'error';
    return 'completed';
  });

  async function fetchMarkets() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getMirofishMarkets();
      markets.value = result.data || [];
      return result;
    } catch (e) {
      error.value = e;
      console.error('Mirofish markets fetch error:', e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function predict(question, scenario = 'default') {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.mirofishPredict(question, scenario);
      predictions.value.unshift(result);
      lastPrediction.value = result;
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function getDecision(params) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.getMirofishDecision(params);
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function runSimulation(simulationParams) {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.runSimulation(simulationParams);
      simulationResults.value = result;
      return result;
    } catch (e) {
      error.value = e;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchDimensions() {
    try {
      const result = await window.GO2SE.getDimensions();
      dimensions.value = result.data || [];
      return result;
    } catch (e) {
      console.error('Dimensions fetch error:', e);
    }
  }

  async function fetchSimulationResults() {
    try {
      const result = await window.GO2SE.getSimulationResults();
      simulationResults.value = result;
      return result;
    } catch (e) {
      console.error('Simulation results fetch error:', e);
    }
  }

  function updateFromWebSocket(message) {
    if (message.type === 'mirofish_prediction' && message.data) {
      predictions.value.unshift(message.data);
      lastPrediction.value = message.data;
    }
    if (message.type === 'simulation_update' && message.data) {
      simulationResults.value = {
        ...simulationResults.value,
        ...message.data,
      };
    }
  }

  return {
    markets,
    predictions,
    simulationResults,
    dimensions,
    loading,
    error,
    lastPrediction,
    latestPrediction,
    predictionHistory,
    simulationStatus,
    fetchMarkets,
    predict,
    getDecision,
    runSimulation,
    fetchDimensions,
    fetchSimulationResults,
    updateFromWebSocket,
  };
});
