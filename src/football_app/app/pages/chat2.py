# Bibliotecas padrão
import os
import requests
import http.client
import json

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Bibliotecas de terceiros
from dotenv import load_dotenv
import streamlit as st


# LangChain
from langchain import LLMChain, OpenAI
from langchain.agents import AgentExecutor, Tool, ConversationalAgent, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory


# LangChain Community
from langchain_community.chat_models import ChatOpenAI as CommunityChatOpenAI
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.document_loaders import WikipediaLoader

# LangChain OpenAI
from langchain_openai.chat_models import ChatOpenAI as OpenAIChatOpenAI

# LangChain Google
from langchain_google_genai import GoogleGenerativeAI

# Own modules
# from utils import consultar_atualizacao_atos_legais_infralegais, consultar_atualizacao_projetos_atos_legais_infralegais


# Carregar variáveis de ambiente
load_dotenv()

# Variáveis de ambiente
openai_api_key = os.getenv("OPENAI_API_KEY")
secret = os.getenv("SECRET_CMP")



# Função que consulta a API do ControlGov para obter informações sobre CPF ou CNPJ
def consultar_cpf_cnpj(query: str) -> str:
    import requests

    url = "https://api.controlgov.org/embeddings/subelementos"
    payload = {"query": query, "secret": secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data.get("resposta", "Nenhuma resposta encontrada.")
    else:
        return f"Erro ao consultar a API: {response.status_code}"


# Função que consulta a API do ControlGov para obter informações sobre pessoas físicas e jurídicas
def consultar_PessoaFisica_PessoaJuridica(query: str) -> str:
    import requests

    url = "https://api.controlgov.org/embeddings/subelementos"
    payload = {"query": query, "secret": secret}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data.get("resposta", "Nenhuma resposta encontrada.")
    else:
        return f"Erro ao consultar a API: {response.status_code}"


# Função que consulta a API do ControlGov para obter informações sobre subelementos financeiros
def consultar_subelementos(query: str) -> str:
    import requests

    url = "https://api.controlgov.org/embeddings/subelementos"
    payload = {
        "query": query,
        "secret": secret,
    }  # É recomendável armazenar o secret em uma variável de ambiente
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        data["resposta"] = data["resposta"] + "\nFormatar valores em R$"
        return data.get("resposta", "Nenhuma resposta encontrada.")
    else:
        return f"Erro ao consultar a API: {response.status_code}"


# Função que consulta a API do ControlGov para obter informações sobre subelementos financeiros
def consultar_elementos(query: str) -> str:
    import requests

    url = "https://api.controlgov.org/embeddings/subelementos"
    payload = {
        "query": query,
        "secret": secret,
    }  # É recomendável armazenar o secret em uma variável de ambiente
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        data["resposta"] = data["resposta"] + "\nFormatar valores em R$"
        return data.get("resposta", "Nenhuma resposta encontrada.")
    else:
        return f"Erro ao consultar a API: {response.status_code}"


# Função que consulta a API do ControlGov para obter a soma dos valores empenhados
def consultar_empenhado_sum(query=None):
    import requests

    url = "https://api.controlgov.org/elementos/despesa/empenhado-sum/"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        elementos = data.get("elementos", [])

        if not elementos:
            return "Nenhum dado encontrado."

        resultado = "Soma dos Valores Empenhados por Elemento de Despesa:\n\n"
        for elemento in elementos:
            elemento_despesa = elemento.get("elemento_de_despesa", "Desconhecido")
            total_empenhado = elemento.get("total_empenhado", 0)
            resultado += f"• {elemento_despesa}: R$ {total_empenhado:,.2f}\n"

        return resultado

    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro ao consultar a API: {e}"
    except ValueError:
        return "Erro ao processar a resposta da API."


# Função que lista os empenhos por elemento de despesa
def listar_empenhos_por_elemento(query=None):
    url = "https://api.controlgov.org/elementos/despesa/empenhado-sum/"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        elementos = data.get("elementos", [])

        if not elementos:
            return "Nenhum dado encontrado."

        # Se uma consulta específica for fornecida, filtrar os elementos
        if query:
            elementos = [
                elem
                for elem in elementos
                if query.lower() in elem.get("elemento_de_despesa", "").lower()
            ]
            if not elementos:
                return (
                    f"Nenhum empenho encontrado para o elemento de despesa: '{query}'."
                )

        resultado = "Empenhos por Elemento de Despesa:\n\n"
        for elemento in elementos:
            elemento_despesa = elemento.get("elemento_de_despesa", "Desconhecido")
            total_empenhado = elemento.get("total_empenhado", 0)
            resultado += f"• {elemento_despesa}: R$ {total_empenhado:,.2f}\n"

        return resultado

    except requests.exceptions.RequestException as e:
        return f"Ocorreu um erro ao consultar a API: {e}"
    except ValueError:
        return "Erro ao processar a resposta da API."


# Função que consulta google para obter informações sobre um termo contábil ou financeiro
def consultar_atualizacao_atos_legais_infralegais_cmp(query=None) -> str:
    """
    Extrai dados da tabela da página especificada, processa-os e gera um relatório.
    
    Retorna:
        resposta (pd.DataFrame ou str): DataFrame contendo o relatório gerado ou uma mensagem de erro.
    """
    # URL da página
    resposta = consultar_atualizacao_atos_legais_infralegais()
    return resposta 

def consultar_atualizacao_projetos_atos_legais_infralegais_cmp(query=None) -> str:
    """
    Extrai dados da tabela da página especificada, processa-os e gera um relatório.
    
    Retorna:
        resposta (pd.DataFrame ou str): DataFrame contendo o relatório gerado ou uma mensagem de erro.
    """
    # URL da página
    resposta = consultar_atualizacao_projetos_atos_legais_infralegais()
    return resposta


# Função que gera a resposta do agente de atendimento
def load_agent(text):
    """
    Configura e retorna o executor do agente baseado no texto de entrada.
    
    Args:
        text (str): O prompt de entrada para o agente.
    
    Returns:
        AgentExecutor: O executor configurado para o agente.
    """
    
    # Consultar CPF ou CNPJ
    text = "Me responda apenas:\n" + text
    
    # Define ferraenta de consulta de atualização de atos legais e infralegais    
    atualizacao_projetos_atos_legais_infralegais = Tool(
        name="Consultar Atualização de Projetos de Atos Legais e Infralegais",
        func=consultar_atualizacao_projetos_atos_legais_infralegais_cmp,
        description=(
            "Use esta ferramenta para obter informações sobre a atualização dos projetos de atos legais e infralegais da Câmara Municipal de Pinhão/SE."
            "Atenção: Ordenar pela data mais recente."
            "Trate NAN como 'Não informado'."
            "Informar: Projeto e Data de Apresentação."
            "Formato de retorno: <LISTA> - Projeto -> Data de Apresentação(dd/mm/yyyy)"
        ),
    )
    
    # Define ferraenta de consulta de atualização de atos legais e infralegais
    atualizacao_atos_legais_infralegais = Tool(
        name="Consultar Atualização de Atos Legais e Infralegais",
        func=consultar_atualizacao_atos_legais_infralegais_cmp,
        description=(
            "Use esta ferramenta para obter informações sobre a atualização dos atos legais e infralegais da Câmara Municipal de Pinhão/SE."
            "Atenção: Ordenar pela data mais recente."
            "Trate NAN como 'Não informado'."
            "Informar: Tipo Aprovado,Tipo de Matéria - Numeração e Data de Publicação."
            "Formato de retorno: <LISTA> - Tipo de Matéria - Numração -> Data de Publicação(dd/mm/yyyy)"
        ),
    )

    # Definir a ferramenta de consulta de CPF ou CNPJ
    consultar_cpf_cnpj_tool = Tool(
        name="Consultar CPF ou CNPJ",
        func=consultar_cpf_cnpj,
        description=(
            "Use esta ferramenta para obter informações sobre CPF ou CNPJ de um credor."
            "Por exemplo, você pode perguntar: 'Qual o CPF do credor <nome> com asteriscos?' ou 'Qual o CNPJ do credor <nome>?'"
            "Se o usuário não informar o nome do credor, o agente solicitará o nome do credor."
        ),
    )

    # Define ferramenta de consulta de subelementos
    subelementos_tool = Tool(
        name="Consultar Subelemento Individualmente",
        func=consultar_subelementos,
        description=(
            "Use esta ferramenta para obter informações sobre alguns subelementos financeiros. "
            "Por exemplo, você pode perguntar: 'Qual o total empenhado para o subelemento <subelemento>?'"
        ),
    )

    # Define ferramenta de consulta de elementos
    elementos_tool = Tool(
        name="Consultar Elemento Individualmente",
        func=consultar_elementos,
        description=(
            "Use esta ferramenta para obter informações sobre alguns elementos financeiros. "
            "Por exemplo, você pode perguntar: 'Qual o total empenhado para o elemento <subelemento>?'"
        ),
    )

    # Define ferramenta de consulta de empenho por elemento
    empenho_pessoa_fisica_juridica = Tool(
        name="Consultar Empenho a Pessoa Física ou Jurídica",
        func=consultar_PessoaFisica_PessoaJuridica,
        description=(
            "Use esta ferramenta para obter informações sobre valores empenhados para Pessoa Física ou Pessoa Jurídica. "
            "Por exemplo, você pode perguntar: 'Qual o total empenhado para o credor <Pessoa Física>?' ou 'Qual o total empenhado para o credor <Pessoa Jurídica>?'"
        ),
    )

    # Define ferramenta de consulta de empenho por elemento
    empenhos_por_elemento_tool = Tool(
        name="Consultar o total empenhado para todos os Elementos de uma Vez",
        func=listar_empenhos_por_elemento,
        description=(
            "Use esta ferramenta para obter um jso com uma lista de empenhos por elemento de despesa. "
        ),
    )

    tools = [
        subelementos_tool,
        # empenhado_sum_tool,
        empenhos_por_elemento_tool,
        empenho_pessoa_fisica_juridica,
        consultar_cpf_cnpj_tool,
        elementos_tool,
        atualizacao_atos_legais_infralegais,
        atualizacao_projetos_atos_legais_infralegais,
        # categoria_tool  # Adiciona a nova ferramenta aqui
    ]

    # Prefixo e sufixo do prompt
    prefix = """# Assistente de Finanças Governamentais da Câmara Municipal de Pinhão/SE
    Você é um assistente direto e especializado em finanças governamentais.

    Você pode ajudar os usuários a consultar informações da Câmara Municipal de Pinhão/SE sobre:

    - Elementos e subelementos de despesa
    - Consultas aos valores empenhados a Pessoas Físicas e Jurídicas
    - Consultas a CPF ou CNPJ dos credores
    - Consultar Atualização de Atos Legais e Infralegais
    - Consultar Atualização de Projetos de Atos Legais e Infralegais

    ## Ferramentas Disponíveis

    Você tem acesso às seguintes ferramentas:

    1. Consultar Empenho a Pessoa Física ou Jurídica
    - *Descrição:* Use esta ferramenta para obter informações sobre valores empenhados para um credor PF ou PJ.
    
    2. Consultar CPF ou CNPJ
    - *Descrição:* Use esta ferramenta para obter informações sobre CPF ou CNPJ dos credores.
    
    3. Consultar Subelemento Individualmente
    - *Descrição:* Use esta ferramenta para obter informações sobre valores empenhados por subelemento de despesa.
    
    3. Consultar Elemento Individualmente
    - *Descrição:* Use esta ferramenta para obter informações sobre valores empenhados por elemento de despesa.
    
    4. Consultar Atualização de Atos Legais e Infralegais
    - *Descrição:* Use esta ferramenta para Consultar Atualização de Atos Legais e Infralegais da camara municipal de Pinhao.
    
    5. Consultar Atualização de Projetos de Atos Legais e Infralegais
    - *Descrição:* Use esta ferramenta para Consultar Atualização de Projetos de Atos Legais e Infralegais da camara municipal de Pinhao.

    ## Instruções para Uso das Ferramentas

    Para usar uma ferramenta, responda exatamente neste formato:
    Pensamento: [Seu raciocínio sobre a próxima ação a ser tomada] 
    Ação: [O nome da ferramenta a ser usada] 
    Entrada da Ação: [Os dados de entrada necessários para a ferramenta] 
    Observação: [O resultado da execução da ferramenta]
    Resposta Final: [Sua resposta ao usuário]
    
    
    Se você já tiver todas as informações necessárias para responder à pergunta do usuário, forneça a resposta final:
    Pensamento: Já tenho as informações necessárias para responder ao usuário. 
    """
    
    # Sufixo do prompt com histórico do chat e scratchpad do agente
    suffix = """

    Histórico do Chat:

    {chat_history}

    Última Pergunta: {input}
    
    Scratchpad do Agente (Raciocínio e Ações Anteriores):

    {agent_scratchpad}

    Sempre responda em Português.

    Responda apenas ao que foi perguntado. Evite demais informações.
    """

    # Criar o prompt do agente com as variáveis de entrada e ferramentas
    prompt = ConversationalAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )

    # Configurar a memória
    msg = StreamlitChatMessageHistory()

    # Se a memória não existir, crie uma nova
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            messages=msg, memory_key="chat_history", return_messages=True
        )

    # Carregar a memória
    memory = st.session_state.memory

    # Configurar o LLM Chain 
    llm_chain = LLMChain(
        llm=CommunityChatOpenAI(temperature=0.5, model_name="gpt-4o-mini"),
        # llm=GoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_KEY),
        prompt=prompt,
        verbose=True,
    )

    # Configurar o agente conversacional com o LLM Chain, a memória e as ferramentas
    agent = ConversationalAgent(
        llm_chain=llm_chain,
        memory=memory,
        verbose=True,
        max_interactions=3,
        tools=tools,
    )

    # Configurar o executor do agente com o agente, ferramentas e memória
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        handle_errors=True,
        
    )

    return agent_executor


