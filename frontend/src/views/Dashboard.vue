<template>
  <section class="page" data-module="dashboard">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">汇总各业务模块的关键指标；点击卡片可下钻查看各模块待处理量与异常量。</p>
      </div>
      <div class="page-actions">
        <div class="period-switch" role="group" aria-label="统计区间">
          <button
            v-for="option in PERIOD_OPTIONS"
            :key="option.value"
            type="button"
            class="btn period-btn"
            :class="{ active: option.value === dashboard.period }"
            @click="changePeriod(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
        <button class="btn" type="button" @click="reload">刷新看板</button>
      </div>
    </header>

    <div class="stat-row">
      <button
        v-for="card in cards"
        :key="card.key"
        type="button"
        class="stat-card stat-card-btn"
        :class="{ active: card.key === dashboard.metric }"
        @click="dashboard.setMetric(card.key)"
      >
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ loading ? '—' : card.value }}</strong>
        <span class="stat-hint">查看模块分布 →</span>
      </button>
    </div>

    <section class="drill-panel">
      <header class="drill-head">
        <h3>{{ activeCardLabel }} · 模块明细</h3>
        <span class="page-desc">
          统计区间：{{ periodLabel(dashboard.period) }} · 按待处理量排列 ·
          有数据 {{ activeCount }} 个模块，暂无数据 {{ emptyCount }} 个
        </span>
      </header>
      <table class="data-table">
        <thead>
          <tr>
            <th>业务模块</th>
            <th>最近记录时间</th>
            <th :class="{ 'col-focus': dashboard.metric === 'pending' }">待处理量</th>
            <th :class="{ 'col-focus': dashboard.metric === 'abnormal' }">异常量</th>
            <th>区间新增</th>
            <th>入口</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in sortedModules" :key="row.key">
            <td>
              <RouterLink class="link" :to="row.path">{{ row.name }}</RouterLink>
            </td>
            <td>{{ row.latest_at ?? '暂无记录' }}</td>
            <td :class="{ 'col-focus': dashboard.metric === 'pending' }">
              <span v-if="row.pending === null" class="empty-text">暂无</span>
              <template v-else>{{ row.pending }}</template>
            </td>
            <td :class="{ 'col-focus': dashboard.metric === 'abnormal' }">
              <span v-if="row.abnormal === null" class="empty-text">暂无</span>
              <template v-else>{{ row.abnormal }}</template>
            </td>
            <td>
              <span v-if="row.created === null" class="empty-text">暂无</span>
              <template v-else>{{ row.created }}</template>
            </td>
            <td>
              <RouterLink class="link" :to="row.path">进入模块 →</RouterLink>
            </td>
          </tr>
          <tr v-if="!loading && !sortedModules.length">
            <td colspan="6" class="empty-state">看板数据加载失败，点击右上角「刷新看板」重试</td>
          </tr>
        </tbody>
      </table>
      <footer class="page-foot">
        <span v-if="emptyCount > 0" class="empty-text">
          标注「暂无」的模块在当前统计区间内没有记录，不计入卡片合计，与数量为 0 区分。
        </span>
        <span v-else>当前区间内所有模块均有记录。</span>
        <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
      </footer>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'
import { MODULES, PERIOD_OPTIONS, periodLabel, type PeriodValue } from '@/config/modules'
import { useDashboardStore, type DrillMetric } from '@/stores/dashboard'

type OverviewCard = { key: DrillMetric; label: string; value: number }
type ModuleStat = {
  key: string
  name: string
  path: string
  created: number | null
  pending: number | null
  abnormal: number | null
  latest_at: string | null
}
type Overview = { period: string; cards: OverviewCard[]; modules: ModuleStat[] }

const dashboard = useDashboardStore()

const cards = ref<OverviewCard[]>([])
const modules = ref<ModuleStat[]>([])
const loading = ref(false)
const errorMessage = ref('')

// 模块在注册表中的序号：待处理量相同时按导航顺序兜底，保证排序稳定、可对照。
const registryIndex = new Map(MODULES.map((item, index) => [item.key, index]))

const sortedModules = computed(() =>
  [...modules.value].sort((a, b) => {
    // 区间内无记录的模块（null）统一沉底，不与真实的 0 混排。
    const pendingGap = (b.pending ?? -1) - (a.pending ?? -1)
    if (pendingGap !== 0) return pendingGap
    const abnormalGap = (b.abnormal ?? -1) - (a.abnormal ?? -1)
    if (abnormalGap !== 0) return abnormalGap
    return (registryIndex.get(a.key) ?? 0) - (registryIndex.get(b.key) ?? 0)
  }),
)

const activeCount = computed(() => modules.value.filter((item) => item.created !== null).length)
const emptyCount = computed(() => modules.value.length - activeCount.value)
const activeCardLabel = computed(
  () => cards.value.find((card) => card.key === dashboard.metric)?.label ?? '待处理',
)

async function loadOverview() {
  loading.value = true
  errorMessage.value = ''
  try {
    const payload = await fetchJson<Overview>(`/api/overview?period=${dashboard.period}`)
    cards.value = payload.cards
    modules.value = payload.modules
  } catch (error) {
    // 失败时保留上一次数据并给出说明，不伪造一排 0 让看板显得「正常」。
    cards.value = []
    modules.value = []
    errorMessage.value = error instanceof Error ? error.message : '运营概览加载失败'
  } finally {
    loading.value = false
  }
}

// 切换区间：偏好落到 store（localStorage），重新拉数后排序随区间变化。
function changePeriod(period: PeriodValue) {
  if (period === dashboard.period) return
  dashboard.setPeriod(period)
  void loadOverview()
}

function reload() {
  void loadOverview()
}

// 每次进入看板（含从模块页返回）都重新拉数，保证卡片数字与模块实际状态一致；
// 区间与下钻卡片从 store 恢复，不会被重置成默认值。
onMounted(loadOverview)
</script>
