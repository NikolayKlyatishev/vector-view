<template>
  <div class="database-view">
    <!-- Верхняя панель поиска -->
          <div class="top-search-bar">
            <div class="search-controls">
              <span class="search-label">Search</span>
              <input 
                type="text" 
                class="search-input" 
                placeholder="Введите текст для поиска..." 
                v-model="searchQuery"
                @keyup.enter="performSearch"
              />
              <select class="search-type-select" v-model="searchType">
                <option value="text">По тексту</option>
                <option value="embedding">По эмбеддингу</option>
              </select>
              <select class="limit-select" v-model="documentLimit">
                <option value="10">10</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
              <button class="search-button" @click="performSearch" :disabled="isSearching">
                <span v-if="isSearching">⏳</span>
                <span v-else>🔍</span>
                {{ isSearching ? 'Searching...' : 'Search' }}
              </button>
              <button class="clear-button" @click="clearSearch" v-if="isSearchActive">
                ✕ Clear
              </button>
            </div>
            
            <!-- Статус модели эмбеддингов -->
            <div class="model-status" v-if="isModelLoading || modelInfo.name">
              <span v-if="isModelLoading" class="model-loading">
                ⏳ Загрузка модели эмбеддингов...
              </span>
              <span v-else-if="modelInfo.loaded" class="model-loaded">
                ✅ Модель загружена: {{ modelInfo.name }}
              </span>
              <span v-else class="model-error">
                ❌ Ошибка загрузки модели
              </span>
            </div>
          </div>

    <div class="main-layout">
      <!-- Левая панель с деревом навигации -->
      <div class="sidebar">
        <!-- Навигационное дерево -->
        <div class="navigation-tree">
          <div class="tree-section">
            <div class="tree-header" @click="toggleSection('tenants')">
              <ChevronRight v-if="!expandedSections.tenants" class="icon" />
              <ChevronDown v-else class="icon" />
              Tenants
            </div>
            <div v-if="expandedSections.tenants" class="tree-content">
              <div 
                v-for="tenant in tenants" 
                :key="tenant.name"
                class="tree-item"
                :class="{ active: selectedTenant === tenant.name }"
                @click="selectTenant(tenant.name)"
              >
                <Database class="icon" />
                {{ tenant.name }}
              </div>
            </div>
          </div>

          <div v-if="selectedTenant" class="tree-section">
            <div class="tree-header" @click="toggleSection('databases')">
              <ChevronRight v-if="!expandedSections.databases" class="icon" />
              <ChevronDown v-else class="icon" />
              Databases
            </div>
            <div v-if="expandedSections.databases" class="tree-content">
              <div 
                v-for="database in databases" 
                :key="database.name"
                class="tree-item"
                :class="{ active: selectedDatabase === database.name }"
                @click="selectDatabase(database.name)"
              >
                <Database class="icon" />
                {{ database.name }}
              </div>
            </div>
          </div>

          <div v-if="selectedDatabase" class="tree-section">
            <div class="tree-header" @click="toggleSection('collections')">
              <ChevronRight v-if="!expandedSections.collections" class="icon" />
              <ChevronDown v-else class="icon" />
              Collections ({{ collections.length }})
            </div>
            <div v-if="expandedSections.collections" class="tree-content">
              <div 
                v-for="collection in collections" 
                :key="collection.id"
                class="tree-item"
                :class="{ active: selectedCollection === collection.id }"
                @click="selectCollection(collection)"
              >
                <Folder class="icon" />
                {{ collection.name }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Правая панель с данными -->
      <div class="main-panel">
        <div class="data-table-container">
          <table class="data-table" v-if="selectedCollection && documents.length > 0">
            <thead>
              <tr>
                <th>ID</th>
                <th>Document</th>
                <th>Metadata</th>
                <th v-if="isSearchActive">Distance</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(doc, index) in documents" :key="doc.id || index">
                <td class="id-cell">{{ doc.id || `doc_${index}` }}</td>
                <td class="document-cell">{{ doc.document || '<empty>' }}</td>
                <td class="metadata-cell">
                  <span v-if="doc.metadata" class="json-cell">
                    {{ formatJsonValue(doc.metadata) }}
                  </span>
                  <span v-else>&lt;null&gt;</span>
                </td>
                <td v-if="isSearchActive" class="distance-cell">
                  <span v-if="doc.distance !== undefined" class="distance-value">
                    {{ doc.distance.toFixed(4) }}
                  </span>
                  <span v-else>-</span>
                </td>
              </tr>
            </tbody>
          </table>
          
          <div v-else-if="selectedCollection && documents.length === 0" class="no-data">
            <FileText class="icon" style="width: 48px; height: 48px; opacity: 0.3;" />
            <p>Коллекция пуста или документы не найдены</p>
          </div>
          
          <div v-else class="no-data">
            <Database class="icon" style="width: 48px; height: 48px; opacity: 0.3;" />
            <p>Выберите коллекцию для просмотра документов</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Нижняя статус-панель -->
    <div class="status-bar">
      <div class="breadcrumb">
        <span>vector-db</span>
        <span v-if="selectedTenant" class="breadcrumb-separator">></span>
        <span v-if="selectedTenant">{{ selectedTenant }}</span>
        <span v-if="selectedDatabase" class="breadcrumb-separator">></span>
        <span v-if="selectedDatabase">{{ selectedDatabase }}</span>
        <span v-if="selectedCollection" class="breadcrumb-separator">></span>
        <span v-if="selectedCollection">{{ selectedCollectionName }}</span>
      </div>
      <div class="status-info">
        <span v-if="selectedCollection">Doc</span>
        <span v-else>Ready</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { 
  ChevronRight, 
  ChevronDown, 
  Database, 
  Folder, 
  Search,
  FileText
} from 'lucide-vue-next'
import { apiService } from '../services/api'
import { embeddingService } from '../services/embeddingService'

export default {
  name: 'DatabaseView',
  components: {
    ChevronRight,
    ChevronDown,
    Database,
    Folder,
    Search,
    FileText
  },
  setup() {
    const router = useRouter()
    
    // Состояние навигации
    const selectedTenant = ref(null)
    const selectedDatabase = ref(null)
    const selectedCollection = ref(null)
    const selectedCollectionName = ref('')
    
    // Данные
    const tenants = ref([])
    const databases = ref([])
    const collections = ref([])
    const documents = ref([])
    
    // Поиск и фильтрация
    const searchQuery = ref('')
    const searchType = ref('text')
    const documentLimit = ref(50)
    const isSearchActive = ref(false)
    const isSearching = ref(false)
    const isModelLoading = ref(false)
    const modelInfo = ref({ loaded: false, isLoading: false, name: '' })
    
    const expandedSections = reactive({
      tenants: true,
      databases: false,
      collections: false
    })

    const toggleSection = (section) => {
      expandedSections[section] = !expandedSections[section]
    }

    const selectTenant = async (tenantName) => {
      selectedTenant.value = tenantName
      selectedDatabase.value = null
      selectedCollection.value = null
      selectedCollectionName.value = ''
      documents.value = []
      
      try {
        const data = await apiService.getDatabases(tenantName)
        databases.value = data || []
        expandedSections.databases = true
      } catch (error) {
        console.error('Error loading databases:', error)
        // Если API не работает, используем уже загруженные данные
        expandedSections.databases = true
      }
    }

    const selectDatabase = async (databaseName) => {
      selectedDatabase.value = databaseName
      selectedCollection.value = null
      selectedCollectionName.value = ''
      documents.value = []
      
      try {
        const data = await apiService.getCollections(selectedTenant.value, databaseName)
        collections.value = data || []
        expandedSections.collections = true
      } catch (error) {
        console.error('Error loading collections:', error)
        // Если API не работает, показываем пустой список
        collections.value = []
        expandedSections.collections = true
      }
    }

    const selectCollection = async (collection) => {
      selectedCollection.value = collection.id
      selectedCollectionName.value = collection.name
      
      try {
        const data = await apiService.getDocuments(
          selectedTenant.value, 
          selectedDatabase.value, 
          collection.id, 
          parseInt(documentLimit.value)
        )
        documents.value = formatDocumentsData(data)
      } catch (error) {
        console.error('Error loading documents:', error)
        // Если коллекция пуста или API не работает, показываем пустое состояние
        documents.value = []
      }
    }

    const performSearch = async () => {
      if (!selectedCollection.value || !searchQuery.value.trim()) {
        return
      }
      
      isSearching.value = true
      try {
        let data
        if (searchType.value === 'text') {
          data = await apiService.searchByText(
            selectedTenant.value,
            selectedDatabase.value,
            selectedCollection.value,
            searchQuery.value,
            parseInt(documentLimit.value)
          )
        } else {
          // Поиск по эмбеддингу - создаем случайный эмбеддинг для демонстрации
          const randomEmbedding = Array.from({length: 5}, () => Math.random())
          data = await apiService.searchDocuments(
            selectedTenant.value,
            selectedDatabase.value,
            selectedCollection.value,
            { embeddings: [randomEmbedding] },
            parseInt(documentLimit.value)
          )
        }
        
        documents.value = formatSearchResults(data)
        isSearchActive.value = true
      } catch (error) {
        console.error('Error performing search:', error)
        // Показываем сообщение об ошибке пользователю
        alert(`Ошибка поиска: ${error.response?.data?.message || error.message}`)
      } finally {
        isSearching.value = false
      }
    }

    const clearSearch = async () => {
      searchQuery.value = ''
      isSearchActive.value = false
      
      // Загружаем все документы из коллекции
      if (selectedCollection.value) {
        try {
          const data = await apiService.getDocuments(
            selectedTenant.value, 
            selectedDatabase.value, 
            selectedCollection.value, 
            parseInt(documentLimit.value)
          )
          documents.value = formatDocumentsData(data)
        } catch (error) {
          console.error('Error loading documents:', error)
          documents.value = []
        }
      }
    }

    const formatDocumentsData = (data) => {
      if (!data || !data.ids) return []
      
      const result = []
      const ids = data.ids
      const documents = data.documents || []
      const metadatas = data.metadatas || []
      const embeddings = data.embeddings || []
      
      for (let i = 0; i < ids.length; i++) {
        result.push({
          id: ids[i],
          document: documents[i] || null,
          metadata: metadatas[i] || null,
          embedding: embeddings[i] || null
        })
      }
      
      return result
    }

    const formatSearchResults = (data) => {
      if (!data || !data.ids) return []
      
      const result = []
      const ids = data.ids[0] || data.ids
      const documents = data.documents?.[0] || data.documents || []
      const metadatas = data.metadatas?.[0] || data.metadatas || []
      const distances = data.distances?.[0] || data.distances || []
      
      for (let i = 0; i < ids.length; i++) {
        result.push({
          id: ids[i],
          document: documents[i] || null,
          metadata: metadatas[i] || null,
          distance: distances[i] || null
        })
      }
      
      return result
    }


    const formatJsonValue = (value) => {
      if (!value) return '<null>'
      if (typeof value === 'object') {
        return JSON.stringify(value).substring(0, 50) + '...'
      }
      return value
    }

    onMounted(async () => {
      try {
        // Получаем реальные данные из API
        const identity = await apiService.getUserIdentity()
        tenants.value = [{ name: identity.tenant }]
        databases.value = identity.databases.map(db => ({ name: db }))
        
        if (identity.tenant) {
          selectedTenant.value = identity.tenant
          expandedSections.tenants = true
          expandedSections.databases = true
        }
      } catch (error) {
        console.error('Error loading data from API:', error)
        // Fallback на демо-данные
        tenants.value = [{ name: 'default_tenant' }]
        databases.value = [{ name: 'default_database' }]
        selectedTenant.value = 'default_tenant'
        expandedSections.tenants = true
        expandedSections.databases = true
      }

      // Инициализируем модель эмбеддингов в фоне
      initializeEmbeddingModel()
    })

    const initializeEmbeddingModel = async () => {
      try {
        isModelLoading.value = true
        modelInfo.value = { ...embeddingService.getModelInfo(), isLoading: true }
        
        await embeddingService.initialize()
        
        modelInfo.value = embeddingService.getModelInfo()
        console.log('Embedding model initialized successfully')
      } catch (error) {
        console.error('Error initializing embedding model:', error)
        modelInfo.value = { loaded: false, isLoading: false, name: 'Failed to load' }
      } finally {
        isModelLoading.value = false
      }
    }

    return {
      selectedTenant,
      selectedDatabase,
      selectedCollection,
      selectedCollectionName,
      tenants,
      databases,
      collections,
      documents,
      searchQuery,
      searchType,
      documentLimit,
      isSearchActive,
      isSearching,
      isModelLoading,
      modelInfo,
      expandedSections,
      toggleSection,
      selectTenant,
      selectDatabase,
      selectCollection,
      performSearch,
      clearSearch,
      formatJsonValue
    }
  }
}
</script>

<style scoped>
.database-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #1a1a1a;
}

