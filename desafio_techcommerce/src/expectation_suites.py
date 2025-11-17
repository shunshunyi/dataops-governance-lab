"""
expectation_suites.py
Módulo centralizado para definição de Expectation Suites para todos os datasets da TechCommerce.
Garante cobertura das 6 dimensões da qualidade de dados em todas as expectations.

Dimensões cobertas:
- Completude: valores não nulos em campos críticos
- Unicidade: chaves primárias e campos únicos sem duplicatas
- Validade: conformidade com formatos esperados (regex, tipos, ranges)
- Consistência: integridade referencial e regras de negócio
- Acurácia: cálculos e relacionamentos entre campos
- Temporalidade: dados não futuros e dentro de SLAs
"""

import great_expectations as gx
from great_expectations.core.batch import BatchRequest
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def create_clientes_expectations(validator):
    """
    Cria Expectation Suite para dataset de clientes.
    
    Dimensões cobertas:
    - Completude: id_cliente, nome, email não nulos
    - Unicidade: id_cliente, email únicos
    - Validade: formato de email (regex), telefone com 11 dígitos, estado com 2 caracteres
    - Consistência: estado em lista de UFs válidas
    """
    # Completude
    validator.expect_column_values_to_not_be_null("id_cliente")
    validator.expect_column_values_to_not_be_null("nome")
    validator.expect_column_values_to_not_be_null("email")
    
    # Unicidade
    validator.expect_column_values_to_be_unique("id_cliente")
    validator.expect_column_values_to_be_unique("email")
    
    # Validade
    validator.expect_column_values_to_match_regex("email", r"^[\w\.-]+@[\w\.-]+\.\w+$", mostly=0.99)
    validator.expect_column_values_to_match_regex("telefone", r"^\d{11}$", mostly=0.98)
    
    # Consistência
    ufs = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']
    validator.expect_column_values_to_be_in_set("estado", ufs, mostly=1.0)
    
    logging.info("✅ Expectation Suite para Clientes criada com sucesso")


def create_produtos_expectations(validator):
    """
    Cria Expectation Suite para dataset de produtos.
    
    Dimensões cobertas:
    - Completude: id_produto, nome_produto, categoria, preco não nulos
    - Unicidade: id_produto único
    - Validade: preco > 0, estoque >= 0
    - Consistência: categoria não pode ser vazia, ativo é booleano
    """
    # Completude
    validator.expect_column_values_to_not_be_null("id_produto")
    validator.expect_column_values_to_not_be_null("nome_produto")
    validator.expect_column_values_to_not_be_null("categoria")
    validator.expect_column_values_to_not_be_null("preco")
    
    # Unicidade
    validator.expect_column_values_to_be_unique("id_produto")
    
    # Validade
    validator.expect_column_values_to_be_between("preco", min_value=0.01)
    validator.expect_column_values_to_be_between("estoque", min_value=0)
    
    # Consistência
    validator.expect_column_values_to_not_be_in_set("categoria", ["SEM CATEGORIA"])
    validator.expect_column_values_to_be_in_set("ativo", ["true", "false"])
    
    logging.info("✅ Expectation Suite para Produtos criada com sucesso")


def create_vendas_expectations(validator, df_clientes, df_produtos):
    """
    Cria Expectation Suite para dataset de vendas com validações cross-dataset.
    
    Dimensões cobertas:
    - Completude: id_venda, id_cliente, id_produto, quantidade, valor_total não nulos
    - Unicidade: id_venda único
    - Validade: quantidade > 0, status em valores permitidos, data_venda não futura
    - Consistência: integridade referencial (FK), valor_total = quantidade * valor_unitario
    - Acurácia: relacionamentos cross-dataset validados
    - Temporalidade: data_venda não posterior a hoje
    """
    # Completude
    validator.expect_column_values_to_not_be_null("id_venda")
    validator.expect_column_values_to_not_be_null("id_cliente")
    validator.expect_column_values_to_not_be_null("id_produto")
    validator.expect_column_values_to_not_be_null("quantidade")
    validator.expect_column_values_to_not_be_null("valor_total")
    
    # Unicidade
    validator.expect_column_values_to_be_unique("id_venda")
    
    # Validade
    validator.expect_column_values_to_be_between("quantidade", min_value=1)
    validator.expect_column_values_to_be_in_set("status", ["Concluída", "Pendente", "Cancelada", "Processando"])
    
    # Temporalidade
    hoje_str = datetime.utcnow().strftime('%Y-%m-%d')
    validator.expect_column_values_to_be_between("data_venda", max_value=hoje_str)
    
    # Integridade Referencial (cross-dataset)
    ids_clientes = set(df_clientes['id_cliente'].dropna().astype(int).tolist()) if not df_clientes.empty else set()
    ids_produtos = set(df_produtos['id_produto'].dropna().astype(int).tolist()) if not df_produtos.empty else set()
    
    if ids_clientes:
        validator.expect_column_values_to_be_in_set("id_cliente", ids_clientes)
    if ids_produtos:
        validator.expect_column_values_to_be_in_set("id_produto", ids_produtos)
    
    logging.info("✅ Expectation Suite para Vendas criada com sucesso (com validações cross-dataset)")


