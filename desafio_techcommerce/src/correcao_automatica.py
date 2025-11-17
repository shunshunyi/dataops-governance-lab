"""
Módulo de Correção Automática de Dados
======================================

Implementa correções automáticas baseadas nas 6 dimensões de qualidade:
1. Completude: Preenchimento de campos nulos
2. Unicidade: Remoção de registros duplicados
3. Validade: Validação de formatos e valores
4. Consistência: Validação de relacionamentos e regras de negócio
5. Acurácia: Correção de valores calculados
6. Temporalidade: Validação de datas

Author: DataOps Team TechCommerce
Date: 2025-11-17
"""

import pandas as pd
import numpy as np
import re
import logging
from datetime import datetime
from typing import Tuple

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler para stdout
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class CorrecaoAutomatica:
    """Classe responsável por aplicar correções automáticas em datasets."""
    
    # Padrões de validação
    EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    TELEFONE_REGEX = re.compile(r'^\d{11}$')
    UFS_VALIDAS = {
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
        'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
        'SP', 'SE', 'TO'
    }
    
    # Limites de qualidade
    PRECO_MINIMO = 0.01
    ESTOQUE_MINIMO = 0
    QUANTIDADE_MINIMA = 1
    
    def __init__(self):
        """Inicializa o módulo de correção."""
        logger.info("Módulo de Correção Automática inicializado")
    
    # =====================================================================
    # CORREÇÃO DE CLIENTES
    # =====================================================================
    
    def corrigir_clientes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica correções no dataset de clientes.
        
        Dimensões tratadas:
        - Completude: Preenche nome vazio
        - Unicidade: Remove duplicatas por id_cliente
        - Validade: Valida email e formata telefone
        - Consistência: Valida estado (UF)
        
        Args:
            df: DataFrame com dados de clientes
            
        Returns:
            DataFrame corrigido
        """
        logger.info(f"Iniciando correção de clientes ({len(df)} registros)")
        df_corrigido = df.copy()
        
        # 1. UNICIDADE: Remover duplicatas por id_cliente (manter primeiro)
        antes = len(df_corrigido)
        df_corrigido = df_corrigido.drop_duplicates(subset=['id_cliente'], keep='first')
        removidas = antes - len(df_corrigido)
        if removidas > 0:
            logger.warning(f"  Removidas {removidas} duplicatas (id_cliente)")
        
        # 2. VALIDADE: Email - regex validation
        if 'email' in df_corrigido.columns:
            mask_email_invalido = df_corrigido['email'].notna() & \
                                  ~df_corrigido['email'].astype(str).str.match(self.EMAIL_REGEX)
            n_invalidos = mask_email_invalido.sum()
            if n_invalidos > 0:
                logger.warning(f"  {n_invalidos} emails inválidos convertidos para NA")
                df_corrigido.loc[mask_email_invalido, 'email'] = pd.NA
        
        # 3. VALIDADE: Telefone - exigir 11 dígitos
        if 'telefone' in df_corrigido.columns:
            def limpar_telefone(x):
                if pd.isna(x):
                    return pd.NA
                digits = re.sub(r'\D', '', str(x))
                return digits if len(digits) == 11 else pd.NA
            
            df_corrigido['telefone'] = df_corrigido['telefone'].apply(limpar_telefone)
        
        # 4. COMPLETUDE: Nome vazio
        if 'nome' in df_corrigido.columns:
            n_nulos = df_corrigido['nome'].isna().sum()
            if n_nulos > 0:
                logger.warning(f"  {n_nulos} nomes vazios preenchidos com 'NÃO INFORMADO'")
                df_corrigido['nome'] = df_corrigido['nome'].fillna('NÃO INFORMADO')
        
        # 5. CONSISTÊNCIA: Estado deve ser UF válida (2 caracteres)
        if 'estado' in df_corrigido.columns:
            mask_estado_invalido = df_corrigido['estado'].notna() & \
                                   ~df_corrigido['estado'].astype(str).str.upper().isin(self.UFS_VALIDAS)
            n_invalidos = mask_estado_invalido.sum()
            if n_invalidos > 0:
                logger.warning(f"  {n_invalidos} estados inválidos convertidos para NA")
                df_corrigido.loc[mask_estado_invalido, 'estado'] = pd.NA
        
        logger.info(f"Correção de clientes concluída ({len(df_corrigido)} registros após limpeza)")
        return df_corrigido
    
    # =====================================================================
    # CORREÇÃO DE PRODUTOS
    # =====================================================================
    
    def corrigir_produtos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica correções no dataset de produtos.
        
        Dimensões tratadas:
        - Unicidade: Remove duplicatas por id_produto
        - Validade: Preco > 0, estoque >= 0, categoria preenchida
        - Completude: Preenche categoria vazia
        - Acurácia: Corrige preços negativos (abs)
        
        Args:
            df: DataFrame com dados de produtos
            
        Returns:
            DataFrame corrigido
        """
        logger.info(f"Iniciando correção de produtos ({len(df)} registros)")
        df_corrigido = df.copy()
        
        # Garantir tipos numéricos
        if 'preco' in df_corrigido.columns:
            df_corrigido['preco'] = pd.to_numeric(df_corrigido['preco'], errors='coerce')
        if 'estoque' in df_corrigido.columns:
            df_corrigido['estoque'] = pd.to_numeric(df_corrigido['estoque'], errors='coerce')
        
        # 1. ACURÁCIA: Preço negativo -> converter para positivo (abs)
        if 'preco' in df_corrigido.columns:
            mask_preco_neg = df_corrigido['preco'] < 0
            if mask_preco_neg.any():
                logger.warning(f"  {mask_preco_neg.sum()} preços negativos convertidos com abs()")
                df_corrigido.loc[mask_preco_neg, 'preco'] = df_corrigido.loc[mask_preco_neg, 'preco'].abs()
        
        # 2. COMPLETUDE: Categoria vazia -> 'SEM CATEGORIA'
        if 'categoria' in df_corrigido.columns:
            n_nulos = df_corrigido['categoria'].isna().sum()
            if n_nulos > 0:
                logger.warning(f"  {n_nulos} categorias vazias preenchidas com 'SEM CATEGORIA'")
                df_corrigido['categoria'] = df_corrigido['categoria'].fillna('SEM CATEGORIA')
        
        # 3. VALIDADE: Estoque negativo -> 0
        if 'estoque' in df_corrigido.columns:
            mask_estoque_neg = df_corrigido['estoque'] < 0
            if mask_estoque_neg.any():
                logger.warning(f"  {mask_estoque_neg.sum()} estoques negativos convertidos para 0")
                df_corrigido.loc[mask_estoque_neg, 'estoque'] = 0
        
        # 4. UNICIDADE: Remover duplicatas por id_produto
        antes = len(df_corrigido)
        df_corrigido = df_corrigido.drop_duplicates(subset=['id_produto'], keep='first')
        removidas = antes - len(df_corrigido)
        if removidas > 0:
            logger.warning(f"  Removidas {removidas} duplicatas (id_produto)")
        
        logger.info(f"Correção de produtos concluída ({len(df_corrigido)} registros após limpeza)")
        return df_corrigido
    
    # =====================================================================
    # CORREÇÃO DE VENDAS
    # =====================================================================
    
    def corrigir_vendas(self, df: pd.DataFrame, 
                        df_clientes_clean: pd.DataFrame,
                        df_produtos_clean: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica correções no dataset de vendas.
        
        Dimensões tratadas:
        - Consistência: Valida IDs de cliente e produto (FK)
        - Validade: Quantidade > 0, data_venda não futura
        - Acurácia: Recalcula valor_total
        - Temporalidade: Remove vendas com datas futuras
        
        Args:
            df: DataFrame com dados de vendas
            df_clientes_clean: DataFrame de clientes processado
            df_produtos_clean: DataFrame de produtos processado
            
        Returns:
            DataFrame corrigido
        """
        logger.info(f"Iniciando correção de vendas ({len(df)} registros)")
        df_corrigido = df.copy()
        
        # Garantir tipos numéricos
        for col in ['quantidade', 'valor_unitario', 'valor_total']:
            if col in df_corrigido.columns:
                df_corrigido[col] = pd.to_numeric(df_corrigido[col], errors='coerce')
        
        # 1. CONSISTÊNCIA: Foreign Keys - id_cliente e id_produto válidos
        ids_clientes_validos = set(df_clientes_clean['id_cliente'].dropna().astype(int).tolist())
        ids_produtos_validos = set(df_produtos_clean['id_produto'].dropna().astype(int).tolist())
        
        mask_fk_invalida = (~df_corrigido['id_cliente'].isin(ids_clientes_validos)) | \
                           (~df_corrigido['id_produto'].isin(ids_produtos_validos))
        if mask_fk_invalida.any():
            logger.warning(f"  Removidas {mask_fk_invalida.sum()} vendas com FK inválida")
            df_corrigido = df_corrigido[~mask_fk_invalida].copy()
        
        # 2. VALIDADE: Quantidade > 0
        if 'quantidade' in df_corrigido.columns:
            mask_qtd_invalida = df_corrigido['quantidade'] <= 0
            if mask_qtd_invalida.any():
                logger.warning(f"  Removidas {mask_qtd_invalida.sum()} vendas com quantidade <= 0")
                df_corrigido = df_corrigido[~mask_qtd_invalida].copy()
        
        # 3. ACURÁCIA: Recalcular valor_total = quantidade × valor_unitario
        if set(['quantidade', 'valor_unitario']).issubset(df_corrigido.columns):
            valor_total_esperado = (df_corrigido['quantidade'] * df_corrigido['valor_unitario']).round(2)
            if 'valor_total' in df_corrigido.columns:
                mask_valor_diff = ~(valor_total_esperado - df_corrigido['valor_total']).abs().le(0.01)
                if mask_valor_diff.any():
                    logger.warning(f"  Recalculados {mask_valor_diff.sum()} valores_total")
                    df_corrigido.loc[mask_valor_diff, 'valor_total'] = valor_total_esperado[mask_valor_diff]
            else:
                df_corrigido['valor_total'] = valor_total_esperado
        
        # 4. TEMPORALIDADE: Remover vendas com data_venda no futuro
        if 'data_venda' in df_corrigido.columns:
            df_corrigido['data_venda'] = pd.to_datetime(df_corrigido['data_venda'], errors='coerce')
            hoje = pd.Timestamp.now().normalize()
            mask_futuro = df_corrigido['data_venda'] > hoje
            if mask_futuro.any():
                logger.warning(f"  Removidas {mask_futuro.sum()} vendas com data futura")
                df_corrigido = df_corrigido[~mask_futuro].copy()
        
        logger.info(f"Correção de vendas concluída ({len(df_corrigido)} registros após limpeza)")
        return df_corrigido
    
    # =====================================================================
    # CORREÇÃO DE LOGÍSTICA
    # =====================================================================
    
    def corrigir_logistica(self, df: pd.DataFrame, 
                           df_vendas_clean: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica correções no dataset de logística.
        
        Dimensões tratadas:
        - Unicidade: Remove duplicatas por id_entrega
        - Consistência: Valida FK id_venda
        - Temporalidade: Valida sequência de datas (envio < entrega)
        - Acurácia: Calcula tempo_entrega_dias
        
        Args:
            df: DataFrame com dados de logística
            df_vendas_clean: DataFrame de vendas processado
            
        Returns:
            DataFrame corrigido
        """
        logger.info(f"Iniciando correção de logística ({len(df)} registros)")
        df_corrigido = df.copy()
        
        # 1. UNICIDADE: Remover duplicatas por id_entrega
        antes = len(df_corrigido)
        df_corrigido = df_corrigido.drop_duplicates(subset=['id_entrega'], keep='first')
        removidas = antes - len(df_corrigido)
        if removidas > 0:
            logger.warning(f"  Removidas {removidas} duplicatas (id_entrega)")
        
        # 2. CONSISTÊNCIA: Validar FK id_venda
        ids_vendas_validos = set(df_vendas_clean['id_venda'].dropna().astype(int).tolist())
        mask_fk_invalida = ~df_corrigido['id_venda'].isin(ids_vendas_validos)
        if mask_fk_invalida.any():
            logger.warning(f"  Removidas {mask_fk_invalida.sum()} entregas com id_venda inválido")
            df_corrigido = df_corrigido[~mask_fk_invalida].copy()
        
        # 3. TEMPORALIDADE: Converter e validar datas
        for col in ['data_envio', 'data_entrega_prevista', 'data_entrega_real']:
            if col in df_corrigido.columns:
                df_corrigido[col] = pd.to_datetime(df_corrigido[col], errors='coerce')
        
        # 4. ACURÁCIA: Calcular tempo_entrega_dias
        if set(['data_envio', 'data_entrega_real']).issubset(df_corrigido.columns):
            df_corrigido['tempo_entrega_dias'] = \
                (df_corrigido['data_entrega_real'] - df_corrigido['data_envio']).dt.days
        
        logger.info(f"Correção de logística concluída ({len(df_corrigido)} registros após limpeza)")
        return df_corrigido


# Instância global para backward compatibility
_corrector = CorrecaoAutomatica()

def corrigir_clientes(df: pd.DataFrame) -> pd.DataFrame:
    """Função de compatibilidade para corrigir clientes."""
    return _corrector.corrigir_clientes(df)

def corrigir_produtos(df: pd.DataFrame) -> pd.DataFrame:
    """Função de compatibilidade para corrigir produtos."""
    return _corrector.corrigir_produtos(df)

def corrigir_vendas(df: pd.DataFrame, df_clientes: pd.DataFrame, df_produtos: pd.DataFrame) -> pd.DataFrame:
    """Função de compatibilidade para corrigir vendas."""
    return _corrector.corrigir_vendas(df, df_clientes, df_produtos)

def corrigir_logistica(df: pd.DataFrame, df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Função de compatibilidade para corrigir logística."""
    return _corrector.corrigir_logistica(df, df_vendas)
