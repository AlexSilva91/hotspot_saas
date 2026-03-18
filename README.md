<div align="center">

# 🌐 Hotspot SaaS
### Plataforma Multi-Tenant para Gerenciamento de Hotspots MikroTik

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-AGPL_v3-blue?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)

*Sistema SaaS multi-tenant para gerenciamento centralizado de hotspots MikroTik RouterOS*

</div>

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias](#-tecnologias)
- [Banco de Dados](#-banco-de-dados)
- [Multi-Tenant](#-sistema-multi-tenant)
- [Sistema de Planos](#-sistema-de-planos)
- [Segurança](#-segurança)
- [API REST](#-api-rest)
- [Integração MikroTik](#-integração-mikrotik)
- [Funcionalidades](#-funcionalidades)
- [Instalação](#-instalação)
- [Roadmap](#-roadmap)
- [Licença](#-licença)
- [Autor](#-autor)

---

## 🎯 Visão Geral

O **Hotspot SaaS** é uma plataforma que centraliza a administração de hotspots baseados em **MikroTik RouterOS**, permitindo que **múltiplas empresas gerenciem seus hotspots em um único sistema**, com **isolamento total de dados**, **controle de planos** e **automação de configurações do RouterOS**.

### O que o sistema oferece:

| Recurso | Descrição |
|---|---|
| 🔀 Gerenciamento remoto | Controle de múltiplos roteadores MikroTik |
| 👥 Controle de usuários | Administração de hotspots remotamente |
| 🔥 Firewall automatizado | Configuração automática de regras e NAT |
| 📦 Planos flexíveis | Definição de limites por plano de uso |
| 🎨 Personalização | Customização de páginas de login |
| 🔐 Autenticação | Controle centralizado de acesso |

---

## 🏗 Arquitetura

O sistema segue uma separação clara de responsabilidades em camadas:

```
Request (HTTP)
      ↓
  Routes  ──────────── Ponto de entrada das requisições
      ↓
 Services ──────────── Regras de negócio
      ↓
Repositories ────────── Acesso ao banco de dados
      ↓
  Models  ──────────── Entidades SQLAlchemy
      ↓
 Database ──────────── PostgreSQL
```

---

## 📁 Estrutura do Projeto

```
hotspot_saas
├── app
│   ├── cli
│   │   ├── __init__.py
│   │   └── user_cli.py
│   ├── controller
│   │   ├── __init__.py
│   │   └── base_controller.py
│   ├── decorators
│   │   ├── __init__.py
│   │   ├── login_required.py
│   │   └── plan_limit.py
│   ├── integrations
│   │   ├── __init__.py
│   │   └── mikrotik_api.py
│   ├── middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── routes_error_handlers_middleware.py
│   │   └── tenant_middleware.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── active_session.py
│   │   ├── bypass_device.py
│   │   ├── hotspot_template.py
│   │   ├── hotspot_user.py
│   │   ├── ip_pool.py
│   │   ├── plan.py
│   │   ├── router.py
│   │   ├── tenant.py
│   │   └── user.py
│   ├── repositories
│   │   ├── __init__.py
│   │   ├── active_session_repository.py
│   │   ├── base_repository.py
│   │   ├── bypass_device_repository.py
│   │   ├── hotspot_template_repository.py
│   │   ├── hotspot_user_repository.py
│   │   ├── ip_pool_repository.py
│   │   ├── plan_repository.py
│   │   ├── router_repository.py
│   │   ├── tenant_repository.py
│   │   └── user_repository.py
│   ├── routes
│   │   ├── __init__.py
│   │   ├── active_session_routes.py
│   │   ├── auth_routes.py
│   │   ├── bypass_device_routes.py
│   │   ├── dashboard_routes.py
│   │   ├── error_test_routes.py
│   │   ├── hotspot_template_routes.py
│   │   ├── hotspot_user_routes.py
│   │   ├── ip_pool_routes.py
│   │   ├── plan_routes.py
│   │   ├── router_routes.py
│   │   ├── tenant_routes.py
│   │   └── user_routes.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── active_session_service.py
│   │   ├── auth_service.py
│   │   ├── base_service.py
│   │   ├── bypass_device_service.py
│   │   ├── hotspot_template_service.py
│   │   ├── hotspot_user_service.py
│   │   ├── ip_pool_service.py
│   │   ├── plan_service.py
│   │   ├── router_service.py
│   │   ├── tenant_service.py
│   │   └── user_service.py
│   ├── static
│   │   ├── assets
│   │   │   ├── logo_solveon.png
│   │   │   ├── logo_solveon_2.png
│   │   │   └── logo_solveon_3.png
│   │   ├── css
│   │   │   ├── dashboard.css
│   │   │   ├── error_pages.css
│   │   │   ├── style.css
│   │   │   └── style_login.css
│   │   └── js
│   │       └── login.js
│   ├── templates
│   │   ├── auth
│   │   │   └── login.html
│   │   ├── bypass_devices
│   │   │   └── list.html
│   │   ├── components
│   │   │   ├── bypass_devices
│   │   │   │   ├── create_bypass_device_modal.html
│   │   │   │   └── edit_bypass_device_modal.html
│   │   │   ├── hotspot_templates
│   │   │   │   ├── create_template_modal.html
│   │   │   │   └── edit_template_modal.html
│   │   │   ├── hotspot_users
│   │   │   │   ├── create_hotspot_user_modal.html
│   │   │   │   └── edit_hotspot_user_modal.html
│   │   │   ├── ip_pools
│   │   │   │   ├── create_pool_modal.html
│   │   │   │   └── edit_pool_modal.html
│   │   │   ├── plans
│   │   │   │   ├── create_plan_modal.html
│   │   │   │   └── edit_plan_modal.html
│   │   │   ├── routers
│   │   │   │   ├── create_router_modal.html
│   │   │   │   ├── details_router_modal.html
│   │   │   │   └── edit_router_modal.html
│   │   │   ├── tenants
│   │   │   │   ├── create_tenant_modal.html
│   │   │   │   ├── details_tenant_modal.html
│   │   │   │   └── edit_tenant_modal.html
│   │   │   ├── users
│   │   │   │   ├── create_user_modal.html
│   │   │   │   └── edit_user_modal.html
│   │   │   └── flash_messages.html
│   │   ├── dashboard
│   │   │   └── index.html
│   │   ├── errors
│   │   │   ├── 400.html
│   │   │   ├── 401.html
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   ├── 405.html
│   │   │   ├── 500.html
│   │   │   └── generic.html
│   │   ├── hotspot_templates
│   │   │   └── list.html
│   │   ├── hotspot_users
│   │   │   └── list.html
│   │   ├── ip_pools
│   │   │   └── list.html
│   │   ├── plans
│   │   │   └── list.html
│   │   ├── routers
│   │   │   └── list.html
│   │   ├── tenants
│   │   │   └── list.html
│   │   ├── users
│   │   │   └── list.html
│   │   └── base.html
│   ├── utils
│   │   ├── __init__.py
│   │   ├── error_handlers.py
│   │   ├── filters.py
│   │   └── logger.py
│   ├── __init__.py
│   ├── config.py
│   └── extensions.py
├── logs
├── .gitignore
├── README.md
├── requirements.txt
├── run.py
└── secret.py
```

---

## 🛠 Tecnologias

### Backend
| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.12 | Linguagem principal |
| Flask | 2.x | Framework web |
| SQLAlchemy | — | ORM |
| Alembic | — | Migrações de banco |
| PyJWT | — | Autenticação JWT |

### Banco de Dados
| Tecnologia | Uso |
|---|---|
| PostgreSQL | Banco de dados principal |

### Infraestrutura
| Tecnologia | Status |
|---|---|
| Docker | 🔜 Planejado |
| Nginx | 🔜 Planejado |
| Gunicorn | 🔜 Planejado |

### Integração
| Tecnologia | Uso |
|---|---|
| MikroTik RouterOS API | Comunicação com roteadores |

---

## 🗄 Banco de Dados

### Diagrama de Entidades

```
┌─────────────┐       ┌─────────────┐
│    Plan     │       │   Tenant    │
├─────────────┤       ├─────────────┤
│ id          │◄──────│ id          │
│ name        │       │ name        │
│ max_routers │       │ plan_id     │
│ max_users   │       │ created_at  │
└─────────────┘       └──────┬──────┘
                             │
              ┌──────────────┴───────────────┐
              │                              │
       ┌──────▼──────┐                ┌──────▼──────┐
       │   Router    │                │    User     │
       ├─────────────┤                ├─────────────┤
       │ id          │                │ id          │
       │ tenant_id   │                │ tenant_id   │
       │ name        │                │ email       │
       │ ip_address  │                │ password_h  │
       │ username    │                │ role        │
       │ password    │                └─────────────┘
       └─────────────┘
```

---

## 🏢 Sistema Multi-Tenant

Cada registro do sistema possui relação direta com um `tenant_id`, garantindo isolamento completo entre empresas.

```python
# Todas as queries são automaticamente filtradas por tenant
Router.query.filter_by(tenant_id=current_tenant.id).all()
```

**Benefícios:**

- 🔒 **Isolamento de dados** — empresas não acessam dados umas das outras
- 🛡 **Segurança** — queries sempre filtradas por `tenant_id`
- 📈 **Escalabilidade** — estrutura pronta para crescer

```
Empresa A  →  Routers A  →  Usuários A
Empresa B  →  Routers B  →  Usuários B
```

---

## 📦 Sistema de Planos

Cada empresa possui um plano associado que define seus limites de uso. O middleware aplica os controles automaticamente.

| Plano | Routers | Usuários |
|---|:---:|:---:|
| 🟢 **Starter** | 2 | 200 |
| 🔵 **Pro** | 10 | 1.000 |
| 🟣 **Enterprise** | ∞ | ∞ |

**Controle de limites em tempo real:**

```python
# Middleware bloqueia automaticamente ao atingir o limite
# Plano Starter: max_routers = 2
# Tentativa de adicionar 3º router → 403 Forbidden
```

---

## 🔐 Segurança

### Autenticação JWT

```
POST /login
    ↓
Validação de credenciais
    ↓
Geração do token JWT
    ↓
Token enviado nas requisições
```

**Header esperado em todas as requisições protegidas:**

```http
Authorization: Bearer <TOKEN>
```

### Isolamento de Tenants

Todas as queries filtram automaticamente pelo `tenant_id`, impedindo que uma empresa acesse dados de outra.

### Controle de Planos

O middleware de planos intercepta requisições e bloqueia operações que excedam os limites contratados.

---

## 🌐 API REST

### Autenticação
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/login` | Autenticar e obter token JWT |

### Planos
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/plans` | Criar novo plano |
| `GET` | `/plans` | Listar planos disponíveis |

### Tenants
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/tenants` | Cadastrar empresa |
| `GET` | `/tenants` | Listar empresas |

### Roteadores
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/routers` | Adicionar roteador |
| `GET` | `/routers` | Listar roteadores |

### Usuários
| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/users` | Criar usuário |
| `GET` | `/users` | Listar usuários |

---

## 📡 Integração MikroTik

A plataforma se conecta diretamente ao **RouterOS via API** para automação completa.

**Funções planejadas:**

- [ ] Criar e configurar hotspot
- [ ] Gerenciar usuários hotspot
- [ ] Controlar sessões ativas
- [ ] Liberar MAC bypass
- [ ] Aplicar regras de firewall
- [ ] Configurar NAT automaticamente
- [ ] Personalizar templates de hotspot

---

## ✅ Funcionalidades

### Implementadas
- [x] Arquitetura SaaS multi-tenant
- [x] Separação por camadas (routes / services / repositories)
- [x] Modelos de dados principais
- [x] Sistema de planos com limites
- [x] Controle de recursos por plano
- [x] Autenticação JWT
- [x] Isolamento de tenants
- [x] Estrutura inicial da API REST
- [x] Integração inicial com MikroTik

### Em Desenvolvimento
- [ ] Gerenciamento completo de routers
- [ ] Integração avançada com RouterOS
- [ ] Gerenciamento de usuários hotspot
- [ ] Controle de sessões ativas
- [ ] Criação automática de firewall rules
- [ ] Configuração automática de NAT
- [ ] Personalização de templates hotspot

### Planejadas
- [ ] **Painel Administrativo** — dashboard, estatísticas, controle de planos
- [ ] **Gestão de Hotspot** — captive portal customizado, limite de banda e tempo
- [ ] **Monitoramento** — dispositivos conectados, logs, alertas
- [ ] **Sistema de Billing** — assinaturas, cobrança recorrente, gateway de pagamento

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.12+
- PostgreSQL
- pip

### Passo a Passo

**1. Clone o repositório**
```bash
git clone git@github.com:AlexSilva91/hotspot_saas.git
cd hotspot_saas
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql://user:password@localhost/hotspot
SECRET_KEY=supersecretkey
```

**5. Execute as migrações**
```bash
flask db upgrade
```

**6. Inicie o servidor**
```bash
python run.py
```

---

## 🌿 Branches e Fluxo de Trabalho

```
main  ──────────────────────── produção estável
  └── dev  ─────────────────── desenvolvimento ativo
        ├── feat/nova-feature ─ novas funcionalidades
        └── fix/correcao ────── correções de bugs
```

---

## 🗺 Roadmap

```
[✅] Fase 1 — Finalizar API base
[🔄] Fase 2 — Integração completa MikroTik
[🔜] Fase 3 — Interface web (painel administrativo)
[🔜] Fase 4 — Sistema de billing
[🔜] Fase 5 — Deploy cloud
[🔜] Fase 6 — Escalabilidade multi-região
```

---

## 📄 Licença

Este projeto está licenciado sob a **GNU Affero General Public License v3.0 (AGPL-3.0)**.

Isso garante que qualquer modificação distribuída — ou utilizada como serviço — mantenha o código-fonte aberto e acessível.

Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

<div align="center">

**Alex Silva**  
Analista de Sistemas

[![GitHub](https://img.shields.io/badge/GitHub-AlexSilva91-181717?style=for-the-badge&logo=github)](https://github.com/AlexSilva91)

</div>

---

<div align="center">
  <sub>Feito com ☕ e muita dedicação.</sub>
</div>