# 📦 Установка NT EXHAUST - CRYPTAL AI AUTO BOT

## Системные требования

- **Python 3.7+** (рекомендуется Python 3.8+)
- **pip** (менеджер пакетов Python)
- **Интернет соединение**
- **Linux/Windows/macOS**

## 🔧 Пошаговая установка

### 1. Проверка Python

```bash
# Проверьте версию Python
python3 --version
# или
python --version

# Должно быть 3.7.0 или выше
```

### 2. Клонирование проекта

```bash
# Если у вас есть git
git clone <repository-url>
cd airdrop-farm

# Или просто скопируйте все файлы в папку airdrop-farm
```

### 3. Установка зависимостей

```bash
cd airdrop-farm

# Рекомендуется создать виртуальное окружение
python3 -m venv venv

# Активация виртуального окружения
# На Linux/macOS:
source venv/bin/activate
# На Windows:
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 4. Настройка файлов конфигурации

#### Токены (обязательно)
```bash
# Откройте файл токенов
nano data/token.txt

# Добавьте ваши токены, по одному на строку:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Прокси (опционально)
```bash
# Откройте файл прокси
nano data/proxy.txt

# Добавьте прокси в поддерживаемых форматах:
http://user:pass@proxy.example.com:8080
socks5://user:pass@proxy.example.com:1080
https://proxy.example.com:3128
```

### 5. Проверка установки

```bash
# Тест импорта основных модулей
python3 -c "from src.utils.logger import Logger; Logger.info('Установка прошла успешно!', emoji='🎉')"
```

## 🚀 Первый запуск

### Простой запуск
```bash
python3 main.py
```

### Запуск с параметрами
```bash
# Показать справку
python3 run.py --help

# Запуск один раз
python3 run.py --mode once

# Запуск без прокси
python3 run.py --no-proxy
```

## 🐛 Решение проблем

### Проблема: ModuleNotFoundError
```bash
# Убедитесь, что вы в правильной директории
pwd  # должно показывать .../airdrop-farm

# Переустановите зависимости
pip install -r requirements.txt --upgrade
```

### Проблема: Permission denied
```bash
# Сделайте файлы исполняемыми
chmod +x main.py run.py
```

### Проблема: No tokens found
```bash
# Проверьте файл токенов
cat data/token.txt

# Убедитесь, что токены не пустые и валидные
```

### Проблема: Proxy connection failed
```bash
# Проверьте формат прокси в data/proxy.txt
# Или запустите без прокси:
python3 run.py --no-proxy
```

## 📝 Структура после установки

```
airdrop-farm/
├── src/                    # Исходный код
│   ├── core/              # Основные модули
│   ├── modules/           # Бизнес-логика
│   └── utils/             # Вспомогательные функции
├── data/                  # Данные
│   ├── token.txt         # Ваши токены
│   └── proxy.txt         # Прокси серверы
├── venv/                 # Виртуальное окружение (если создано)
├── main.py               # Основной файл запуска
├── run.py                # Расширенный запуск
├── config.json           # Конфигурация
└── requirements.txt      # Зависимости
```

## 🔄 Обновление

```bash
# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Обновление кода (если есть новая версия)
# Скопируйте новые файлы, сохранив data/ и config.json
```

## 🆘 Поддержка

- **Telegram Channel**: @NTExhaust
- **Issues**: Проверьте README.md для дополнительной информации

## ⚡ Оптимизация производительности

### Для больших объемов аккаунтов:
```bash
# Увеличьте timeout в config.json
"api": {
    "timeout": 120,  # увеличьте с 60 до 120
    "retries": 5     # увеличьте количество попыток
}
```

### Для стабильного соединения:
```bash
# Уменьшите delays в config.json
"delays": {
    "between_accounts": 3,  # уменьшите с 5 до 3
    "between_tasks": 1      # уменьшите с 2 до 1
}
```