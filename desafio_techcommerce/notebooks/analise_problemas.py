# Conteúdo para o arquivo 'analise_problemas.ipynb' (em formato .py)

import pandas as pd
import io
import re
from datetime import datetime

def load_data_from_string(data_string, sep='\t'):
    """Função auxiliar para carregar dados de string para DataFrame."""
    return pd.read_csv(io.StringIO(data_string), sep=sep)

# --- 1. Carregando os Dados (Simulação) ---
# Em um cenário real, carregaríamos de 'data/raw/*.csv'
# Para este script autônomo, os dados são embutidos.

clientes_csv_data = """id_cliente\tnome\temail\ttelefone\tdata_nascimento\tcidade
1\tJoão Silva\tjoao@email.com\t11999887766\t1985-03-15\tSão Paulo
2\tMaria Santos\t\t11888776655\t1990-07-22\tRio de Janeiro
1\tJoão Silva\tjoao@email.com\t11999887766\t1985-03-15\tSão Paulo
3\tPedro\tpedro@invalid\t119999\t2000-12-01\tBelo Horizonte
4\t\tana@email.com\t11777665544\t1995-05-30\tSão Paulo
5\tCarlos Oliveira\tcarlos@email.com\t11666554433\t1988-11-12\tPorto Alegre
6\tAna Costa\tana.costa@gmail.com\t11555443322\t1992-08-25\tSalvador
7\tRoberto Lima\troberto@email.com\t11444332211\t1980-04-18\tCuritiba
8\tFernanda Santos\t\t11333221100\t1995-09-30\tFlorianópolis
9\tMarcos Pereira\tmarcos@email.com\t11222110099\t1987-12-05\tGoiânia
10\tLucia Oliveira\tlucia@invalid-email\t11111000999\t2010-01-01\tRecife
11\tPaulo Silva\tpaulo@email.com\t1199988\t1975-06-10\tFortaleza
12\tSandra Costa\tsandra@email.com\t11888777666\t1983-02-28\tBrasília
13\t\tteste@email.com\t11777666555\t1990-05-15\tManaus
14\tRicardo Santos\tricardo@email.com\t11666555444\t1978-10-22\tBelém
15\tJuliana Lima\tjuliana@email.com\t11555444333\t1992-07-08\tVitória
"""
df_clientes = load_data_from_string(clientes_csv_data)

produtos_csv_data = """id_produto\tnome_produto\tcategoria\tpreco\testoque\tdata_criacao\tativo
101\tSmartphone XYZ\tEletrônicos\t899.99\t50\t2023-01-01\ttrue
102\tNotebook ABC\t\t1299.99\t25\t2023-01-05\ttrue
103\tMouse Gamer\tInformática\t-29.99\t100\t2023-01-10\ttrue
104\tTeclado Mecânico\tInformática\t199.99\t0\t2023-01-15\tfalse
105\tSmartphone XYZ\tEletrônicos\t899.99\t50\t2023-01-01\ttrue
106\t\tCasa e Jardim\t45.90\t200\t2023-01-20\ttrue
107\tHeadset Gamer\tInformática\t299.99\t-10\t2023-01-25\ttrue
108\tMonitor 24 pol\tEletrônicos\t599.99\t15\t2023-02-01\ttrue
109\tCadeira Gamer\tMóveis\t799.99\t8\t2023-02-05\ttrue
110\tWebcam HD\tInformática\t0\t30\t2023-02-10\ttrue
111\tMicrofone USB\tEletrônicos\t149.99\t25\t2023-02-15\ttrue
112\tTablet Android\tEletrônicos\t399.99\t12\t2023-02-20\ttrue
113\tCarregador Wireless\tAcessórios\t89.99\t100\t2023-02-25\ttrue
114\tCabo HDMI\tAcessórios\t25.99\t500\t2023-03-01\ttrue
115\tSSD 1TB\tInformática\t299.99\t20\t2023-03-05\ttrue
116\tMemória RAM 16GB\tInformática\t399.99\t15\t2023-03-10\ttrue
117\tPlaca de Vídeo\tInformática\t1599.99\t5\t2023-03-15\ttrue
118\tProcessador Intel\tInformática\t899.99\t10\t2023-03-20\ttrue
119\tFonte 650W\tInformática\t199.99\t25\t2023-03-25\ttrue
120\tGabinete Gamer\tInformática\t299.99\t18\t2023-04-01\ttrue
"""
df_produtos = load_data_from_string(produtos_csv_data)

