# https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb
import openai
from typing import Dict, List, Tuple
import numpy as np
import tiktoken
import os

from dotenv import load_dotenv

load_dotenv()

COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"

openai.api_key = os.getenv('OPEN_AI_API_KEY')

def get_embedding(text: str, model: str=EMBEDDING_MODEL) -> List[float]:
	result = openai.Embedding.create(
	  model=model,
	  input=text
	)
	return result["data"][0]["embedding"]

def vector_similarity(x: List[float], y: List[float]) -> float:
	"""
	Returns the similarity between two vectors.
	
	Because OpenAI Embeddings are normalized to length 1, the cosine similarity is the same as the dot product.
	"""
	return np.dot(np.array(x), np.array(y))

def order_document_sections_by_query_similarity(query: str, contexts: Dict[int, np.array]) -> List[Tuple[float, Tuple[str, str]]]:
	"""
	Find the query embedding for the supplied query, and compare it against all of the pre-calculated document embeddings
	to find the most relevant sections. 
	
	Return the list of document sections, sorted by relevance in descending order.
	"""
	query_embedding = get_embedding(query)
	
	document_similarities = sorted([
		(vector_similarity(query_embedding, doc_embedding), doc_index) for doc_index, doc_embedding in contexts.items()
	], reverse=True)
	
	return document_similarities

MAX_SECTION_LEN = 500
SEPARATOR = "\n* "
ENCODING = "gpt2"  # encoding for text-davinci-003

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

EMBEDDINGS_HEADER = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained, then make your best inference. You should use emojis in your response at the end of a sentence. If a translation is asked for, provide it, but refer the user to the /translate command for text translations or /translate-chat command for chat translations. "\n\nContext:\n"""

def construct_prompt(question: str, context_embeddings: dict, messages: Dict[int, str]) -> str:
	"""
	Fetch relevant 
	"""
	most_relevant_document_sections = order_document_sections_by_query_similarity(question, context_embeddings)
	
	chosen_sections = []
	chosen_sections_len = 0
	chosen_sections_indexes = []
	 
	for _, section_index in most_relevant_document_sections:
		# Add contexts until we run out of space.		
		document_section = messages[section_index]
		
		chosen_sections_len += len(encoding.encode(document_section)) + separator_len
		if chosen_sections_len > MAX_SECTION_LEN:
			break

		chosen_sections.append(SEPARATOR + document_section.replace("\n", " "))
		chosen_sections_indexes.append(str(section_index))
			
	# Useful diagnostic information
	print(f"Selected {len(chosen_sections)} document sections:")
	print("\n".join(chosen_sections_indexes))
	
	return EMBEDDINGS_HEADER + "".join(chosen_sections) + "\n\n Q: " + question + "\n A:"

def query_summary(query: str, messages: Dict[int, str]) -> str:
	embeddings = {
		id: get_embedding(message) for id, message in messages.items()
	}

	prompt = construct_prompt(
		query,
		embeddings,
		messages,
	)

	completion = openai.Completion.create(
		model=COMPLETIONS_MODEL,
		prompt=prompt,
		temperature=0,
		max_tokens=320,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)

	return completion.choices[0].text.strip()

start_sequence = "Summarize text channel activity in one sentence, including who was speaking, what they were speaking about, and for how long they were speaking about it. Then provide chat highlights in the form of 5 bullet points, in your own words. "

restart_sequence = "Are there any more questions you have?"

def generate_summary(messages: List[str]) -> str:
	completion = openai.Completion.create(
	  model=COMPLETIONS_MODEL,
	  prompt=f"""{start_sequence}
```
{messages}
```
""",
	  temperature=0,
	  max_tokens=320,
	  top_p=1,
	  frequency_penalty=0,
	  presence_penalty=0
	)

	return completion.choices[0].text.strip()

	
