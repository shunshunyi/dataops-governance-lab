# 📘 Manual do Usuário - TechCommerce DataOps Pipeline

## 📋 Visão Geral

Este manual descreve como usar a solução completa de DataOps e Governança de Dados da TechCommerce, incluindo pipeline de ingestão, correção automática de dados, validações com Great Expectations e geração de relatórios de qualidade.

## 🏗️ Arquitetura da Solução

```
data/raw/*.csv (dados brutos com problemas)
       ↓
pipeline_ingestao.py (orquestrador principal)
       ↓
correcao_automatica.py (limpeza e correção)
       ↓
data/processed/*_clean.csv (dados processados)
       ↓
great_expectations_setup.py / expectation_suites.py (definição de expectations)
       ↓
checkpoints (validação automatizada)
       ↓
dashboard_qualidade.py (relatórios executivos)
       ↓
data_docs/ (HTML interativo) + PDF (relatório executivo)
```

## 🚀 Como Executar o Pipeline

### Pré-requisitos
```bash
pip install pandas great_expectations numpy
```

### Opção 1: Executar Pipeline Completo (Recomendado)
```bash
cd desafio_techcommerce
python src/pipeline_ingestao.py
```

Saída esperada:
```
--- 1. Limpando Dados ---
dados_brutos: 4 arquivos carregados
  ✅ clientes_clean.csv salvo (4 linhas)
  ✅ produtos_clean.csv salvo (5 linhas)
  ✅ vendas_clean.csv salvo (5 linhas)
  ✅ logistica_clean.csv salvo (4 linhas)

--- 2. Configurando Great Expectations ---
✅ Expectation Suite para Clientes criada com sucesso
✅ Expectation Suite para Produtos criada com sucesso
✅ Expectation Suite para Vendas criada com sucesso
✅ Expectation Suite para Logística criada com sucesso

--- 3. Executando Validação ---
✅ Checkpoint 'techcommerce_processed_data_checkpoint' executado

✅ Pipeline de validação concluído com sucesso!
```

### Opção 2: Executar Pipeline Alternativo
```bash
python src/pipeline_completo.py
```

## 📊 Estrutura de Dados

### Datasets Raw (entrada)
- **clientes.csv**: id_cliente, nome, email, telefone, data_nascimento, cidade, estado, data_cadastro
- **produtos.csv**: id_produto, nome_produto, categoria, preco, estoque, data_criacao, ativo
- **vendas.csv**: id_venda, id_cliente, id_produto, quantidade, valor_unitario, valor_total, data_venda, status
- **logistica.csv**: id_entrega, id_venda, transportadora, data_envio, data_entrega_prevista, data_entrega_real, status_entrega

### Datasets Processed (saída)
- **clientes_clean.csv**: Dados corrigidos com emails validados, telefones normalizados, duplicatas removidas
- **produtos_clean.csv**: Preços negativos corrigidos, categorias preenchidas, duplicatas removidas
- **vendas_clean.csv**: Referências validadas (FK), quantidade e valor_total corrigidos, datas futuras removidas
- **logistica_clean.csv**: Integridade referencial validada, datas corrigidas, tempo_entrega_dias calculado

## 🔧 Módulos Principais

### 1. `correcao_automatica.py`
Aplica regras de limpeza e correção automática em cada dataset:

```python
from src.correcao_automatica import corrigir_clientes

df_clientes = pd.read_csv('data/raw/clientes.csv')
df_clientes_clean = corrigir_clientes(df_clientes)
```

**Correções por dataset:**
- **Clientes**: Deduplicação, validação de email/telefone, preenchimento de nome
- **Produtos**: Correção de preços negativos, preenchimento de categoria, deduplicação
- **Vendas**: Validação referencial, remoção de quantidade negativa, recalcução de valor_total
- **Logística**: Deduplicação, validação de datas, cálculo de tempo de entrega

### 2. `expectation_suites.py`
Define as Expectation Suites que validam as 6 dimensões da qualidade:

```python
from src.expectation_suites import create_clientes_expectations
import great_expectations as gx

context = gx.get_context()
batch_request = BatchRequest(datasource_name='techcommerce_source', data_asset_name='clientes_clean')
validator = context.get_validator(batch_request=batch_request, expectation_suite_name='techcommerce.clientes.warning')
create_clientes_expectations(validator)
validator.save_expectation_suite(discard_failed_expectations=False)
```

### 3. `great_expectations_setup.py`
Cria e salva todas as Expectation Suites:

```bash
python src/great_expectations_setup.py
```

### 4. `dashboard_qualidade.py`
Gera relatórios executivos de qualidade:

```python
from src.dashboard_qualidade import gerar_relatorio_executivo
import great_expectations as gx

context = gx.get_context()
gerar_relatorio_executivo(context, 'techcommerce_processed_data_checkpoint')
```

### 5. `sistema_alertas.py`
Sistema de alertas customizado integrado aos checkpoints (em desenvolvimento para integração com Slack/Email).

## 📈 Validação com Great Expectations

### Listar Expectation Suites
```python
import great_expectations as gx
context = gx.get_context()
for suite_name in context.list_expectation_suite_names():
    print(suite_name)
```

### Executar um Checkpoint
```python
results = context.run_checkpoint(checkpoint_name='techcommerce_processed_data_checkpoint')
print(f"Validação {'✅ PASSOU' if results.success else '❌ FALHOU'}")
```