vendas_csv_data = """id_venda\tid_cliente\tid_produto\tquantidade\tvalor_unitario\tvalor_total\tdata_venda\tstatus
1001\t1\t101\t2\t899.99\t1799.98\t2023-03-01\tConcluída
1002\t2\t102\t1\t1299.99\t1299.99\t2023-03-02\tPendente
1003\t999\t103\t3\t29.99\t89.97\t2023-03-03\tConcluída
1004\t1\t104\t-1\t199.99\t-199.99\t2023-03-04\tCancelada
1005\t3\t101\t1\t899.99\t899.99\t2024-12-31\tProcessando
1006\t5\t108\t1\t599.99\t599.99\t2023-03-06\tConcluída
1007\t6\t109\t2\t799.99\t1599.98\t2023-03-07\tConcluída
1008\t7\t110\t1\t0\t0\t2023-03-08\tPendente
1009\t8\t111\t3\t149.99\t449.97\t2023-03-09\tConcluída
1010\t9\t112\t1\t399.99\t399.99\t2023-03-10\tConcluída
1011\t10\t113\t5\t89.99\t449.95\t2023-03-11\tCancelada
1012\t11\t114\t10\t25.99\t259.90\t2023-03-12\tConcluída
1013\t12\t115\t1\t299.99\t299.99\t2023-03-13\tConcluída
1014\t13\t116\t2\t399.99\t799.98\t2023-03-14\tPendente
1015\t14\t117\t1\t1599.99\t1599.99\t2023-03-15\tConcluída
1016\t15\t118\t1\t899.99\t899.99\t2023-03-16\tConcluída
1017\t1\t119\t2\t199.99\t399.98\t2023-03-17\tConcluída
1018\t2\t120\t1\t299.99\t299.99\t2023-03-18\tPendente
1019\t500\t101\t0\t899.99\t0\t2023-03-19\tErro
1020\t3\t999\t1\t199.99\t199.99\t2023-03-20\tConcluída
1021\t4\t102\t3\t1299.99\t3899.97\t2023-03-21\tConcluída
1022\t5\t103\t2\t29.99\t59.98\t2023-03-22\tConcluída
1023\t6\t104\t1\t199.99\t199.99\t2023-03-23\tCancelada
1024\t7\t105\t4\t899.99\t3599.96\t2023-03-24\tConcluída
1025\t8\t106\t1\t45.90\t45.90\t2023-03-25\tPendente
"""
df_vendas = load_data_from_string(vendas_csv_data)

logistica_csv_data = """id_entrega\tid_venda\ttransportadora\tdata_envio\tdata_entrega_prevista\tdata_entrega_real\tstatus_entrega
2001\t1001\tCorreios\t2023-03-02\t2023-03-05\t2023-03-04\tEntregue
2002\t1002\tTransportadora XYZ\t2023-03-03\t\t2023-03-10\tEntregue
2003\t1003\tCorreios\t2023-03-04\t2023-03-07\t\tEm Trânsito
2004\t1004\t\t\t\t\tCancelada
2005\t1006\tCorreios\t2023-03-07\t2023-03-10\t2023-03-09\tEntregue
2006\t1007\tTransportadora ABC\t2023-03-08\t2023-03-12\t2023-03-11\tEntregue
2007\t1008\tCorreios\t2023-03-09\t2023-03-12\t\tEm Trânsito
2008\t1009\tTransportadora XYZ\t2023-03-10\t2023-03-14\t2023-03-13\tEntregue
2009\t1010\tCorreios\t2023-03-11\t2023-03-15\t2023-03-14\tEntregue
2010\t1012\tTransportadora ABC\t2023-03-13\t2023-03-17\t2023-03-16\tEntregue
2011\t1013\tCorreios\t2023-03-14\t2023-03-18\t2023-03-17\tEntregue
2012\t1015\tTransportadora XYZ\t2023-03-16\t2023-03-20\t2023-03-19\tEntregue
2013\t1016\tCorreios\t2023-03-17\t2023-03-21\t2023-03-20\tEntregue
2014\t1017\tTransportadora ABC\t2023-03-18\t2023-03-22\t2023-03-21\tEntregue
2015\t1020\tCorreios\t2023-03-21\t2023-03-25\t2023-03-24\tEntregue
2016\t1021\tTransportadora XYZ\t2023-03-22\t2023-03-26\t2023-03-25\tEntregue
2017\t1022\tCorreios\t2023-03-23\t2023-03-27\t2023-03-26\tEntregue
2018\t1024\tTransportadora ABC\t2023-03-25\t2023-03-29\t2023-03-28\tEntregue
2019\t9999\tCorreios\t2023-03-26\t2023-03-30\t\tEm Trânsito
2020\t1006\tTransportadora XYZ\t2023-03-02\t2023-03-05\t2023-03-04\tEntregue
2021\t1007\tCorreios\t2023-02-28\t2023-03-03\t2023-03-05\tEntregue
2022\t1025\t\t2023-03-26\t2023-03-30\t\tPendente
"""
df_logistica = load_data_from_string(logistica_csv_data)

