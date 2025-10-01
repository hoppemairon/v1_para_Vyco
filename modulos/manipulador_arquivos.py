import pandas as pd
import streamlit as st
from typing import Union, Optional
import io

class ManipuladorArquivos:
    """Classe responsável por manipular arquivos Excel"""
    
    def __init__(self):
        self.extensoes_suportadas = ['.xlsx', '.xls']
    
    def ler_excel(self, arquivo: Union[str, io.BytesIO]) -> pd.DataFrame:
        """
        Lê um arquivo Excel e retorna um DataFrame
        
        Args:
            arquivo: Caminho do arquivo ou objeto BytesIO
            
        Returns:
            pd.DataFrame: Dados do arquivo Excel
        """
        try:
            # Se for um arquivo carregado pelo Streamlit
            if hasattr(arquivo, 'read'):
                dados = pd.read_excel(arquivo)
            else:
                dados = pd.read_excel(arquivo)
            
            # Limpar dados básicos
            dados = self._limpar_dados_basicos(dados)
            
            return dados
            
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo Excel: {str(e)}")
    
    def _limpar_dados_basicos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Aplica limpeza básica nos dados
        
        Args:
            df: DataFrame a ser limpo
            
        Returns:
            pd.DataFrame: DataFrame limpo
        """
        # Remover linhas completamente vazias
        df = df.dropna(how='all')
        
        # Remover colunas completamente vazias
        df = df.dropna(axis=1, how='all')
        
        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()
        
        # Resetar índice
        df = df.reset_index(drop=True)
        
        return df
    
    def validar_colunas_obrigatorias(self, df: pd.DataFrame, colunas_obrigatorias: list) -> bool:
        """
        Valida se as colunas obrigatórias estão presentes no DataFrame
        
        Args:
            df: DataFrame a ser validado
            colunas_obrigatorias: Lista de colunas que devem estar presentes
            
        Returns:
            bool: True se todas as colunas estão presentes
        """
        colunas_faltantes = set(colunas_obrigatorias) - set(df.columns)
        
        if colunas_faltantes:
            st.error(f"Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}")
            return False
        
        return True
    
    def obter_preview_arquivo(self, df: pd.DataFrame, num_linhas: int = 5) -> pd.DataFrame:
        """
        Retorna um preview do DataFrame
        
        Args:
            df: DataFrame
            num_linhas: Número de linhas para preview
            
        Returns:
            pd.DataFrame: Preview dos dados
        """
        return df.head(num_linhas)
    
    def obter_informacoes_arquivo(self, df: pd.DataFrame) -> dict:
        """
        Retorna informações sobre o arquivo
        
        Args:
            df: DataFrame
            
        Returns:
            dict: Informações do arquivo
        """
        return {
            'total_registros': len(df),
            'total_colunas': len(df.columns),
            'colunas': list(df.columns),
            'tipos_dados': df.dtypes.to_dict(),
            'registros_vazios': df.isnull().sum().to_dict()
        }
    
    def salvar_excel(self, df: pd.DataFrame, caminho: str, nome_planilha: str = 'Dados') -> None:
        """
        Salva DataFrame em arquivo Excel
        
        Args:
            df: DataFrame a ser salvo
            caminho: Caminho do arquivo
            nome_planilha: Nome da planilha
        """
        try:
            with pd.ExcelWriter(caminho, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=nome_planilha, index=False)
                
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo Excel: {str(e)}")
    
    def ler_arquivo_modelo(self, caminho_modelo: str) -> pd.DataFrame:
        """
        Lê um arquivo modelo para obter a estrutura esperada
        
        Args:
            caminho_modelo: Caminho do arquivo modelo
            
        Returns:
            pd.DataFrame: Estrutura do modelo
        """
        try:
            return pd.read_excel(caminho_modelo)
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo modelo: {str(e)}")
    
    def ler_arquivo_preenchimento(self, caminho_txt: str) -> list:
        """
        Lê arquivo TXT com instruções de preenchimento
        
        Args:
            caminho_txt: Caminho do arquivo TXT
            
        Returns:
            list: Lista com as instruções
        """
        try:
            with open(caminho_txt, 'r', encoding='utf-8') as arquivo:
                linhas = arquivo.readlines()
            
            # Limpar linhas vazias e espaços
            instrucoes = [linha.strip() for linha in linhas if linha.strip()]
            
            return instrucoes
            
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo de instruções: {str(e)}")