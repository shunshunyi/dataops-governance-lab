# 📁 Datasets do Desafio TechCommerce

## 📋 Descrição dos Arquivos

Este diretório contém os datasets da empresa **TechCommerce** com problemas intencionais de qualidade de dados para o desafio final do curso de DataOps e Governança de Dados.

### 📊 Arquivos Disponíveis

#### 1. `clientes.csv` (16 registros)
**Colunas**: `id_cliente`, `nome`, `email`, `telefone`, `data_nascimento`, `cidade`, `estado`, `data_cadastro`

**Problemas Intencionais**:
- ❌ **Duplicatas**: Cliente ID 1 aparece 2 vezes
- ❌ **Campos vazios**: Nomes e emails em branco
- ❌ **Emails inválidos**: Formatos incorretos (ex: `pedro@invalid`)
- ❌ **Telefones inconsistentes**: Tamanhos diferentes (ex: `119999`, `1199988`)
- ❌ **Idades impossíveis**: Data nascimento 2010 (criança de 13 anos)

#### 2. `produtos.csv` (20 registros)
**Colunas**: `id_produto`, `nome_produto`, `categoria`, `preco`, `estoque`, `data_criacao`, `ativo`

**Problemas Intencionais**:
- ❌ **Duplicatas**: Produto ID 105 = ID 101
- ❌ **Campos vazios**: Categoria e nome_produto em branco
- ❌ **Preços negativos**: Produto 103 com preço -29.99
- ❌ **Estoque negativo**: Produto 107 com estoque -10
- ❌ **Preço zero**: Produto 110 com preço 0

#### 3. `vendas.csv` (25 registros)
**Colunas**: `id_venda`, `id_cliente`, `id_produto`, `quantidade`, `valor_unitario`, `valor_total`, `data_venda`, `status`

**Problemas Intencionais**:
- ❌ **Integridade referencial**: Cliente 999 e 500 não existem
- ❌ **Produto inexistente**: Produto 999 não existe
- ❌ **Quantidade negativa**: Venda 1004 com quantidade -1
- ❌ **Quantidade zero**: Venda 1019 com quantidade 0
- ❌ **Data futura**: Venda 1005 em 2024-12-31
- ❌ **Status inválido**: Status "Erro" não é padrão
- ❌ **Cálculos incorretos**: Valor total ≠ quantidade × valor unitário

#### 4. `logistica.csv` (22 registros)
**Colunas**: `id_entrega`, `id_venda`, `transportadora`, `data_envio`, `data_entrega_prevista`, `data_entrega_real`, `status_entrega`

**Problemas Intencionais**:
- ❌ **Integridade referencial**: Venda 9999 não existe
- ❌ **Campos vazios**: Transportadora em branco
- ❌ **Duplicatas**: Entregas 2005 e 2020 para mesma venda 1006
- ❌ **Datas inconsistentes**: Data entrega antes do envio
- ❌ **Datas faltantes**: Data prevista ou real em branco
- ❌ **Status inconsistente**: "Entregue" sem data de entrega

## 🎯 Objetivos do Desafio

### Identificar e Corrigir:
1. **Completude**: Campos obrigatórios vazios
2. **Unicidade**: Registros duplicados
3. **Validade**: Formatos e domínios inválidos
4. **Consistência**: Regras de negócio violadas
5. **Pontualidade**: Datas futuras ou inconsistentes
6. **Acurácia**: Dados incorretos ou impossíveis

### Implementar com Great Expectations:
- ✅ **Expectation Suites** para cada dataset
- ✅ **Checkpoints** para automação
- ✅ **Data Docs** para relatórios
- ✅ **Validações cross-dataset**

## 📊 Estatísticas dos Problemas

| Dataset | Total Registros | Problemas Identificados | Taxa de Problemas |
|---------|----------------|------------------------|-------------------|
| Clientes | 16 | ~8 problemas | ~50% |
| Produtos | 20 | ~6 problemas | ~30% |
| Vendas | 25 | ~10 problemas | ~40% |
| Logística | 22 | ~8 problemas | ~36% |

## 🚀 Como Usar

### 📓 Notebooks Disponíveis
1. **`notebooks/exporaDataSets.ipynb`** - Exploração inicial dos dados
2. **`notebooks/Lab_DataOps_Governanca_Qualidade.ipynb`** - Laboratório completo

### 🔄 Fluxo Recomendado
1. **Execute primeiro** `exporaDataSets.ipynb` para entender os dados
2. **Carregue os datasets** no seu ambiente PySpark
3. **Analise os problemas** usando Great Expectations
4. **Crie Expectation Suites** para cada dimensão da qualidade
5. **Configure Checkpoints** para automação
6. **Implemente correções** automáticas
7. **Gere Data Docs** profissionais

## 💡 Dicas

- Use `pandas.read_csv()` ou `spark.read.csv()` para carregar
- Configure `header=True` e `inferSchema=True`
- Trate encoding como `utf-8`
- Considere tipos de dados apropriados

## 🔗 Recursos

- **Great Expectations**: https://docs.greatexpectations.io/
- **PySpark**: https://spark.apache.org/docs/latest/api/python/
- **Pandas**: https://pandas.pydata.org/docs/

---

**Boa sorte no desafio!** 🚀📊✨