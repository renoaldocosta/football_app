```markdown
# Football Match Analysis App

## Descrição do Projeto

Este projeto consiste no desenvolvimento de uma aplicação de análise de partidas de futebol, utilizando abordagens data-driven para fornecer insights detalhados sobre uma única partida. A aplicação explora dados de uma partida específica, cria perfis de jogadores, resume eventos e oferece narrativas personalizadas aos usuários. O projeto é dividido em duas versões distintas:

1. **FastAPI + LLM**: Criação de uma API para geração de perfis de jogadores, sumarização e narrativas.
2. **Streamlit + LangChain (ReAct Agent + Tools)**: Desenvolvimento de uma interface interativa para explorar os mesmos dados de forma visual e amigável.

### Objetivo

Consolidar conhecimentos em programação, APIs, Modelos de Linguagem de Grande Porte (LLMs) e interfaces interativas através da criação de uma aplicação robusta e funcional que permita a análise aprofundada de partidas de futebol.

## Funcionalidades Principais

- **Perfil de Jogador**: Estatísticas detalhadas e análise sobre jogadores da partida.
- **Sumarização de Eventos**: Transformação dos eventos da partida em um texto descritivo.
- **Narração Personalizada**: Geração de textos de narração de acordo com o estilo escolhido pelo usuário.

## Estrutura do Projeto

```
football_match_analysis/
│
├── src/
│   └── football_app/
│       ├── app.py                       # Aplicação Streamlit
│       ├── notebook_exercicios.ipynb    # Executa as questões 3, 4 e 6
│       └── main.py                      # API FastAPI
│
├── requirements.in                        # Lista de dependências
├── .env                                   # Variáveis de ambiente
└── README.md                              # Este arquivo
```

## Tecnologias Utilizadas

- **Linguagem**: Python 3.8+
- **Bibliotecas**:
  - `statsbombpy`
  - `langchain`
  - `langchain_community`
  - `langchain_google_genai`
  - `streamlit`
  - `fastapi`
  - `mplsoccer`
  - `matplotlib`
  - `wikipedia`
  - `uvicorn`
  - `streamlit_option_menu`
  - `plotly`
  - `langchain_openai`
  - `langchain-core`
  - `langchain-openai`

## Configuração do Ambiente

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/football_match_analysis.git
cd football_match_analysis
```

### 2. Criar e Ativar um Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar as Dependências

