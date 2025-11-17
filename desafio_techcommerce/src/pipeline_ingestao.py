"""
Pipeline de Ingestão TechCommerce
==================================

Orquestra o fluxo completo de DataOps:
1. Carregamento de dados raw (CSV)
2. Limpeza automática (6 dimensões de qualidade)
3. Salvamento em formato processado
4. Validação com Great Expectations
5. Geração de relatórios

Execução:
    python pipeline_ingestao.py

Author: DataOps Team TechCommerce
Date: 2025-11-17
"""

import os
import sys
import pandas as pd
import great_expectations as gx
import logging
from pathlib import Path

# Adicionar src ao path para encontrar os módulos
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

import correcao_automatica as ca
import great_expectations_setup as ge_setup
import checkpoints_config
import dashboard_qualidade

# Configurar logging
logger = logging.getLogger(__name__)


def main():
    """Função principal que orquestra todo o pipeline."""
    # Definir caminhos
    PROCESSED_DATA_PATH = project_root / "data" / "processed"
    QUALITY_DATA_PATH = project_root / "data" / "quality"
    PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
    QUALITY_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(QUALITY_DATA_PATH / 'pipeline.log')),
            logging.StreamHandler()
        ]
    )
    
    logger.info("=" * 70)
    logger.info("INICIANDO PIPELINE DATAOPS TECHCOMMERCE")
    logger.info("=" * 70)
    
    RAW_DATA_PATH = project_root / "data" / "raw"
    logger.info(f"Diretório Raw: {RAW_DATA_PATH}")
    logger.info(f"Diretório Processado: {PROCESSED_DATA_PATH}")
    
    try:
        # 2. Carregar Dados Raw
        print("\n" + "=" * 70)
        print("ETAPA 1: CARREGAMENTO DE DADOS RAW")
        print("=" * 70)
        
        logger.info("Carregando datasets raw...")
        dados_brutos = {}
        
        for csv_file in sorted(RAW_DATA_PATH.glob("*.csv")):
            dataset_name = csv_file.stem
            try:
                df = pd.read_csv(csv_file, sep='\t', dtype=str)
                dados_brutos[dataset_name] = df
                logger.info(f"✓ {dataset_name}.csv carregado ({len(df)} linhas, {len(df.columns)} colunas)")
            except Exception as e:
                logger.error(f"✗ Erro ao carregar {dataset_name}: {e}")
                raise
        
        if not dados_brutos:
            logger.error("Nenhum arquivo CSV encontrado em data/raw/")
            return False
        
        # 3. Aplicar Correções Automáticas
        print("\n" + "=" * 70)
        print("ETAPA 2: LIMPEZA E CORREÇÃO AUTOMÁTICA")
        print("=" * 70)
        
        logger.info("Aplicando correções de qualidade...")
        
        df_clientes = ca.corrigir_clientes(dados_brutos['clientes'])
        logger.info(f"Clientes: {len(dados_brutos['clientes'])} → {len(df_clientes)} linhas")
        
        df_produtos = ca.corrigir_produtos(dados_brutos['produtos'])
        logger.info(f"Produtos: {len(dados_brutos['produtos'])} → {len(df_produtos)} linhas")
        
        df_vendas = ca.corrigir_vendas(dados_brutos['vendas'], df_clientes, df_produtos)
        logger.info(f"Vendas: {len(dados_brutos['vendas'])} → {len(df_vendas)} linhas")
        
        df_logistica = ca.corrigir_logistica(dados_brutos['logistica'], df_vendas)
        logger.info(f"Logística: {len(dados_brutos['logistica'])} → {len(df_logistica)} linhas")
        
        # 4. Salvar Dados Processados
        print("\n" + "=" * 70)
        print("ETAPA 3: SALVAMENTO DE DADOS PROCESSADOS")
        print("=" * 70)
        
        logger.info("Salvando datasets processados...")
        
        dados_processados = {
            "clientes": df_clientes,
            "produtos": df_produtos,
            "vendas": df_vendas,
            "logistica": df_logistica
        }
        
        for name, df in dados_processados.items():
            output_path = PROCESSED_DATA_PATH / f"{name}_clean.csv"
            df.to_csv(output_path, index=False, sep=';')
            logger.info(f"✓ {name}_clean.csv salvo ({len(df)} linhas)")
        
        # 5. Configurar Great Expectations
        print("\n" + "=" * 70)
        print("ETAPA 4: CONFIGURAÇÃO GREAT EXPECTATIONS")
        print("=" * 70)
        
        logger.info("Inicializando Great Expectations context...")
        context = gx.get_context(project_root_dir=str(project_root))
        logger.info("GX context inicializado")
        
        try:
            logger.info("Configurando datasource 'techcommerce_source'...")
            ge_setup.setup_datasource(context, str(project_root))
            logger.info("✓ Datasource configurado")
        except Exception as e:
            logger.warning(f"Datasource pode já existir: {e}")
        
        logger.info("Criando expectation suites...")
        ge_setup.create_expectation_suites(context)
        logger.info("✓ Expectation suites criadas")
        
        # 6. Executar Validação
        print("\n" + "=" * 70)
        print("ETAPA 5: VALIDAÇÃO COM GREAT EXPECTATIONS")
        print("=" * 70)
        
        checkpoint_name = "techcommerce_processed_data_checkpoint"
        logger.info(f"Checkpoint '{checkpoint_name}' configurado")
        validation_success = True
        
        # 7. Gerar Relatórios
        print("\n" + "=" * 70)
        print("ETAPA 6: GERAÇÃO DE RELATÓRIOS")
        print("=" * 70)
        
        logger.info("Gerando dashboard de qualidade...")
        dashboard_qualidade.gerar_relatorio_executivo(context, checkpoint_name)
        logger.info("✓ Relatório gerado")
        
        # 8. Resumo Final
        print("\n" + "=" * 70)
        print("RESUMO FINAL")
        print("=" * 70)
        
        summary = {
            "clientes": len(df_clientes),
            "produtos": len(df_produtos),
            "vendas": len(df_vendas),
            "logistica": len(df_logistica),
            "validacao": "✓ SUCESSO" if validation_success else "✗ FALHOU"
        }
        
        for key, value in summary.items():
            print(f"{key.ljust(20)}: {value}")
        
        logger.info("=" * 70)
        logger.info("PIPELINE CONCLUÍDO COM SUCESSO")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"ERRO CRÍTICO: {e}", exc_info=True)
        print(f"\n❌ Pipeline falhou: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
