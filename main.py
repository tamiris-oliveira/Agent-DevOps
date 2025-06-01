from typing import List, Optional
import os
import re
import pandas as pd
import unicodedata
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

def list_spreadsheets(directory: str) -> List[str]:
    return [
        os.path.join(root, file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith((".xlsx", ".xls"))
    ]

def read_spreadsheet(file_path: str) -> Optional[pd.DataFrame]:
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        print(f"Error reading '{file_path}': {e}")
        return None

def load_spreadsheets(directory: str) -> tuple[list[pd.DataFrame], list[str]]:
    spreadsheet_paths = list_spreadsheets(directory)
    dataframes = []
    for path in spreadsheet_paths:
        print(f"Reading: {path}")
        df = read_spreadsheet(path)
        if df is not None:
            dataframes.append(df)
    return dataframes, spreadsheet_paths


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


def process_with_agent(llm, df: pd.DataFrame, file_name: str) -> str:
    column_names = list(df.columns)
    file_name = os.path.basename(file_name)

    agent = Agent(
        role="Column Normalizer",
        goal=(
            "Carefully analyze the spreadsheet columns and identify two columns:\n"
            "- One that contains the employee's CPF (or similar identifier)\n"
            "- One that contains the total cost\n"
            "Create a dictionary with these columns and the file name\n"
            "Use the 'Normalize Spreadsheets' tool to rename the columns in the loaded file\n"
            "Return whether saving the spreadsheet was successful or not"
        ),
        backstory="You are a specialist in standardizing employee cost spreadsheets.",
        tools=[NormalizeSpreadsheetsTool],
        verbose=True,
        llm=llm
    )

    task = Task(
        description=(
            f"You are processing the spreadsheet '{file_name}'.\n\n"
            f"Columns found: {column_names}.\n"
            "Your task is to identify which columns represent:\n"
            "- CPF or personal identifier (e.g., cpf, document, registration...)\n"
            "- Total tool or benefit cost (e.g., total value, cost, monthly fee...)\n\n"
            "Then, you must pass as input to the 'Normalize Spreadsheets' tool a Python dict in the format:\n"
            '''{
    "args": {
        "columns": [<cpf_column_name>, <cost_column_name>],
        "file_name": "<original file name.xlsx>"
    }
}'''
            "\nThis dict will be used by the 'Normalize Spreadsheets' tool to rename the columns and save the file."
        ),
        tools=[NormalizeSpreadsheetsTool],
        expected_output="Success. Columns renamed:",
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], tools=[NormalizeSpreadsheetsTool], verbose=True)
    result = crew.kickoff()
    return result


def merge_normalized_spreadsheets(
    output_directory: str = "data/output",
    base_file_name: str = "Dados Colaboradores.xlsx",
    merged_file_name: str = "Custo Colaboradores Final.xlsx"
) -> str:

    base_file_path = os.path.join(output_directory, base_file_name)
    if not os.path.exists(base_file_path):
        return f"Arquivo base '{base_file_name}' não encontrado na pasta '{output_directory}'."

    try:
        base_df = pd.read_excel(base_file_path)
    except Exception as e:
        return f"Erro ao ler o arquivo base '{base_file_name}': {e}"

    output_files = [f for f in list_spreadsheets(output_directory) if os.path.basename(f) != base_file_name]

    if not output_files:
        return "Nenhum arquivo normalizado encontrado para mesclar."

    custo_columns = [] 

    for file_path in output_files:
        try:
            df = pd.read_excel(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0].replace("normalized_", "")

            if "CPF" in df.columns and "Fatura" in df.columns:
                df_subset = df[["CPF", "Fatura"]].copy()
                df_subset.rename(columns={"Fatura": base_name}, inplace=True)

                base_df = pd.merge(base_df, df_subset, on="CPF", how="left")
                custo_columns.append(base_name)

        except Exception as e:
            print(f"Erro ao processar '{file_path}': {e}")

    base_df.drop_duplicates(subset=["CPF", "Nome"], inplace=True)

    try:
        base_df["Custo Total"] = base_df[["Salario"] + custo_columns].fillna(0).sum(axis=1)
    except KeyError as e:
        return f"Coluna esperada não encontrada: {e}"

    merged_file_path = os.path.join(output_directory, merged_file_name)

    try:
        base_df.to_excel(merged_file_path, index=False)
    except Exception as e:
        return f"Erro ao salvar a planilha mesclada: {e}"

    return f"Merge completo com sucesso. Planilha salva em '{merged_file_path}'"


@tool("Normalize CPF Column")
def NormalizeCpfTool(args: dict) -> str:
    """
    Normalizes CPF-like columns by removing '.', '-', and spaces.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """
    file_path = args.get("file_name")
    columns = args.get("columns", [])

    if not file_path:
        return "Missing 'file_name'."
    if not columns:
        return "Missing 'columns'."

    try:
        df = pd.read_excel(file_path)
        for col in columns:
            if col not in df.columns:
                return f"Column '{col}' not found in file."
            df[col] = df[col].astype(str).str.replace(r'[.\-\s]', '', regex=True)

        df.to_excel(file_path, index=False)
        return f"Success. Columns normalize: {columns}"
    except Exception as e:
        return f"Error"



