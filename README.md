<p align="center">
  <img src="./assets/banner.svg" alt="Ligreus — student developer, learning in public" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/student-learning%20in%20public-0b0e12?style=flat-square&labelColor=000000" alt="student">
  <img src="https://img.shields.io/badge/focus-web%20apps%20%C2%B7%20ai%20tooling-0b0e12?style=flat-square&labelColor=000000" alt="focus">
  <a href="https://github.com/logreus-cloud?tab=repositories"><img src="https://img.shields.io/badge/all%20repos-%E2%86%92-0b0e12?style=flat-square&labelColor=000000" alt="all repos"></a>
</p>

---

### About

<img align="right" width="200" src="./assets/loop.gif" alt="Looping black-and-white anime-style portrait">

I'm a student learning to build software by shipping it. Most of what you see here started as a
weekend idea, a practice task, or a hackathon prototype — small web apps, AI-assisted tools, and
experiments that taught me something even when they didn't survive.

My rule of thumb: **deploy first, get clever later.** A working public URL on day one beats a
perfect codebase nobody can open.

### What I'm working on

- Building small web apps with **Flask** and **Express**, deployed on **Render** and **Cloudflare Pages**
- Learning where an LLM genuinely helps — and where plain deterministic rules do the job better
- Writing the core parts myself instead of configuring them: a BM25 search engine, a Markdown → DOCX pipeline
- Preparing for hackathons: a reusable project template, deploy in under an hour, a demo that holds up

### Tech Stack

**Languages**

<img src="https://skillicons.dev/icons?i=py,js,html,css&theme=dark" alt="Python, JavaScript, HTML, CSS">

**Web**

<img src="https://skillicons.dev/icons?i=flask,fastapi,express,nodejs,nextjs,astro&theme=dark" alt="Flask, FastAPI, Express, Node.js, Next.js, Astro">

**Data & deploy**

<img src="https://skillicons.dev/icons?i=sqlite,docker,cloudflare&theme=dark" alt="SQLite, Docker, Cloudflare"> <img src="./assets/render.svg" height="48" alt="Render">

**Tooling**

<img src="https://skillicons.dev/icons?i=git,github,vscode,powershell&theme=dark" alt="Git, GitHub, VS Code, PowerShell">

### Projects

Only what actually runs — the rest is private or too rough to show.

