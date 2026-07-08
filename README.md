# M1-B2 — Squelette repo (Pyrenex Crédit scoring API)

> **Repo template GitHub.** Clique sur **« Use this template »** en haut à
> droite de cette page → **Create a new repository** → nomme-le
> `M1-B2-scoring-api-<prénom>` sur **ton** compte GitHub personnel.
> C'est ce nouveau repo que tu cloneras pour travailler.

---

## 🚀 Démarrage

```bash
# 0. Clone ton repo perso fraîchement créé
git clone git@github.com:<ton-user>/M1-B2-scoring-api-<prenom>.git
cd M1-B2-scoring-api-<prenom>

# 1. Environnement virtuel
python -m venv .venv && source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate                              # Windows

# 2. Dépendances
pip install -r requirements.txt
#    ▸ Option uv (si tu as suivi le setup avec uv) — un `uv venv` n'embarque
#      PAS pip, il faut donc `uv pip` :
# uv venv --python 3.11 && source .venv/bin/activate
# uv pip install -r requirements.txt

# 3. Copie ton modèle M1-B1 (cf. section « Modèle » ci-dessous) — le service
#    ne démarre PAS sans lui
cp ../M1-B1-scoring-<prenom>/models/pyrenex_risk_v2.joblib ./models/
cp ../M1-B1-scoring-<prenom>/models/pyrenex_risk_v2.json   ./models/

# 4. Vérification
uvicorn app.main:app --reload                          # → démarre sans erreur
```

Ensuite (autre terminal) :

```bash
curl http://localhost:8000/health                      # → 200
curl http://localhost:8000/info
pytest -v                                              # → tests "skipped" tant que les TODO
                                                       #   ne sont pas faits : c'est NORMAL au départ
```

> ℹ️ Sans le modèle dans `models/`, uvicorn refuse de démarrer (c'est voulu :
> une API de scoring sans modèle ne doit pas prétendre être en bonne santé)
> et `pytest` skippe les tests avec un message explicite. Si tu vois ça,
> retourne à l'étape 3.

---

## 📁 Structure du repo

```
M1-B2-scoring-api-<prenom>/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + lifespan + routes
│   ├── schemas.py               # Pydantic schemas (LoanApplication, Prediction)
│   └── middleware.py            # LoggingMiddleware Loguru
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # fixtures pytest (client + valid_payload)
│   ├── test_model_contract.py   # test 0 — valide le .joblib avant l'API
│   └── test_api.py              # tests routes /health, /info, /predict
├── models/                      # ton .joblib + .json depuis M1-B1
│   └── .gitkeep
├── logs/                        # logs rotatifs (gitignored)
│   └── .gitkeep
├── ressources/                  # 📚 mini-cours d'appui (lecture juste-à-temps)
│   ├── 01_FastAPI_Pydantic_ml_essentiel.md
│   ├── 02_Dockerfile_Python_essentiel.md
│   ├── 03_Pytest_TestClient_essentiel.md
│   ├── 04_Loguru_middleware_essentiel.md
│   ├── 05_Versionning_modele_essentiel.md
│   ├── liens_officiels.md
│   └── README.md                # ordre de mobilisation + objectifs
├── Dockerfile                   # à compléter (cf. ressources/02)
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md (ce fichier — à compléter avec schéma Mermaid + démarrage)
```

---

## 📚 Mini-cours d'appui

Les **5 mini-cours pédagogiques** du brief sont fournis dans
[`./ressources/`](./ressources/). Lecture juste-à-temps, ~15-20 min chacun :

| Tâche | Mini-cours |
|---|---|
| Routes FastAPI + Pydantic ML | [`01_FastAPI_Pydantic_ml_essentiel.md`](./ressources/01_FastAPI_Pydantic_ml_essentiel.md) |
| Dockerfile Python production | [`02_Dockerfile_Python_essentiel.md`](./ressources/02_Dockerfile_Python_essentiel.md) |
| Tests pytest + TestClient | [`03_Pytest_TestClient_essentiel.md`](./ressources/03_Pytest_TestClient_essentiel.md) |
| Loguru middleware structuré | [`04_Loguru_middleware_essentiel.md`](./ressources/04_Loguru_middleware_essentiel.md) |
| Versionning sémantique modèle | [`05_Versionning_modele_essentiel.md`](./ressources/05_Versionning_modele_essentiel.md) |

Cf. [`./ressources/README.md`](./ressources/README.md) pour l'ordre de mobilisation détaillé.

---

## 📥 Modèle (depuis M1-B1)

**Avant tout**, copie ton modèle M1-B1 :

```bash
cp ../M1-B1-scoring-<prenom>/models/pyrenex_risk_v2.joblib ./models/
cp ../M1-B1-scoring-<prenom>/models/pyrenex_risk_v2.json   ./models/
```

Le service ne démarre pas sans ces 2 fichiers.

---

## 🧭 Démarche attendue

### Mercredi après-midi — sync (2 h 15)

1. **Sanity check** : recharger le `.joblib` dans un script séparé (5 min)
2. **Squelette FastAPI** : `/health`, `/info`, `/predict` (1 h 15)
3. **Dockerfile minimal** : build + run + curl OK (30 min)
4. **Tour de table** Discord 16h30 : démo curl + discussion versionning (30 min)

### Async jeudi/vendredi (6 h)

5. **Contract test** d'abord (`test_model_contract.py`) puis **tests d'API**
   (≥ 3) en local **et** dans le container — **volume monté** en priorité
   (voie rapide), `Dockerfile.test` en option CI/CD (cf. mini-cours 03)
   (1 h 30)
6. **Loguru middleware** avec `request_id` + format JSON + rotation logs.
   ⚠️ **Aucune PII** dans les logs (cf. mini-cours 04) (45 min)
7. **README complet** + schéma Mermaid + tag `v0.1.0-api` (2 h)
8. **Finition** + préparation RDV vendredi (1 h 45)

Mini-cours d'appui : voir [`./ressources/`](./ressources/).

---

## ✅ Conventions de code

- Python 3.11+
- Type hints sur toutes les signatures publiques
- Pas de `print` — utiliser Loguru
- `pathlib.Path` pour les chemins (pas de `os.path`)
- Tests pytest **avec fixtures** (pas de boilerplate dupliqué)
- Loguru en **JSON** (`serialize=True`) sur fichier, coloré en console

---

## 🆘 Bloqué·e ?

1. **Swagger** : ouvre `http://localhost:8000/docs` — souvent le plus
   rapide pour débugger.
2. **Logs** : lis `logs/api.log` pour repérer les exceptions.
3. **Tests local d'abord, Docker ensuite** : si `pytest` est rouge en
   local, inutile de tester Docker — fix le code d'abord.
4. **`docker logs <container>`** : voir ce que le container raconte au
   démarrage.
5. Mini-cours dédiés dans [`./ressources/`](./ressources/).
