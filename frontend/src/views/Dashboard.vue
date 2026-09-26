<template>
  <section class="page">
    <header class="page-head">
      <div>
        <h2>运营概览</h2>
        <p class="page-desc">按统计区间汇总各业务模块的待处理与异常，点开卡片可下钻到模块积压明细。</p>
      </div>
      <div class="range-switch" role="group" aria-label="统计区间">
        <button
          v-for="item in ranges"
          :key="item.key"
          type="button"
          class="btn"
          :class="{ primary: item.key === store.overviewRange }"
          @click="switchRange(item.key)"
        >
          {{ item.label }}
        </button>
      </div>
    </header>

    <div class="stat-row">
      <article
        v-for="card in cards"
        :key="card.key"
        class="stat-card clickable"
        :class="{ active: card.key === store.overviewCard }"
        role="button"
        tabindex="0"
        @click="toggleCard(card.key)"
        @keydown.enter="toggleCard(card.key)"
      >
        <span class="stat-label">{{ card.label }}</span>
        <strong class="stat-value">{{ card.value }}</strong>
        <span class="stat-hint">{{ card.key === store.overviewCard ? '点击收起明细' : '点击查看模块明细' }}</span>
      </article>
    </div>

    <div v-if="activeCard" class="drill-panel">
      <div class="drill-head">
        <span class="drill-title">{{ activeCard.label }} · 模块明细</span>
        <span class="drill-tip">统计区间：{{ rangeLabel }} · 按待处理量排列</span>
      </div>
      <table class="data-table">
        <thead>
          <tr>
            <th>业务模块</th>
            <th class="num-col">待处理</th>
            <th class="num-col">异常量</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in modules" :key="row.name">
            <td>
              <RouterLink :to="row.path" class="module-link">{{ row.label }}</RouterLink>
              <span v-if="row.latest_at" class="latest-at">最近记录 {{ row.latest_at }}</span>
            </td>
            <template v-if="row.has_data">
              <td class="num-col">
                <span :class="{ 'num-alert': row.pending > 0 }">{{ row.pending }}</span>
              </td>
              <td class="num-col">
                <span :class="{ 'num-alert': row.abnormal > 0 }">{{ row.abnormal }}</span>
              </td>
            </template>
            <td v-else colspan="2" class="empty-state">
              {{ emptyText }}
              <template v-if="row.latest_at">，可进入模块查看历史数据</template>
            </td>
          </tr>
          <tr v-if="!modules.length">
            <td colspan="3" class="empty-state">暂无业务模块数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <footer class="page-foot">
      <span>共 {{ modules.length }} 个业务模块，与左侧导航入口一一对应</span>
      <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchJson } from '@/api/client'
import { useSessionStore } from '@/stores/session'

type OverviewCard = { key: string; label: string; value: number }
type OverviewModule = {
  name: string
  label: string
  path: string
  created: number
  pending: number
  abnormal: number
  latest_at: string | null
  has_data: boolean
}
type Overview = {
  range: string
  range_label: string
  cards: OverviewCard[]
  modules: OverviewModule[]
}

// 与后端 OVERVIEW_RANGES 对应，用来渲染区间切换按钮；empty 是各区间下“暂无”的说明文案。
const ranges = [
  { key: 'today', label: '今日', empty: '今日暂无记录' },
  { key: 'week', label: '近7天', empty: '近7天内暂无记录' },
  { key: 'month', label: '近30天', empty: '近30天内暂无记录' },
  { key: 'all', label: '全部', empty: '暂无记录' },
]

const store = useSessionStore()
const cards = ref<OverviewCard[]>([])
const modules = ref<OverviewModule[]>([])
const rangeLabel = ref('')
const errorMessage = ref('')

const activeCard = computed<OverviewCard | null>(
  () => cards.value.find((card) => card.key === store.overviewCard) ?? null,
)
const emptyText = computed(
  () => ranges.find((item) => item.key === store.overviewRange)?.empty ?? '暂无记录',
)

async function loadOverview() {
  errorMessage.value = ''
  try {
    const payload = await fetchJson<Overview>(`/api/overview?range=${encodeURIComponent(store.overviewRange)}`)
    cards.value = payload.cards
    modules.value = payload.modules
    rangeLabel.value = payload.range_label
  } catch (error) {
    cards.value = []
    modules.value = []
    rangeLabel.value = ranges.find((item) => item.key === store.overviewRange)?.label ?? ''
    errorMessage.value = error instanceof Error ? error.message : '运营概览读取失败'
  }
}

function switchRange(key: string) {
  if (key === store.overviewRange) return
  store.setOverviewRange(key)
  void loadOverview()
}

function toggleCard(key: string) {
  store.setOverviewCard(key === store.overviewCard ? '' : key)
}

// 每次进入看板都重新拉取，保证与模块页处理后的数字一致；区间与展开卡片存在 session store 里，不重置。
onMounted(loadOverview)
</script>
