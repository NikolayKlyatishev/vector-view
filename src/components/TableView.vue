<template>
  <div class="table-view">
    <div class="main-content">
      <div class="content-header">
        <div class="content-filters">
          <div class="filter-group">
            <span class="filter-label">WHERE</span>
            <input type="text" class="filter-input" placeholder="Filter conditions" />
          </div>
          <div class="filter-group">
            <span class="filter-label">ORDER BY</span>
            <input type="text" class="filter-input" placeholder="Sort by" />
          </div>
        </div>
      </div>

      <div class="data-table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="column in tableColumns" :key="column.name">
                <Filter class="icon" />
                {{ column.name }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in tableData" :key="index">
              <td v-for="column in tableColumns" :key="column.name">
                <span v-if="column.type === 'json'" class="json-cell">
                  {{ formatJsonValue(row[column.name]) }}
                </span>
                <span v-else>{{ row[column.name] || '<null>' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="status-bar">
        <div class="breadcrumb">
          <span>database</span>
          <span class="breadcrumb-separator">></span>
          <span>nlmk_admin@localhost</span>
          <span class="breadcrumb-separator">></span>
          <span>granular-slag-formation</span>
          <span class="breadcrumb-separator">></span>
          <span>public</span>
          <span class="breadcrumb-separator">></span>
          <span>tables</span>
          <span class="breadcrumb-separator">></span>
          <span>{{ tableName }}</span>
        </div>
        <div class="status-info">
          <span>SUM: Not enough values</span>
          <div class="status-icons">
            <Eye class="icon" />
            <Settings class="icon" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Filter, Eye, Settings } from 'lucide-vue-next'
import { apiService } from '../services/api'

export default {
  name: 'TableView',
  props: {
    tableName: {
      type: String,
      required: true
    }
  },
  components: {
    Filter,
    Eye,
    Settings
  },
  setup(props) {
    const tableData = ref([])
    const tableColumns = ref([])

    const loadTableData = async () => {
      try {
        const data = await apiService.getTableData(props.tableName)
        tableData.value = data.rows || []
        tableColumns.value = data.columns || []
      } catch (error) {
        console.error('Error loading table data:', error)
        // Заглушка для демонстрации
        tableData.value = generateMockData()
        tableColumns.value = generateMockColumns()
      }
    }

    const generateMockData = () => {
      return [
        {
          id: '3ff98e6c-0ece-4fe7-94bd-51b63e9efa2e',
          number: 226,
          created_at: '2025-08-27 11:02:56.260254',
          created_by: 'BORISOVA_AV',
          chemistry: { grade: 2, humidity: 0.0, calcGroup: 0, indicators: 'test' }
        },
        {
          id: '4ff98e6c-0ece-4fe7-94bd-51b63e9efa2e',
          number: 47,
          created_at: '2025-08-27 10:45:32.123456',
          created_by: 'SHANDURENKO_AV',
          chemistry: null
        }
      ]
    }

    const generateMockColumns = () => {
      return [
        { name: 'id', type: 'uuid' },
        { name: 'number', type: 'integer' },
        { name: 'created_at', type: 'timestamp' },
        { name: 'created_by', type: 'varchar' },
        { name: 'chemistry', type: 'json' }
      ]
    }

    const formatJsonValue = (value) => {
      if (!value) return '<null>'
      if (typeof value === 'object') {
        return JSON.stringify(value).substring(0, 50) + '...'
      }
      return value
    }

    onMounted(() => {
      loadTableData()
    })

    return {
      tableData,
      tableColumns,
      formatJsonValue
    }
  }
}
</script>

<style scoped>
.table-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-icons {
  display: flex;
  gap: 4px;
}
</style>
