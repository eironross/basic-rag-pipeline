from typing import List
from interface.base_datastore import BaseDataStore
from schema.schema import DataItem

# production db vector LLM application  
# use chromevb if you just need something for POC
from lancedb.table import Table 
import lancedb

import pyarrow as pa
from openai import OpenAI

from concurrent.futures import ThreadPoolExecutor

class DataStore(BaseDataStore):
    # attributes but owned by the Class
    DB_PATH = "data/sample-lancedb"
    DB_TABLE_NAME = "rag_table"
    VECTOR_DIMENSIONS = 1536

    def __init__ (self):
        # attributes own by the instance
        self.vector_dimension = self.VECTOR_DIMENSIONS # openai dimensions
        self.open_ai_client = OpenAI()
        self.vector_db = lancedb.connect(self.DB_PATH)
        self.table: Table = self._get_table()

    def reset(self) -> Table:
        try:
            self.vector_db.drop_table(self.DB_TABLE_NAME)
            
        except Exception as e:
            print("Unable to drop Table. Assuming it doesn't exists.")

        # Create a new table
        schema = pa.schema(
            [
                pa.field("vector", pa.list_(pa.float32(), self.vector_dimension)),
                pa.field("content", pa.utf8()),
                pa.field("source", pa.utf8()),
            ]
        )

        self.vector_db.create_table(self.DB_TABLE_NAME, schema=schema)
        self.table = self.vector_db.open_table(self.DB_TABLE_NAME)
        print(f"Table reset/Created: {self.DB_TABLE_NAME} in {self.DB_PATH}")
        return self.table

    def get_vector(self, content: str) -> List[float]:
        response = self.open_ai_client.embeddings.create(
            input=content,
            model="text-embedding-3-small",
            dimensions=self.vector_dimensions
        )

        embeddings = response.data[0].embedding
        return embeddings

    def add_items(self, items: List[DataItem]):
        # multiple worker, threadpool finish all task in one go, assembly
        # one worker, async, liked an employee swivel. 
        #   do task while wating do another task then work another task then go to another task
        with ThreadPoolExecutor(max_workers=8) as executor:
            entries = list(
                executor.map(self._convert_item_to_entry, items)
            )      

        self.table.merge_insert(
            "source",
        ).when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute(entries)

    def search(self, query: str, top_k: int = 5) -> List[str]:
        vector = self.get_vector(query)
        results = (
            self.table.search(vector)
            .select(["content", "source"])
            .limit(top_k)
            .to_list()
        )
        result_content = [result.get("content") for result in results]
        return result_content

    def _get_table(self) -> Table:
        try:    
            return self.vector_db.open_table(self.DB_TABLE_NAME)

        except Exception as e:
            print(f"Error opening table. Try resetting the datastore.")
            return self.reset()

    def _convert_item_to_entry(self, item: DataItem) -> dict:
        vector = self.get_vector(item.content)
        return {
            "vector": vector,
            "content": item.content,
            "source": item.source,
        }