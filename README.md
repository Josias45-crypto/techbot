# 🤖 TechBot — Sistema Inteligente de Soporte Técnico

Sistema de atención al cliente con NLP para resolución de consultas técnicas:
compatibilidad de piezas, instalación de drivers y diagnóstico de problemas.

## 🛠️ Stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, Alembic
- **NLP/IA:** spaCy, Transformers (HuggingFace), PyTorch, NLTK, Sentence-Transformers
- **Base de datos:** PostgreSQL + pgvector
- **Caché:** Redis
- **Seguridad:** JWT + bcrypt
- **Data:** Pandas, NumPy, SciPy, Matplotlib, Seaborn
- **Infraestructura:** Docker + docker-compose

## 🚀 Setup

### 1. Clonar el repositorio
```bash
git clone https://github.com/Josias45-crypto/techbot.git
cd techbot
```

### 2. Entorno virtual
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Base de datos
```bash
alembic upgrade head
```

### 5. Levantar servidor
```bash
uvicorn main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## 📁 Estructura
```
techbot/
├── backend/
│   ├── app/
│   │   ├── models/       # Modelos SQLAlchemy
│   │   ├── schemas/      # Esquemas Pydantic
│   │   ├── api/          # Endpoints FastAPI
│   │   ├── core/         # Config, seguridad, DB
│   │   ├── services/     # Lógica de negocio
│   │   ├── nlp/          # Motor NLP
│   │   └── utils/        # Utilidades
│   └── alembic/          # Migraciones
├── frontend/             # Widget React
├── database/             # Scripts SQL
├── scripts/              # Utilidades
└── docs/                 # Documentación
```

## 📦 Módulos
| Módulo | Estado |
|--------|--------|
| Base de datos (27 tablas) | ✅ Completo |
| Backend FastAPI | 🔜 En desarrollo |
| Motor NLP | 🔜 Pendiente |
| Frontend Widget | 🔜 Pendiente |
| Docker | 🔜 Pendiente |
