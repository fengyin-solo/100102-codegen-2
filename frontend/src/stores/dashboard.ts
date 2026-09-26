import { defineStore } from 'pinia'

import type { PeriodValue } from '@/config/modules'

export type DrillMetric = 'modules' | 'created' | 'pending' | 'abnormal'

const PERIOD_KEY = 'dashboard.period'
const METRIC_KEY = 'dashboard.metric'

function readPeriod(): PeriodValue {
  const value = window.localStorage.getItem(PERIOD_KEY)
  return value === 'today' || value === 'week' || value === 'month' || value === 'all'
    ? value
    : 'month'
}

function readMetric(): DrillMetric {
  const value = window.localStorage.getItem(METRIC_KEY)
  return value === 'modules' || value === 'created' || value === 'pending' || value === 'abnormal'
    ? value
    : 'pending'
}

interface DashboardState {
  period: PeriodValue
  metric: DrillMetric
}

/**
 * 看板偏好独立于页面组件保存：进入某个模块再返回时，组件会重建并重新拉数，
 * 但统计区间与展开的下钻卡片从这里恢复，不会每次都跳回默认的那一组。
 */
export const useDashboardStore = defineStore('dashboard', {
  state: (): DashboardState => ({
    period: readPeriod(),
    metric: readMetric(),
  }),
  actions: {
    setPeriod(period: PeriodValue) {
      this.period = period
      window.localStorage.setItem(PERIOD_KEY, period)
    },
    setMetric(metric: DrillMetric) {
      this.metric = metric
      window.localStorage.setItem(METRIC_KEY, metric)
    },
  },
})