/* Верхняя панель поиска */
.top-search-bar {
  background-color: #2d2d2d;
  border-bottom: 1px solid #404040;
  padding: 8px 16px;
  display: flex;
  justify-content: flex-end;
}

  .search-controls {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .search-label {
    color: #cccccc;
    font-size: 14px;
    font-weight: 500;
  }

  .search-input {
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    width: 250px;
  }

  .search-type-select {
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 14px;
    min-width: 120px;
  }

  .limit-select {
    background: #1a1a1a;
    border: 1px solid #404040;
    color: #ffffff;
    padding: 6px 8px;
    border-radius: 4px;
    font-size: 14px;
    min-width: 60px;
  }

  .search-button {
    background: #007acc;
    border: none;
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
  }

  .search-button:hover:not(:disabled) {
    background: #005a9e;
  }

  .search-button:disabled {
    background: #555555;
    cursor: not-allowed;
    opacity: 0.7;
  }

  .clear-button {
    background: #dc3545;
    border: none;
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
  }

  .clear-button:hover {
    background: #c82333;
  }

  .model-status {
    margin-top: 8px;
    font-size: 12px;
    text-align: center;
  }

  .model-loading {
    color: #ffc107;
    font-weight: 500;
  }

  .model-loaded {
    color: #28a745;
    font-weight: 500;
  }

  .model-error {
    color: #dc3545;
    font-weight: 500;
  }

/* Основная компоновка */
.main-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* Основная панель с данными */
.main-panel {
  flex: 1;
  background-color: #1a1a1a;
  display: flex;
  flex-direction: column;
}

/* Левая боковая панель с деревом */
.sidebar {
  width: 15%;
  min-width: 200px;
  background-color: #252525;
  border-right: 1px solid #404040;
  display: flex;
  flex-direction: column;
}

/* Навигационное дерево */
.navigation-tree {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.tree-section {
  margin-bottom: 4px;
}

.tree-header {
  padding: 8px 16px;
  background-color: #2d2d2d;
  border-bottom: 1px solid #404040;
  font-weight: 600;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #ffffff;
}

.tree-content {
  background-color: #1a1a1a;
}

.tree-item {
  padding: 8px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #cccccc;
  border-left: 3px solid transparent;
}

.tree-item:hover {
  background-color: #2d2d2d;
}

.tree-item.active {
  background-color: #404040;
  border-left-color: #007acc;
  color: #ffffff;
}


/* Контейнер таблицы данных */
.data-table-container {
  flex: 1;
  overflow: auto;
  padding: 16px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.data-table th {
  background-color: #2d2d2d;
  color: #ffffff;
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #404040;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table td {
  padding: 12px 16px;
  border-bottom: 1px solid #333333;
  color: #cccccc;
}

.data-table tr:hover {
  background-color: #2d2d2d;
}

.data-table tr:nth-child(even) {
  background-color: #1f1f1f;
}

.data-table tr:nth-child(even):hover {
  background-color: #2d2d2d;
}

/* Стили для ячеек таблицы */
.id-cell {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #888888;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-cell {
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.metadata-cell {
  max-width: 300px;
}

  .json-cell {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    background-color: #1f1f1f;
    padding: 4px 8px;
    border-radius: 4px;
    max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    display: inline-block;
  }

  .distance-cell {
    text-align: center;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    color: #888888;
  }

  .distance-value {
    background-color: #2d2d2d;
    padding: 4px 8px;
    border-radius: 4px;
    color: #00ff88;
    font-weight: 600;
  }

/* Пустое состояние */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666666;
  gap: 16px;
}

.no-data p {
  margin-top: 8px;
  font-size: 14px;
  color: #888888;
}

/* Статус-бар */
.status-bar {
  background-color: #2d2d2d;
  border-top: 1px solid #404040;
  padding: 8px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #cccccc;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
}

.breadcrumb-separator {
  margin: 0 4px;
  opacity: 0.5;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Иконки */
.icon {
  width: 16px;
  height: 16px;
  display: inline-block;
}

/* Скроллбар */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #2d2d2d;
}

::-webkit-scrollbar-thumb {
  background: #555555;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #666666;
}
</style>
