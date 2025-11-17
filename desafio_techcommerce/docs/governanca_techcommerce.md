---
# **Governança de Dados — TechCommerce**

Documento oficial que estabelece papéis, responsabilidades, políticas de qualidade e padrões de dados para a TechCommerce. Este documento tem caráter normativo para todas as áreas envolvidas no ciclo de vida dos dados (negócio, produtos, engenharia e operações).

---

## **Organograma de Dados**

Para cada domínio de dados, a TechCommerce define papéis com responsabilidades claras. Abaixo estão as atribuições iniciais (nomes fictícios) para operacionalizar a governança.

| Domínio | Data Owner (Estratégico) | Data Steward (Tático) | Data Custodian (Técnico) |
| :------ | :----------------------: | :-------------------: | :----------------------: |
| Clientes | Carlos Mendes (Head Comercial) | Ana Oliveira (CRM Lead) | Roberto Lima (Eng. de Dados) |
| Produtos | Mariana Silva (Head de Produto) | Felipe Souza (Gerente de Categoria) | Lucas Pereira (Eng. de Dados) |
| Vendas | Juliana Costa (Head de Operações) | Beatriz Almeida (Analista de Vendas Sr.) | Marco Ribeiro (Eng. de Dados) |
| Logística | Ricardo Gomes (Head de Logística) | Paula Ferreira (Coordenadora de Entregas) | Eduardo Nascimento (Eng. de Dados) |

### Responsabilidades (práticas)
- **Data Owner**:
	- Define políticas e SLAs de negócio para o domínio.
	- Aprova regras de qualidade, retenção e compartilhamento.
	- Atua como ponto de escalonamento para incidentes críticos.
	- Prioriza recursos e aprova exceções justificadas.
- **Data Steward**:
	- Define glossário, dicionário de dados e regras de transformação.
	- Monitora métricas de qualidade e conduz ações corretivas.
	- Coordena com times de produto e atendimento para reconciliação de dados.
	- Garante que as Expectation Suites (Great Expectations) reflitam regras de negócio.
- **Data Custodian**:
	- Implementa pipelines, storage, backups e controles de acesso.
	- Automatiza validações, checkpoints e Data Docs.
	- Garante segurança, auditoria e rastreabilidade técnica.
	- Executa correções técnicas e rollback quando necessário.

---

## **Políticas de Qualidade de Dados**

Para cada dimensão da qualidade, detalhamos definição operacional, métricas (SLAs), forma de medição e ações corretivas.

### 1) Completude
- Definição: campos obrigatórios para operação e tomada de decisão não podem ser nulos ou vazios (ex.: `email`, `id_cliente`, `preco`).
- Métrica / SLA:
	- Campos críticos (`email`, `id_cliente`, `id_produto`, `preco`): máximo 2% de nulos por carga/periodicidade.
	- Campos secundários: máximo 5% de nulos.
- Como medir: cálculo de taxa de não-nulos por coluna em cada batch de ingestão; monitoramento via Great Expectations e relatórios diários.
- Ações corretivas:
	1. Pipeline classifica registros em `quarantine` (automático) — responsável: `Data Custodian` (0–2 horas).
	2. `Data Steward` analisa e aplica regras de preenchimento ou solicita contato ao time Comercial (24–72 horas).
	3. Se não corrigível em 30 dias, `Data Owner` decide arquivamento/exclusão.

### 2) Unicidade
- Definição: identificadores de entidades (PKs) e campos chave (ex.: `email` quando definido como único) não devem ter duplicidades.
- Métrica / SLA:
	- 100% unicidade para chaves primárias em datasets de referência.
	- < 0.01% de duplicados tolerados em datasets derivados (com justificativa).
- Como medir: detecção de duplicidade durante ingestão e profiling periódico.
- Ações corretivas:
	1. Isolar duplicatas em fluxo de quarentena — `Data Custodian` (imediato).
	2. `Data Steward` aplica política de merge (identificar master record) e registra decisão no catálogo (24–72 horas).
	3. `Data Owner` aprova mudanças que impactem relatórios financeiros ou operacionais.

### 3) Validade
- Definição: formatos e tipos devem seguir padrões definidos (
	datas, telefones, emails, códigos fiscais, limites numéricos).
- Métrica / SLA:
	- >= 99% de conformidade com regex/tipos nos campos críticos por ingestão.
- Como medir: validações automatizadas (Great Expectations) e checks de schema.
- Ações corretivas:
	1. Correção automática (ex.: normalização de DDD, remoção de espaços) — `Data Custodian` (automático).
	2. Se correção automática falhar, registrar incidente e notificar `Data Steward` (24 horas).
	3. Rejeição ou marcação para revisão manual dependendo do impacto.

### 4) Consistência
- Definição: dados entre sistemas e dentro do mesmo sistema não devem conter contradições de regras de negócio (ex.: `valor_total` = `quantidade` × `valor_unitario`).
- Métrica / SLA:
	- 100% de consistência para regras críticas de integridade referencial; discrepâncias devem ser < 0.1% para dados analíticos com justificativa.
