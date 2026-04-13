# Векторный индекс базы знаний для RAG-бота

## Использованная модель эмбеддингов
- **Название:** `intfloat/multilingual-e5-base`
- **Размерность вектора:** 768
- **Особенности:** мультиязычная, высокая точность поиска.

## База знаний
- **Источник:** вселенная Star Wars https://starwars.fandom.com/wiki/Main_Page
- **Документы:** 30 оригинальных документов с полной заменой терминов (персонажи, планеты, технологии, расы, события).
- **Словарь замен:** `terms_map.json` (более 78 замен).
- **Оригинальный текст:** `raw_texts/`
- **База знаний для RAG:** `knowledge_base/`

## Статистика индекса
- **Количество чанков:** 13251
- **Размер чанка:** 500 символов (с перекрытием 50 символов)
- **Среднее количество чанков на документ:** ~441

## Время генерации
- **Общее время генерации индекса:** 1207 секунд
- **Генерация эмбеддингов:** 1176 секунд (CPU Ryzen 5)

## Запуск
```bash
# Создание индекса
py build_index.py

# Выполнение тестовых поисковых запросов
py query_index.py

```

## Результаты тестовых поисковых запросов
```
============================================================
Запрос: Кто такой Xarn Velgor и какая у него роль?
============================================================

--- Результат 1 (расстояние = 0.2781) ---
Источник: Anakin_Skywalker, чанк 2004/2217
Текст:
thumb|left|230px|Xarn Velgor was the dreaded enforcer of his Nyxian Cabal Master and the galaxy-wide empire they forged....


--- Результат 2 (расстояние = 0.3078) ---
Источник: Anakin_Skywalker, чанк 2025/2217
Текст:
thumb|right|280px|Xarn Velgor was a warrior of hatred who carried out a campaign of terror and death....
```

```
============================================================
Запрос: Что такое Void Core и для чего он использовался?
============================================================

--- Результат 1 (расстояние = 0.3115) ---
Источник: Death_Star, чанк 1/19
Текст:
A '''Void Core''' was a gargantuan space station armed with a planet-destroying superlaser powered by kyber crystals created by Grand Moff Wilhuff Tarkin.

==Death Stars==
===DS-1 Battle Station===...

--- Результат 2 (расстояние = 0.3315) ---
Источник: Galactic_Empire, чанк 309/1035
Текст:
=====Reveal of the Void Core=====...
```

```
============================================================
Запрос: Опиши планету Dusthal и её особенности.
============================================================

--- Результат 1 (расстояние = 0.2966) ---
Источник: Ben_Solo, чанк 403/926
Текст:
=====The sands of Dusthal=====...

--- Результат 2 (расстояние = 0.2983) ---
Источник: Tatooine, чанк 1/124
Текст:
'''Dusthal''' was a sparsely inhabited circumbinary desert planet located in the galaxy's Outer Rim Territories. Part of a binary star system, the planet orbited two scorching suns, resulting in the world lacking the necessary surface water to sustain large populations. As a result, many residents of the planet instead drew water from the atmosphere via moisture farms. The planet also had little surface vegetation. It was the homeworld to the native Jawa and Tusken Raider species and of Anakin...

```