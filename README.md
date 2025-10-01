# Conversor do Sistema V1 para Vyco

Sistema desenvolvido em Python com Streamlit para converter dados financeiros do sistema V1 para o formato do sistema Vyco.

## 📋 Funcionalidades

- **Interface Web Intuitiva**: Aplicação Streamlit com processo passo-a-passo
- **Upload de Arquivos**: Suporte para arquivos Excel (.xlsx, .xls)
- **Validação de Dados**: Verificação automática de consistência
- **Mapeamento de Categorias**: Interface interativa para mapear categorias antigas para novas
- **Geração Automática**: Criação de todas as planilhas no formato Vyco
- **Download em Lote**: Download de todas as planilhas em arquivo ZIP

## 🚀 Como Usar

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Aplicação

```bash
# Iniciar aplicação Streamlit
streamlit run app.py
```

### 3. Processo de Conversão

O sistema guia você através de 5 etapas:

1. **Upload de Lançamentos**: Carregar arquivo `RelatorioDetalhado.xlsx`
2. **Upload de Transferências**: Carregar arquivo `Transferencias.xlsx`
3. **Upload de Categorias**: Carregar arquivo `Categorias.xlsx`
4. **Validação de Categorias**: Mapear categorias antigas para novas
5. **Geração de Planilhas**: Download das planilhas convertidas

## 📁 Estrutura do Projeto

```
conversor_V1_Vyco/
├── app.py                          # Aplicação principal Streamlit
├── requirements.txt                # Dependências Python
├── README.md                      # Documentação
├── modulos/                       # Módulos do sistema
│   ├── __init__.py
│   ├── manipulador_arquivos.py    # Manipulação de arquivos Excel
│   ├── processador_dados.py       # Processamento e transformação
│   ├── mapeador_categorias.py     # Mapeamento de categorias
│   └── gerador_excel.py          # Geração das planilhas finais
├── modelos_v1/                    # Arquivos de entrada (V1)
│   ├── Categorias.xlsx
│   ├── RelatorioDetalhado.xlsx
│   └── Transferencias.xlsx
├── modelos_vyco/                  # Modelos de saída (Vyco)
│   ├── Cadastros - Categorias.xlsx
│   ├── Cadastros - Centros de Custo.xlsx
│   ├── Cadastros - Contas Corrente.xlsx
│   ├── Cadastros - Contatos.xlsx
│   ├── Financeiro - Lançamentos.xlsx
│   └── Financeiro - Transferências.xlsx
└── preenchimento_vyco/            # Instruções de preenchimento
    ├── Cadastros - Categorias.txt
    ├── Cadastros - Centros de Custo.txt
    ├── Cadastros - Contas Corrente.txt
    ├── Cadastros - Contatos.txt
    ├── Financeiro - Lançamentos.txt
    └── Financeiro - Transferências.txt
```

## 📊 Arquivos Gerados

O sistema gera as seguintes planilhas no formato Vyco:

### Cadastros
- **Categorias**: Plano de contas
- **Centros de Custo**: Centros de custo únicos
- **Contas Correntes**: Contas bancárias
- **Contatos**: Clientes e fornecedores

### Financeiro
- **Lançamentos**: Movimentações financeiras
- **Transferências**: Transferências entre contas

## 🔧 Configuração

### Arquivos de Entrada (Sistema V1)

Coloque os seguintes arquivos na pasta `modelos_v1/`:

- `RelatorioDetalhado.xlsx`: Lançamentos do sistema V1
- `Transferencias.xlsx`: Transferências do sistema V1
- `Categorias.xlsx`: Plano de contas do sistema V1

### Modelos de Saída

Os modelos Vyco em `modelos_vyco/` são usados como referência para a estrutura das planilhas geradas.

### Instruções de Preenchimento

Os arquivos `.txt` em `preenchimento_vyco/` contêm as instruções de como cada campo deve ser preenchido.

## 🎯 Processo de Conversão

### 1. Extração de Dados
- Leitura dos arquivos Excel do V1
- Validação da estrutura dos dados
- Identificação das colunas relevantes

### 2. Processamento
- Limpeza e normalização dos dados
- Extração de valores únicos (categorias, contas, contatos, etc.)
- Aplicação de regras de negócio

### 3. Mapeamento de Categorias
- Comparação entre categorias antigas e novas
- Interface interativa para mapeamento
- Validação de consistência

### 4. Geração das Planilhas
- Aplicação do formato Vyco
- Formatação de datas e valores
- Validação final dos dados

## 🔍 Funcionalidades Avançadas

- **Preview de Dados**: Visualização dos dados antes do processamento
- **Validação Automática**: Verificação de colunas obrigatórias
- **Sugestão de Categorias**: Algoritmo de similaridade para sugerir mapeamentos
- **Estatísticas**: Informações detalhadas sobre os dados processados
- **Log de Operações**: Registro de todas as operações realizadas

## 📝 Notas Importantes

- Certifique-se de que os arquivos Excel estejam no formato correto
- Verifique se todas as colunas obrigatórias estão presentes
- O mapeamento de categorias é obrigatório para categorias inconsistentes
- Todas as planilhas são geradas simultaneamente

## 🆘 Suporte

Em caso de dúvidas ou problemas:

1. Verifique se todos os arquivos de entrada estão corretos
2. Consulte as instruções de preenchimento
3. Valide se as dependências estão instaladas corretamente

## 📈 Versão

Versão atual: 1.0.0

Sistema desenvolvido para facilitar a migração do sistema V1 para o sistema Vyco, mantendo a integridade dos dados financeiros.