- Como medir: validações cross-check entre fontes (referential integrity tests) e regras personalizadas em Expectation Suites.
- Ações corretivas:
	1. Alerta imediato ao `Data Steward` e ao `Data Owner` se impacto for crítico.
	2. Reconciliar fontes: origem da discrepância deve ser corrigida na fonte quando aplicável (72 horas).
	3. Aplicar correção temporal (correção retroativa) com registro de auditoria.

### 5) Acurácia
- Definição: representatividade do dado em relação ao mundo real (ex.: endereço de entrega correto, preço refletido corretamente).
- Métrica / SLA:
	- Acurácia verificada por amostragem: meta >= 95% em amostras mensais para dados críticos.
- Como medir: amostragem, cruzamento com fontes externas (transportadoras, catálogos), feedbacks de clientes e reconciliações financeiras.
- Ações corretivas:
	1. `Data Steward` inicia investigação e confirma a fonte do erro (7 dias).
	2. Corrigir a origem quando possível; atualizar registros históricos com log de auditoria.
	3. Notificar stakeholders impactados e revisar processos relacionados.

### 6) Temporalidade (Freshness & Latency)
- Definição: dados devem estar disponíveis dentro do SLA definido para cada caso de uso (ex.: relatórios diários, dashboard em near-real-time).
- Métrica / SLA:
	- Vendas: ingestão D+1 (dados do dia anterior) com 99% das transações disponíveis para relatórios até 07:00 UTC do dia seguinte.
	- Catálogo de Produtos: atualizações refletidas em até 5 minutos para operações críticas.
- Como medir: monitoramento de pipelines, logs de processamento e métricas de latency.
- Ações corretivas:
	1. `Data Custodian` executa rollback ou reprocessamento incremental (imediato).
	2. `Data Owner` é informado se houver impacto em relatórios executivos (1 hora).
	3. Post-mortem técnico e plano de mitigação.

---

## **Glossário de Negócios**

| Termo | Definição | Critério / Exemplo |
| :--- | :--- | :--- |
| **Cliente Ativo** | Cliente que realizou pelo menos uma compra nos últimos 12 meses. | `is_active = true` se última compra >= hoje - 365 dias. |
| **Venda Válida** | Transação registrada com `status = 'Concluída'` e valores coerentes. | `quantidade > 0` e `valor_total = quantidade * valor_unitario`. |
| **Produto Ativo** | Item disponível para venda no catálogo e com `ativo = true`. | `estoque >= 0` e `ativo = true`. |
| **Entrega no Prazo** | Entrega cujo `data_entrega_real` <= `data_entrega_prevista`. | Marca `on_time = true` quando satisfeita. |

---

## **Padrões de Formato**

- **Datas**: `YYYY-MM-DD` (ISO 8601). Todos os timestamps devem ser armazenados em UTC; ex.: `2025-11-17`.
- **Telefones**: formato numérico sem máscara, 11 dígitos (DDNNNNNNNNN). Ex.: `11999887766`.
- **Emails**: regex validadora: ``^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$``. Campos de e-mail devem ser armazenados em minúsculas e sem espaços.
- **UF (Códigos de Estado)**: lista válida de códigos de unidade federativa (Brasil):

```
['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
```

---

## **Mecanismos de Aplicação e Auditoria**

- **Validações Automatizadas**: toda ingestão passa por Expectation Suites (Great Expectations) e Checkpoints configurados; falhas automaticamente registradas em `data_quality/alerts`.
- **Catálogo e Dicionário de Dados**: termo, origem, responsável e última revisão documentados; versão controlada (Git) para alterações nas regras.
- **Logging e Rastreabilidade**: cada alteração de dado deve gerar evento de auditoria com `user/service`, `timestamp`, `versao_schema` e `motivo`.
- **Escalonamento**:
	- Incidentes críticos (impacto financeiro/operacional): notificar `Data Owner` e CTO, SLA de resposta 1 hora.
	- Incidentes médios: notificar `Data Steward`, SLA de resposta 24 horas.
	- Incidentes menores: pipeline de correção automática ou fila de backlog.

---

## **Exceções e Gestão de Mudanças**

- Mudanças em schemas, regras ou SLAs devem ser aprovadas pelo `Data Owner` e documentadas no repositório de governança com plano de rollout e rollback.
- Exceções temporárias (por até 30 dias) devem ter justificativa, dono da exceção e plano de mitigação.

---

## **Governança Operacional — Checklists Rápidos**

- Ao criar um novo dataset: definir `Data Owner`, `Data Steward`, formato, frequência, SLAs e Expectation Suite.
- Ao registrar um incidente: criar ticket com ID, descrição, impacto, responsável e prazo; anexar logs e amostra dos registros afetados.
- Revisão trimestral: `Data Owners` e `Data Stewards` revisam políticas, SLAs e resultados de qualidade.

---

## **Contato e Responsabilidades**

- Contato central de Governança: `governanca@techcommerce.local` (para notificações e solicitações de alteração).
- Comitê de Governança (mensal): Data Owners, representantes de Engenharia, Compliance e Segurança da Informação.

---

> Observação: este documento é a base inicial da governança de dados da TechCommerce e deve evoluir com maturidade. Todas as decisões operacionais e exceções devem ser registradas e versionadas.
