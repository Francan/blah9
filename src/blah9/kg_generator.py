import os
from functools import reduce
import re
import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_core.messages import HumanMessage, SystemMessage
from src.blah9.merge_output_schema import MergerModel
from src.blah9.prompts import (
    NER_PROMPT,
    DATASET_MERGE_PROMPT,
    SYSTEM_PROMPT,
    CYPHER_GENERATION_TEMPLATE,
)


MODEL_VERSION: str = "gpt-4o"
MODEL_TEMPERATURE: float = 0


class KgGenerator:
    def __init__(self, dfs_n_descs: list[tuple[str, pd.DataFrame]]) -> None:
        self.__dfs_n_descs = dfs_n_descs
        # Initialize the model
        self.llm: BaseChatModel = ChatOpenAI(
            model=MODEL_VERSION,
            temperature=MODEL_TEMPERATURE,
        )

        self.__neo4j = self.__init_neo4j_driver()

    def ner(self):
        # existing_schema: dict[str, Any] = self.__neo4j.get_structured_schema
        # existing_prompt: str = (
        #     "The current schema looks like this:\n"
        #     f"node_props: {existing_schema['node_props']}\n"
        #     f"rel_props: {existing_schema['rel_props']}\n"
        #     f"relationships: {existing_schema['relationships']}\n"
        # )

        system_prompt: str = SYSTEM_PROMPT
        merge_prompt: str = NER_PROMPT

        data_prompt: list[str] = self.__get_data_prompt()

        user_prompt: str = merge_prompt + "\n\n" + "\n".join(data_prompt)
        merge_prompt_template = [
            SystemMessage(system_prompt),
            HumanMessage(user_prompt),
        ]
        res: str = self.__llm.invoke(merge_prompt_template).content

        match = re.search(r"```cypher\n(.*?)\n```", res, re.DOTALL)

        if match:
            content = match.group(1)
            self.__neo4j.query(content)
            print(content)
        else:
            print("No match found.")

    def __get_data_prompt(self) -> list[str]:
        new_schemas: list[str] = []
        for idx, (desc, df) in enumerate(self.__dfs_n_descs):
            example_values = ""
            for c_name in df.columns.values:
                samples = df[c_name][0:3].values
                samples = [
                    (
                        sample
                        if not isinstance(sample, str)
                        else (
                            f"{' '.join(sample.split()[:4])}..."
                            if len(sample.split()) > 5
                            else sample
                        )
                    )
                    for sample in samples
                ]
                text = f"\t{c_name}: [{reduce(lambda acc,elem: f'{acc}, {elem}', samples)}]\n"

                example_values += text

            text = (
                f"Dataset {idx}:\n"
                f"Columns: [{', '.join(df.columns.values.tolist())}]\n"
                f"Sample data:\n{example_values}"
                f"Explanation: {desc}\n"
            )
            new_schemas.append(text)

        return new_schemas

    def merge(
        self,
    ):
        data_prompt: list[str] = self.__get_data_prompt()

        parser = JsonOutputParser(pydantic_object=MergerModel)

        prompt_template = PromptTemplate(
            template=DATASET_MERGE_PROMPT,
            partial_variables={"format_instructions": parser.get_format_instructions()},
            input_variables=["user_input"],
        )

        chain = prompt_template | self.llm | parser

        # Ev. compute cosine similarity score between column names and provide it in the prompt
        response: MergerModel = MergerModel.model_validate(
            chain.invoke(
                {
                    "user_input": "\n".join(data_prompt),
                }
            )
        )

        for idx, (desc, df) in enumerate(self.__dfs_n_descs):
            for c_name in df.columns:
                for shared_columns in response.shared_columns:
                    # for dataset_idx, shared_c_name in shared_columns.items():
                    if c_name in shared_columns.values():
                        df.rename(
                            columns={c_name: list(shared_columns.values())[0]},
                            inplace=True,
                        )
                        re.sub(c_name, list(shared_columns.values())[0], desc)

        dfs: list[pd.DataFrame] = []
        for _, df in self.__dfs_n_descs:
            column_intersection: list[str] = list(
                set(df.columns.values).intersection(
                    set(response.combined_dataset_schema)
                )
            )
            dfs.append(df[column_intersection])

        merged_dfs: pd.DataFrame = dfs[1]
        for df in dfs[1:]:
            for shared_columns in response.shared_columns:
                column_names: list[str] = list(shared_columns.values())
                if set(df.columns.values).intersection(set(column_names)):
                    merged_dfs = pd.merge(merged_dfs, df, on=column_names[0])
                    break

        merged_dfs

    def __cypher_query_gen(self):
        cypher_generation_prompt = PromptTemplate(
            template=CYPHER_GENERATION_TEMPLATE,
            input_variables=["schema", "question"],
        )

        cypher_chain = GraphCypherQAChain.from_llm(
            self.__llm,
            graph=self.__neo4j,
            cypher_prompt=cypher_generation_prompt,
            verbose=True,
            allow_dangerous_requests=True,
        )

        cypher_chain.invoke({"query": "List all entities and relationships"})

    def __init_neo4j_driver(
        self,
    ) -> Neo4jGraph:
        # Neo4J driver
        url = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        return Neo4jGraph(
            url=url,
            username=username,
            password=password,
        )
