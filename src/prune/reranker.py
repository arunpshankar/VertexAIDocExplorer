from src.config.logging import logger
from collections import defaultdict
from typing import Dict, List, Any
from functools import lru_cache
from src.prune.llm import LLM
import jsonlines
import json
import re 


class SearchResult:
    """
    Class representing a search result from a JSONL file.
    """
    def __init__(self, query, rank, title, link, snippet, metatags_title, subject, creationdate):
        self.query = query
        self.rank = rank
        self.title = title
        self.link = link
        self.snippet = snippet
        self.metatags_title = metatags_title
        self.subject = subject
        self.creationdate = creationdate

    def __repr__(self):
        return f"<SearchResult for: {self.query}>"

    def to_dict(self):
        """
        Converts the SearchResult instance into a dictionary.
        """
        return {
            'query': self.query,
            'rank': self.rank,
            'title': self.title,
            'link': self.link,
            'snippet': self.snippet,
            'metatags_title': self.metatags_title,
            'subject': self.subject,
            'creationdate': self.creationdate
        }


class Reranker:
    """
    A utility class for re-ranking site search results based on specific query components.
    This class leverages a Large Language Model (LLM) for parsing and scoring search result metadata.
    """

    def __init__(self, cache_size=100) -> None:
        """
        Initializes the Reranker with an instance of LLM and sets up caching.
        :param cache_size: The maximum number of cached query results.
        """
        self.llm = LLM()
        self.parse_query_cached = lru_cache(maxsize=cache_size)(self._parse_query_uncached)
        logger.info("Reranker initialized with cache size: %s", cache_size)

    def _parse_jsonl_file(self, file_path: str):
        """
        Reads and parses a JSONL file, yielding each line as a SearchResult object.

        :param file_path: Path to the JSONL file.
        :return: Generator yielding each line as a SearchResult object.
        """
        with jsonlines.open(file_path) as reader:
            for obj in reader:
                search_result = SearchResult(**obj)
                yield search_result


    @lru_cache(maxsize=None)  # Cache for repeated queries
    def _parse_query_uncached(self, query: str) -> dict:
        """
        Internal method to parse a query using LLM, without caching.
        :param query: Query string to be parsed.
        :return: Dictionary of parsed query components.
        """
        try:
            components = []
            prompt = f"""Given a query (QUERY), break it into key-value pairs (KV), similar to the examples shown below:

QUERY => Brookline Bancorp Inc USA 2022 10-K/A site:cloudfront.net/ filetype:pdf
KV => company_name=Brookline Bancorp Inc|country=USA|year=2022|report_type=10-K/A

QUERY => Commerzbank AG GERMANY 2022 10-Q site:commerzbank.com/ filetype:pdf
KV => company_name=Commerzbank AG|country=GERMANY|year=2022|report_type=10-Q

QUERY => Hamburger Sparkasse AG GERMANY 2022 Annual Report site:haspa.de/ filetype:pdf
KV => company_name=Hamburger Sparkasse AG|country=GERMANY|year=2022|report_type=Annual Report

QUERY => {query}
KV =>"""
            prediction = self.llm.model.predict(prompt)
            return prediction
        except Exception as e:
            logger.error(f"Error parsing query with LLM: {e}")
            return {}
        

    def _parse_query(self, query: str) -> dict:
        """
        Parses the query string into key-value pairs, using caching for repeated queries.
        :param query: Query string to be parsed.
        :return: Dictionary of parsed query components.
        """
        return self.parse_query_cached(query)
    

    def _extract_score_and_rationale(self, input_string):
        """
        Extracts the score and rationale from a given string containing JSON data.

        Parameters:
        input_string (str): A string containing JSON data.

        Returns:
        dict: A dictionary with 'score' and 'rationale' extracted from the JSON data.
        """
        # Extracting JSON substring from the input
        json_start = input_string.find('{')
        json_end = input_string.rfind('}') + 1
        json_string = input_string[json_start:json_end]

        # Replacing newline characters with escape characters for JSON parsing
        json_string_fixed = json_string.replace('\n', '\\n')

        # Parsing the JSON string
        try:
            json_data = json.loads(json_string_fixed)
        except json.JSONDecodeError as e:
            return {"error": "JSON decoding error: " + str(e)}

        # Extracting the desired data
        score = json_data.get('total_score', 'Not found')
        rationale = json_data.get('rationale', 'Not found')

        return {
            "score": score,
            "rationale": rationale
        }


    def _score_result(self, query_components: dict, metadata_components) -> float:
        """
        Scores a search result based on its alignment with the query components.

        :param result: A single search result.
        :param query_components: Parsed query components.
        :return: Score for the search result.
        """
        prompt = f"""Given query components (QUERY_COMPONENTS) and metadata components (METADATA_COMPONENTS), compute the alignment scores of each query component against its corresponding metadata component from the search result.

QUERY_COMPONENTS => {query_components}
METADATA COMPONENTS => {metadata_components}

Assign a score to each query component based on these confidence levels:
0 = not confident
0.5 = partially confident
1 = confident

Subsequently, multiply each score by its corresponding weight:
company name = 4
report type = 3
year = 2
country = 1

IMPORTANT: REMEMBER TO MULTIPLY BY THE WEIGHTS

SCORES =>

Next, calculate the total score by summing all the weighted scores.

TOTAL SCORE =>

Then, explain the reasoning behind each assigned confidence level for every calculated score.

RATIONALE =>

Lastly, compile a valid JSON with two keys: total_score and rationale. IMPORTANT: Remember to escape double quotes."""
        prediction = self.llm.model.predict(prompt)
        return prediction
    

    def _rerank_rows_by_score(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Reranks the rows in the provided dictionary based on their 'score' in descending order.

        Parameters:
        data (Dict[str, List[Dict[str, Any]]]): A dictionary where the key is a string (typically a query) and
                                                the value is a list of dictionaries, each representing a row
                                                with various attributes like query, rank, title, link, snippet, etc.

        Returns:
        Dict[str, List[Dict[str, Any]]]: An updated dictionary with the same key, but with the list of rows
                                        reordered based on their 'score' in descending order.
        """

        # Assuming there's only one key in the dictionary and reordering the list based on 'score'
        for key in data:
            data[key] = sorted(data[key], key=lambda x: float(x['score']), reverse=True)

        return data


    def rerank(self, input_file_path, output_file_path, k=10) -> None:
        scored_rows = defaultdict(list)

        for row in self._parse_jsonl_file(input_file_path):
            rank = row.rank
            if rank <= k:
                query = row.query
                logger.info(f'Query: {query}')
                query_components = self._parse_query(query)
                snippet = row.snippet
                title = row.title
                subject = row.subject
                link = row.link
                creation_date = row.creationdate
                metatags_title = row.metatags_title
                result = f"snippet={snippet}|title={title}|subject={subject}|link={link}|creation_date={creation_date}|metatags_title={metatags_title}"
                prediction = self._score_result(query_components, result)
                score_rationale = self._extract_score_and_rationale(prediction)
                score = score_rationale.get('score')
                rationale = score_rationale.get('rationale')
                row_dict = row.to_dict()

                if not isinstance(score, float) and score is None:
                    score = 0.0

                row_dict['score'] = score
                row_dict['rationale'] = rationale
                scored_rows[query].append(row_dict)
        
        reranked_dict = self._rerank_rows_by_score(scored_rows)
        with jsonlines.open(output_file_path, mode='w') as writer:
            for _, rows in reranked_dict.items():
                for i, row in enumerate(rows):
                    row['new_rank'] = i+1
                    writer.write(row)

            
if __name__ == '__main__':
    reranker = Reranker()
    reranker.rerank('./data/evaluate/site-search-results-test-set-3-cdn.jsonl', './data/evaluate/site-search-results-test-set-3-cdn-reranked.jsonl', k=10)