import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

class ProcessadorDados:
    """Classe responsável por processar e transformar os dados do V1 para Vyco"""
    
    def __init__(self):
        self.dados_processados = {}
    
    def processar_todos_os_dados(self, 
                                dados_lancamentos: pd.DataFrame,
                                dados_transferencias: pd.DataFrame,
                                dados_categorias: pd.DataFrame,
                                mapeamento_categorias: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Processa todos os dados e gera as estruturas necessárias para o Vyco
        
        Args:
            dados_lancamentos: DataFrame com lançamentos do V1
            dados_transferencias: DataFrame com transferências do V1
            dados_categorias: DataFrame com categorias do V1
            mapeamento_categorias: Dicionário com mapeamento de categorias antigas para novas
            
        Returns:
            Dict com todos os DataFrames processados
        """
        try:
            # Aplicar mapeamento de categorias nos lançamentos se existir
            if mapeamento_categorias:
                dados_lancamentos_processados = self._aplicar_mapeamento_categorias(
                    dados_lancamentos, mapeamento_categorias
                )
            else:
                dados_lancamentos_processados = dados_lancamentos.copy()
            
            # Processar cada tipo de dados
            self.dados_processados = {
                'categorias': self._processar_categorias(dados_categorias),
                'centros_custo': self._processar_centros_custo(dados_lancamentos_processados),
                'contas_correntes': self._processar_contas_correntes(dados_lancamentos_processados),
                'contatos': self._processar_contatos(dados_lancamentos_processados),
                'lancamentos': self._processar_lancamentos(dados_lancamentos_processados),
                'transferencias': self._processar_transferencias(dados_transferencias)
            }
            
            return self.dados_processados
            
        except Exception as e:
            raise Exception(f"Erro ao processar dados: {str(e)}")
    
    def _aplicar_mapeamento_categorias(self, 
                                      dados_lancamentos: pd.DataFrame, 
                                      mapeamento: Dict[str, str]) -> pd.DataFrame:
        """
        Aplica o mapeamento de categorias antigas para novas
        
        Args:
            dados_lancamentos: DataFrame com lançamentos
            mapeamento: Dicionário com mapeamento de categorias
            
        Returns:
            pd.DataFrame: Lançamentos com categorias atualizadas
        """
        dados_processados = dados_lancamentos.copy()
        
        # CORREÇÃO: Procurar especificamente pela coluna 'Categoria' (não 'CodigoCategoria')
        colunas_categoria = [col for col in dados_processados.columns 
                           if col == 'Categoria' or 
                           ('categoria' in col.lower() and 'codigo' not in col.lower()) or
                           'plano' in col.lower()]
        
        if colunas_categoria:
            coluna_categoria = colunas_categoria[0]
            
            # Aplicar mapeamento
            for categoria_antiga, categoria_nova in mapeamento.items():
                mask = dados_processados[coluna_categoria] == categoria_antiga
                dados_processados.loc[mask, coluna_categoria] = categoria_nova
        
        return dados_processados
    
    def _processar_categorias(self, dados_categorias: pd.DataFrame) -> pd.DataFrame:
        """
        Processa dados de categorias mantendo estrutura completa do V1
        Preserva códigos originais e nomes das categorias
        
        Args:
            dados_categorias: DataFrame com categorias do V1
            
        Returns:
            pd.DataFrame: Categorias processadas para Vyco
        """
        categorias_processadas = dados_categorias.copy()
        
        # Garantir que temos coluna Codigo
        if 'Codigo' not in categorias_processadas.columns:
            # Procurar por colunas que podem conter códigos
            colunas_possiveis_codigo = ['Código', 'Code', 'ID', 'Código Pai']
            coluna_codigo_encontrada = None
            
            for col in colunas_possiveis_codigo:
                if col in categorias_processadas.columns:
                    coluna_codigo_encontrada = col
                    break
            
            if coluna_codigo_encontrada:
                # Usar a coluna encontrada como código
                categorias_processadas['Codigo'] = categorias_processadas[coluna_codigo_encontrada]
            elif 'Nome' in categorias_processadas.columns:
                # Tentar extrair códigos do formato "2.2.1 - ÁGUA"
                codigos = []
                nomes_limpos = []
                
                for item in categorias_processadas['Nome']:
                    if isinstance(item, str) and ' - ' in item:
                        partes = item.split(' - ', 1)
                        if len(partes) == 2:
                            codigos.append(partes[0].strip())
                            nomes_limpos.append(partes[1].strip())
                        else:
                            codigos.append('')
                            nomes_limpos.append(item)
                    else:
                        codigos.append('')
                        nomes_limpos.append(str(item) if item is not None else '')
                
                categorias_processadas['Codigo'] = codigos
                categorias_processadas['Nome'] = nomes_limpos
            else:
                # Criar códigos sequenciais se não houver nenhuma informação
                categorias_processadas['Codigo'] = range(1, len(categorias_processadas) + 1)
        
        # Garantir que temos coluna Nome
        if 'Nome' not in categorias_processadas.columns:
            if any(col for col in categorias_processadas.columns if 'nome' in col.lower()):
                nome_col = next(col for col in categorias_processadas.columns if 'nome' in col.lower())
                categorias_processadas['Nome'] = categorias_processadas[nome_col]
            else:
                categorias_processadas['Nome'] = 'Categoria ' + categorias_processadas['Codigo'].astype(str)
        
        # Manter apenas as colunas essenciais para processamento posterior
        colunas_finais = ['Codigo', 'Nome']
        
        # Adicionar outras colunas se existirem
        for col in categorias_processadas.columns:
            if col not in colunas_finais and col.lower() in ['tipo', 'ativo', 'descricao']:
                colunas_finais.append(col)
        
        return categorias_processadas[colunas_finais]
    
    def _processar_centros_custo(self, dados_lancamentos: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai centros de custo únicos dos lançamentos
        
        Args:
            dados_lancamentos: DataFrame com lançamentos
            
        Returns:
            pd.DataFrame: Centros de custo no formato Vyco
        """
        # Encontrar coluna de centro de custo
        colunas_centro_custo = [col for col in dados_lancamentos.columns 
                               if 'centro' in col.lower() and 'custo' in col.lower()]
        
        if not colunas_centro_custo:
            # Se não encontrar, criar DataFrame vazio com estrutura
            return pd.DataFrame(columns=['Codigo', 'Nome', 'Ativo'])
        
        coluna_centro_custo = colunas_centro_custo[0]
        
        # Obter valores únicos, removendo NaN
        centros_unicos = dados_lancamentos[coluna_centro_custo].dropna().unique()
        
        # Criar DataFrame
        centros_custo = pd.DataFrame({
            'Codigo': range(1, len(centros_unicos) + 1),
            'Nome': centros_unicos,
            'Ativo': 'Sim'
        })
        
        return centros_custo
    
    def _processar_contas_correntes(self, dados_lancamentos: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai contas correntes únicas dos lançamentos
        
        Args:
            dados_lancamentos: DataFrame com lançamentos
            
        Returns:
            pd.DataFrame: Contas correntes no formato Vyco
        """
        # Encontrar coluna de conta corrente
        colunas_conta = [col for col in dados_lancamentos.columns 
                        if 'conta' in col.lower() or 'banco' in col.lower()]
        
        if not colunas_conta:
            return pd.DataFrame(columns=['Codigo', 'Nome', 'Tipo', 'Ativo', 'DataInicial'])
        
        coluna_conta = colunas_conta[0]
        
        # Encontrar coluna de data
        colunas_data = [col for col in dados_lancamentos.columns 
                       if 'data' in col.lower() and col.lower() != 'datacompetencia']
        
        if not colunas_data:
            # Se não encontrar coluna de data, usar valores únicos simples
            contas_unicas = dados_lancamentos[coluna_conta].dropna().unique()
            contas_correntes = pd.DataFrame({
                'Codigo': range(1, len(contas_unicas) + 1),
                'Nome': contas_unicas,
                'Tipo': 1,
                'Ativo': 'Sim',
                'DataInicial': ''
            })
            return contas_correntes
        
        coluna_data = colunas_data[0]
        
        # Converter coluna de data para datetime
        dados_com_data = dados_lancamentos.copy()
        # Tentar diferentes formatos de data
        dados_com_data[coluna_data] = pd.to_datetime(dados_com_data[coluna_data], 
                                                    format='%d/%m/%Y', errors='coerce')
        if dados_com_data[coluna_data].isna().all():
            # Se falhou, tentar formato americano
            dados_com_data[coluna_data] = pd.to_datetime(dados_com_data[coluna_data], 
                                                        format='%m/%d/%Y', errors='coerce')
        if dados_com_data[coluna_data].isna().all():
            # Se ainda falhou, usar inferência automática
            dados_com_data[coluna_data] = pd.to_datetime(dados_com_data[coluna_data], errors='coerce')
        
        # Calcular primeira data para cada conta
        contas_com_data = []
        for conta in dados_com_data[coluna_conta].dropna().unique():
            movimentacoes_conta = dados_com_data[dados_com_data[coluna_conta] == conta]
            primeira_data = movimentacoes_conta[coluna_data].min()
            
            if pd.notna(primeira_data):
                # Data inicial = primeira movimentação - 1 dia
                data_inicial = primeira_data - pd.Timedelta(days=1)
                data_inicial_str = data_inicial.strftime('%d/%m/%Y')
            else:
                data_inicial_str = ''
            
            contas_com_data.append({
                'Nome': conta,
                'Tipo': 1,
                'Ativo': 'Sim',
                'DataInicial': data_inicial_str
            })
        
        # Criar DataFrame final
        contas_correntes = pd.DataFrame(contas_com_data)
        contas_correntes['Codigo'] = range(1, len(contas_correntes) + 1)
        
        return contas_correntes
    
    def _processar_contatos(self, dados_lancamentos: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai contatos únicos dos lançamentos conforme especificação Vyco
        
        Args:
            dados_lancamentos: DataFrame com lançamentos
            
        Returns:
            pd.DataFrame: Contatos no formato Vyco completo
        """
        # Encontrar coluna de contato com busca mais ampla
        colunas_contato = []
        for col in dados_lancamentos.columns:
            col_lower = col.lower()
            if any(palavra in col_lower for palavra in ['contato', 'cliente', 'fornecedor', 'pessoa', 'empresa']):
                colunas_contato.append(col)
        
        # Se não encontrou por nome, verificar se existe coluna 'Contato' diretamente
        if not colunas_contato and 'Contato' in dados_lancamentos.columns:
            colunas_contato = ['Contato']

        if not colunas_contato:
            # Retornar DataFrame vazio com todas as colunas necessárias
            return pd.DataFrame(columns=[
                'Nome', 'Tipo', 'Documento', 'E-mail', 'Enviar e-mail?',
                'Telefone Residencial', 'Telefone Comercial', 'Telefone Celular',
                'Contribuinte ICMS?', 'Inscrição Estadual', 'Inscrição Municipal'
            ])
        
        coluna_contato = colunas_contato[0]

        # Obter valores únicos, removendo vazios e nulos
        contatos_series = dados_lancamentos[coluna_contato].dropna()
        contatos_series = contatos_series[contatos_series != '']  # Remover strings vazias
        contatos_unicos = contatos_series.unique()

        # Criar DataFrame com estrutura completa do Vyco
        contatos_data = []
        for contato in contatos_unicos:
            # Ignorar valores nulos ou vazios
            if pd.notna(contato) and str(contato).strip() != '':
                contatos_data.append({
                    'Nome': str(contato).strip(),
                    'Tipo': 0,  # 0 - Não Identificado (padrão)
                    'Documento': '',  # Vazio
                    'E-mail': '',  # Vazio
                    'Enviar e-mail?': '',  # Não
                    'Telefone Residencial': '',  # Vazio
                    'Telefone Comercial': '',  # Vazio
                    'Telefone Celular': '',  # Vazio
                    'Contribuinte ICMS?': '',  # Não
                    'Inscrição Estadual': '',  # Vazio
                    'Inscrição Municipal': ''  # Vazio
                })

        return pd.DataFrame(contatos_data)

    def _processar_lancamentos(self, dados_lancamentos: pd.DataFrame) -> pd.DataFrame:
        """
        Processa lançamentos do V1 para formato Vyco
        IMPORTANTE: dados_lancamentos já devem vir com mapeamento de categorias aplicado
        
        Args:
            dados_lancamentos: DataFrame com lançamentos do V1 (já com mapeamento aplicado)
            
        Returns:
            pd.DataFrame: Lançamentos no formato Vyco
        """
        # Criar DataFrame com a estrutura Vyco completa
        lancamentos_vyco = pd.DataFrame()
        
        # Mapeamento direto das colunas V1 para Vyco
        # IMPORTANTE: usar dados_lancamentos que já vem com mapeamento aplicado
        
        # Campos obrigatórios - mapeamento direto
        lancamentos_vyco['Confirmado'] = dados_lancamentos['Confirmado'] if 'Confirmado' in dados_lancamentos.columns else 'Sim'
        # Para Data, fazer cópia direta primeiro (será tratada no final)
        lancamentos_vyco['Data'] = dados_lancamentos['Data'] if 'Data' in dados_lancamentos.columns else ''
        lancamentos_vyco['Valor'] = dados_lancamentos['Valor'] if 'Valor' in dados_lancamentos.columns else 0
        # Usar dados já com mapeamento aplicado
        lancamentos_vyco['Categoria'] = dados_lancamentos['Categoria'] if 'Categoria' in dados_lancamentos.columns else ''
        
        # Campos opcionais - podem ser nulos
        lancamentos_vyco['Data Emissão'] = None  # Campo não existe no V1, pode ser nulo
        lancamentos_vyco['Valor Emissão'] = None  # Campo não existe no V1, pode ser nulo
        lancamentos_vyco['Repetição'] = 0  # 0 = Única (padrão conforme especificação)
        
        # Campos com mapeamento direto
        lancamentos_vyco['Total Parcelas'] = dados_lancamentos['Parcela'] if 'Parcela' in dados_lancamentos.columns else 1
        lancamentos_vyco['Descrição'] = dados_lancamentos['Descricao'] if 'Descricao' in dados_lancamentos.columns else ''
        lancamentos_vyco['Centro de Custo'] = dados_lancamentos['CentroDeCusto'] if 'CentroDeCusto' in dados_lancamentos.columns else None
        lancamentos_vyco['Conta Corrente'] = dados_lancamentos['Conta'] if 'Conta' in dados_lancamentos.columns else None
        lancamentos_vyco['Contato'] = dados_lancamentos['Contato'] if 'Contato' in dados_lancamentos.columns else None
        
        # Garantir que campos obrigatórios não sejam nulos (mas preservar dados originais)
        lancamentos_vyco['Confirmado'] = lancamentos_vyco['Confirmado'].fillna('Sim')
        # IMPORTANTE: Preservar datas originais - não alterar dados do usuário
        # Se a data original estava vazia, deve continuar vazia
        lancamentos_vyco['Valor'] = lancamentos_vyco['Valor'].fillna(0)
        lancamentos_vyco['Categoria'] = lancamentos_vyco['Categoria'].fillna('')
        
        return lancamentos_vyco
    
    def _processar_transferencias(self, dados_transferencias: pd.DataFrame) -> pd.DataFrame:
        """
        Processa transferências do V1 para formato Vyco
        
        Args:
            dados_transferencias: DataFrame com transferências do V1
            
        Returns:
            pd.DataFrame: Transferências no formato Vyco
        """
        if dados_transferencias.empty:
            return pd.DataFrame(columns=['Data', 'Valor', 'Descrição', 'Conta Débito', 'Conta Crédito'])
        
        transferencias_vyco = dados_transferencias.copy()
        
        # Processar coluna Movimentação para extrair Conta Débito e Conta Crédito
        if 'Movimentação' in transferencias_vyco.columns:
            contas_debito = []
            contas_credito = []
            
            for movimentacao in transferencias_vyco['Movimentação']:
                if pd.isna(movimentacao) or ' para ' not in str(movimentacao):
                    contas_debito.append('')
                    contas_credito.append('')
                else:
                    partes = str(movimentacao).split(' para ', 1)
                    if len(partes) == 2:
                        contas_debito.append(partes[0].strip())
                        contas_credito.append(partes[1].strip())
                    else:
                        contas_debito.append('')
                        contas_credito.append('')
            
            transferencias_vyco['Conta Débito'] = contas_debito
            transferencias_vyco['Conta Crédito'] = contas_credito
            
            # Remover coluna original
            transferencias_vyco = transferencias_vyco.drop('Movimentação', axis=1)
        
        # Garantir que temos todas as colunas obrigatórias
        colunas_obrigatorias = ['Data', 'Valor', 'Descrição', 'Conta Débito', 'Conta Crédito']
        
        for coluna in colunas_obrigatorias:
            if coluna not in transferencias_vyco.columns:
                if coluna == 'Data':
                    transferencias_vyco[coluna] = datetime.now().strftime('%d/%m/%Y')
                elif coluna == 'Valor':
                    transferencias_vyco[coluna] = 0.0
                else:
                    transferencias_vyco[coluna] = ''
        
        # IMPORTANTE: Preservar datas originais - não alterar dados do usuário
        # Se a data original estava vazia, deve continuar vazia
        
        # Reordenar colunas conforme modelo
        transferencias_vyco = transferencias_vyco[colunas_obrigatorias]
        
        return transferencias_vyco
    
    def obter_estatisticas_processamento(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do processamento
        
        Returns:
            Dict: Estatísticas dos dados processados
        """
        estatisticas = {}
        
        for nome_planilha, dados in self.dados_processados.items():
            estatisticas[nome_planilha] = {
                'total_registros': len(dados),
                'colunas': list(dados.columns),
                'registros_vazios': dados.isnull().sum().to_dict()
            }
        
        return estatisticas