"""
Utilitários auxiliares para o Conversor V1 para Vyco
"""

import pandas as pd
import logging
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

def configurar_logging():
    """Configura o sistema de logging"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f"logs/conversor_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def validar_estrutura_diretorios() -> bool:
    """
    Valida se a estrutura de diretórios necessária existe
    
    Returns:
        bool: True se todos os diretórios existem
    """
    diretorios_necessarios = [
        'modelos_v1',
        'modelos_vyco', 
        'preenchimento_vyco'
    ]
    
    diretorios_faltantes = []
    
    for diretorio in diretorios_necessarios:
        if not os.path.exists(diretorio):
            diretorios_faltantes.append(diretorio)
    
    if diretorios_faltantes:
        print(f"❌ Diretórios faltantes: {', '.join(diretorios_faltantes)}")
        return False
    
    return True

def criar_estrutura_diretorios():
    """Cria a estrutura de diretórios necessária"""
    diretorios = [
        'modelos_v1',
        'modelos_vyco',
        'preenchimento_vyco',
        'planilhas_geradas',
        'logs'
    ]
    
    for diretorio in diretorios:
        os.makedirs(diretorio, exist_ok=True)
        print(f"✅ Diretório criado/verificado: {diretorio}")

def limpar_texto(texto: str) -> str:
    """
    Limpa e normaliza texto
    
    Args:
        texto: Texto a ser limpo
        
    Returns:
        str: Texto limpo
    """
    if not isinstance(texto, str):
        return str(texto) if texto is not None else ""
    
    # Remover espaços extras
    texto = texto.strip()
    
    # Normalizar espaços
    import re
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def converter_para_float(valor: Any) -> float:
    """
    Converte valor para float, tratando diferentes formatos
    
    Args:
        valor: Valor a ser convertido
        
    Returns:
        float: Valor convertido ou 0.0 se não for possível
    """
    if pd.isna(valor) or valor is None:
        return 0.0
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    if isinstance(valor, str):
        # Remover caracteres não numéricos exceto vírgula, ponto e sinal
        import re
        valor_limpo = re.sub(r'[^\d,.-]', '', valor)
        
        # Substituir vírgula por ponto
        valor_limpo = valor_limpo.replace(',', '.')
        
        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0
    
    return 0.0

def converter_para_data(valor: Any) -> Optional[datetime]:
    """
    Converte valor para datetime, tratando diferentes formatos
    
    Args:
        valor: Valor a ser convertido
        
    Returns:
        datetime: Data convertida ou None se não for possível
    """
    if pd.isna(valor) or valor is None:
        return None
    
    if isinstance(valor, datetime):
        return valor
    
    if isinstance(valor, str):
        formatos_data = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d/%m/%y',
            '%d-%m-%y'
        ]
        
        for formato in formatos_data:
            try:
                return datetime.strptime(valor, formato)
            except ValueError:
                continue
    
    return None

def obter_colunas_similares(df: pd.DataFrame, palavras_chave: List[str]) -> List[str]:
    """
    Encontra colunas que contenham palavras-chave
    
    Args:
        df: DataFrame para pesquisar
        palavras_chave: Lista de palavras-chave
        
    Returns:
        List[str]: Lista de colunas encontradas
    """
    colunas_encontradas = []
    
    for coluna in df.columns:
        coluna_lower = coluna.lower()
        for palavra in palavras_chave:
            if palavra.lower() in coluna_lower:
                colunas_encontradas.append(coluna)
                break
    
    return colunas_encontradas

def gerar_backup_dados(dados: Dict[str, pd.DataFrame], prefixo: str = "backup") -> str:
    """
    Gera backup dos dados processados
    
    Args:
        dados: Dicionário com DataFrames
        prefixo: Prefixo para o nome do arquivo
        
    Returns:
        str: Caminho do arquivo de backup
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_arquivo = f"{prefixo}_{timestamp}.xlsx"
    caminho_backup = os.path.join('logs', nome_arquivo)
    
    try:
        with pd.ExcelWriter(caminho_backup, engine='openpyxl') as writer:
            for nome_planilha, df in dados.items():
                df.to_excel(writer, sheet_name=nome_planilha, index=False)
        
        return caminho_backup
        
    except Exception as e:
        print(f"Erro ao criar backup: {str(e)}")
        return ""