### Visualizar Data Docs
Abra em um navegador:
```
gx/uncommitted/data_docs/local_site/index.html
```

## 🧪 Testes Unitários

Executar testes de correção automática:
```bash
python tests/test_correcao_automatica.py
```

Saída esperada:
```
======================================================================
🧪 INICIANDO TESTES DO MÓDULO DE CORREÇÃO AUTOMÁTICA
======================================================================

✅ test_corrigir_clientes_duplicatas PASSOU
✅ test_corrigir_clientes_email_invalido PASSOU
✅ test_corrigir_produtos_preco_negativo PASSOU
✅ test_corrigir_vendas_quantidade_negativa PASSOU
✅ test_corrigir_logistica_duplicatas PASSOU

======================================================================
✅ TODOS OS TESTES PASSARAM COM SUCESSO!
======================================================================
```

## 📋 Problemas Identificados e Resolvidos

### Dataset de Clientes
| Problema | Dimensão | Solução |
|----------|----------|--------|
| Registros duplicados (id_cliente = 1) | Unicidade | Removidos mantendo primeiro registro |
| Email vazio (Maria Santos) | Completude | Marcado como None/NA |
| Email inválido (pedro@invalid) | Validade | Marcado como None/NA |
| Nome vazio (cliente 4) | Completude | Seria preenchido conforme política |

### Dataset de Produtos
| Problema | Dimensão | Solução |
|----------|----------|--------|
| Categoria vazia (Notebook ABC) | Completude | Preenchida com "SEM CATEGORIA" |
| Preço negativo (Mouse Gamer) | Validade | Convertido para valor absoluto |
| Duplicata de produto (Smartphone XYZ) | Unicidade | Removida mantendo primeiro |

### Dataset de Vendas
| Problema | Dimensão | Solução |
|----------|----------|--------|
| id_cliente inválido (999) | Consistência | Removida (FK inválida) |
| Quantidade negativa | Validade | Removida |
| Valor total incorreto | Acurácia | Recalculado |
| Data futura (2024-12-31) | Temporalidade | Removida |

### Dataset de Logística
| Problema | Dimensão | Solução |
|----------|----------|--------|
| Data entrega vazia | Completude | Preenchida ou removida |
| Integridade referencial | Consistência | Validada contra tabela de vendas |

## 🔍 Métricas de Qualidade

Após execução do pipeline, você pode visualizar:
- **Taxa de Completude**: % de valores não nulos por coluna
- **Taxa de Unicidade**: % de registros únicos em chaves primárias
- **Taxa de Validade**: % de valores conformes com formato esperado
- **Taxa de Integridade Referencial**: % de FKs válidas
- **Tempo de Processamento**: Quanto tempo levou a ingestão e limpeza
- **Registros Processados**: Total de registros processados por dataset

## 📁 Estrutura de Diretórios

```
desafio_techcommerce/
├── data/
│   ├── raw/              # Dados originais com problemas
│   ├── processed/        # Dados limpos (*_clean.csv)
│   └── quality/          # Relatórios de qualidade
├── gx/                   # Great Expectations config
│   ├── great_expectations.yml
│   ├── checkpoints/
│   ├── expectations/
│   └── uncommitted/data_docs/
├── src/
│   ├── pipeline_ingestao.py
│   ├── pipeline_completo.py
│   ├── correcao_automatica.py
│   ├── great_expectations_setup.py
│   ├── expectation_suites.py
│   ├── checkpoints_config.py
│   ├── dashboard_qualidade.py
│   └── sistema_alertas.py
├── tests/
│   └── test_correcao_automatica.py
├── docs/
│   ├── governanca_techcommerce.md
│   ├── relatorio_executivo.md
│   └── manual_usuario.md
├── notebooks/
│   ├── analise_problemas.ipynb
│   └── [outros notebooks]
└── README.md
```

## 🆘 Troubleshooting

### Erro: "Datasource 'techcommerce_source' não encontrado"
**Solução**: Verifique se `great_expectations.yml` contém a definição correta:
```yaml
fluent_datasources:
  techcommerce_source:
    type: pandas
    assets:
      clientes_clean:
        type: csv
        filepath_or_buffer: .../data/processed/clientes_clean.csv
        sep: ;
      # ... outros assets
```

### Erro: "Arquivo não encontrado: data/raw/clientes.csv"
**Solução**: Certifique-se de que:
1. Os CSVs estão em `desafio_techcommerce/data/raw/`
2. Os nomes dos arquivos são corretos (sem espaços, sem caracteres especiais)
3. O pipeline está sendo executado do diretório raiz do projeto

### Expectation Suite não foi salva
**Solução**: Verifique se `gx/expectations/` tem permissão de escrita e se há espaço em disco disponível.

## 📞 Suporte

Para questões técnicas, consulte:
- Documentação de Governança: `docs/governanca_techcommerce.md`
- Relatório Executivo: `docs/relatorio_executivo.md`
- Notebook de Análise: `notebooks/analise_problemas.ipynb`
- Great Expectations Docs: https://docs.greatexpectations.io

---

**Versão**: 1.0  
**Última atualização**: Novembro 2025  
**Mantido por**: Equipe DataOps TechCommerce
