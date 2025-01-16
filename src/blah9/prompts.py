SYSTEM_PROMPT: str = ""
NER_PROMPT: str = """
From the following list of structured datasets explanations, column names and samples, identify the entities and possible relationships suitable to be stored in a graph database like Neo4J
Respond with a valid CYPHER query that would generate the entities and the connecting relationships, if there are any.
Columns with the exact same name among the different datasets represent shared columns, which allow the datasets to be connected between one another

Respond only with the CYPHER query, nothing else.
This is an example where the input are 2 datasets:

BEGIN Example
BEGIN Set number: 0
Description: Dataset about drugs and diseases to treat a disease. disease is the disease name and drug_id is the drug name. 
Column names and example data: 
    Column name: disease  
    Column data samples: HEPATITIS A | HEPATITIS B | HEPATITIS C
    Column name: drug_id  
    Column data samples: interferon | ribavirin | antiviral
END Set number: 0

BEGIN Set number: 1
Description: Dataset about drugs and drug quantities to inject. drug_id is the drug name and drug_quantity is the amount to inject. 
    Column name: drug_id    
    Column data samples: interferon | ribavirin | antiviral
    Column name: drug_quantity  
    Column data samples: 5 | 10 | 20
END Set number: 1

Response:
MERGE (e1:drug_id {description: drug name})
MERGE (e2:disease {description: disease is the disease name})
MERGE (e3:drug_quantity {description: amount to inject})
MERGE (e1)-[:TREATMENT_FOR]->(e2)
MERGE (e1)<-[:TREATED_WITH]-(e2)
MERGE (e1)-[:INJECTABLE_QUANTITY]->(e3)

END Example

Input structured datasets:
"""

# Consider the column name, the sample data it contains and the dataset explanation to decide whether two or more columns from different datasets can be merged toghether.
DATASET_MERGE_PROMPT: str = """
You are an advanced data analysis assistant. Your task is to analyze datasets, identify columns that are conceptually or semantically related, and suggest subsets of data that can be merged based on these shared or related columns.

### Input details:
1. Each dataset will be provided with:
    - Column names.
    - Sample data for each column.
    - A general explanation of the dataset's purpose and context (if available).
2. Datasets may come from different sources and may use different naming conventions for related data.

### Task instruction:
1. Identify columns that are semantically or conceptually related across datasets. Consider:
   - Synonyms or closely related terms (e.g., `condition` and `disease`).
   - Column descriptions or dataset context to infer relationships.
   - Overlapping or similar sample data values.
2. Suggest subsets of data from each dataset that can be combined based on these related columns.
3. Create a schema for the combined dataset, listing all relevant columns from each dataset.
4. If relationships are unclear, explain the reasoning behind your decisions.

### Output Format:
Provide the output as a JSON object with the following structure:
{{
  "shared_columns": [
    {{
      "dataset_1_column": "column_name_from_dataset_1",
      "dataset_2_column": "column_name_from_dataset_2"
    }}
  ],
  "combined_dataset_schema": [
    "column_name_1",
    "column_name_2",
    "column_name_3",
    "...additional_column_names"
  ],
  "explanation": "Explanation of why these columns were combined."
}}
If no shared columns are found, return:
{{
  "shared_columns": [],
  "combined_dataset_schema": [],
  "explanation": "No shared columns were found. Consider additional metadata or transformations."
}}

{format_instructions}

### Example Input:
Dataset A:
* Columns: [drug_names, diseases, prescription_count]
* Sample data:
    * drug_names: ["Aspirin", "Paracetamol", "Ibuprofen"]
    * diseases: ["Headache", "Fever", "Arthritis"]
    * prescription_count: [100, 200, 300]
* Explanation: This dataset contains information about drugs prescribed for various diseases.
Dataset B:
* Columns: [drugs, toxicity_level, side_effects]
* Sample data:
    * drugs: ["Aspirin", "Ibuprofen", "Amoxicillin"]
    * toxicity_level: ["Low", "Moderate", "High"]
    * side_effects: ["Nausea", "Drowsiness", "Rash"]
* Explanation: This dataset lists drugs with their toxicity levels and common side effects.

### Example Output:
{{
  "shared_columns": [
    {{
      "dataset_1_column": "drug_names",
      "dataset_2_column": "drugs"
    }}
  ],
  "combined_dataset_schema": [
    "drug_names",
    "diseases",
    "prescription_count",
    "toxicity_level",
    "side_effects"
  ],
  "explanation": "The shared column `drug_names` in Dataset A matches `drugs` in Dataset B. This allows us to combine drug information, diseases, prescription counts, toxicity levels, and side effects."
}}

Now analyze the following datasets and provide the output in JSON format:
[Insert dataset details here]
{user_input}
"""

