# https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb
import openai
from typing import Dict, List, Tuple
import numpy as np
import tiktoken

COMPLETIONS_MODEL = "text-davinci-003"
EMBEDDING_MODEL = "text-embedding-ada-002"

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

EMBEDDINGS_HEADER = """Answer the question as truthfully as possible using the provided context, and if the answer is not contained, then make your best inference. Respond in the style and mannerisms of James Charles. You should use emojis in your response at the end of a sentence. At the end of your response give a suggestion for a message to send in chat. "\n\nContext:\n"""

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

start_sequence = start_sequence = "Paraphrase, in detail, what was being discussed in this text channel. The summary should include the people who were speaking, what they were talking about, and how long they were talking about it. A lot of the language will be slang, please interpret it non literally, a lot of these terms are defined by Urban Dictionary. Use these terms to explain what's happening in chat without defining the terms in your answer. DO NOT DEFINE THE JARGON BEING USED. For example, if a person says ong fr, do not translate that statements or expand the meaning, just use it in context. If you approach language that isn't common, do not give it an explanation or a defintiion."

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

	