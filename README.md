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
│       ├── app.py                 # Aplicação Streamlit
│       ├── notebook_exercicios.ipynb  # Executa as questões 3, 4 e 6
│       └── main.py                # API FastAPI
│
├── requirements.in                # Lista de dependências
├── .env                           # Variáveis de ambiente
└── README.md                      # Este arquivo
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

**Entrada**: ID da partida (e.g., `12345`)

**Saída**:
```
"O time A venceu o time B por 3 a 1. Os destaques foram os gols de João e Lucas, além de uma assistência de Ana."
```

### 2. Perfil de Jogador

**Entrada**: Nome do jogador (e.g., `João`)

**Saída**:
```json
{
  "nome": "João",
  "estatisticas": {
    "passes": 45,
    "finalizações": 5,
    "desarmes": 3,
    "minutos_jogados": 90
  }
}
```

### 3. Narração Personalizada

**Entrada**: Estilo de narração (`Formal`, `Humorístico`, `Técnico`)

**Saída**:
- **Formal**:
  ```
  "O time A garantiu a vitória sobre o time B com um placar de 3 a 1. João e Lucas marcaram os gols decisivos, enquanto Ana contribuiu com uma assistência importante."
  ```
- **Humorístico**:
  ```
  "Que jogo! O time A deu um showzinho e venceu o time B por 3 a 1. João e Lucas foram os craques do momento, e Ana fez aquela assistência marota."
  ```
- **Técnico**:
  ```
  "Na partida, o time A dominou a posse de bola e finalizou 15 vezes, resultando em 3 gols de João e Lucas. Ana foi crucial na criação das jogadas, fornecendo uma assistência chave. O time B conseguiu reduzir para 1, mas não foi suficiente para mudar o resultado final."
  ```

## Contribuição

Sinta-se à vontade para contribuir com este projeto! Abra issues e faça pull requests para melhorias e novas funcionalidades.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Para mais informações, entre em contato com [seu-email@example.com](mailto:seu-email@example.com).

```