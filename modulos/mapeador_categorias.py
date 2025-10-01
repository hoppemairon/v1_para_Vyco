import pandas as pd
import streamlit as st
from typing import List, Dict, Set

class MapeadorCategorias:
    """Classe responsável por mapear categorias antigas para novas"""
    
    def __init__(self):
        self.categorias_antigas = set()
        self.categorias_novas = set()
        self.categorias_inconsistentes = set()
    
    def _limpar_categoria(self, categoria_texto: str) -> tuple:
        """
        Separa código e nome da categoria
        Exemplo: "2.2.1 - ÁGUA" retorna ("2.2.1", "ÁGUA")
        
        Args:
            categoria_texto: Texto completo da categoria
            
        Returns:
            tuple: (codigo, nome_categoria)
        """
        if not isinstance(categoria_texto, str):
            categoria_texto = str(categoria_texto) if categoria_texto is not None else ""
        
        categoria_texto = categoria_texto.strip()
        
        # Padrões comuns de separação
        separadores = [' - ', ' – ', ' — ', ' | ', ': ', ' :: ']
        
        for separador in separadores:
            if separador in categoria_texto:
                partes = categoria_texto.split(separador, 1)  # Divide apenas na primeira ocorrência
                if len(partes) == 2:
                    codigo = partes[0].strip()
                    nome = partes[1].strip()
                    return (codigo, nome)
        
        # Se não encontrar separador, tenta identificar padrão de código no início
        import re
        
        # Padrão: números e pontos no início (ex: "2.2.1 ÁGUA")
        match = re.match(r'^(\d+(?:\.\d+)*)\s+(.+)$', categoria_texto)
        if match:
            codigo = match.group(1)
            nome = match.group(2)
            return (codigo, nome)
        
        # Padrão: letras e números no início (ex: "A1 ÁGUA")
        match = re.match(r'^([A-Za-z]\d+(?:\.\d+)*)\s+(.+)$', categoria_texto)
        if match:
            codigo = match.group(1)
            nome = match.group(2)
            return (codigo, nome)
        
        # Se nada funcionar, retorna vazio para código e o texto completo para nome
        return ("", categoria_texto)
    
    def _processar_categorias_com_codigo(self, df: pd.DataFrame, coluna: str) -> pd.DataFrame:
        """
        Processa DataFrame separando códigos dos nomes das categorias
        
        Args:
            df: DataFrame original
            coluna: Nome da coluna com categorias
            
        Returns:
            pd.DataFrame: DataFrame com colunas separadas
        """
        df_processado = df.copy()
        
        # Aplicar limpeza em todas as categorias
        codigos = []
        nomes_limpos = []
        
        for categoria in df_processado[coluna]:
            codigo, nome = self._limpar_categoria(categoria)
            codigos.append(codigo)
            nomes_limpos.append(nome)
        
        # Adicionar novas colunas
        df_processado[f'{coluna}_Codigo'] = codigos
        df_processado[f'{coluna}_Nome_Limpo'] = nomes_limpos
        
        return df_processado
    
    def encontrar_categorias_inconsistentes(self, 
                                          dados_lancamentos: pd.DataFrame,
                                          dados_categorias: pd.DataFrame,
                                          coluna_lancamentos_manual: str = None,
                                          coluna_plano_manual: str = None) -> List[str]:
        """
        Encontra categorias presentes nos lançamentos que não existem no plano de contas atual
        
        Args:
            dados_lancamentos: DataFrame com lançamentos do V1
            dados_categorias: DataFrame com plano de contas atual
            
        Returns:
            List[str]: Lista de categorias inconsistentes
        """
        try:
            # Configurar colunas automaticamente
            if coluna_lancamentos_manual:
                coluna_categoria_lancamentos = coluna_lancamentos_manual
            else:
                # Usar coluna fixa "Categoria" para V1
                coluna_categoria_lancamentos = "Categoria"
            
            if coluna_plano_manual:
                coluna_categoria_plano = coluna_plano_manual
            else:
                # Encontrar coluna de categoria no plano de contas silenciosamente
                colunas_categoria_plano = self._encontrar_coluna_categoria(dados_categorias)
                
                if not colunas_categoria_plano:
                    st.error("❌ Coluna de categoria não encontrada no plano de contas")
                    return []
                
                coluna_categoria_plano = colunas_categoria_plano[0]
            
            # Processar categorias do plano de contas para separar códigos dos nomes
            dados_categorias_processados = self._processar_categorias_com_codigo(
                dados_categorias, coluna_categoria_plano
            )
            
            # Obter categorias únicas de cada fonte
            self.categorias_antigas = set(dados_lancamentos[coluna_categoria_lancamentos].dropna().unique())
            
            # Usar nomes limpos do plano de contas
            coluna_nomes_limpos = f'{coluna_categoria_plano}_Nome_Limpo'
            self.categorias_novas = set(dados_categorias_processados[coluna_nomes_limpos].dropna().unique())
            
            # Encontrar categorias inconsistentes
            self.categorias_inconsistentes = self.categorias_antigas - self.categorias_novas
            
            return sorted(list(self.categorias_inconsistentes))
            
        except Exception as e:
            st.error(f"Erro ao analisar categorias: {str(e)}")
            return []
    
    def _encontrar_coluna_categoria(self, df: pd.DataFrame) -> List[str]:
        """
        Encontra possíveis colunas de categoria no DataFrame
        
        Args:
            df: DataFrame para analisar
            
        Returns:
            List[str]: Lista de nomes de colunas que podem ser categoria
        """
        # Expandir palavras-chave para capturar mais variações
        palavras_chave = [
            'categoria', 'plano', 'conta', 'classificacao', 'classificação',
            'nome', 'descricao', 'descrição', 'grupo', 'tipo',
            'receita', 'despesa', 'centro', 'custo'
        ]
        
        colunas_encontradas = []
        
        for coluna in df.columns:
            coluna_lower = coluna.lower().strip()
            for palavra in palavras_chave:
                if palavra in coluna_lower:
                    colunas_encontradas.append(coluna)
                    break
        
        # Se não encontrar nada, tentar com a primeira coluna que contenha texto
        if not colunas_encontradas:            
            for coluna in df.columns:
                # Verificar se a coluna tem dados de texto (não numéricos)
                if df[coluna].dtype == 'object' and not df[coluna].isna().all():
                    amostra = df[coluna].dropna().iloc[0] if not df[coluna].dropna().empty else ""
                    if isinstance(amostra, str) and len(amostra) > 2:
                        colunas_encontradas.append(coluna)
                        break
        
        return colunas_encontradas
    
    def obter_categorias_validas(self, dados_categorias: pd.DataFrame, 
                                coluna_categoria: str = None) -> List[str]:
        """
        Obtém lista de categorias válidas do plano de contas atual (nomes limpos)
        
        Args:
            dados_categorias: DataFrame com plano de contas
            coluna_categoria: Nome da coluna de categoria (opcional)
            
        Returns:
            List[str]: Lista de categorias válidas (nomes limpos)
        """
        try:
            if not coluna_categoria:
                colunas_categoria = self._encontrar_coluna_categoria(dados_categorias)
                if not colunas_categoria:
                    return []
                coluna_categoria = colunas_categoria[0]
            
            # Processar categorias para separar códigos dos nomes
            dados_processados = self._processar_categorias_com_codigo(dados_categorias, coluna_categoria)
            
            # Usar nomes limpos
            coluna_nomes_limpos = f'{coluna_categoria}_Nome_Limpo'
            categorias_validas = dados_processados[coluna_nomes_limpos].dropna().unique()
            
            # Remover categorias vazias
            categorias_validas = [cat for cat in categorias_validas if cat.strip()]
            
            return sorted(list(categorias_validas))
            
        except Exception as e:
            st.error(f"Erro ao obter categorias válidas: {str(e)}")
            return []
    
    def criar_interface_mapeamento(self, categorias_inconsistentes: List[str],
                                  categorias_validas: List[str]) -> Dict[str, str]:
        """
        Cria interface interativa para mapeamento de categorias
        
        Args:
            categorias_inconsistentes: Lista de categorias que precisam ser mapeadas
            categorias_validas: Lista de categorias válidas para mapeamento
            
        Returns:
            Dict[str, str]: Dicionário com mapeamento categoria_antiga -> categoria_nova
        """
        mapeamento = {}
        
        if not categorias_inconsistentes:
            st.success("✅ Todas as categorias estão consistentes!")
            return mapeamento
        
        st.subheader("🔄 Mapeamento de Categorias")
