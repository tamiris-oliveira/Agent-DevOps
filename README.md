# 🚀 Bem-vindo ao Projeto de Construção de Agente de IA para Rateio de Custos! 🌟

Olá!
Se você chegou até aqui, é porque está prestes a conhecer um projeto feito para facilitar o rateio de custos com a ajuda de inteligência artificial.
Basta seguir os passos e rodar tudo na sua máquina. Vamos nessa? 😎

---

## 📋 O que você vai encontrar aqui?

🔗 **Veja o projeto em funcionamento:**  
[🎥 Clique aqui para assistir ao vídeo do projeto rodando](https://drive.google.com/file/d/1cPjreSfWSd6b8IrwDY6-vGf7RJvyxb2K/view?usp=sharing)  
*Demonstração prática com explicação passo a passo.*

### 🎯 Objetivo do Projeto

Empresas frequentemente enfrentam o desafio de alocar corretamente os custos relacionados a **ferramentas** (como licenças de software e equipamentos) e **benefícios** (plano de saúde, vale-refeição, etc.) entre os colaboradores ou centros de custo. Esse processo, normalmente manual e distribuído em diversas planilhas, é:

- Demorado
- Repetitivo
- Propenso a erros humanos

#### 🧠 O Desafio

Criar um **Agente Inteligente** capaz de:

##### 📥 Inputs

Receber arquivos `.xlsx` com:

- ✅ Uma planilha com os dados dos colaboradores (nome, ID, centro de custo etc.)
- 🛠️ Uma ou mais planilhas listando quais colaboradores usam quais ferramentas
- 🎁 Uma ou mais planilhas com os custos de benefícios recebidos por colaborador

##### ⚙️ Processamento

O agente é responsável por:

- Ler e padronizar automaticamente os dados das planilhas, mesmo com nomes de colunas variados
- Identificar o uso de cada ferramenta e benefício por colaborador
- Calcular os custos correspondentes, incluindo:
  - Custos fixos por ferramenta
  - Custos variáveis e coparticipações de benefícios
- Consolidar todos os dados em um único relatório por colaborador

##### 📤 Output

Gerar uma planilha consolidada com:

- 🆔 ID do Colaborador  
- 🙋 Nome do Colaborador  
- 🏢 Centro de Custo  
- 💻 Custo por Ferramenta  
- 🧾 Custo por Benefício  
- 💰 Custo Total (Ferramentas + Benefícios)

O resultado: Um agente de IA que orquestra o fluxo de trabalho, toma decisões sobre quais etapas executar e como processar os dados.

---

## 🗂️ Estrutura do Projeto

```plaintext
├── data/                             # Diretório que contém as planilhas de dados usadas no projeto
│   ├── Dados Colaboradores.xlsx      # Planilha com os dados dos colaboradores
│   └── costs/                        # Diretório com os custos dos benefícios e ferramentas
│       ├── Beneficios/               # Planilhas com os custos de benefícios
│       └── Ferramentas/              # Planilhas com os custos das ferramentas
│
├── .env                              # Arquivo com a API Key (Groq)
├── main.py                           # Arquivo principal com a implementação do projeto
├── README.md                         # Documentação principal do projeto com instruções de uso
├── requirements.txt                  # Lista de dependências do projeto
```

---

## Como Rodar o Projeto 🚀

### 1. Clone o repositório

Abra seu terminal e cole os seguintes comandos:

```bash
git clone https://github.com/seu-usuario/seu-projeto.git
cd seu-projeto
```

### 2. Crie e ative seu ambiente virtual 🐍

Isso vai garantir que você tenha todas as dependências necessárias sem afetar outros projetos:

No Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

No Windows (PowerShell):

```powershell
python -m venv venv
.
env\Scripts\Activate.ps1
```

### 3. Instale as dependências

Com o ambiente ativado, vamos instalar as dependências:

```bash
pip install -r requirements.txt
```

### 4. Configure sua API Key 🔑

Este projeto usa uma **API Key Groq** para acessar modelos LLM (Large Language Models) hospedados pela Groq, que são usados para geração de texto, processamento e outras funcionalidades de inteligência artificial.

#### O que é a API Key Groq?

A API Key Groq é uma chave de autenticação que permite que seu projeto se comunique com os serviços de IA da Groq, garantindo acesso seguro e autorizado aos modelos de linguagem.

#### Como criar sua API Key Groq?

1. Acesse o site da Groq: [https://www.groq.ai](https://www.groq.ai)  
2. Cadastre-se ou faça login na sua conta.  
3. Navegue até a seção de APIs ou configurações da conta.  
4. Gere uma nova API Key para uso em seu projeto.  
5. Copie essa chave.

#### Como usar a API Key?

- Crie um arquivo `.env` na raiz do projeto (caso ainda não tenha).  
- Adicione a sua chave neste arquivo, assim:

```ini
export GROQ_API_KEY=<suachaveaqui>
```

### 5. Rodando o projeto

Finalmente, é hora do show! Rode o script principal:

```bash
python main.py
```

---

## ⚙️ Funcionalidades principais

Este é o fluxo de funcionamento:

### 1. Listagem e Leitura de Planilhas

O projeto possui funções para buscar, ler e carregar planilhas Excel de forma automática, facilitando o processamento dos dados.

#### Função `list_spreadsheets`

Percorre um diretório e seus subdiretórios buscando arquivos com extensão `.xlsx` ou `.xls`:

```python
def list_spreadsheets(directory: str) -> List[str]:
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith((".xlsx", ".xls"))
    ]
```

#### Função `read_spreadsheet`

Tenta ler uma planilha Excel e retorna um DataFrame do Pandas. Em caso de erro, captura a exceção e retorna `None`:

```python
def read_spreadsheet(file_path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return None
```

#### Função `load_spreadsheets`

Carrega todas as planilhas encontradas em um diretório, lendo cada arquivo e acumulando os DataFrames em uma lista:

```python
def load_spreadsheets(directory: str) -> tuple[list[pd.DataFrame], list[str]]:
    spreadsheet_paths = list_spreadsheets(directory)
    dataframes = []
    for path in spreadsheet_paths:
        print(f"Reading: {path}")
        df = read_spreadsheet(path)
        if df is not None:
            dataframes.append(df)
    return dataframes, spreadsheet_paths
```

---

### 2. Agente e Tool de Normalização dos Nomes das Colunas
Após as planilhas serem devidamente lidas e armazenadas em DataFrames, foi criado um agente inteligente responsável por processar cada planilha. Esse agente tem a função de analisar as colunas do DataFrame, identificar automaticamente quais colunas correspondem ao CPF do colaborador (ou identificador pessoal similar) e ao custo total da ferramenta ou benefício, montar os parâmetros necessários e executar a ferramenta **NormalizeSpreadsheetsTool** para realizar a normalização dos nomes dessas colunas.

O agente é estruturado com três componentes principais:

#### Goal (Objetivo):
Define claramente o que o agente deve alcançar, por exemplo:

> "Analisar cuidadosamente as colunas da planilha para identificar duas colunas específicas — uma que contenha o CPF do colaborador (ou identificador similar) e outra que contenha o custo total — montar um dicionário com esses dados e o nome do arquivo, e usar a ferramenta de normalização para renomear as colunas e salvar o arquivo."

#### Backstory (Contexto):
Fornece ao agente uma "história" que ajuda a direcionar seu comportamento e abordagem, como:

> "Você é um especialista em padronização de planilhas de custo de colaboradores."

#### Execução da Task (Tarefa):
A task é o passo prático em que o agente recebe os dados (nomes das colunas e nome do arquivo), identifica as colunas corretas para CPF e custo, e monta o dicionário de parâmetros que será passado para a ferramenta **NormalizeSpreadsheetsTool**. Essa task também define o formato esperado de saída para garantir que o agente executou a tarefa com sucesso.


```python
    agent = Agent(
        role="Column Normalizer",
        goal=(
            "Carefully analyze the spreadsheet columns and identify two columns:\\n"
            "- One that contains the employee's CPF (or similar identifier)\\n"
            "- One that contains the total cost\\n"
            "Create a dictionary with these columns and the file name\\n"
            "Use the 'Normalize Spreadsheets' tool to rename the columns in the loaded file\\n"
            "Return whether saving the spreadsheet was successful or not"
        ),
        backstory="You are a specialist in standardizing employee cost spreadsheets.",
        tools=[NormalizeSpreadsheetsTool],
        verbose=True,
        llm=llm
    )

    task = Task(
        description=(
            f"You are processing the spreadsheet '{file_name}'.\\n\\n"
            f"Columns found: {column_names}.\\n"
            "Your task is to identify which columns represent:\\n"
            "- CPF or personal identifier (e.g., cpf, document, registration...)\\n"
            "- Total tool or benefit cost (e.g., total value, cost, monthly fee...)\\n\\n"
            "Then, you must pass as input to the 'Normalize Spreadsheets' tool a Python dict in the format:\\n"
            '''{
    "args": {
        "columns": [<cpf_column_name>, <cost_column_name>],
        "file_name": "<original file name.xlsx>"
    }
}'''
            "\\nThis dict will be used by the 'Normalize Spreadsheets' tool to rename the columns and save the file."
        ),
        tools=[NormalizeSpreadsheetsTool],
        expected_output="Success. Columns renamed:",
        agent=agent
    )
```

#### Ferramenta 
Também foi desenvolvida a ferramenta **NormalizeSpreadsheetsTool**, que recebe como entrada um dicionário contendo o nome do arquivo e uma lista com duas colunas: a primeira representa a coluna referente ao CPF do colaborador, e a segunda corresponde ao valor total ou custo relacionado. A ferramenta então renomeia essas colunas no arquivo para os nomes padrão **"CPF"** e **"Fatura"**, garantindo a padronização dos dados para processos posteriores.


```python
@tool("Normalize Spreadsheets")
def NormalizeSpreadsheetsTool(args: dict) -> str:
    """
    Renames specific columns in an Excel spreadsheet to standardize data.

    This tool receives a dictionary containing:
    - The name of the source Excel file (`file_name`)
    - A list with two column names:
        - The column representing a personal identifier (e.g., CPF, Registration, Document)
        - The column representing the tool or benefit cost (e.g., Total Cost, Monthly Fee)

    The columns will be renamed to:
        - "CPF"
        - "Fatura"

    The renamed file will be saved as 'output/normalized_<original_name>.xlsx'.
    Returns whether saving the spreadsheet was successful or not.
    """

    file_name = args.get("file_name")
    column_names = args.get("columns", [])

    if not file_name:
        return "Parameter 'file_name' is required."

    if not isinstance(column_names, list) or len(column_names) < 2:
        return "You must provide the columns for CPF and cost to rename."

    search_directory = "data/costs"
    matching_files = [
        path for path in list_spreadsheets(search_directory)
        if os.path.basename(path) == file_name
    ]

    if not matching_files:
        return f"File '{file_name}' not found in '{search_directory}'."

    file_path = matching_files[0]

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return f"Error opening file '{file_name}': {e}"

    col_cpf, col_cost = column_names[0], column_names[1]

    if col_cpf not in df.columns or col_cost not in df.columns:
        return f"Specified columns not found in spreadsheet: {df.columns.tolist()}"

    rename_map = {
        col_cpf: "CPF",
        col_cost: "Fatura"
    }

    df.rename(columns=rename_map, inplace=True)

    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"normalized_{file_name}")

    try:
        df.to_excel(output_file, index=False)
    except Exception as e:
        return f"Error saving the file: {e}"

    renamed = ", ".join(f"'{old}' → '{new}'" for old, new in rename_map.items())
    return f"Success. Columns renamed: {renamed}"

```

---



### 3. Mesclagem de Planilhas Normalizadas

A função `merge_normalized_spreadsheets` é responsável por consolidar os dados provenientes das planilhas normalizadas, combinando-os com uma planilha base chamada `Dados Colaboradores.xlsx`. 

Essa função realiza os seguintes passos principais:

- Carrega a planilha base contendo os dados dos colaboradores.
- Localiza todos os arquivos normalizados na pasta de saída, exceto a planilha base.
- Para cada arquivo normalizado, extrai as colunas `CPF` e `Fatura`, renomeia a coluna `Fatura` para o nome do arquivo (identificando o custo da respectiva ferramenta/benefício), e faz o merge (junção) dos dados com a planilha base usando a coluna `CPF` como chave.
- Após incluir os custos de todas as ferramentas/benefícios, calcula a coluna `Custo Total` somando o salário do colaborador com os custos agregados.
- Salva o dataframe resultante em um arquivo chamado `Custo Colaboradores Final.xlsx`.

Trecho do código principal:

```python
def merge_normalized_spreadsheets(
    output_directory: str = "data/output",
    base_file_name: str = "Dados Colaboradores.xlsx",
    merged_file_name: str = "Custo Colaboradores Final.xlsx"
) -> str:
    base_file_path = os.path.join(output_directory, base_file_name)
    if not os.path.exists(base_file_path):
        return f"Arquivo base '{base_file_name}' não encontrado na pasta '{output_directory}'."

    base_df = pd.read_excel(base_file_path)
    output_files = [f for f in list_spreadsheets(output_directory) if os.path.basename(f) != base_file_name]

    custo_columns = []

    for file_path in output_files:
        df = pd.read_excel(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0].replace("normalized_", "")

        if "CPF" in df.columns and "Fatura" in df.columns:
            df_subset = df[["CPF", "Fatura"]].copy()
            df_subset.rename(columns={"Fatura": base_name}, inplace=True)

            base_df = pd.merge(base_df, df_subset, on="CPF", how="left")
            custo_columns.append(base_name)

    base_df.drop_duplicates(subset=["CPF", "Nome"], inplace=True)
    base_df["Custo Total"] = base_df[["Salario"] + custo_columns].fillna(0).sum(axis=1)

    merged_file_path = os.path.join(output_directory, merged_file_name)
    base_df.to_excel(merged_file_path, index=False)

    return f"Merge completo com sucesso. Planilha salva em '{merged_file_path}'"
```

Esse processo permite consolidar todas as informações de custo dos colaboradores em uma única planilha, facilitando análises e relatórios posteriores.


### 4. Agente de Limpeza e Normalização de Dados

Após a geração da planilha consolidada (`Custo Colaboradores Final.xlsx`), é essencial realizar uma **limpeza e padronização final dos dados** para garantir a consistência dos campos de texto, CPF e valores monetários. Para isso, foi criado um agente inteligente responsável por identificar e normalizar automaticamente essas colunas.

#### Objetivo do Agente

Esse agente tem como missão:

> "Analisar os primeiros registros da planilha e identificar colunas contendo dados textuais, CPFs e valores monetários. Em seguida, utilizar ferramentas específicas para normalizar essas colunas e retornar se a operação foi bem-sucedida."

#### Estrutura do Agente

O agente é definido com três componentes principais:

- **Role (Função):** `"Especialista em limpezade dados"`
- **Goal (Objetivo):** Identificar e normalizar colunas relevantes da planilha final (`textuais`, `CPF`, `valores`).
- **Backstory (História):** `"Você é um especialista em limpeza e padronização de dados de RH."`

#### Ferramentas Utilizadas

O agente tem acesso a três ferramentas específicas:

- `NormalizeTextTool`: Normaliza colunas textuais (como nome de funcionários, cargos etc.).
- `NormalizeCpfTool`: Padroniza e limpa os valores de CPF.
- `NormalizeMonetaryValuesTool`: Converte e normaliza valores monetários (ex.: salários, benefícios).

#### Execução da Tarefa

A tarefa entregue ao agente é detalhada e orientada por exemplos. Abaixo está um trecho do código responsável por essa execução:

```python
    agent = Agent(
        role="Data Cleaning Specialist",
        goal=(
            "Analyze the first records of the spreadsheet and identify columns containing textual datas, CPFs, and monetary values. "
            "Use the appropriate tools to normalize these columns."
            "Return whether saving the spreadsheet was successful or not"
        ),
        backstory="You are a specialist in HR data cleaning and normalization.",
        tools=[NormalizeTextTool, NormalizeCpfTool, NormalizeMonetaryValuesTool],
        llm=llm,
        verbose=True
    )

    task_description = (
        f"You are analyzing the spreadsheet '{file_path}'.\n\n"
        f"Columns: {columns}\n"
        f"Sample records:\n{sample_rows}\n\n"
        "Your task is:\n"
        "1. Identificar colunas com:\n"
        "   - Dados textuais (ex.: Nome, Cargo, Departamento)\n"
        "   - CPFs ou identificadores similares\n"
        "   - Valores monetários (ex.: Salário, Benefício)\n\n"
        "2. Para cada categoria identificada, chamar a ferramenta correspondente com a lista de colunas.\n"
        "3. Retornar se o processo de normalização foi bem-sucedido, indicando as colunas alteradas."
    )

    task = Task(
        description=task_description,
        expected_output="Final Answer: Success. Columns normalize: [<list of columns>]",
        tools=[NormalizeTextTool, NormalizeCpfTool, NormalizeMonetaryValuesTool],
        agent=agent
    )
```

#### Ferramentas
O agente criado utiliza três ferramentas específicas para normalizar dados em planilhas do Excel. Cada ferramenta é responsável por tratar um tipo específico de dado comum em planilhas de RH: CPFs, textos nominais (como nomes de funcionários) e valores monetários. 

##### 1. NormalizeCpfTool – "Normalize CPF Column"

**Objetivo:**  
Padronizar colunas que contenham CPFs ou identificadores similares, removendo pontos (`.`), hífens (`-`) e espaços em branco.

**Funcionamento:**

- Espera um dicionário com:
  - `'file_name'`: nome do arquivo Excel.
  - `'columns'`: lista de colunas com CPFs.

- Para cada coluna informada:
  - Converte os valores para string.
  - Remove todos os caracteres especiais com regex (`.`, `-`, espaços).
  
- Salva novamente a planilha com os valores normalizados.


```python

@tool("Normalize CPF Column")
def NormalizeCpfTool(args: dict) -> str:
    """
    Normalizes CPF-like columns by removing '.', '-', and spaces.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """
```

##### 2. NormalizeTextTool – "Normalize Text"

**Objetivo:**  
Padronizar colunas de texto como nomes de funcionários, cargos ou departamentos, removendo acentos, espaços extras e aplicando formatação em Title Case (inicial maiúscula em cada palavra).

**Funcionamento:**

- Espera um dicionário com:
  - `'file_name'`: nome do arquivo Excel.
  - `'columns'`: lista de colunas com texto nominal.

- Para cada coluna informada:
  - Remove espaços em branco extras.

  - Coloca em formato "Nome Sobrenome".

  - Remove acentos usando unicodedata.
  
- Salva novamente a planilha com os valores normalizados.


```python


@tool("Normalize Text")
def NormalizeTextTool(args: dict) -> str:
    """
    Normalizes name columns by removing accents, trimming spaces, and converting to title case.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """
```

##### 3. NormalizeMonetaryValuesTool – "Normalize Monetary Values"

**Objetivo:**  
Tratar colunas de valores financeiros, como salários ou benefícios, removendo símbolos (R$, $, etc.), convertendo para float e aplicando uma formatação padronizada com vírgula como separador decimal.

**Funcionamento:**

- Espera um dicionário com:
  - `'file_name'`: nome do arquivo Excel.
  - `'columns'`: lista de colunas com texto nominal.

- Para cada coluna informada:
  - Remove símbolos e caracteres não numéricos.

  - Converte o valor para float.

  - Reaplica a formatação no estilo brasileiro, como "1.234,56".
  
- Salva novamente a planilha com os valores normalizados.


```python


@tool("Normalize Text")
def NormalizeTextTool(args: dict) -> str:
    """
    Normalizes name columns by removing accents, trimming spaces, and converting to title case.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """
```

















