from src.config.logging import logger
from collections import defaultdict
from functools import lru_cache
from src.prune.llm import LLM
from typing import Generator
from typing import Tuple
from typing import Dict
from typing import List
from typing import Any
import jsonlines
import string
import re


class SearchResult:
    """
    Represents a search result from a JSONL file.

    Attributes:
        query (str): The search query.
        rank (int): The rank of the search result.
        title (str): The title of the search result.
        link (str): The URL link of the search result.
        snippet (str): The snippet or summary of the search result.
        metatags_title (str): The title obtained from metadata.
        subject (str): The subject or category of the search result.
        creationdate (str): The creation date of the search result.
    """

    def __init__(self, query: str, rank: int, title: str, link: str, snippet: str, 
                 metatags_title: str, subject: str, creationdate: str) -> None:
        self.query = query
        self.rank = rank
        self.title = title
        self.link = link
        self.snippet = snippet
        self.metatags_title = metatags_title
        self.subject = subject
        self.creationdate = creationdate

    def __repr__(self) -> str:
        return f"<SearchResult for: {self.query}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the SearchResult instance into a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the SearchResult instance.
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
    Utility class for re-ranking site search results based on specific query components using a Large Language Model (LLM).

    Attributes:
        llm (LLM): An instance of a Large Language Model for parsing search results.
        cache_size (int): The maximum number of cached query results.
    """

    def __init__(self, cache_size: int = 100) -> None:
        """
        Initializes the Reranker with an instance of LLM and sets up caching.

        Parameters:
            cache_size (int): The maximum number of cached query results.
        """
        self.llm = LLM()
        self.parse_query_cached = lru_cache(maxsize=cache_size)(self._parse_query_uncached)
        logger.info("Reranker initialized with cache size: %s", cache_size)

    def _parse_jsonl_file(self, file_path: str) -> Generator[SearchResult, None, None]:
        """
        Reads and parses a JSONL file, yielding each line as a SearchResult object.

        Parameters:
            file_path (str): Path to the JSONL file.

        Yields:
            SearchResult: An instance of SearchResult for each line in the JSONL file.
        """
        with jsonlines.open(file_path) as reader:
            for obj in reader:
                yield SearchResult(**obj)

    @lru_cache(maxsize=None)  # Cache for repeated queries
    def _parse_query_uncached(self, query: str) -> dict:
        """
        Internal method to parse a query using LLM, without caching.
        :param query: Query string to be parsed.
        :return: Dictionary of parsed query components.
        """
        try:
            # Remove 'site:' and 'filetype:' parts
            query = re.sub(r"\s+site:.*?(\s|$)", " ", query)
            query = re.sub(r"\s+filetype:.*?(\s|$)", " ", query)

            # Extract year using a regular expression for any four-digit number
            year_match = re.search(r"\b(\d{4})\b", query)
            if not year_match:
                return "Year not found in query"

            year = year_match.group(1)
            year_index = query.index(year)

            # Everything after year is report type
            report_type = query[year_index + len(year):].strip()

            # Everything before year is split into country and company name
            before_year = query[:year_index].strip()
            country_name_split = before_year.rsplit(' ', 1)  # Splitting at the last space

            if len(country_name_split) != 2:
                return "Could not find country and company name properly"

            company_name, country = country_name_split

            return {
                "company_name": company_name,
                "country": country,
                "year": year,
                "report_type": report_type
            }
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

    def _score_result(self, query_components: Dict[str, str], metadata_components: Dict[str, str]) -> Tuple[float, str]:
        """
        Scores a search result based on its alignment with the query components using string matching techniques.
        Applies different weights for different types of matches.

        Parameters:
        query_components (Dict[str, str]): Parsed query components.
        metadata_components (Dict[str, str]): Parsed metadata components.

        Returns:
        Tuple[float, str]: A tuple containing the score and rationale for the search result.
        """
        match_score = 0.0
        rationale = []

        # Function to remove punctuation and convert to lower case
        def clean_string(s):
            if s is None:
                return ""
            return s.translate(str.maketrans('', '', string.punctuation)).lower()


        # Weights for different components
        weights = {
            "company_name": 8,
            "report_type": 4,
            "year": 2,
            "country": 1
        }

        for key, value in query_components.items():
            cleaned_value = clean_string(value)
            for meta_key, meta_value in metadata_components.items():
                cleaned_meta_value = clean_string(meta_value)
                # Exact match
                if cleaned_value in cleaned_meta_value:
                    # Apply the weight based on the component type
                    weight = weights.get(key, 1)  # Default weight is 1 if key is not found in weights
                    match_score += 2 * weight  # Base score is 2, multiplied by the component's weight
                    rationale.append(f"Exact match for {key}={value} in {meta_key}={meta_value} with weight {weight}.")
        rationale_str = ' | '.join(rationale)
        logger.info(f"Scoring result with match score: {match_score} and rationale: {rationale_str}")
        return match_score, rationale_str
    

    def _score_result_for_penalty(self, query_components: Dict[str, str], metadata_components: Dict[str, str]) -> Tuple[float, str]:
        """
        Scores a search result for penalties based on its alignment with the query components using string matching.

        Parameters:
        query_components (Dict[str, str]): Parsed query components.
        metadata_components (Dict[str, str]): Parsed metadata components.

        Returns:
        Tuple[float, str]: A tuple containing the penalty score and rationale for the search result.
        """

        penalty_score = 0.0
        rationale = []

        # Weights for different components
        weights = {
            "company_name": 8,
            "report_type": 4,
            "year": 2,
            "country": 1
        }

        # Function to remove punctuation and convert to lower case
        def clean_string(s):
            if s is None:
                return ""
            return s.translate(str.maketrans('', '', string.punctuation)).lower()

        # Clean the strings in query and metadata components
        cleaned_query_components = {k: clean_string(v) for k, v in query_components.items()}
        cleaned_metadata_components = {k: clean_string(v) for k, v in metadata_components.items()}

        # Implement the penalty scoring logic using string matching techniques.
        for key, value in cleaned_query_components.items():
            if value not in cleaned_metadata_components.values():
                # Apply the corresponding weight for the penalty
                weight = weights.get(key, 1)  # Default weight is 1 if the key is not found in the weights dictionary
                penalty_score -= weight
                rationale.append(f"Penalty for missing {key} (Weight: {weight}).")

        rationale_str = ' | '.join(rationale)
        logger.info(f"Penalty scoring result with total score: {penalty_score} and rationale: {rationale_str}")

        return penalty_score, rationale_str

    

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


    def rerank(self, input_file_path, output_file_path, k=500) -> None:
        scored_rows = defaultdict(list)

        for row in self._parse_jsonl_file(input_file_path):
            rank = row.rank
            if rank <= k:
                query = row.query
                logger.info(f'Query: {query} | Rank: {rank}')
                query_components = self._parse_query(query)
                logger.info(f'Query components = {query_components}')
                snippet = row.snippet
                title = row.title
                subject = row.subject
                link = row.link
                creation_date = row.creationdate
                metatags_title = row.metatags_title
                result = {'snippet': snippet, 'title': title, 'subject': subject, 'link': link, 'creation_date': creation_date, 'metatags_title': metatags_title}
                match_score, match_rationale = self._score_result(query_components, result)
                penalty_score, penalty_rationale = self._score_result_for_penalty(query_components, result)
                row_dict = row.to_dict()
                row_dict['match_score'] = match_score
                row_dict['match_rationale'] = match_rationale
                row_dict['penalty_score'] = penalty_score
                row_dict['penalty_rationale'] = penalty_rationale
                row_dict['score'] = match_score + penalty_score  # additon since penalty_score is already negated
                scored_rows[query].append(row_dict)
        
        reranked_dict = self._rerank_rows_by_score(scored_rows)
        with jsonlines.open(output_file_path, mode='w') as writer:
            for _, rows in reranked_dict.items():
                for i, row in enumerate(rows):
                    row['new_rank'] = i+1
                    writer.write(row)

            
if __name__ == '__main__':
    reranker = Reranker()
    reranker.rerank('./data/evaluate/site-search-results-test-set-3-cdn.jsonl', './data/evaluate/site-search-results-test-set-3-cdn-reranked-string-matching.jsonl', k=30)