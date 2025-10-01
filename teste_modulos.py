"""
Script para testar o funcionamento dos módulos do conversor
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from modulos import ManipuladorArquivos, ProcessadorDados, MapeadorCategorias, GeradorExcel

def criar_dados_teste():
    """Cria dados de teste para demonstrar o funcionamento"""
    
    # Criar dados de lançamentos de exemplo
    dados_lancamentos = pd.DataFrame({
        'Data': [
            '01/01/2024', '02/01/2024', '03/01/2024', '04/01/2024', '05/01/2024'
        ],
        'Descricao': [
            'Venda de produtos', 'Pagamento fornecedor', 'Recebimento cliente', 
            'Despesa escritório', 'Taxa bancária'
        ],
        'Categoria': [
            'Receita Vendas', 'Despesa Fornecedores', 'Receita Serviços',
            'Despesa Administrativa', 'Despesa Bancária'
        ],
        'Valor': [1500.00, -800.00, 2200.00, -300.00, -25.00],
        'Conta Corrente': ['Banco A', 'Banco A', 'Banco B', 'Banco A', 'Banco A'],
        'Contato': ['Cliente X', 'Fornecedor Y', 'Cliente Z', 'Papelaria ABC', 'Banco A'],
        'Centro de Custo': ['Vendas', 'Compras', 'Vendas', 'Administrativo', 'Financeiro']
    })
    
    # Criar dados de transferências de exemplo
    dados_transferencias = pd.DataFrame({
        'Data': ['01/01/2024', '15/01/2024', '30/01/2024'],
        'Conta Origem': ['Banco A', 'Banco B', 'Banco A'],
        'Conta Destino': ['Banco B', 'Banco C', 'Banco C'],
        'Valor': [500.00, 1000.00, 750.00],
        'Descricao': ['Transferência para investimento', 'Equalização de saldos', 'Reserva de emergência']
    })
    
    # Criar dados de categorias de exemplo (plano de contas atual)
    dados_categorias = pd.DataFrame({
        'Codigo': ['1.01', '1.02', '2.01', '2.02', '2.03'],
        'Nome': [
            'Receita de Vendas', 'Receita de Serviços', 'Despesa com Fornecedores',
            'Despesa Administrativa', 'Despesa Financeira'
        ],
        'Tipo': ['Receita', 'Receita', 'Despesa', 'Despesa', 'Despesa']
    })
    
    return dados_lancamentos, dados_transferencias, dados_categorias

def testar_manipulador_arquivos():
    """Testa o módulo ManipuladorArquivos"""
    print("🔍 Testando ManipuladorArquivos...")
    
    manipulador = ManipuladorArquivos()
    
    # Criar dados de teste
    dados_teste = pd.DataFrame({
        'Coluna1': [1, 2, 3],
        'Coluna2': ['A', 'B', 'C']
    })
    
    # Testar limpeza de dados
    dados_limpos = manipulador._limpar_dados_basicos(dados_teste)
    print(f"✅ Dados limpos: {len(dados_limpos)} registros")
    
    # Testar informações do arquivo
    info = manipulador.obter_informacoes_arquivo(dados_teste)
    print(f"✅ Informações obtidas: {info['total_registros']} registros, {info['total_colunas']} colunas")

def testar_processador_dados():
    """Testa o módulo ProcessadorDados"""
    print("\n🔄 Testando ProcessadorDados...")
    
    processador = ProcessadorDados()
    dados_lancamentos, dados_transferencias, dados_categorias = criar_dados_teste()
    
    # Simular mapeamento de categorias
    mapeamento = {
        'Receita Vendas': 'Receita de Vendas',
        'Despesa Fornecedores': 'Despesa com Fornecedores',
        'Receita Serviços': 'Receita de Serviços',
        'Despesa Administrativa': 'Despesa Administrativa',
        'Despesa Bancária': 'Despesa Financeira'
    }
    
    # Processar todos os dados
    dados_processados = processador.processar_todos_os_dados(
        dados_lancamentos, dados_transferencias, dados_categorias, mapeamento
    )
    
    print(f"✅ Dados processados:")
    for tipo, dados in dados_processados.items():
        print(f"   - {tipo}: {len(dados)} registros")

def testar_mapeador_categorias():
    """Testa o módulo MapeadorCategorias"""
    print("\n🗺️ Testando MapeadorCategorias...")
    
    mapeador = MapeadorCategorias()
    dados_lancamentos, _, dados_categorias = criar_dados_teste()
    
    # Encontrar categorias inconsistentes
    inconsistentes = mapeador.encontrar_categorias_inconsistentes(
        dados_lancamentos, dados_categorias
    )
    
    print(f"✅ Categorias inconsistentes encontradas: {len(inconsistentes)}")
    for categoria in inconsistentes:
        print(f"   - {categoria}")
    
    # Obter categorias válidas
    validas = mapeador.obter_categorias_validas(dados_categorias)
    print(f"✅ Categorias válidas: {len(validas)}")

def testar_gerador_excel():
    """Testa o módulo GeradorExcel"""
    print("\n📊 Testando GeradorExcel...")
    
    gerador = GeradorExcel()
    
    # Criar dados de exemplo para gerar Excel
    dados_exemplo = {
        'categorias': pd.DataFrame({
            'Codigo': ['1.01', '2.01'],
            'Nome': ['Receita', 'Despesa'],
            'Tipo': ['Receita', 'Despesa'],
            'Ativo': ['Sim', 'Sim']
        }),
        'lancamentos': pd.DataFrame({
            'Data': ['01/01/2024', '02/01/2024'],
            'Descricao': ['Teste 1', 'Teste 2'],
            'Valor': [100.00, -50.00],
            'Categoria': ['Receita', 'Despesa']
        })
    }
    
    # Criar diretório de teste
    diretorio_teste = "teste_saida"
    os.makedirs(diretorio_teste, exist_ok=True)
    
    # Testar formatação específica
    for tipo, dados in dados_exemplo.items():
        dados_formatados = gerador._aplicar_formatacao_especifica(tipo, dados)
        print(f"✅ {tipo} formatado: {len(dados_formatados)} registros")

def executar_todos_os_testes():
    """Executa todos os testes dos módulos"""
    print("🚀 Iniciando testes dos módulos do Conversor V1 para Vyco")
    print("=" * 60)
    
    try:
        testar_manipulador_arquivos()
        testar_processador_dados()
        testar_mapeador_categorias()
        testar_gerador_excel()
        
        print("\n" + "=" * 60)
        print("✅ Todos os testes foram executados com sucesso!")
        print("🎉 Sistema pronto para uso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        print("🔧 Verifique a instalação das dependências")

if __name__ == "__main__":
    executar_todos_os_testes()