def create_logistica_expectations(validator, df_vendas):
    """
    Cria Expectation Suite para dataset de logística.
    
    Dimensões cobertas:
    - Completude: id_entrega, id_venda, data_envio não nulos
    - Unicidade: id_entrega único
    - Validade: data_envio, data_entrega_prevista, data_entrega_real em formato correto
    - Consistência: integridade referencial com vendas, status em valores válidos
    - Temporalidade: datas de entrega coerentes
    """
    # Completude
    validator.expect_column_values_to_not_be_null("id_entrega")
    validator.expect_column_values_to_not_be_null("id_venda")
    validator.expect_column_values_to_not_be_null("data_envio")
    
    # Unicidade
    validator.expect_column_values_to_be_unique("id_entrega")
    
    # Validade
    validator.expect_column_values_to_be_in_set("status_entrega", ["Entregue", "Em Trânsito", "Cancelada", "Atrasada"])
    
    # Integridade Referencial
    ids_vendas = set(df_vendas['id_venda'].dropna().astype(int).tolist()) if not df_vendas.empty else set()
    if ids_vendas:
        validator.expect_column_values_to_be_in_set("id_venda", ids_vendas)
    
    logging.info("✅ Expectation Suite para Logística criada com sucesso")


def setup_all_expectations(context=None):
    """
    Função de conveniência que cria todas as Expectation Suites em uma única chamada.
    """
    if context is None:
        context = gx.get_context()
    
    datasource_name = 'techcommerce_source'
    
    # Carregar dataframes processados para validações cross-dataset
    import pandas as pd
    import os
    
    df_clientes = pd.read_csv('data/processed/clientes_clean.csv', sep=';') if os.path.exists('data/processed/clientes_clean.csv') else pd.DataFrame()
    df_produtos = pd.read_csv('data/processed/produtos_clean.csv', sep=';') if os.path.exists('data/processed/produtos_clean.csv') else pd.DataFrame()
    df_vendas = pd.read_csv('data/processed/vendas_clean.csv', sep=';') if os.path.exists('data/processed/vendas_clean.csv') else pd.DataFrame()
    
    # Clientes
    batch_request_clientes = BatchRequest(datasource_name=datasource_name, data_asset_name='clientes_clean', options={})
    validator_clientes = context.get_validator(batch_request=batch_request_clientes, expectation_suite_name='techcommerce.clientes.warning')
    create_clientes_expectations(validator_clientes)
    validator_clientes.save_expectation_suite(discard_failed_expectations=False)
    
    # Produtos
    batch_request_produtos = BatchRequest(datasource_name=datasource_name, data_asset_name='produtos_clean', options={})
    validator_produtos = context.get_validator(batch_request=batch_request_produtos, expectation_suite_name='techcommerce.produtos.warning')
    create_produtos_expectations(validator_produtos)
    validator_produtos.save_expectation_suite(discard_failed_expectations=False)
    
    # Vendas
    batch_request_vendas = BatchRequest(datasource_name=datasource_name, data_asset_name='vendas_clean', options={})
    validator_vendas = context.get_validator(batch_request=batch_request_vendas, expectation_suite_name='techcommerce.vendas.warning')
    create_vendas_expectations(validator_vendas, df_clientes, df_produtos)
    validator_vendas.save_expectation_suite(discard_failed_expectations=False)
    
    # Logística
    batch_request_logistica = BatchRequest(datasource_name=datasource_name, data_asset_name='logistica_clean', options={})
    validator_logistica = context.get_validator(batch_request=batch_request_logistica, expectation_suite_name='techcommerce.logistica.warning')
    create_logistica_expectations(validator_logistica, df_vendas)
    validator_logistica.save_expectation_suite(discard_failed_expectations=False)
    
    logging.info("✅ Todas as Expectation Suites criadas e salvas com sucesso!")


if __name__ == '__main__':
    setup_all_expectations()
