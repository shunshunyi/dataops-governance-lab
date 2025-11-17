"""
test_correcao_automatica.py
Testes unitários para o módulo de correção automática de dados.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import correcao_automatica as ca


class TestCorrecaoAutomatica:
    """Testes para funções de correção de dados"""
    
    @staticmethod
    def test_corrigir_clientes_duplicatas():
        """Verifica se duplicatas de id_cliente são removidas"""
        df = pd.DataFrame({
            'id_cliente': [1, 2, 1],
            'nome': ['João', 'Maria', 'João'],
            'email': ['joao@test.com', 'maria@test.com', 'joao@test.com'],
            'telefone': ['11999887766', '11888776655', '11999887766'],
            'data_nascimento': ['1985-03-15', '1990-07-22', '1985-03-15'],
            'cidade': ['SP', 'RJ', 'SP'],
            'estado': ['SP', 'RJ', 'SP'],
            'data_cadastro': ['2023-01-10', '2023-01-15', '2023-01-10']
        })
        
        df_corrigido = ca.corrigir_clientes(df)
        assert len(df_corrigido) == 2, f"Esperado 2 registros, obteve {len(df_corrigido)}"
        print("✅ test_corrigir_clientes_duplicatas PASSOU")
    
    @staticmethod
    def test_corrigir_clientes_email_invalido():
        """Verifica se emails inválidos são convertidos para None"""
        df = pd.DataFrame({
            'id_cliente': [1, 2],
            'nome': ['João', 'Pedro'],
            'email': ['joao@test.com', 'pedro@invalid'],  # segundo é inválido
            'telefone': ['11999887766', '11888776655'],
            'data_nascimento': ['1985-03-15', '1990-07-22'],
            'cidade': ['SP', 'RJ'],
            'estado': ['SP', 'RJ'],
            'data_cadastro': ['2023-01-10', '2023-01-15']
        })
        
        df_corrigido = ca.corrigir_clientes(df)
        assert pd.isna(df_corrigido.iloc[1]['email']), "Email inválido deveria ser None"
        print("✅ test_corrigir_clientes_email_invalido PASSOU")
    
    @staticmethod
    def test_corrigir_produtos_preco_negativo():
        """Verifica se preços negativos são convertidos em abs()"""
        df = pd.DataFrame({
            'id_produto': [101, 102],
            'nome_produto': ['Mouse', 'Teclado'],
            'categoria': ['Periféricos', 'Periféricos'],
            'preco': [29.99, -199.99],
            'estoque': [50, 30],
            'data_criacao': ['2023-01-01', '2023-01-05'],
            'ativo': ['true', 'true']
        })
        
        df_corrigido = ca.corrigir_produtos(df)
        assert df_corrigido.iloc[1]['preco'] > 0, "Preço negativo deveria ser convertido em abs()"
        assert df_corrigido.iloc[1]['preco'] == 199.99, f"Esperado 199.99, obteve {df_corrigido.iloc[1]['preco']}"
        print("✅ test_corrigir_produtos_preco_negativo PASSOU")
    
    @staticmethod
    def test_corrigir_vendas_quantidade_negativa():
        """Verifica se vendas com quantidade <= 0 são removidas"""
        df = pd.DataFrame({
            'id_venda': [1001, 1002, 1003],
            'id_cliente': [1, 2, 3],
            'id_produto': [101, 102, 103],
            'quantidade': [2, 1, -1],  # terceira é negativa
            'valor_unitario': [100.0, 200.0, 50.0],
            'valor_total': [200.0, 200.0, -50.0],
            'data_venda': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'status': ['Concluída', 'Pendente', 'Cancelada']
        })
        
        df_clientes = pd.DataFrame({'id_cliente': [1, 2, 3]})
        df_produtos = pd.DataFrame({'id_produto': [101, 102, 103]})
        
        df_corrigido = ca.corrigir_vendas(df, df_clientes, df_produtos)
        assert len(df_corrigido) == 2, f"Esperado 2 registros, obteve {len(df_corrigido)}"
        assert (df_corrigido['quantidade'] > 0).all(), "Todas as quantidades deveriam ser > 0"
        print("✅ test_corrigir_vendas_quantidade_negativa PASSOU")
    
    @staticmethod
    def test_corrigir_logistica_duplicatas():
        """Verifica se duplicatas de id_entrega em logística são removidas"""
        df = pd.DataFrame({
            'id_entrega': [2001, 2001, 2003],  # primeira duplicada por id_entrega
            'id_venda': [1001, 1001, 1002],
            'transportadora': ['Correios', 'Correios', 'SEDEX'],
            'data_envio': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'data_entrega_prevista': ['2023-01-05', '2023-01-06', '2023-01-07'],
            'data_entrega_real': ['2023-01-04', '2023-01-05', '2023-01-06'],
            'status_entrega': ['Entregue', 'Entregue', 'Entregue']
        })
        
        df_vendas = pd.DataFrame({'id_venda': [1001, 1002]})
        
        df_corrigido = ca.corrigir_logistica(df, df_vendas)
        assert len(df_corrigido) == 2, f"Esperado 2 registros, obteve {len(df_corrigido)}"
        print("✅ test_corrigir_logistica_duplicatas PASSOU")


def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "="*70)
    print("🧪 INICIANDO TESTES DO MÓDULO DE CORREÇÃO AUTOMÁTICA")
    print("="*70 + "\n")
    
    try:
        TestCorrecaoAutomatica.test_corrigir_clientes_duplicatas()
        TestCorrecaoAutomatica.test_corrigir_clientes_email_invalido()
        TestCorrecaoAutomatica.test_corrigir_produtos_preco_negativo()
        TestCorrecaoAutomatica.test_corrigir_vendas_quantidade_negativa()
        TestCorrecaoAutomatica.test_corrigir_logistica_duplicatas()
        
        print("\n" + "="*70)
        print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("="*70 + "\n")
        return True
    
    except AssertionError as e:
        print(f"\n❌ ERRO NO TESTE: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
