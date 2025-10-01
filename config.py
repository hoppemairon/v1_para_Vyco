"""
Configurações do Sistema Conversor V1 para Vyco
"""

import os

# Configurações de Diretórios
DIRETORIO_MODELOS_V1 = "modelos_v1"
DIRETORIO_MODELOS_VYCO = "modelos_vyco"
DIRETORIO_PREENCHIMENTO = "preenchimento_vyco"
DIRETORIO_SAIDA = "planilhas_geradas"

# Configurações de Arquivos
ARQUIVOS_ENTRADA_V1 = {
    'lancamentos': 'RelatorioDetalhado.xlsx',
    'transferencias': 'Transferencias.xlsx',
    'categorias': 'Categorias.xlsx'
}

ARQUIVOS_SAIDA_VYCO = {
    'categorias': 'Cadastros - Categorias.xlsx',
    'centros_custo': 'Cadastros - Centros de Custo.xlsx',
    'contas_correntes': 'Cadastros - Contas Corrente.xlsx',
    'contatos': 'Cadastros - Contatos.xlsx',
    'lancamentos': 'Financeiro - Lançamentos.xlsx',
    'transferencias': 'Financeiro - Transferências.xlsx'
}

# Configurações de Colunas Esperadas
COLUNAS_ESPERADAS = {
    'categorias': ['Codigo', 'Nome', 'Tipo', 'Ativo'],
    'centros_custo': ['Codigo', 'Nome', 'Ativo'],
    'contas_correntes': ['Codigo', 'Nome', 'Tipo', 'Ativo'],
    'contatos': ['Codigo', 'Nome', 'Tipo', 'Ativo'],
    'lancamentos': ['Data', 'Descricao', 'Categoria', 'Valor', 'Tipo', 'ContaCorrente', 'Contato', 'CentroCusto'],
    'transferencias': ['Data', 'ContaOrigem', 'ContaDestino', 'Valor', 'Descricao', 'Status']
}

# Configurações de Mapeamento de Colunas (V1 para Vyco)
MAPEAMENTO_COLUNAS_V1 = {
    'data': ['data', 'dt_lancamento', 'data_lancamento', 'dt_movimento'],
    'descricao': ['descricao', 'historico', 'observacao', 'descr'],
    'valor': ['valor', 'vlr_lancamento', 'montante', 'vlr'],
    'categoria': ['categoria', 'plano_conta', 'conta', 'classificacao'],
    'conta_corrente': ['conta_corrente', 'banco', 'conta_banco', 'cc_banco'],
    'contato': ['contato', 'cliente', 'fornecedor', 'pessoa'],
    'centro_custo': ['centro_custo', 'cc', 'setor', 'departamento'],
    'conta_origem': ['conta_origem', 'de', 'origem', 'conta_saida'],
    'conta_destino': ['conta_destino', 'para', 'destino', 'conta_entrada']
}

# Configurações de Validação
EXTENSOES_SUPORTADAS = ['.xlsx', '.xls']
TAMANHO_MAXIMO_ARQUIVO = 50 * 1024 * 1024  # 50MB

# Configurações de Formatação
FORMATO_DATA = '%d/%m/%Y'
FORMATO_VALOR = '0.00'
ENCODING_PADRAO = 'utf-8'

# Configurações de Interface
CORES_INTERFACE = {
    'sucesso': '#28a745',
    'erro': '#dc3545',
    'aviso': '#ffc107',
    'info': '#17a2b8'
}

# Mensagens do Sistema
MENSAGENS = {
    'sucesso_upload': '✅ Arquivo carregado com sucesso!',
    'erro_upload': '❌ Erro ao carregar arquivo: {}',
    'aviso_colunas': '⚠️ Colunas obrigatórias não encontradas: {}',
    'info_processamento': 'ℹ️ Processando dados...',
    'sucesso_geracao': '✅ Planilhas geradas com sucesso!',
    'erro_geracao': '❌ Erro ao gerar planilhas: {}'
}

# Configurações de Log
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'