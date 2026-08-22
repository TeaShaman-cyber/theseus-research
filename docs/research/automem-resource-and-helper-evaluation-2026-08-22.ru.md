# Исследование ресурсов и вспомогательных моделей AutoMem

**Статус:** исследовательская заметка · агрегированные результаты опубликованы для открытого ревью
**Дата:** 2026-08-22
**Языки:** [English — международный референсный текст](automem-resource-and-helper-evaluation-2026-08-22.md) · Русский
**Область:** уменьшение локальных ресурсов AutoMem и ограниченное обогащение памяти вспомогательной моделью
**Связанная программа:** [контракт Theseus](../../README.ru.md) · [Садхана инженерии](../methodology.ru.md)

## Краткое содержание

В этой заметке описан ограниченный эксперимент Theseus с двумя целями:

1. уменьшить локальную ресурсную нагрузку семантической памяти AutoMem;
2. сделать сохранённые воспоминания полезнее для основных агентов через
   вспомогательную модель, не выдавая ей самостоятельные права записи и
   управления инфраструктурой.

Локальный результат использует FastEmbed BGE-base размерности 768 вместо
BGE-large размерности 1024. В проверенном replay качество поиска не просело,
а потребление памяти API заметно уменьшилось. Для первого эксплуатационного
helper выбран Solar Pro4: Laguna S получила более высокую оценку на небольшом
размеченном семантическом наборе, но Solar оказался надёжнее на реальном
JSON-протоколе AutoMem.

Это ограниченные доказательства, а не универсальный рейтинг моделей и не
утверждение, что AutoMem заменил активный маршрут памяти Hermes/Hindsight.

## Граница исследования

Маршруты намеренно разделялись:

```text
активный маршрут памяти Hermes: Hindsight
локальный экспериментальный профиль: AutoMem / путь Codex
облачная среда проверки: временный Timeweb lab
```

Рабочий банк Hindsight не использовался как тестовый корпус. В публикацию не
входят реальные пользовательские memories, credentials, provider payloads или
backup-архивы.

## Метод

Работа проходила по этапам:

1. зафиксировать локальный baseline BGE-large;
2. сравнить BGE-large и BGE-base на изолированной копии с фиксированными
   запросами;
3. отдельно проверить внешние embedding endpoints;
4. сравнить helper-кандидатов на протокольном и размеченном семантическом
   наборах;
5. реализовать включаемый advisory-контур для summary, tags и entities;
6. проверить его во временном cloud worker, а затем одним локальным live
   canary;
7. сохранить rollback и проверить read-back/delete postconditions.

Публичный manifest агрегированного fixture находится в
[`automem-resource-and-helper-evaluation-fixture-2026-08-22.json`](automem-resource-and-helper-evaluation-fixture-2026-08-22.json).
Исходный рабочий fixture не публикуется: в нём есть текст, связанный с
конкретным рабочим процессом. Нейтральный публичный повтор — отдельная задача.

## Результаты по embeddings

Удалённое сравнение на одном хосте использовало один граф и фиксированный
replay из 100 запросов:

| Вариант | Recall@10 | MRR | NDCG@10 | RAM API | Средняя задержка | p95 |
|---|---:|---:|---:|---:|---:|---:|
| BGE-large / 1024d | 0.9100 | 0.7825 | 0.8130 | 2.57 GiB | 682.9 ms | 831.1 ms |
| BGE-base / 768d | 0.9200 | 0.7823 | 0.8152 | 979.6 MiB | 788.7 ms | 927.2 ms |

Повторный replay BGE-base воспроизвёл те же метрики качества. Это хороший
компромисс ресурсов и качества: BGE-base сэкономил около 62% памяти API и
оказался несколько медленнее в этом тесте. Это не доказательство победы на
любом корпусе.

При локальном cutover была создана отдельная коллекция `memories_base`, граф
был переобучен, а исходная коллекция 1024d и backup-архивы сохранены. Health
показывает отфильтрованный видимый счётчик; прямое сравнение ID графа и
векторов дало 401/401 без сиротских ID. Локальный runtime использует 768d и
остаётся healthy.

## Результаты по helper-моделям

### Протокол и семантическое качество — разные вопросы

Ранний размеченный набор из 14 кейсов дал 100% и Solar, и Laguna S. Он был
намеренно простым и заменён более широким набором из 21 кейса:

| Модель | Valid JSON | Верные типы | Accuracy | Средняя задержка | p95 |
|---|---:|---:|---:|---:|---:|
| Laguna S | 21/21 | 17/21 | **81.0%** | 3.00 s | 4.97 s |
| Solar Pro4 | 21/21 | 15/21 | 71.4% | 3.59 s | 5.69 s |
| Hy3 | 21/21 | 13/21 | 61.9% | 3.82 s | 5.85 s |

Все вызовы вернули валидный JSON. В этом ограниченном семантическом fixture
победила Laguna S.

Реальный dry-run AutoMem дал другую операционную картину:

```text
Solar Pro4, 128 tokens:  10/10, parser errors 0
Laguna S, 256 tokens:    10/10, parser errors 1
Laguna S, 512 tokens:    10/10, parser errors 1
```

Поэтому для первого эксплуатационного helper выбран Solar Pro4. Это не
утверждение, что Solar умнее семантически; это выбор в пользу надёжности
протокола памяти, где malformed output не должен незаметно стать обычным
типом памяти.

