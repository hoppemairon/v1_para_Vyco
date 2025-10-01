# 🔄 Conversor V1 para Vyco - Versão Nuvem

Sistema de conversão de dados do V1 para formato Vyco, otimizado para deployment em nuvem.

## ☁️ Características da Versão Nuvem

- **Processamento em Memória:** Todos os dados são processados na RAM - nenhum arquivo é salvo no servidor
- **Downloads Diretos:** Arquivos gerados ficam disponíveis para download imediato
- **Sem Persistência:** Ideal para ambientes de nuvem onde o armazenamento temporário não é desejável
- **Segurança:** Dados não ficam armazenados no servidor após o processamento

## 🚀 Funcionalidades

### ✅ Upload de Arquivos
- Lançamentos (RelatorioDetalhado.xlsx)
- Transferências (Transferencias.xlsx) 
- Categorias (Categorias.xlsx)

### ✅ Mapeamento de Categorias
- Interface visual para mapear categorias do V1 para Vyco
- Visualização de quantos registros serão afetados
- Validação automática de categorias inconsistentes

### ✅ Geração de Planilhas
- **6 arquivos Excel** gerados automaticamente:
  - Cadastros - Categorias.xlsx
  - Cadastros - Centros de Custo.xlsx
  - Cadastros - Contas Corrente.xlsx
  - Cadastros - Contatos.xlsx
  - Financeiro - Lançamentos.xlsx
  - Financeiro - Transferências.xlsx

### ✅ Downloads
- **ZIP completo** com todas as planilhas
- **Downloads individuais** de cada arquivo
- **Processamento em tempo real** sem necessidade de armazenamento

## 🛠️ Instalação Local

```bash
# Clonar repositório
git clone [seu-repositorio]
cd conversor_V1_Vyco

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

## 🌐 Deploy em Nuvem

### Streamlit Cloud
1. Faça fork do repositório
2. Conecte no [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy automático a partir do GitHub

### Heroku
```bash
# Criar Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
git add .
git commit -m "Deploy para Heroku"
git push heroku main
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

## 📋 Estrutura do Projeto

```
conversor_V1_Vyco/
├── app.py                     # Interface principal Streamlit
├── modulos/
│   ├── processador_dados.py   # Processamento e transformação
│   ├── gerador_excel.py       # Geração de arquivos Excel
│   ├── mapeador_categorias.py # Mapeamento de categorias
│   └── manipulador_arquivos.py # Manipulação de arquivos
├── modelos_vyco/              # Templates do Vyco
├── preenchimento_vyco/        # Arquivos de apoio
├── requirements.txt           # Dependências Python
└── .gitignore                 # Arquivos ignorados pelo Git
```

## 🔧 Tecnologias

- **Streamlit:** Interface web
- **Pandas:** Manipulação de dados
- **OpenPyXL:** Geração de arquivos Excel
- **Python 3.11+:** Linguagem base

## 📝 Changelog da Versão Nuvem

### ✅ Melhorias Implementadas
- ✅ Processamento 100% em memória
- ✅ Remoção de todas as operações de arquivo temporário
- ✅ Downloads diretos via Streamlit
- ✅ Geração de ZIP em memória
- ✅ Interface otimizada para nuvem
- ✅ Eliminação de dependências de sistema de arquivos

### ❌ Funcionalidades Removidas
- ❌ Salvamento de arquivos no disco
- ❌ Diretórios temporários
- ❌ Cache de arquivos

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique se todos os arquivos Excel estão fechados
2. Use arquivos no formato correto (.xlsx)
3. Certifique-se de que os dados estão completos

---

**Versão:** 2.0 - Nuvem
**Última Atualização:** Setembro 2025