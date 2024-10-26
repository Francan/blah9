# blah9
Project proposal for the Biomedical Linked Annotation Hackathon 9
# Dataset extraction from Graph & Vector DB with automatic relation generation using LLM

## Abstract
Biomedical datasets for AI training are becoming increasingly available, yet each still requires extensive analysis to assess intra-dataset connections, column relevance, etc., which enforces repetitive per-project manual work to find and select the relevant data.
What we propose instead is an automatic system that supports loading arbitrary datasets into a central graph database to form a relationship-based collection, supporting unstructured user queries. The relations between entities are automatically generated by the system, identifying connection points that can relate the imported data. The user will then be able to write a query in natural language about the task at hand, which will result in a selection from the available data relevant for the user.
The objective is to expedite the data selection process, enabling a data-lake-like workflow, relying on the automatic system for the task-specific dataset selection. Additionally, the automatically generated entity relations may bring out relevant connections that could have otherwise gone unused.
## Project Goals:
1. Develop a system capable of extracting subsets of data from a larger collection that fits a user unstructured query.
2. Explore and report on the abilities of the chosen LLM in the creation of automatic entity relationships and data selection upon user query.
## Procedures:
1. Dataset pre-processing: A pipeline for pre-processing operations such as loading, normalization, and structurization of the datasets.
2. Database import: Pipeline responsible for optimal mapping of the source data to Neo4J representations.
3. Entity Relation automatic generation: Explore LLM for generating automatic entity relations.
4. User query: Explore embeddings & similarity scores versus LLM for returning the most fitting data selection to the user.
5. Validation: compare the automatic system selection relevance, against a fixed set of known optimal results.


## Technology Stack:
- Neo4j: Neo4J is a database that supports both graph and vector storage, which simplifies data retrieval when using vector similarity-based algorithms.
- LLM: given the constrained time available for the hackathon, training or fine-tuning an AI may be detrimental to achieving the set goals, therefore a more sensible alternative would be to employ off-the-shelf SOTA LLMs, such as ChatGPT or Gemini.
- Python: python is the most widely used programming language when working with AI, and provide numerous libraries and frameworks suited for AI projects.
- Langchain: Langchain is a framework that simplifies the creation of LLM’s chains, from prompting, to RAG strategies. The use of Langchain would greatly abstract the development from the LLM of choice API and standardize the workflow around good practices.


## Datasets:
As a provisional dataset selection, the following are datasets in the biomedical fields that may be used throughout the development. All are openly accessible, and contain data related to drugs and diseases.
- https://www.kaggle.com/datasets/jessicali9530/kuc-hackathon-winter-2018: A dataset containing data about drugs, the patient condition and patients’ review of the drug.
- https://www.kaggle.com/datasets/sergeguillemart/drugbank/data: Renown Drugbank collection of drugs information such as name, brand names and indications.
- https://healthdata.gov/dataset/Project-Tycho-Level-1-Data/g89t-x93h/about_data: Dataset about diseases counts by US states and cities.


While the datasets have been chosen as candidates to highlight the goal of the proposed project, they are not meant as a one-off use case for this solution.

![Reference image](/assets/images/proposal_image.png "Proposal Image")