### Advisory-обогащение

Helper получает текст memory и возвращает структурированные предложения:

```text
summary;
нормализованные tags;
заземлённые entities: tools, projects, people, concepts, organizations.
```

AutoMem проверяет JSON, требует присутствия entity в исходном тексте,
исправляет конфликтующие категории и сам применяет принятый результат. При
сбое провайдера или невалидном JSON сохраняется rule-based путь. Helper не
может напрямую писать в FalkorDB/Qdrant, репозитории или инфраструктуру.

В cloud A/B на одном тексте rules-only поместил `Laguna S` и `Timeweb Lab` в
`people`. Helper-assisted путь исправил их на `tools` и `projects`, удалил
ошибочные записи `people`, сохранил `AutoMem` как организацию и создал более
короткое summary с сохранённой неопределённостью.

Десятикейсовый cloud canary дал:

```text
обработано:             10/10
helper metadata:        10/10
summary:                10/10
ошибки:                  0
точечная очистка:       10/10
```

Локальный профиль явно включает тот же advisory-контур:

```text
ENRICHMENT_LLM_ENABLED=true
ENRICHMENT_LLM_MODEL=upstage/solar-pro4:free
ENRICHMENT_LLM_MAX_TOKENS=256
```

Один локальный live canary прошёл enrichment, read-back и удаление по точному
ID (`HTTP 200`, затем `HTTP 404`). Focused regression subset дал
`210 passed, 1 skipped, 0 failed`.

## Внешние embedding routes

Отдельно от локального cutover были проверены внешние пути:

```text
семейство Voyage-4:
  live 1024d; первые 200M токенов аккаунта бесплатны, но не навсегда.

OpenRouter LFM:
  live 1024d free route; лимиты зависят от аккаунта и модели.

BotHub bge-m3:
  live 1024d; бесплатный тариф не подтверждён.

Groq и Nous embeddings:
  рабочий маршрут с проверенными credentials не получен.

Ollama:
  нативный путь AutoMem, но Ollama не был установлен/запущен.

Hugging Face / Cloudflare / Google / Jina:
  адаптеры либо квоты/региональные условия остались нерешёнными.
```

Одинаковая размерность не делает embedding-пространства взаимозаменяемыми.
Любой внешний switch требует полного isolated re-embed и нового сравнения
recall.

## Инженерные уроки

- Жёсткий бюджет классификации 50 tokens слишком мал для многих
  reasoning/free-моделей. Бюджеты классификации и enrichment разделены.
- VLESS HAPP subscription не является HTTP proxy URL. Обратимый cloud-маршрут:
  subscription → VLESS profile → временный sing-box → private Docker network.
- Доступность провайдера, JSON-совместимость и semantic quality нужно измерять
  раздельно.
- Backup, отдельная vector collection, прямое сравнение ID и read-back важнее
  одного успешного health check контейнера.
- Helper должен советовать и структурировать, а родительский сервис сохраняет
  право принять, отклонить или позже исправить результат.

## Связанные работы и благодарности upstream

Работа опиралась на публичные документацию, исходный код и обсуждения AutoMem
и Hindsight. Это prior art, а не endorsement Theseus и не утверждение, что
мейнтейнеры участвовали в нашем эксперименте:

- AutoMem custom OpenAI-compatible base URL:
  [verygoodplugins/automem#96](https://github.com/verygoodplugins/automem/issues/96)
- AutoMem summary-first recall:
  [verygoodplugins/automem#180](https://github.com/verygoodplugins/automem/issues/180)
- предложение circuit breaker для quota enrichment:
  [verygoodplugins/automem#222](https://github.com/verygoodplugins/automem/issues/222)
- model-specific `max_tokens` в Hindsight:
  [vectorize-io/hindsight#978](https://github.com/vectorize-io/hindsight/issues/978)
- structured output и malformed JSON в Hindsight:
  [#1002](https://github.com/vectorize-io/hindsight/issues/1002),
  [#2668](https://github.com/vectorize-io/hindsight/issues/2668),
  [#3683](https://github.com/vectorize-io/hindsight/issues/3683)
- native multi-LLM implementation Hindsight:
  [`multi_llm.py`](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/engine/multi_llm.py)
- upstream AutoMem configuration and implementation:
  [`docs/ENVIRONMENT_VARIABLES.md`](https://github.com/verygoodplugins/automem/blob/main/docs/ENVIRONMENT_VARIABLES.md),
  [`automem/config.py`](https://github.com/verygoodplugins/automem/blob/main/automem/config.py)

## Ограничения и дальнейшая работа

Исследование не устанавливает универсально лучшую helper-модель, постоянный
бесплатный provider или переключение memory provider Hermes. Query rewriting и
отдельный reranker не реализованы. Cloud VPS и HAPP-маршрут были временной
исследовательской инфраструктурой. Для будущего публичного повтора нужен
нейтральный fixture, полный текст которого можно публиковать без раскрытия
рабочего или личного контекста.

## Данные и ревью

Опубликованы только агрегированные метрики, synthetic examples, публичные
ссылки upstream и очищенное описание метода. API keys, HAPP subscription,
raw private memory, backup-архивы и полный transcript сессии не включены.
Отзывы приветствуются по методике, границам доказательств,
воспроизводимости и ограничениям.
