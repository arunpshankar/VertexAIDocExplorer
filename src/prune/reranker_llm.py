from src.config.logging import logger
from collections import defaultdict
from typing import Dict, List, Any
from functools import lru_cache
from src.prune.llm import LLM
import jsonlines
import json


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
    

    def _extract_score_and_rationale(self, input_string) -> dict:
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

        return {
            "score": score,
            "rationale": input_string
        }
    

    def _score_result_for_penalty(self, query_components: dict, metadata_components) -> str:
        """
        Scores a search result based on its alignment with the query components.

        :param result: A single search result.
        :param query_components: Parsed query components.
        :param metadata_components: Parsed metadata components. 
        :return: Score for the search result as a JSON string.
        """
        prompt = f"""First, extract all the company names from the provided metadata components. List them numerically under the heading 'EXTRACTED COMPANY NAMES'.
important: focus on the title and snippet fields from the metadata components provided below especially
METADATA COMPONENTS: => {metadata_components}

EXTRACTED COMPANY NAMES =>

Next, remove the company name from the extracted list if the company name is already present in the QUERY COMPONENTS provided below.
QUERY COMPONENTS => {query_components}

The resulting list now, labeled 'REMAINING COMPANY NAMES', should only contain only the company names that were not removed.
REMAINING COMPANY NAMES =>

Start with an initial penalty score of 0
INITIAL_PENALTY_SCORE_COMPANY_NAMES = 0

Subtract 4 from the initial penalty score for each one of the companies in REMAINING COMPANY NAMES list.
VERY IMPORTANT: DO NOT count None, nothing, or an empty list as 1 when computing scores. Validate this by counting the number of REMAINING COMPANY NAMES. If it is 0, DO NOT subtract.

IMPORTANT: The FINAL PENALTY SCORE should always be zero or negative.

Provide a rationale for each score and explain how the FINAL PENALTY SCORE was computed.

RATIONALE =>

FINAL PENALTY SCORE =>

IMPORTANT: The FINAL PENALTY SCORE should match what is explained in the rationale.

Lastly, create a JSON string with a single key, "total_score". The value should be the final penalty score calculated in the previous step.""" 
        prediction = self.llm.model.predict(prompt)
        return prediction

    def _score_result(self, query_components: dict, metadata_components) -> str:
        """
        Scores a search result based on its alignment with the query components.

        :param result: A single search result.
        :param query_components: Parsed query components.
        :param metadata_components: Parsed metadata components. 
        :return: Score for the search result as a JSON string.
        """
        prompt = f"""First, calculate the matching scores for each query component against each metadata component using the given query components (QUERY_COMPONENTS) and metadata components (METADATA_COMPONENTS).

For example, search `company_name` against `snippet`, `title`, `subject`, `link`, and `metatags_title` in that order. Repeat this process for `report_type`, `country`, and `year`. Additionally, perform an extra search for `year` against `creation_date`.

QUERY_COMPONENTS => {query_components}
METADATA_COMPONENTS => {metadata_components}

Next, assign a score to each query component based on confidence levels:
0 = not confident
1 = partially confident
2 = confident

Then, multiply each score by its corresponding weight:
company name = 8
report type = 4
year = 2
country = 1

Remember to apply the weights.

A query component like `company_name` might match several metadata components such as `title`, `snippet`, and `link`. In these cases, add the scores for each match.

IMPORTANT: If there is an exact match with the company name, double the score. An "exact match" is when a specific sequence of words is found in the text exactly as it appears, with no variation. For example, if the company name is "Columbia Financial Inc.", the snippet should contain these three words in the correct order. Casing and minor punctuation should be ignored.
DO NOT double the score if it is a partial match. 

SCORES =>

Next, calculate the total score by adding all the weighted scores.

TOTAL SCORE =>

Then, provide a rationale for each assigned confidence level and the calculated score for each component. Specify where the match was found, such as the company name in the snippet, or the report type in the subject.

RATIONALE =>

Finally, generate a valid JSON output with the ONLY ONE key as `total_score`, and the value being the total score computed above."""
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
                logger.info(f'Query: {query} | Rank: {rank}')
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
                penalty_prediction = self._score_result_for_penalty(query_components, result)
                score_rationale = self._extract_score_and_rationale(penalty_prediction)
                penalty_score = score_rationale.get('score')  
                penalty_rationale = score_rationale.get('rationale') 
                row_dict = row.to_dict()

                if not isinstance(score, float) and score is None:
                    score = 0.0

                if not isinstance(penalty_score, float) and penalty_score is None:
                    penalty_score = 0.0

                row_dict['match_score'] = score
                row_dict['match_rationale'] = rationale
                row_dict['penalty_score'] = penalty_score
                row_dict['penalty_rationale'] = penalty_rationale
                row_dict['score'] = score + penalty_score  # additon since penalty_score is already negated
                scored_rows[query].append(row_dict)
        
        reranked_dict = self._rerank_rows_by_score(scored_rows)
        with jsonlines.open(output_file_path, mode='w') as writer:
            for _, rows in reranked_dict.items():
                for i, row in enumerate(rows):
                    row['new_rank'] = i+1
                    writer.write(row)

            
if __name__ == '__main__':
    reranker = Reranker()
    reranker.rerank('./data/evaluate/site-search-results-test-set-3-cdn.jsonl', './data/evaluate/site-search-results-test-set-3-cdn-reranked.jsonl', k=25)