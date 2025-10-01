import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

# Importar módulos personalizados
from modulos.manipulador_arquivos import ManipuladorArquivos
from modulos.processador_dados import ProcessadorDados
from modulos.mapeador_categorias import MapeadorCategorias
from modulos.gerador_excel import GeradorExcel

def configurar_pagina():
    """Configura a página do Streamlit"""
    st.set_page_config(
        page_title="Conversor V1 para Vyco",
        page_icon="🔄",
        layout="wide"
    )
    
    st.title("🔄 Conversor do Sistema V1 para Vyco")
    st.markdown("### Sistema de Conversão de Fluxo de Caixa")
    
    # Aviso sobre processamento em nuvem
    st.info("☁️ **Versão Nuvem:** Todos os dados são processados em memória - nenhum arquivo é salvo no servidor!")
    
    st.markdown("---")

def exibir_progresso(etapa_atual):
    """Exibe barra de progresso das etapas"""
    etapas = [
        "Upload de Lançamentos",
        "Upload de Transferências", 
        "Upload de Categorias",
        "Validação de Categorias",
        "Geração das Planilhas"
    ]
    
    progresso = (etapa_atual / len(etapas)) * 100
    st.progress(progresso / 100)
    
    # Mostrar etapas
    col1, col2, col3, col4, col5 = st.columns(5)
    colunas = [col1, col2, col3, col4, col5]
    
    for i, etapa in enumerate(etapas):
        with colunas[i]:
            if i < etapa_atual:
                st.success(f"✅ {etapa}")
            elif i == etapa_atual:
                st.info(f"🔄 {etapa}")
            else:
                st.write(f"⏳ {etapa}")