# Processar categorias inconsistentes
        
        # Criar interface para cada categoria inconsistente
        for i, categoria_antiga in enumerate(categorias_inconsistentes):
            with st.expander(f"Mapear: {categoria_antiga}", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.write("**Categoria antiga:**")
                    st.code(categoria_antiga)
                
                with col2:
                    # Tentar sugerir categoria similar
                    categoria_sugerida = self._sugerir_categoria_similar(
                        categoria_antiga, categorias_validas
                    )
                    
                    # Selectbox para escolha da nova categoria
                    categoria_nova = st.selectbox(
                        "Selecione a nova categoria:",
                        options=[""] + categorias_validas,
                        index=categorias_validas.index(categoria_sugerida) + 1 if categoria_sugerida else 0,
                        key=f"mapeamento_{i}_{categoria_antiga}",
                        help=f"Selecione a categoria do novo plano para substituir '{categoria_antiga}'"
                    )
                    
                    if categoria_nova:
                        mapeamento[categoria_antiga] = categoria_nova
                        st.success(f"✅ {categoria_antiga} → {categoria_nova}")
                    else:
                        st.warning("⚠️ Selecione uma categoria válida")
        
        return mapeamento
    
    def _sugerir_categoria_similar(self, categoria_antiga: str, categorias_validas: List[str]) -> str:
        """
        Sugere uma categoria similar baseada em similaridade de texto
        
        Args:
            categoria_antiga: Categoria que precisa ser mapeada
            categorias_validas: Lista de categorias válidas
            
        Returns:
            str: Categoria sugerida (ou string vazia se nenhuma for encontrada)
        """
        categoria_antiga_lower = categoria_antiga.lower()
        
        # Buscar por correspondência exata
        for categoria in categorias_validas:
            if categoria.lower() == categoria_antiga_lower:
                return categoria
        
        # Buscar por correspondência parcial
        for categoria in categorias_validas:
            categoria_lower = categoria.lower()
            
            # Verificar se alguma palavra da categoria antiga está na nova
            palavras_antigas = categoria_antiga_lower.split()
            palavras_novas = categoria_lower.split()
            
            for palavra_antiga in palavras_antigas:
                if len(palavra_antiga) > 3:  # Apenas palavras com mais de 3 caracteres
                    for palavra_nova in palavras_novas:
                        if palavra_antiga in palavra_nova or palavra_nova in palavra_antiga:
                            return categoria
        
        # Se nenhuma correspondência for encontrada, retornar vazio
        return ""
    
    def validar_mapeamento_completo(self, mapeamento: Dict[str, str],
                                   categorias_inconsistentes: List[str]) -> bool:
        """
        Valida se o mapeamento está completo
        
        Args:
            mapeamento: Dicionário com mapeamento atual
            categorias_inconsistentes: Lista de categorias que precisam ser mapeadas
            
        Returns:
            bool: True se o mapeamento está completo
        """
        categorias_mapeadas = set(mapeamento.keys())
        categorias_faltantes = set(categorias_inconsistentes) - categorias_mapeadas
        
        if categorias_faltantes:
            st.error(f"❌ Categorias ainda não mapeadas: {', '.join(categorias_faltantes)}")
            return False
        
        # Verificar se todas as categorias mapeadas têm valor
        categorias_sem_valor = [k for k, v in mapeamento.items() if not v]
        
        if categorias_sem_valor:
            st.error(f"❌ Categorias sem mapeamento definido: {', '.join(categorias_sem_valor)}")
            return False
        
        st.success("✅ Mapeamento completo!")
        return True
    
    def exibir_resumo_mapeamento(self, mapeamento: Dict[str, str]) -> None:
        """
        Exibe resumo do mapeamento realizado
        
        Args:
            mapeamento: Dicionário com mapeamento
        """
        if not mapeamento:
            pass  # Sem categorias para mapear
            return
        
        st.subheader("📋 Resumo do Mapeamento")
        
        # Criar DataFrame para exibição
        df_mapeamento = pd.DataFrame([
            {"Categoria Antiga": k, "Categoria Nova": v}
            for k, v in mapeamento.items()
        ])
        
        st.dataframe(df_mapeamento, use_container_width=True)
        
        # Estatísticas
        # Mapeamento concluído
    
    def salvar_mapeamento(self, mapeamento: Dict[str, str], caminho: str) -> None:
        """
        Salva o mapeamento em arquivo para referência futura
        
        Args:
            mapeamento: Dicionário com mapeamento
            caminho: Caminho do arquivo para salvar
        """
        try:
            df_mapeamento = pd.DataFrame([
                {"categoria_antiga": k, "categoria_nova": v, "data_mapeamento": pd.Timestamp.now()}
                for k, v in mapeamento.items()
            ])
            
            df_mapeamento.to_excel(caminho, index=False)
            
        except Exception as e:
            st.error(f"Erro ao salvar mapeamento: {str(e)}")
    
    def carregar_mapeamento(self, caminho: str) -> Dict[str, str]:
        """
        Carrega mapeamento salvo anteriormente
        
        Args:
            caminho: Caminho do arquivo de mapeamento
            
        Returns:
            Dict[str, str]: Mapeamento carregado
        """
        try:
            df_mapeamento = pd.read_excel(caminho)
            
            mapeamento = dict(zip(
                df_mapeamento['categoria_antiga'],
                df_mapeamento['categoria_nova']
            ))
            
            return mapeamento
            
        except Exception as e:
            st.error(f"Erro ao carregar mapeamento: {str(e)}")
            return {}