# 📝 Padrão de Commits — SOLVEON

> Baseado no padrão [Conventional Commits](https://www.conventionalcommits.org/)

---

## Estrutura
```
<tipo>(<escopo>): <descrição curta no imperativo>

- detalhe opcional 1
- detalhe opcional 2
```

---

## Tipos

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `refactor` | Refatoração sem alterar comportamento |
| `chore` | Manutenção, dependências, configurações |
| `docs` | Documentação |
| `style` | Formatação, sem mudança de lógica |
| `test` | Adição ou correção de testes |
| `perf` | Melhoria de performance |

---

## Escopos

| Escopo | Módulo |
|--------|--------|
| `auth` | Autenticação e login |
| `router` | Gerenciamento de roteadores |
| `hotspot` | Provisionamento de hotspot |
| `bypass-devices` | Dispositivos em bypass |
| `users` | Usuários do hotspot |
| `plans` | Planos e perfis |
| `tenant` | Multi-tenancy |
| `ssh` | Serviço SSH MikroTik |
| `db` | Models e migrations |
| `ui` | Templates e frontend |

---

## Regras

**Descrição sempre no imperativo, minúscula e sem ponto final.**

| | Exemplo |
|-|---------|
| ✅ | `adiciona`, `corrige`, `remove`, `atualiza`, `implementa` |
| ❌ | `adicionado`, `Adiciona`, `correção feita.` |

- O escopo é opcional, mas recomendado
- Os detalhes no corpo são opcionais — use quando houver múltiplas mudanças relevantes

---

## Exemplos
```bash
feat(bypass-devices): adiciona ativação e desativação de ip-binding via SSH

fix(ssh): corrige erro de conexão em RouterOS 6.x com algoritmos legados

refactor(hotspot): extrai lógica de rollback para método dedicado

chore(db): adiciona campos active e binding_type na tabela bypass_devices

feat(router): adiciona campo hotspot_name no model Router

fix(bypass-devices): corrige server=None ao registrar MAC no MikroTik

feat(ui): atualiza modal de edição de bypass com tipo e status
```