def main():
    """Função principal da aplicação"""
    configurar_pagina()
    
    # Botão para reiniciar processo
    if st.button("🔄 Reiniciar Processo", help="Limpa todos os dados e reinicia"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Inicializar estado da sessão
    if 'etapa_atual' not in st.session_state:
        st.session_state.etapa_atual = 0
    if 'dados_lancamentos' not in st.session_state:
        st.session_state.dados_lancamentos = None
    if 'dados_transferencias' not in st.session_state:
        st.session_state.dados_transferencias = None
    if 'dados_categorias' not in st.session_state:
        st.session_state.dados_categorias = None
    if 'mapeamento_categorias' not in st.session_state:
        st.session_state.mapeamento_categorias = {}
    
    # Exibir progresso
    exibir_progresso(st.session_state.etapa_atual)
    
    # Executar etapa atual
    manipulador = ManipuladorArquivos()
    processador = ProcessadorDados()
    mapeador = MapeadorCategorias()
    
    if st.session_state.etapa_atual == 0:
        etapa_upload_lancamentos(manipulador)
    elif st.session_state.etapa_atual == 1:
        etapa_upload_transferencias(manipulador)
    elif st.session_state.etapa_atual == 2:
        etapa_upload_categorias(manipulador)
    elif st.session_state.etapa_atual == 3:
        etapa_validacao_categorias(mapeador)
    elif st.session_state.etapa_atual == 4:
        etapa_geracao_planilhas(processador)

def etapa_upload_lancamentos(manipulador):
    """Etapa 1: Upload do arquivo de lançamentos"""
    st.header("📊 Etapa 1: Upload do Arquivo de Lançamentos")
    st.info("Faça upload do arquivo 'RelatorioDetalhado.xlsx' do sistema V1")
    
    arquivo_lancamentos = st.file_uploader(
        "Selecione o arquivo de lançamentos",
        type=['xlsx', 'xls'],
        key="upload_lancamentos"
    )
    
    if arquivo_lancamentos:
        try:
            dados = manipulador.ler_excel(arquivo_lancamentos)
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Mostrar preview dos dados
            st.subheader("Preview dos Dados")
            st.dataframe(dados.head(10))
            
            # Mostrar informações do arquivo
            st.info(f"📋 Total de registros: {len(dados)}")
            st.info(f"📅 Colunas encontradas: {list(dados.columns)}")
            
            # Botão para prosseguir
            if st.button("➡️ Prosseguir para Próxima Etapa", type="primary"):
                st.session_state.dados_lancamentos = dados
                st.session_state.etapa_atual = 1
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

def etapa_upload_transferencias(manipulador):
    """Etapa 2: Upload do arquivo de transferências"""
    st.header("💸 Etapa 2: Upload do Arquivo de Transferências")
    st.info("Faça upload do arquivo 'Transferencias.xlsx' do sistema V1")
    
    arquivo_transferencias = st.file_uploader(
        "Selecione o arquivo de transferências",
        type=['xlsx', 'xls'],
        key="upload_transferencias"
    )
    
    if arquivo_transferencias:
        try:
            dados = manipulador.ler_excel(arquivo_transferencias)
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Mostrar preview dos dados
            st.subheader("Preview dos Dados")
            st.dataframe(dados.head(10))
            
            # Mostrar informações do arquivo
            st.info(f"📋 Total de registros: {len(dados)}")
            st.info(f"📅 Colunas encontradas: {list(dados.columns)}")
            
            # Botões de navegação
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Voltar"):
                    st.session_state.etapa_atual = 0
                    st.rerun()
            with col2:
                if st.button("➡️ Prosseguir para Próxima Etapa", type="primary"):
                    st.session_state.dados_transferencias = dados
                    st.session_state.etapa_atual = 2
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

def etapa_upload_categorias(manipulador):
    """Etapa 3: Upload do arquivo de categorias"""
    st.header("📂 Etapa 3: Upload do Plano de Contas (Categorias)")
    st.info("Faça upload do arquivo 'Categorias.xlsx' do sistema V1")
    
    arquivo_categorias = st.file_uploader(
        "Selecione o arquivo de categorias",
        type=['xlsx', 'xls'],
        key="upload_categorias"
    )
    
    if arquivo_categorias:
        try:
            dados = manipulador.ler_excel(arquivo_categorias)
            st.success("✅ Arquivo carregado com sucesso!")
            
            # Mostrar preview dos dados
            st.subheader("Preview dos Dados")
            st.dataframe(dados.head(10))
            
            # Mostrar informações do arquivo
            st.info(f"📋 Total de registros: {len(dados)}")
            st.info(f"📅 Colunas encontradas: {list(dados.columns)}")
            
            # Botões de navegação
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Voltar"):
                    st.session_state.etapa_atual = 1
                    st.rerun()
            with col2:
                if st.button("➡️ Prosseguir para Validação", type="primary"):
                    st.session_state.dados_categorias = dados
                    st.session_state.etapa_atual = 3
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")

def etapa_validacao_categorias(mapeador):
    """Etapa 4: Validação e mapeamento de categorias"""
    st.header("🔍 Etapa 4: Validação de Categorias")
    st.info("Verifique se há categorias antigas que precisam ser mapeadas para o novo plano de contas")
    
    if st.session_state.dados_lancamentos is not None and st.session_state.dados_categorias is not None:
        
        # Configuração fixa de colunas
        st.subheader("🔧 Configuração de Colunas")
        st.info("Usando configuração padrão para análise de categorias:")
        
        # Definir colunas fixas
        coluna_lancamentos_fixa = "Categoria"
        coluna_plano_fixa = "Nome"
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"**Coluna de categoria nos Lançamentos:** `{coluna_lancamentos_fixa}`")
            
        with col2:
            st.success(f"**Coluna de categoria no Plano de Contas:** `{coluna_plano_fixa}`")
        
        # Validar se as colunas existem nos dados
        erro_coluna = False
        if coluna_lancamentos_fixa not in st.session_state.dados_lancamentos.columns:
            st.error(f"❌ Coluna '{coluna_lancamentos_fixa}' não encontrada nos lançamentos")
            st.info(f"Colunas disponíveis: {list(st.session_state.dados_lancamentos.columns)}")
            erro_coluna = True
            
        if coluna_plano_fixa not in st.session_state.dados_categorias.columns:
            st.error(f"❌ Coluna '{coluna_plano_fixa}' não encontrada no plano de contas")
            st.info(f"Colunas disponíveis: {list(st.session_state.dados_categorias.columns)}")
            erro_coluna = True
        
        st.markdown("---")
        
        # Análise de categorias - usar colunas fixas
        if not erro_coluna:
            try:
                st.success(f"✅ Analisando: '{coluna_lancamentos_fixa}' vs '{coluna_plano_fixa}'")
                
                categorias_inconsistentes = mapeador.encontrar_categorias_inconsistentes(
                    st.session_state.dados_lancamentos,
                    st.session_state.dados_categorias,
                    coluna_lancamentos_fixa,
                    coluna_plano_fixa
                )
                
                if categorias_inconsistentes:
                    st.warning(f"⚠️ Encontradas {len(categorias_inconsistentes)} categorias que precisam ser mapeadas:")
                    
                    # Mostrar categorias inconsistentes
                    with st.expander("📋 Ver categorias inconsistentes", expanded=True):
                        for cat in categorias_inconsistentes:
                            st.write(f"• {cat}")
                    
                    # Interface de mapeamento
                    st.subheader("🔄 Mapeamento de Categorias")
                    categorias_validas = mapeador.obter_categorias_validas(
                        st.session_state.dados_categorias, 
                        coluna_plano_fixa
                    )
                    
                    if not categorias_validas:
                        st.error("❌ Não foi possível obter categorias válidas do plano de contas")
                        st.info("💡 Verifique se o arquivo de categorias está correto")
                    else:
                        for categoria_antiga in categorias_inconsistentes:
                            st.write(f"**Categoria antiga:** `{categoria_antiga}`")
                            nova_categoria = st.selectbox(
                                f"Selecione a nova categoria:",
                                options=["-- Selecione --"] + categorias_validas,
                                key=f"mapeamento_{categoria_antiga}",
                                help=f"Escolha uma categoria válida para substituir '{categoria_antiga}'"
                            )
                            if nova_categoria != "-- Selecione --":
                                # Calcular quantas categorias serão alteradas
                                count_alteracoes = st.session_state.dados_lancamentos[
                                    st.session_state.dados_lancamentos['Categoria'] == categoria_antiga
                                ].shape[0]
                                
                                st.session_state.mapeamento_categorias[categoria_antiga] = nova_categoria
                                st.success(f"✅ **{categoria_antiga}** → **{nova_categoria}**")
                                st.info(f"📊 **{count_alteracoes} registros** serão alterados")
                                
                                # Mostrar amostra dos registros que serão alterados
                                registros_afetados = st.session_state.dados_lancamentos[
                                    st.session_state.dados_lancamentos['Categoria'] == categoria_antiga
                                ].head(5)
                                
                                if not registros_afetados.empty:
                                    st.write("📋 **Amostra dos registros que serão alterados:**")
                                    colunas_para_mostrar = ['Data', 'Descrição', 'Categoria', 'Valor']
                                    colunas_existentes = [col for col in colunas_para_mostrar if col in registros_afetados.columns]
                                    st.dataframe(registros_afetados[colunas_existentes], use_container_width=True)
                            st.markdown("---")
                else:
                    st.success("✅ Todas as categorias estão consistentes!")
                    
            except Exception as e:
                st.error(f"❌ Erro na validação de categorias: {str(e)}")
                st.info("💡 Verifique se as colunas 'Categoria' e 'Nome' existem nos arquivos")
        else:
            st.warning("⚠️ Corrija os erros de coluna para continuar")
        
        # Botões de navegação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Voltar"):
                st.session_state.etapa_atual = 2
                st.rerun()
        with col2:
            # Verificar se o mapeamento está completo antes de prosseguir
            categorias_pendentes = []
            if not erro_coluna:
                try:
                    categorias_inconsistentes = mapeador.encontrar_categorias_inconsistentes(
                        st.session_state.dados_lancamentos,
                        st.session_state.dados_categorias,
                        coluna_lancamentos_fixa,
                        coluna_plano_fixa
                    )
                    categorias_pendentes = [cat for cat in categorias_inconsistentes 
                                          if cat not in st.session_state.mapeamento_categorias 
                                          or not st.session_state.mapeamento_categorias[cat]]
                except:
                    categorias_pendentes = []
            else:
                st.warning("⚠️ Corrija os erros de coluna para verificar o mapeamento")
            
            if categorias_pendentes:
                st.warning(f"⚠️ {len(categorias_pendentes)} categorias ainda precisam ser mapeadas")
                st.button("➡️ Gerar Planilhas", disabled=True, help="Complete o mapeamento de categorias primeiro")
            else:
                # Mostrar mapeamento atual para confirmação
                if st.session_state.mapeamento_categorias:
                    # Calcular total de registros afetados
                    total_registros_afetados = 0
                    for categoria_antiga in st.session_state.mapeamento_categorias.keys():
                        count = st.session_state.dados_lancamentos[
                            st.session_state.dados_lancamentos['Categoria'] == categoria_antiga
                        ].shape[0]
                        total_registros_afetados += count
                    
                    st.success("✅ Mapeamento de categorias definido:")
                    st.info(f"🔢 **Total de {total_registros_afetados} registros** serão alterados")
                    
                    with st.expander("📋 Ver detalhes do mapeamento", expanded=True):
                        for antiga, nova in st.session_state.mapeamento_categorias.items():
                            count = st.session_state.dados_lancamentos[
                                st.session_state.dados_lancamentos['Categoria'] == antiga
                            ].shape[0]
                            st.write(f"• **{antiga}** → **{nova}** ({count} registros)")
                else:
                    st.info("ℹ️ Nenhum mapeamento de categoria necessário")
                
                if st.button("➡️ Gerar Planilhas", type="primary"):
                    st.session_state.etapa_atual = 4
                    st.rerun()