datasets = {"clientes": df_clientes, "produtos": df_produtos, "vendas": df_vendas, "logistica": df_logistica}
problems = []

def add_problem(dataset_name, dimension, description, records_affected_df, example_id_col):
    """Função para agregar e formatar os problemas identificados."""
    total_records = len(datasets[dataset_name])
    count = len(records_affected_df)
    if count > 0:
        impact = (count / total_records) * 100
        problems.append({
            "Dataset": dataset_name,
            "Dimensão": dimension,
            "Problema": description,
            "Registros Afetados": count,
            "Impacto (%)": f"{impact:.2f}%",
            "Exemplos de ID": records_affected_df[example_id_col].tolist() if not records_affected_df.empty else []
        })

# --- 2. Análise de Problemas ---

# ANÁLISE DE CLIENTES
duplicated_records_cli = df_clientes[df_clientes.duplicated(keep=False)]
add_problem("clientes", "Unicidade", "Registros completamente duplicados", duplicated_records_cli, "id_cliente")
missing_email = df_clientes[df_clientes['email'].isnull() | (df_clientes['email'] == '')]
add_problem("clientes", "Completude", "Campo 'email' está vazio", missing_email, "id_cliente")
missing_name = df_clientes[df_clientes['nome'].isnull() | (df_clientes['nome'] == '')]
add_problem("clientes", "Completude", "Campo 'nome' está vazio", missing_name, "id_cliente")
email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
invalid_email_format = df_clientes[~df_clientes['email'].astype(str).str.match(email_regex, na=False)]
add_problem("clientes", "Validade", "Formato do 'email' é inválido", invalid_email_format, "id_cliente")
invalid_phone_format = df_clientes[df_clientes['telefone'].astype(str).str.len() != 11]
add_problem("clientes", "Validade", "Formato do 'telefone' inválido (não tem 11 dígitos)", invalid_phone_format, "id_cliente")

# ANÁLISE DE PRODUTOS
duplicated_records_prod = df_produtos[df_produtos.duplicated(keep=False)]
add_problem("produtos", "Unicidade", "Registros completamente duplicados", duplicated_records_prod, "id_produto")
missing_category = df_produtos[df_produtos['categoria'].isnull() | (df_produtos['categoria'] == '')]
add_problem("produtos", "Completude", "Campo 'categoria' está vazio", missing_category, "id_produto")
missing_prod_name = df_produtos[df_produtos['nome_produto'].isnull() | (df_produtos['nome_produto'] == '')]
add_problem("produtos", "Completude", "Campo 'nome_produto' está vazio", missing_prod_name, "id_produto")
invalid_price = df_produtos[df_produtos['preco'] <= 0]
add_problem("produtos", "Validade", "'preco' do produto é negativo ou zero", invalid_price, "id_produto")
invalid_stock = df_produtos[df_produtos['estoque'] < 0]
add_problem("produtos", "Validade", "'estoque' do produto é negativo", invalid_stock, "id_produto")

# ANÁLISE DE VENDAS
invalid_quantity = df_vendas[df_vendas['quantidade'] <= 0]
add_problem("vendas", "Validade", "'quantidade' de venda é zero ou negativa", invalid_quantity, "id_venda")
today = datetime.now().date()
df_vendas['data_venda_dt'] = pd.to_datetime(df_vendas['data_venda']).dt.date
future_sales = df_vendas[df_vendas['data_venda_dt'] > today]
add_problem("vendas", "Validade", "'data_venda' está no futuro", future_sales, "id_venda")
VALID_STATUS_VENDAS = ["Concluída", "Pendente", "Cancelada"]
invalid_status_vendas = df_vendas[~df_vendas['status'].isin(VALID_STATUS_VENDAS)]
add_problem("vendas", "Validade", "Valor do campo 'status' é inválido", invalid_status_vendas, "id_venda")
df_vendas['valor_calculado'] = df_vendas['quantidade'] * df_vendas['valor_unitario']
inconsistent_total = df_vendas[~((df_vendas['valor_total'] - df_vendas['valor_calculado']).abs() < 0.01)]
add_problem("vendas", "Consistência", "Inconsistência na regra: valor_total != qtd * valor_unit", inconsistent_total, "id_venda")
valid_client_ids = set(df_clientes['id_cliente'].unique())
orphan_clients = df_vendas[~df_vendas['id_cliente'].isin(valid_client_ids)]
add_problem("vendas", "Integridade", "Venda com 'id_cliente' inexistente", orphan_clients, "id_venda")
valid_product_ids = set(df_produtos['id_produto'].unique())
orphan_products = df_vendas[~df_vendas['id_produto'].isin(valid_product_ids)]
add_problem("vendas", "Integridade", "Venda com 'id_produto' inexistente", orphan_products, "id_venda")