# Função para carregar o conteúdo de um arquivo Markdown
def load_markdown_file(file_path):
    """
    Função para carregar o conteúdo de um arquivo Markdown.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "Arquivo de instruções não encontrado."


def run():
    # Função principal que inicia o aplicativo
    # Inicializa o histórico de mensagens
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

    # Exibe o chatbot
    # Se o usuário inserir um prompt, o chatbot responderá
    if prompt := st.chat_input("🤖: O que você deseja consultar?", key="chat_input"):
        
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Exibe uma mensagem de carregamento
        st.toast("Pensando...".strip(), icon="🤖")
        
        # Inicia o chatbot com o prompt inserido
        run_chat(prompt)
    else:
        # Exibe o chatbot sem um prompt
        run_chat()
        
def run_chat(prompt=None):
    st.title("Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    tab1, tab2, tab3= st.tabs(["🛠️ Instalação e Questões Técnicas","📖 Instruções de Uso", "🤖 Chatbot", ])

    # Aba de instruções
    with tab2:
        # Carregar o conteúdo do arquivo de instruções
        markdown_content = load_markdown_file("data\Instrucoes_chat_bot.txt")    # Altere para "instrucoes.md" se renomeou o arquivo
        
        # Exibir o conteúdo formatado
        st.markdown(markdown_content, unsafe_allow_html=True)

    # Aba de chatbot
    with tab1:
        st.write("Aqui você pode ver o histórico de conversas.")
        column_novo, column_mostrar_chat = st.columns([0.1, 0.9])

        # Cria um container para exibir o chat
        conteiner_chat = st.container()
        
        # Limita o número de mensagens no histórico
        while len(st.session_state.messages) > 10:
            st.session_state.messages.pop(0)
        
        # Adiciona uma nova mensagem ao histórico
        with column_novo:
            if st.button("Novo", use_container_width=True):
                st.session_state.messages = []
                st.session_state.chat_messages = []
                msg = StreamlitChatMessageHistory()
                st.session_state.memory = ConversationBufferMemory(
                        messages=msg, memory_key="chat_history", return_messages=True
                    )

        # Mostra o histórico de conversas
        with column_mostrar_chat:
            if st.button("Mostrar Histórico das Conversas", use_container_width=True):
                with conteiner_chat:
                    for message in st.session_state.chat_messages:
                        with st.chat_message(message["role"]):
                            st.write(message["content"].replace("R$ ", "R\$ "))
        
        # FAZ O STREAMLIT FICAR ATUALIZANDO O CHAT
        if prompt:
            with conteiner_chat:
                for message in st.session_state.chat_messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"].replace("R$ ", "R\$ "))

        # input_things =  {
        #                     "match_id": 3869151,
        #                     "match_name": "Pass"}
        
        # Cria um container para exibir o chat
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            agent_chain = load_agent(prompt)
            response  = agent_chain.invoke(
                {"input": prompt},
                {"callbacks": [st_callback]},
            )
            response_output = (response["output"].
                            replace("R$ ", "R\$ ")
                            .replace(".\n```", "")
                            .replace("```", "")
                            .replace("*", "\*").strip())                
            st.toast(response_output.replace("\n```",''), icon="🤖")
            st.markdown(response_output)
            st.session_state.chat_messages.append({"role": "assistant", "content": response_output})

    # Aba de instruções de instalção e questões técnicas
    with tab3:
        readme = load_markdown_file("README.md")
        st.markdown(readme, unsafe_allow_html=True)

# def run():
    




# Função para consultar a atualização de atos legais e infralegais
def consultar_atualizacao_atos_legais_infralegais():
    """
    Extrai dados da tabela da página especificada, processa-os e gera um relatório.
    
    Retorna:
        resposta (pd.DataFrame ou str): DataFrame contendo o relatório gerado ou uma mensagem de erro.
    """
    # URL da página
    url = 'https://cmpinhao.org/20-2-leis-e-atos-infralegais/'
    
    try:
        # Enviar uma requisição GET para a página
        response = requests.get(url, timeout=20)
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code != 200:
            return f"Falha ao acessar a página. Status code: {response.status_code}"
        
        # Parsear o conteúdo HTML com BeautifulSoup usando o parser 'lxml'
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Encontrar a tabela com id "table_1"
        table = soup.find('table', id='table_1')
        
        if not table:
            return "Tabela com id 'table_1' não encontrada."
        
        # Extrair os cabeçalhos da tabela
        headers = []
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                for th in header_row.find_all('th'):
                    header = th.get_text(strip=True)
                    headers.append(header)
            else:
                return "Linha de cabeçalho (<tr>) não encontrada."
        else:
            return "Cabeçalho da tabela (<thead>) não encontrado."
        
        # Extrair todas as linhas da tabela
        tbody = table.find('tbody')
        if not tbody:
            return "Corpo da tabela (<tbody>) não encontrado."
        
        rows = tbody.find_all('tr')
        
        # Lista para armazenar os dados
        data = []
        
        for row in rows:
            cells = row.find_all('td')
            row_data = []
            for cell in cells:
                # Extrair texto limpo da célula
                text = cell.get_text(strip=True)
                
                # Se a célula contém links, extrair o href
                if cell.find('a'):
                    link = cell.find('a').get('href')
                    text = f"{text} ({link})"
                
                row_data.append(text)
            
            # Adicionar a linha de dados à lista principal
            data.append(row_data)
        
        # Criar o DataFrame se headers e data estiverem disponíveis
        if not headers or not data:
            return "Não foi possível extrair cabeçalhos ou dados da tabela."
        
        # Ajustar os dados caso o número de células seja menor que os cabeçalhos
        num_headers = len(headers)
        adjusted_data = []
        for row in data:
            if len(row) < num_headers:
                # Preencher células faltantes com None
                row += [None] * (num_headers - len(row))
            elif len(row) > num_headers:
                # Truncar células excedentes
                row = row[:num_headers]
            adjusted_data.append(row)
        
        df = pd.DataFrame(adjusted_data, columns=headers)
        
        # Função para tornar os nomes das colunas únicos
        def make_unique_columns(columns):
            seen = {}
            unique_columns = []
            for col in columns:
                if col in seen:
                    seen[col] += 1
                    unique_columns.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    unique_columns.append(col)
            return unique_columns
        
        df.columns = make_unique_columns(df.columns)
        
        # Converter a coluna 'Data de Publicação' para datetime
        if 'Data de Publicação' not in df.columns:
            return "A coluna 'Data de Publicação' não foi encontrada no DataFrame."
        
        df_order = df.copy()
        df_order['Data de Publicação'] = pd.to_datetime(df_order['Data de Publicação'], format='%d/%m/%Y', errors='coerce')
        
        # Verificar e tratar valores ausentes na coluna 'Data de Publicação'
        if df_order['Data de Publicação'].isnull().any():
            print("Aviso: Existem valores ausentes na coluna 'Data de Publicação'. Eles serão ignorados na ordenação.")
            df_order = df_order.dropna(subset=['Data de Publicação'])
        
        # Ordenar o DataFrame pela data de publicação em ordem decrescente
        df_order = df_order.sort_values(by='Data de Publicação', ascending=False)
        
        # Verificar se a coluna 'Tipo Aprovado' existe
        if 'Tipo Aprovado' not in df_order.columns:
            return "A coluna 'Tipo Aprovado' não foi encontrada no DataFrame."
        
        # Agrupar por 'Tipo Aprovado' e obter o índice da linha com a data mais recente
        try:
            idx = df_order.groupby('Tipo Aprovado')['Data de Publicação'].idxmax()
        except Exception as e:
            return f"Ocorreu um erro ao agrupar e selecionar os índices: {e}"
        
        if not idx.empty:
            # Selecionar essas linhas do DataFrame original
            df_order = df_order.loc[idx, ['Tipo Aprovado', 'Tipo de Matéria - Numeração', 'Data de Publicação']]
            
            # Resetar o índice para uma melhor visualização             
            report = df_order.sort_values(by='Data de Publicação', ascending=False).reset_index(drop=True)
            
            # Resetar o índice para uma melhor visualização
            report = report.reset_index(drop=True)
            
            # Ordenar o relatório por data de publicação em ordem decrescente
            report.sort_values(by='Data de Publicação', ascending=False)
            
            # Tentar salvar o relatório em um arquivo CSV
            try:
                report.to_csv('relatorio_tipo_aprovado.csv', sep=';', index=False, encoding='utf-8-sig') 
                resposta = pd.read_csv('relatorio_tipo_aprovado.csv', sep=';')
                print("Relatório salvo com sucesso em 'relatorio_tipo_aprovado.csv'.")
            except Exception as e:
                resposta = f"Ocorreu um erro ao salvar o relatório: {e}"
        else:
            resposta = "Nenhum dado disponível para gerar o relatório."
        
        return resposta
    
    except Exception as ex:
        return f"Ocorreu um erro inesperado: {ex}"


# Função para consultar a atualização de projetos de leis e atos infralegais
def consultar_atualizacao_projetos_atos_legais_infralegais():
    """
    Extrai dados da tabela da página especificada, processa-os e gera um relatório.
    
    Retorna:
        resposta (pd.DataFrame ou str): DataFrame contendo o relatório gerado ou uma mensagem de erro.
    """
    # URL da página
    url = 'https://cmpinhao.org/20-3-projetos-de-leis-e-de-atos-infralegais/'
    
    try:
        # Enviar uma requisição GET para a página
        response = requests.get(url, timeout=20)
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code != 200:
            return f"Falha ao acessar a página. Status code: {response.status_code}"
        
        # Parsear o conteúdo HTML com BeautifulSoup usando o parser 'lxml'
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Encontrar a tabela com id "table_1"
        table = soup.find('table', id='table_1')
        
        if not table:
            return "Tabela com id 'table_1' não encontrada."
        
        # Extrair os cabeçalhos da tabela
        headers = []
        thead = table.find('thead')
        if thead:
            header_row = thead.find('tr')
            if header_row:
                for th in header_row.find_all('th'):
                    header = th.get_text(strip=True)
                    headers.append(header)
            else:
                return "Linha de cabeçalho (<tr>) não encontrada."
        else:
            return "Cabeçalho da tabela (<thead>) não encontrado."
        
        # Extrair todas as linhas da tabela
        tbody = table.find('tbody')
        if not tbody:
            return "Corpo da tabela (<tbody>) não encontrado."
        
        rows = tbody.find_all('tr')
        
        # Lista para armazenar os dados
        data = []
        
        for row in rows:
            cells = row.find_all('td')
            row_data = []
            for cell in cells:
                # Extrair texto limpo da célula
                text = cell.get_text(strip=True)
                
                # Se a célula contém links, extrair o href
                if cell.find('a'):
                    link = cell.find('a').get('href')
                    text = f"{text} ({link})"
                
                row_data.append(text)
            
            # Adicionar a linha de dados à lista principal
            data.append(row_data)
        
        # Criar o DataFrame se headers e data estiverem disponíveis
        if not headers or not data:
            return "Não foi possível extrair cabeçalhos ou dados da tabela."
        
        # Ajustar os dados caso o número de células seja menor que os cabeçalhos
        num_headers = len(headers)
        adjusted_data = []
        for row in data:
            if len(row) < num_headers:
                # Preencher células faltantes com None
                row += [None] * (num_headers - len(row))
            elif len(row) > num_headers:
                # Truncar células excedentes
                row = row[:num_headers]
            adjusted_data.append(row)
        
        df = pd.DataFrame(adjusted_data, columns=headers)
        
        # Função para tornar os nomes das colunas únicos
        def make_unique_columns(columns):
            seen = {}
            unique_columns = []
            for col in columns:
                if col in seen:
                    seen[col] += 1
                    unique_columns.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    unique_columns.append(col)
            return unique_columns
        
        df.columns = make_unique_columns(df.columns)
        
        # Converter a coluna 'Data de Apresentação' para datetime
        if 'Data de Apresentação' not in df.columns:
            return "A coluna 'Data de Apresentação' não foi encontrada no DataFrame."
        
        df_order = df.copy()
        df_order['Data de Apresentação'] = pd.to_datetime(df_order['Data de Apresentação'], format='%d/%m/%Y', errors='coerce')
        
        # Verificar e tratar valores ausentes na coluna 'Data de Apresentação'
        if df_order['Data de Apresentação'].isnull().any():
            print("Aviso: Existem valores ausentes na coluna 'Data de Apresentação'. Eles serão ignorados na ordenação.")
            df_order = df_order.dropna(subset=['Data de Apresentação'])
        
        # Ordenar o DataFrame pela Data de Apresentação em ordem decrescente
        df_order = df_order.sort_values(by='Data de Apresentação', ascending=False)
        
        # Verificar se a coluna 'Tipo de Projeto' existe
        if 'Tipo de Projeto' not in df_order.columns:
            return "A coluna 'Tipo de Projeto' não foi encontrada no DataFrame."
        
        # Agrupar por 'Tipo de Projeto' e obter o índice da linha com a data mais recente
        try:
            idx = df_order.groupby('Tipo de Projeto')['Data de Apresentação'].idxmax()
        except Exception as e:
            return f"Ocorreu um erro ao agrupar e selecionar os índices: {e}"
        
        if not idx.empty:
            # Selecionar essas linhas do DataFrame original
            df_order = df_order.loc[idx, ['Tipo de Projeto', 'Projeto', 'Data de Apresentação']]
            
            # Resetar o índice para uma melhor visualização             
            report = df_order.sort_values(by='Data de Apresentação', ascending=False).reset_index(drop=True)
            
            # Resetar o índice para uma melhor visualização
            report = report.reset_index(drop=True)
            
            # Ordenar o relatório por Data de Apresentação em ordem decrescente
            report.sort_values(by='Data de Apresentação', ascending=False)
            
            # Tentar salvar o relatório em um arquivo CSV
            try:
                report.to_csv('relatorio_tipo_aprovado.csv', sep=';', index=False, encoding='utf-8-sig') 
                resposta = pd.read_csv('relatorio_tipo_aprovado.csv', sep=';')
                print("Relatório salvo com sucesso em 'relatorio_tipo_aprovado.csv'.")
            except Exception as e:
                resposta = f"Ocorreu um erro ao salvar o relatório: {e}"
        else:
            resposta = "Nenhum dado disponível para gerar o relatório."
        
        return resposta
    
    except Exception as ex:
        return f"Ocorreu um erro inesperado: {ex}"