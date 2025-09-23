import { pipeline } from '@xenova/transformers'

class EmbeddingService {
  constructor() {
    this.model = null
    this.isLoading = false
  }

  async initialize() {
    if (this.model || this.isLoading) {
      return this.model
    }

    this.isLoading = true
    try {
      console.log('Loading embedding model...')
      // Используем легкую модель для быстрой загрузки
      this.model = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2')
      console.log('Embedding model loaded successfully')
      return this.model
    } catch (error) {
      console.error('Error loading embedding model:', error)
      throw error
    } finally {
      this.isLoading = false
    }
  }

  async createEmbedding(text) {
    if (!this.model) {
      await this.initialize()
    }

    try {
      // Создаем эмбеддинг из текста
      const result = await this.model(text, { pooling: 'mean', normalize: true })
      
      // Конвертируем в обычный массив чисел
      const embedding = Array.from(result.data)
      
      console.log(`Created embedding for text: "${text.substring(0, 50)}..."`)
      console.log(`Embedding dimension: ${embedding.length}`)
      
      return embedding
    } catch (error) {
      console.error('Error creating embedding:', error)
      throw error
    }
  }

  async createEmbeddings(texts) {
    if (!Array.isArray(texts)) {
      texts = [texts]
    }

    const embeddings = []
    for (const text of texts) {
      const embedding = await this.createEmbedding(text)
      embeddings.push(embedding)
    }

    return embeddings
  }

  // Создание случайного эмбеддинга для демонстрации
  createRandomEmbedding(dimension = 5) {
    return Array.from({ length: dimension }, () => Math.random())
  }

  // Проверка, загружена ли модель
  isModelLoaded() {
    return this.model !== null
  }

  // Получение информации о модели
  getModelInfo() {
    return {
      loaded: this.isModelLoaded(),
      isLoading: this.isLoading,
      name: 'Xenova/all-MiniLM-L6-v2'
    }
  }
}

// Создаем единственный экземпляр сервиса
export const embeddingService = new EmbeddingService()

export default embeddingService
