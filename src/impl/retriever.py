from interface.base_datastore import BaseDataStore
from interface.base_retriever import BaseRetriever
import cohere

class Retriver(BaseRetriever):
    def __init__(self, datastore: BaseDataStore):
        self.datastore = datastore

    def search(self, query: str, top_k: int = 10) -> list[str]:
        """
            list[str] -> generic type
            List[str] -> enhance

            Vector search finds documents that are on the same topic, 
            while reranking analyzes them deeply to 
            select the ones that actually answer the user's question.
        """
        search_results = self.datastore.search(query, top_k=top_k * 3)
        reranked_results = self._rerank(query, search_results, top_k=top_k)
        return reranked_results 

    def _rerank(self, query: str, search_results: list[str], top_k: int = 10) -> list[str]:

        co = cohere.ClientV2()
        response = co.rerank(
            model="rerank-v3.5",
            query=query,
            documents=search_results,
            top_n=top_k
        )

        result_indices = [result.index for result in response.results]
        print(f"Reranked Indices: {result_indices}")
        return [search_results[i] for i in result_indices]

    