def validar_dados_obrigatorios(df: pd.DataFrame, colunas_obrigatorias: List[str]) -> Dict[str, Any]:
    """
    Valida se os dados obrigatórios estão presentes
    
    Args:
        df: DataFrame a validar
        colunas_obrigatorias: Lista de colunas obrigatórias
        
    Returns:
        Dict: Resultado da validação
    """
    resultado = {
        'valido': True,
        'erros': [],
        'avisos': []
    }
    
    # Verificar colunas faltantes
    colunas_faltantes = set(colunas_obrigatorias) - set(df.columns)
    if colunas_faltantes:
        resultado['valido'] = False
        resultado['erros'].append(f"Colunas obrigatórias faltantes: {', '.join(colunas_faltantes)}")
    
    # Verificar dados vazios em colunas obrigatórias
    for coluna in colunas_obrigatorias:
        if coluna in df.columns:
            valores_vazios = df[coluna].isna().sum()
            if valores_vazios > 0:
                resultado['avisos'].append(f"Coluna '{coluna}' possui {valores_vazios} valores vazios")
    
    return resultado

def obter_estatisticas_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Obtém estatísticas detalhadas de um DataFrame
    
    Args:
        df: DataFrame para analisar
        
    Returns:
        Dict: Estatísticas do DataFrame
    """
    return {
        'total_linhas': len(df),
        'total_colunas': len(df.columns),
        'colunas': list(df.columns),
        'tipos_dados': df.dtypes.to_dict(),
        'valores_nulos': df.isnull().sum().to_dict(),
        'valores_unicos': {col: df[col].nunique() for col in df.columns},
        'memoria_usada': df.memory_usage(deep=True).sum(),
        'linhas_duplicadas': df.duplicated().sum()
    }

def exportar_relatorio_conversao(dados_originais: Dict[str, pd.DataFrame],
                                dados_processados: Dict[str, pd.DataFrame],
                                mapeamento_categorias: Dict[str, str]) -> str:
    """
    Exporta relatório detalhado da conversão
    
    Args:
        dados_originais: Dados originais do V1
        dados_processados: Dados processados para Vyco
        mapeamento_categorias: Mapeamento de categorias aplicado
        
    Returns:
        str: Caminho do arquivo do relatório
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    nome_relatorio = f"relatorio_conversao_{timestamp}.txt"
    caminho_relatorio = os.path.join('logs', nome_relatorio)
    
    try:
        with open(caminho_relatorio, 'w', encoding='utf-8') as arquivo:
            arquivo.write("=" * 50 + "\n")
            arquivo.write("RELATÓRIO DE CONVERSÃO V1 PARA VYCO\n")
            arquivo.write("=" * 50 + "\n\n")
            
            arquivo.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            # Estatísticas dos dados originais
            arquivo.write("DADOS ORIGINAIS (V1):\n")
            arquivo.write("-" * 20 + "\n")
            for nome, df in dados_originais.items():
                stats = obter_estatisticas_dataframe(df)
                arquivo.write(f"{nome.upper()}:\n")
                arquivo.write(f"  - Linhas: {stats['total_linhas']}\n")
                arquivo.write(f"  - Colunas: {stats['total_colunas']}\n")
                arquivo.write(f"  - Colunas: {', '.join(stats['colunas'])}\n\n")
            
            # Estatísticas dos dados processados
            arquivo.write("DADOS PROCESSADOS (VYCO):\n")
            arquivo.write("-" * 25 + "\n")
            for nome, df in dados_processados.items():
                stats = obter_estatisticas_dataframe(df)
                arquivo.write(f"{nome.upper()}:\n")
                arquivo.write(f"  - Linhas: {stats['total_linhas']}\n")
                arquivo.write(f"  - Colunas: {stats['total_colunas']}\n")
                arquivo.write(f"  - Colunas: {', '.join(stats['colunas'])}\n\n")
            
            # Mapeamento de categorias
            if mapeamento_categorias:
                arquivo.write("MAPEAMENTO DE CATEGORIAS:\n")
                arquivo.write("-" * 25 + "\n")
                for categoria_antiga, categoria_nova in mapeamento_categorias.items():
                    arquivo.write(f"  {categoria_antiga} → {categoria_nova}\n")
                arquivo.write(f"\nTotal de categorias mapeadas: {len(mapeamento_categorias)}\n\n")
            
            arquivo.write("=" * 50 + "\n")
            arquivo.write("CONVERSÃO CONCLUÍDA COM SUCESSO\n")
            arquivo.write("=" * 50 + "\n")
        
        return caminho_relatorio
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {str(e)}")
        return ""