Primeiro, instale o [pip-tools](https://github.com/jazzband/pip-tools) se ainda não tiver:

```bash
pip install pip-tools
```

Depois, gere o `requirements.txt` a partir do `requirements.in`:

```bash
pip-compile requirements.in
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
```

Substitua `your_google_api_key` e `your_openai_api_key` pelas suas chaves de API correspondentes.

## Executando a Aplicação

### 1. Executar a API com FastAPI

A API fornece endpoints para sumarização de partidas e perfis de jogadores.

```bash
uvicorn src.football_app.main:app --reload
```

Acesse a documentação interativa da API em [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 2. Executar a Interface com Streamlit

A interface permite explorar os dados de forma visual e interativa.

```bash
streamlit run src/football_app/app.py
```

Acesse a aplicação no navegador através do endereço fornecido no terminal, geralmente [http://localhost:8501](http://localhost:8501).

### 3. Executar o Notebook de Exercícios

Para visualizar e executar as questões 3, 4 e 6:

```bash
jupyter notebook src/football_app/notebook_exercicios.ipynb
```

## Exemplos de Entrada e Saída

### 1. Sumarização de Partida

**Endpoint**: `http://127.0.0.1:8000/match_summary`

**Método**: `POST`

**Entrada**: ID da partida (e.g., `3869151`)

**Requisição**:

```bash
curl -X POST "http://127.0.0.1:8000/match_summary" \
     -H "Content-Type: application/json" \
     -d '{
           "match_id": 3869151
         }'
```

**Saída**:

```json
{
  "summary": "\"O time Argentina venceu o time Austrália por 2 a 0. O primeiro gol foi marcado por Lionel Messi, após assistência de Nicolás Otamendi. O segundo gol foi marcado por Julián Álvarez.\n\nO time Austrália recebeu dois cartões amarelos, um para Jackson Irvine e outro para Miloš Degenek.\""
}
```

### 2. Perfil de Jogador

**Endpoint**: `http://127.0.0.1:8000/player_profile`

**Método**: `POST`

**Entrada**:
- `match_id`: ID da partida (e.g., `3869151`)
- `player_name`: Nome do jogador (e.g., `Mathew Ryan`)

**Requisição**:

```bash
curl -X POST "http://127.0.0.1:8000/player_profile" \
     -H "Content-Type: application/json" \
     -d '{
           "match_id": "3869151",
           "player_name": "Mathew Ryan"
         }'
```

**Saída**:

```json
{
  "stats": "{\n  \"player_name\": \"Mathew Ryan\",\n  \"passes_completed\": 45,\n  \"passes_attempted\": 53,\n  \"shots\": 0,\n  \"shots_on_target\": 0,\n  \"fouls_committed\": 0,\n  \"fouls_won\": 0,\n  \"tackles\": 0,\n  \"interceptions\": 0,\n  \"dribbles_successful\": 1,\n  \"dribbles_attempted\": 1\n}"
}
```

### 3. Narração Personalizada

**Endpoint**: `http://127.0.0.1:8000/narration`

**Método**: `POST`

**Entrada**: Estilo de narração (`Formal`, `Humorístico`, `Técnico`)

**Requisição**:

```bash
curl -X POST "http://127.0.0.1:8000/narration" \
     -H "Content-Type: application/json" \
     -d '{
           "match_id": 3869151,
           "style": "Formal"
         }'
```

**Saída**:

- **Formal**:
  ```
  "O time Argentina garantiu a vitória sobre o time Austrália com um placar de 2 a 0. Lionel Messi abriu o placar após uma assistência de Nicolás Otamendi, seguido por Julián Álvarez para selar o resultado. A equipe Austrália recebeu dois cartões amarelos, um para Jackson Irvine e outro para Miloš Degenek."
  ```
- **Humorístico**:
  ```
  "Que partida emocionante! A Argentina levou a melhor sobre a Austrália com um placar de 2 a 0. Messi mostrou sua magia com um gol assistido por Otamendi, e Álvarez fechou o show. Enquanto isso, a Austrália teve que sair com duas estrelinhas amarelas para Irvine e Degenek. Melhor sorte na próxima!"
  ```
- **Técnico**:
  ```
  "Na partida, a Argentina demonstrou superioridade tática, conseguindo um 2 a 0 contra a Austrália. Lionel Messi finalizou após uma construção de jogada eficaz envolvendo Nicolás Otamendi. Julián Álvarez ampliou a vantagem com precisão nas finalizações. A Austrália enfrentou dificuldades defensivas, resultando em dois cartões amarelos para Jackson Irvine e Miloš Degenek."
  ```

## Detalhamento dos Exemplos

### Sumarização de Partida

- **Descrição**: Este endpoint gera um resumo textual dos principais eventos de uma partida específica.
- **Uso**: Envie o ID da partida para obter uma visão geral dos resultados, gols, assistências e cartões.

### Perfil de Jogador

- **Descrição**: Este endpoint fornece estatísticas detalhadas de um jogador específico em uma partida.
- **Uso**: Envie o ID da partida e o nome do jogador para obter métricas como passes completados, finalizações, desarmes, entre outros.

### Narração Personalizada

- **Descrição**: Este endpoint gera uma narrativa da partida no estilo escolhido pelo usuário.
- **Uso**: Envie o ID da partida e o estilo de narração desejado (`Formal`, `Humorístico`, `Técnico`) para obter uma descrição personalizada dos eventos da partida.

### Explicações Adicionais

- **Formato das Requisições**: Utilizamos o método `POST` para enviar dados no corpo da requisição, garantindo a flexibilidade e segurança no envio de informações.
- **Respostas Estruturadas**: As respostas são retornadas em formato JSON, facilitando a integração com diferentes front-ends e ferramentas de análise.
- **Narração Personalizada**: Oferece diferentes estilos de descrição para atender às preferências dos usuários, tornando a experiência mais envolvente e adaptável.

## Contribuição

Sinta-se à vontade para contribuir com este projeto! Abra issues e faça pull requests para melhorias e novas funcionalidades.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
