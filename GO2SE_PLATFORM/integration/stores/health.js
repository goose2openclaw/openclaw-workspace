/**
 * Health Store - 健康检查状态管理
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useHealthStore = defineStore('health', () => {
  const data = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const lastChecked = ref(null);
  let checkInterval = null;

  const isHealthy = computed(() => {
    return data.value?.status === 'healthy';
  });

  const signals = computed(() => {
    return data.value?.signals || {};
  });

  const dependencies = computed(() => {
    return data.value?.dependencies || {};
  });

  const limits = computed(() => {
    return data.value?.limits || {};
  });

  const hasAlerts = computed(() => {
    const limits_data = limits.value;
    return limits_data.cpu_alert || 
           limits_data.memory_alert || 
           limits_data.disk_alert;
  });

  async function check() {
    loading.value = true;
    error.value = null;
    try {
      const result = await window.GO2SE.healthCheck();
      data.value = result.data;
      lastChecked.value = new Date();
      return result;
    } catch (e) {
      error.value = e;
      data.value = null;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function startAutoCheck(intervalMs = 30000) {
    stopAutoCheck();
    checkInterval = setInterval(check, intervalMs);
  }

  function stopAutoCheck() {
    if (checkInterval) {
      clearInterval(checkInterval);
      checkInterval = null;
    }
  }

  return {
    data,
    loading,
    error,
    lastChecked,
    isHealthy,
    signals,
    dependencies,
    limits,
    hasAlerts,
    check,
    startAutoCheck,
    stopAutoCheck,
  };
});