@tool("Normalize Text")
def NormalizeTextTool(args: dict) -> str:
    """
    Normalizes name columns by removing accents, trimming spaces, and converting to title case.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """

    file_path = args.get("file_name")
    columns = args.get("columns", [])

    if not file_path:
        return "Missing 'file_name'."
    if not columns:
        return "Missing 'columns'."

    try:
        df = pd.read_excel(file_path)

        def normalize_name(name):
            name = str(name).strip().title()
            name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode()
            return name

        for col in columns:
            if col not in df.columns:
                return f"Column '{col}' not found in file."
            df[col] = df[col].apply(normalize_name)

        df.to_excel(file_path, index=False)
        return f"Success. Columns normalize: {columns}"
    except Exception as e:
        return f"Error"


@tool("Normalize Monetary Values")
def NormalizeMonetaryValuesTool(args: dict) -> str:
    """
    Normalizes monetary columns by removing currency symbols, converting to float,
    and formatting with 2 decimal places using comma as decimal separator.

    Expects:
    - 'file_name': Excel file name to process.
    - 'columns': list of column names to normalize.

    Returns whether saving the spreadsheet was successful or not.
    """
    file_path = args.get("file_name")
    columns = args.get("columns", [])

    if not file_path:
        return "Missing 'file_name'."
    if not columns or not isinstance(columns, list):
        return "'columns' must be a non-empty list."

    try:
        df = pd.read_excel(file_path)

        for col in columns:
            if col not in df.columns:
                return f"Column '{col}' not found in file."

            df[col] = (
                df[col]
                .astype(str)
                .str.replace(r'[^\d,.-]', '', regex=True)
                .str.replace(',', '.')
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].apply(
                lambda x: f"{x:,.2f}".replace('.', ',') if pd.notnull(x) else ''
            )

        df.to_excel(file_path, index=False)
        return f"Success. Columns normalized: {columns}"
    except Exception as e:
        return f"Error while processing: {e}"



def run_data_cleaning_agent(llm, file_path: str) -> str:
    df = pd.read_excel(file_path)
    columns = list(df.columns)
    sample_rows = df.head(2).to_dict(orient='records')
    
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
    f"Sample data:\n{sample_rows}\n\n"
    "Do the following:\n\n"
    "1. Categorize the columns into three groups:\n"
    "- name_columns: columns with names or text (e.g., 'Name', 'Employee', 'Department')\n"
    "- cpf_columns: columns with CPF or identifiers (e.g., 'CPF', 'Document')\n"
    "- value_columns: columns with monetary values (e.g., 'Salary', 'Monthly Value')\n\n"
    "2. Return a JSON with these lists:\n"
    '''{
    "name_columns": [...],
    "cpf_columns": [...],
    "value_columns": [...]
    }\n'''
    "3. For each non-empty list, call the matching tool:\n\n"
    "- If 'name_columns' is not empty, call:\n"
    '''{
    "args": {
        "columns": [...],
        "file_name": "<original_file_name.xlsx>"
    }
    }\n'''
    "with the **Normalize Text** tool\n\n"
    "- If 'cpf_columns' is not empty, call:\n"
    '''{
    "args": {
        "columns": [...],
        "file_name": "<original_file_name.xlsx>"
    }
    }\n'''
    "with the **Normalize CPF Column** tool\n\n"
    "- If 'value_columns' is not empty, call:\n"
    '''{
    "args": {
        "columns": [...],
        "file_name": "<original_file_name.xlsx>"
    }
    }\n'''
    "with the **Normalize Monetary Values** tool\n\n"
    "4. At the end, write:\n"
    "Thought: I now know the final answer\n"
    "Final Answer: Success. Columns normalize: [list of all normalized columns]\n"
    )



    task = Task(
        description=task_description,
        expected_output="Success",
        tools=[NormalizeTextTool, NormalizeCpfTool, NormalizeMonetaryValuesTool],
        agent=agent
    )

    crew = Crew(agents=[agent], tasks=[task], tools=[NormalizeTextTool, NormalizeCpfTool, NormalizeMonetaryValuesTool], verbose=False)
    result = crew.kickoff()
    return result


if __name__ == "__main__":
    llm = LLM(model="groq/llama-3.3-70b-versatile")

    data_directory = "data/costs"
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)

    dfs, spreadsheet_paths = load_spreadsheets(data_directory)

    if not dfs:
        print("No spreadsheets were loaded.")
    else:
        print(f"\n{len(dfs)} spreadsheet(s) loaded.\n")

        for i, df in enumerate(dfs):
            file_name = spreadsheet_paths[i]

            print(f"Processing spreadsheet {i+1}: {os.path.basename(file_name)}")

            result = process_with_agent(llm, df, file_name)
            print(f"Result:\n{result}\n")

        print("Iniciando merge das planilhas normalizadas...")
        merge_result = merge_normalized_spreadsheets()
        print(f"Resultado do merge:\n{merge_result}")

        file_path = "data/output/Custo Colaboradores Final.xlsx"
        result = run_data_cleaning_agent(llm, file_path)
        print(result)


