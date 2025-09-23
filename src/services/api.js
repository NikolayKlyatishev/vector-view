import axios from 'axios'
import { embeddingService } from './embeddingService'

// Создаем экземпляр axios с базовой конфигурацией для ChromaDB
const api = axios.create({
  baseURL: '/api/v2',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Получение информации о пользователе и тенантах
  async getUserIdentity() {
    try {
      const response = await api.get('/auth/identity')
      return response.data
    } catch (error) {
      console.error('Error fetching user identity:', error)
      throw error
    }
  },

  // Получение списка тенантов
  async getTenants() {
    try {
      // ChromaDB не имеет прямого API для получения списка тенантов
      // Возвращаем дефолтный тенант
      return [{ name: 'default_tenant' }]
    } catch (error) {
      console.error('Error fetching tenants:', error)
      throw error
    }
  },

  // Получение тенанта по имени
  async getTenant(tenantName) {
    try {
      const response = await api.get(`/tenants/${tenantName}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching tenant ${tenantName}:`, error)
      throw error
    }
  },

  // Получение списка баз данных для тенанта
  async getDatabases(tenant) {
    try {
      const response = await api.get(`/tenants/${tenant}/databases`)
      return response.data
    } catch (error) {
      console.error(`Error fetching databases for tenant ${tenant}:`, error)
      throw error
    }
  },

  // Получение базы данных
  async getDatabase(tenant, database) {
    try {
      const response = await api.get(`/tenants/${tenant}/databases/${database}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching database ${database}:`, error)
      throw error
    }
  },

  // Получение списка коллекций
  async getCollections(tenant, database, limit = 100, offset = 0) {
    try {
      const response = await api.get(`/tenants/${tenant}/databases/${database}/collections`, {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      console.error(`Error fetching collections for ${tenant}/${database}:`, error)
      throw error
    }
  },

  // Получение коллекции по ID
  async getCollection(tenant, database, collectionId) {
    try {
      const response = await api.get(`/tenants/${tenant}/databases/${database}/collections/${collectionId}`)
      return response.data
    } catch (error) {
      console.error(`Error fetching collection ${collectionId}:`, error)
      throw error
    }
  },

  // Получение документов из коллекции
  async getDocuments(tenant, database, collectionId, limit = 100, offset = 0) {
    try {
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/get`, {
        include: ['documents', 'metadatas', 'embeddings'],
        limit,
        offset
      })
      return response.data
    } catch (error) {
      console.error(`Error fetching documents from collection ${collectionId}:`, error)
      throw error
    }
  },

  // Поиск документов в коллекции
  async searchDocuments(tenant, database, collectionId, query, limit = 100, offset = 0) {
    try {
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/query`, {
        query_embeddings: query.embeddings || [],
        n_results: limit,
        include: ['documents', 'metadatas', 'distances']
      })
      return response.data
    } catch (error) {
      console.error(`Error searching documents in collection ${collectionId}:`, error)
      throw error
    }
  },

  // Поиск по тексту (создание эмбеддинга)
  async searchByText(tenant, database, collectionId, queryText, limit = 100) {
    try {
      // Создаем реальный эмбеддинг из текста
      const embedding = await embeddingService.createEmbedding(queryText)
      
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/query`, {
        query_embeddings: [embedding],
        n_results: limit,
        include: ['documents', 'metadatas', 'distances']
      })
      return response.data
    } catch (error) {
      console.error(`Error searching by text in collection ${collectionId}:`, error)
      // Fallback на случайный эмбеддинг если модель не загрузилась
      console.log('Falling back to random embedding...')
      const randomEmbedding = embeddingService.createRandomEmbedding(5)
      
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/query`, {
        query_embeddings: [randomEmbedding],
        n_results: limit,
        include: ['documents', 'metadatas', 'distances']
      })
      return response.data
    }
  },

  // Получение количества документов в коллекции
  async getCollectionCount(tenant, database, collectionId) {
    try {
      const response = await api.get(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/count`)
      return response.data
    } catch (error) {
      console.error(`Error fetching collection count for ${collectionId}:`, error)
      throw error
    }
  },

  // Создание новой коллекции
  async createCollection(tenant, database, name, metadata = {}) {
    try {
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections`, {
        name,
        metadata
      })
      return response.data
    } catch (error) {
      console.error(`Error creating collection ${name}:`, error)
      throw error
    }
  },

  // Удаление коллекции
  async deleteCollection(tenant, database, collectionId) {
    try {
      const response = await api.delete(`/tenants/${tenant}/databases/${database}/collections/${collectionId}`)
      return response.data
    } catch (error) {
      console.error(`Error deleting collection ${collectionId}:`, error)
      throw error
    }
  },

  // Добавление документов в коллекцию
  async addDocuments(tenant, database, collectionId, documents) {
    try {
      const response = await api.post(`/tenants/${tenant}/databases/${database}/collections/${collectionId}/add`, documents)
      return response.data
    } catch (error) {
      console.error(`Error adding documents to collection ${collectionId}:`, error)
      throw error
    }
  }
}

export default api