def etapa_geracao_planilhas(processador):
    """Etapa 5: Geração das planilhas finais"""
    st.header("📋 Etapa 5: Geração das Planilhas Vyco")
    st.info("Gerando todas as planilhas no formato do sistema Vyco...")
    
    # Aviso importante sobre arquivos abertos
    try:
        # Processar dados
        dados_processados = processador.processar_todos_os_dados(
            st.session_state.dados_lancamentos,
            st.session_state.dados_transferencias,
            st.session_state.dados_categorias,
            st.session_state.mapeamento_categorias
        )
        
        # Gerar planilhas em memória (sem salvar no disco)
        gerador = GeradorExcel()
        arquivos_memoria = gerador.gerar_planilhas_memoria(dados_processados)
        
        if arquivos_memoria:
            st.success(f"✅ {len(arquivos_memoria)} planilhas geradas com sucesso!")
            
            # Mostrar arquivos gerados
            st.write("### 📁 Arquivos Gerados:")
            for i, (nome, conteudo) in enumerate(arquivos_memoria.items(), 1):
                tamanho = len(conteudo) / 1024  # KB
                st.write(f"{i}. **{nome}** ({tamanho:.1f} KB)")
            
            # Criar ZIP em memória para download
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for nome_arquivo, conteudo in arquivos_memoria.items():
                    zipf.writestr(nome_arquivo, conteudo)
            
            nome_zip = f"planilhas_vyco_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            # Botão de download do ZIP
            st.download_button(
                label="📥 Baixar Todas as Planilhas (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=nome_zip,
                mime="application/zip",
                type="primary"
            )
            
            # Downloads individuais
            st.write("### 📄 Downloads Individuais:")
            col1, col2 = st.columns(2)
            
            for i, (nome_arquivo, conteudo) in enumerate(arquivos_memoria.items()):
                with col1 if i % 2 == 0 else col2:
                    st.download_button(
                        label=f"📝 {nome_arquivo.replace('.xlsx', '')}",
                        data=conteudo,
                        file_name=nome_arquivo,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        
        else:
            st.error("❌ Nenhuma planilha foi gerada. Verifique os dados e tente novamente.")
        
        # Botão para reiniciar
        st.write("---")
        if st.button("🔄 Fazer Nova Conversão", type="secondary"):
            # Limpar estado da sessão
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Erro ao gerar planilhas: {str(e)}")
        st.write("**Detalhes do erro:**")
        st.code(str(e))
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Tentar Novamente"):
                st.rerun()
        with col2:
            if st.button("⬅️ Voltar"):
                st.session_state.etapa_atual = 3
                st.rerun()

if __name__ == "__main__":
    main()