DATASET_MERGE_PROMPT_2: str = """
You are an advanced data analysis assistant. Your task is to determine whether datasets from different sources share common columns that would allow them to be combined.

Each dataset will be provided in a structured text format with:

1. Column names.
2. Sample data for each column (if available).
3. A general explanation of the dataset, including its source and context.

Instructions:
1. Analyze the column names and sample data of the provided datasets.
2. Identify common or potentially related columns across the datasets.
3. Consider synonyms, variations in naming conventions, and possible data transformations that could align the datasets.
4. Provide a list of matching or related columns, along with a short explanation of why they match (e.g., similar names, overlapping data types, or comparable sample values).

Example Input:
Dataset A:
* Columns: user_id, email, signup_date
* Sample data:
    * user_id: [1, 2, 3]
    * email: [example1@mail.com, example2@mail.com, example3@mail.com]
    * signup_date: [2022-01-01, 2022-01-02, 2022-01-03]
* Explanation: This dataset tracks users who signed up for a newsletter.

Dataset B:
* Columns: client_id, contact_email, registration_date
* Sample data:
    * client_id: [101, 102, 103]
    * contact_email: [example1@mail.com, example4@mail.com, example5@mail.com]
    * registration_date: [2022-01-01, 2022-01-05, 2022-01-07]
* Explanation: This dataset contains information about customers who registered for a product.

Example Output:
Common columns:
* user_id (Dataset A), client_id (Dataset B), these may correspond as unique identifiers for users/customers.
* email (Dataset A), contact_email (Dataset B), these columns share overlapping values and likely represent the same information.
* signup_date (Dataset A), registration_date (Dataset B), similar semantics suggest these track the same type of event.

Notes:
* If you find no common columns, do not respond.
* Assume the datasets are formatted as JSON, CSV, or other structured text inputs.
* For each set of common columns, return the name of the column, its source dataset name and finally an explanation.

Now, analyze the following datasets and identify common columns or potential mappings:
[Insert dataset details here]
"""
DATASET_MERGE_PROMPT_3: str = """
You are an expert in identifying columns across multiple datasets that can be merged toghether.
Your goal is to identify sets of column names that describe the same data.
In the section ##Input structured datasets, you will find a list of datasets, comprising of a general explanation about the dataset, the dataset column names and samples of the data for each column.
There can be no two similar columns within the same dataset, only between a dataset and another.
For each set of identified columns, write the column names, followed by an explanation about why you think those columns are identical.

This is an example where the input are 2 datasets:

BEGIN Example
BEGIN Set number: 0
Description: Dataset about drugs and diseases to treat a disease. drug_id is a drug identifier, disease is the disease name and drug is the drug name. 
Column names and example data: 
    Column name: disease
    Column data examples: HEPATITIS A | HEPATITIS B | HEPATITIS C
    Column name: drug
    Column data examples: paracetamol | SSRI | dafalgan
    Column name: drug_id
    Column data examples: 5150 | 1235 | 99284
END Set number: 0

BEGIN Set number: 1
Description: Dataset about drugs and drug quantities to inject. drug_name is the drug name, drug_identifier is a unique drug id and drug_quantity is the amount to inject. 
    Column name: drug_name
    Column data examples: interferon | ribavirin | antiviral
    Column name: drug_identifier
    Column data examples: 2001 | 1232 | 45678
    Column name: drug_quantity
    Column data examples: 5 | 10 | 20
END Set number: 1

Response:
drug, drug_name, drug and drug_name are the same columns as they contain drugs names
drug_id, drug_identifier, both column stand as identifiers to uniquely identify a drug
END Example

Return only sets where the columns are identical

##Input structured datasets:
"""

NER_CYPHER_PROMPT: str = (
    "You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations."
)

CYPHER_GENERATION_TEMPLATE: str = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about movies and provide recommendations.
Convert the user's question based on the schema.

Schema: {schema}
Question: {question}
"""