| Project | What it is | Stack | State |
| --- | --- | --- | --- |
| [notabene](https://github.com/logreus-cloud/notabene) | Full-text search over your own notes from the terminal or a browser tab. BM25 ranking written by hand, Russian and English stemming, phrase search — one SQLite file, zero runtime dependencies | Python · SQLite | CI · works |
| [labgen](https://github.com/logreus-cloud/labgen) | Write a lab report in Markdown, get a DOCX formatted to GOST 7.32-2017: numbered figures and tables, table of contents, no Word needed | Python | CI · works |
| [triage-mvp](https://github.com/logreus-cloud/triage-mvp) | Patient pre-visit survey: seven questions become a structured card for the doctor with an urgency category and red-flag rules | Next.js · Express · FastAPI | [live](https://triage-web-eaj2.onrender.com/) |
| [analog-prep](https://github.com/logreus-cloud/analog-prep) | Drug analogue lookup: finds interchangeable medicines by the name on the box, compares the price of a full course, and refuses the swap when the rules say it is unsafe | Node · Express | hackathon build · demo mode |
| [genshinflex](https://github.com/logreus-cloud/genshinflex) | Open Genshin Impact guide: builds, teams, character database, pull tracker and an Abyss team checker for the current rotation | Astro · Cloudflare Pages | in progress |
| [HealthTrackerFlask](https://github.com/logreus-cloud/HealthTrackerFlask) | Health tracking app: entries, charts, a Flask backend behind a plain JS frontend | Flask · JS | runs locally |
| [EnergyMind-AI](https://github.com/logreus-cloud/EnergyMind-AI) | AI-assisted energy app — split frontend/backend with a shared API contract and Docker Compose | JavaScript · Docker | in progress |

### Learning next

`testing` · `databases beyond SQLite` · `CI that actually runs` · `reading other people's code`

<details>
<summary><b>По-русски</b></summary>

### О себе

Студент. Учусь разрабатывать, разрабатывая: почти всё здесь начиналось как идея на выходные,
учебная задача или прототип с хакатона — небольшие веб-приложения, инструменты с ИИ и
эксперименты, которые чему-то научили, даже если не выжили.

Принцип простой: **сначала деплой, потом красота.** Рабочая публичная ссылка в первый день
полезнее идеального кода, который никто не может открыть.

### Чем занят сейчас

- Собираю небольшие веб-приложения на **Flask** и **Express**, деплою на **Render** и **Cloudflare Pages**
- Разбираюсь, где языковая модель действительно помогает, а где обычные детерминированные правила работают лучше
- Пишу ключевые части сам, а не настраиваю готовые: поисковый движок на BM25, конвейер Markdown → DOCX
- Готовлюсь к хакатонам: переиспользуемый шаблон проекта, деплой меньше чем за час, демо, которое не разваливается

### Стек

**Языки**

<img src="https://skillicons.dev/icons?i=py,js,html,css&theme=dark" alt="Python, JavaScript, HTML, CSS">

**Веб**

<img src="https://skillicons.dev/icons?i=flask,fastapi,express,nodejs,nextjs,astro&theme=dark" alt="Flask, FastAPI, Express, Node.js, Next.js, Astro">

**Данные и деплой**

<img src="https://skillicons.dev/icons?i=sqlite,docker,cloudflare&theme=dark" alt="SQLite, Docker, Cloudflare"> <img src="./assets/render.svg" height="48" alt="Render">

**Инструменты**

<img src="https://skillicons.dev/icons?i=git,github,vscode,powershell&theme=dark" alt="Git, GitHub, VS Code, PowerShell">

### Проекты

Здесь только то, что действительно работает — остальное приватно или слишком сырое.

| Проект | Что это | Стек | Состояние |
| --- | --- | --- | --- |
| [notabene](https://github.com/logreus-cloud/notabene) | Полнотекстовый поиск по своим заметкам из терминала или вкладки браузера. Ранжирование BM25 написано вручную, стемминг для русского и английского, поиск по фразе — один файл SQLite и ноль зависимостей | Python · SQLite | CI · работает |
| [labgen](https://github.com/logreus-cloud/labgen) | Пишешь отчёт по лабе в Markdown — получаешь DOCX по ГОСТ 7.32-2017: нумерация рисунков и таблиц, содержание, Word не нужен | Python | CI · работает |
| [triage-mvp](https://github.com/logreus-cloud/triage-mvp) | Предварительный опрос пациента: семь вопросов превращаются в карточку для врача с категорией срочности и правилами тревожных признаков | Next.js · Express · FastAPI | [живая ссылка](https://triage-web-eaj2.onrender.com/) |
| [analog-prep](https://github.com/logreus-cloud/analog-prep) | Поиск аналогов лекарств: по названию с упаковки находит взаимозаменяемые препараты, считает цену за курс и запрещает замену там, где правила считают её опасной | Node · Express | хакатон · демо-режим |
| [genshinflex](https://github.com/logreus-cloud/genshinflex) | Открытый справочник по Genshin Impact: билды, команды, база персонажей, трекер круток и проверка команды для Бездны под текущую ротацию | Astro · Cloudflare Pages | в работе |
| [HealthTrackerFlask](https://github.com/logreus-cloud/HealthTrackerFlask) | Трекер здоровья: записи, графики, бэкенд на Flask и фронтенд на чистом JS | Flask · JS | работает локально |
| [EnergyMind-AI](https://github.com/logreus-cloud/EnergyMind-AI) | Приложение с ИИ вокруг энергетики: раздельные фронт и бэк, общий контракт API, Docker Compose | JavaScript · Docker | в работе |

### Что учу дальше

`тесты` · `базы данных сложнее SQLite` · `CI, который реально запускается` · `чтение чужого кода`

</details>

<p align="center">
  <sub>Always mid-project — say hi if anything here is useful to you</sub>
</p>