# ANÁLISE DE LOGÍSTICA
duplicated_delivery = df_logistica[df_logistica['id_venda'].duplicated(keep=False)]
add_problem("logistica", "Unicidade", "Mesma 'id_venda' com múltiplas entregas", duplicated_delivery, "id_entrega")
missing_carrier = df_logistica[(df_logistica['status_entrega'].isin(['Entregue', 'Em Trânsito'])) & (df_logistica['transportadora'].isnull())]
add_problem("logistica", "Completude", "'transportadora' vazia para entregas ativas", missing_carrier, "id_entrega")
valid_sale_ids = set(df_vendas['id_venda'].unique())
orphan_sales = df_logistica[~df_logistica['id_venda'].isin(valid_sale_ids)]
add_problem("logistica", "Integridade", "Entrega com 'id_venda' inexistente", orphan_sales, "id_entrega")
for col in ['data_envio', 'data_entrega_prevista', 'data_entrega_real']:
    df_logistica[col] = pd.to_datetime(df_logistica[col], errors='coerce')
inconsistent_dates = df_logistica[df_logistica['data_envio'] > df_logistica['data_entrega_real']]
add_problem("logistica", "Consistência", "data_envio posterior à data_entrega_real", inconsistent_dates, "id_entrega")
df_logistica_vendas = pd.merge(df_logistica, df_vendas[['id_venda', 'data_venda_dt']], on='id_venda', how='left')
df_logistica_vendas['data_venda'] = pd.to_datetime(df_logistica_vendas['data_venda_dt'], errors='coerce')
shipping_before_sale = df_logistica_vendas[df_logistica_vendas['data_envio'] < df_logistica_vendas['data_venda']]
add_problem("logistica", "Consistência", "data_envio anterior à data_venda", shipping_before_sale, "id_entrega")


# --- 3. Sumário e Priorização ---
print("\n--- RELATÓRIO DE QUALIDADE DE DADOS - TechCommerce ---\n")
if problems:
    df_summary = pd.DataFrame(problems)
    priority_map = {
        "Venda com 'id_cliente' inexistente": "Crítica",
        "Venda com 'id_produto' inexistente": "Crítica",
        "Entrega com 'id_venda' inexistente": "Crítica",
        "'preco' do produto é negativo ou zero": "Crítica",
        "'estoque' do produto é negativo": "Crítica",
        "Registros completamente duplicados": "Alta",
        "Campo 'email' está vazio": "Alta",
        "Formato do 'email' é inválido": "Alta",
        "'quantidade' de venda é zero ou negativa": "Alta",
        "Valor do campo 'status' é inválido": "Alta",
        "'data_venda' está no futuro": "Alta",
        "Mesma 'id_venda' com múltiplas entregas": "Alta",
        "Campo 'nome' está vazio": "Média",
        "Formato do 'telefone' inválido (não tem 11 dígitos)": "Média",
        "Campo 'categoria' está vazio": "Média",
        "Campo 'nome_produto' está vazio": "Média",
        "Inconsistência na regra: valor_total != qtd * valor_unit": "Média",
        "'transportadora' vazia para entregas ativas": "Média",
        "data_envio posterior à data_entrega_real": "Média",
        "data_envio anterior à data_venda": "Média"
    }
    df_summary['Prioridade'] = df_summary['Problema'].map(priority_map).fillna("Baixa")
    df_summary['Prioridade'] = pd.Categorical(df_summary['Prioridade'], ["Crítica", "Alta", "Média", "Baixa"])
    df_summary = df_summary.sort_values(by=['Prioridade', 'Dataset', 'Impacto (%)'], ascending=[True, True, False])
    df_summary = df_summary[['Prioridade', 'Dataset', 'Dimensão', 'Problema', 'Registros Afetados', 'Impacto (%)']]
    print(df_summary.to_string())
else:
    print("Nenhum problema de qualidade de dados identificado.")
