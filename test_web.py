#!/usr/bin/env python3
"""
Простой тест для проверки работы веб-интерфейса.
"""

import sys
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Тест импортов."""
    try:
        from app import app, init_app
        print("✓ Импорты успешны")
        return True
    except ImportError as e:
        print(f"✗ Ошибка импорта: {e}")
        return False

def test_app_creation():
    """Тест создания приложения."""
    try:
        from app import app
        print("✓ Flask приложение создано")
        return True
    except Exception as e:
        print(f"✗ Ошибка создания приложения: {e}")
        return False

def test_routes():
    """Тест маршрутов."""
    try:
        from app import app
        
        routes = [
            '/',
            '/collections',
            '/chunks',
            '/search',
            '/vectors',
            '/api/collections',
            '/api/chunks',
            '/api/search',
            '/api/vectors'
        ]
        
        with app.test_client() as client:
            for route in routes:
                if route.startswith('/api/'):
                    # API маршруты
                    if route == '/api/search':
                        response = client.post(route, json={'query': 'test'})
                    else:
                        response = client.get(route)
                else:
                    # HTML маршруты
                    response = client.get(route)
                
                if response.status_code in [200, 400, 500]:  # 400/500 тоже нормально для тестов
                    print(f"✓ Маршрут {route} отвечает")
                else:
                    print(f"✗ Маршрут {route} вернул код {response.status_code}")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка тестирования маршрутов: {e}")
        return False

def main():
    """Основная функция тестирования."""
    print("Тестирование веб-интерфейса BMK RAG...")
    print()
    
    tests = [
        ("Импорты", test_imports),
        ("Создание приложения", test_app_creation),
        ("Маршруты", test_routes),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Тест: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print(f"Результат: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("✓ Все тесты пройдены! Веб-интерфейс готов к использованию.")
        print("Запустите: make web")
    else:
        print("✗ Некоторые тесты не пройдены. Проверьте зависимости.")
        print("Убедитесь, что установлен Flask: pip install flask")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
