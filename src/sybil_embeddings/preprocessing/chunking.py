# Description: This file contains functions that are used to chunk strings into smaller strings that are less than the max_length of the tokenizer.
import re
import json 
from functools import partial

from bs4 import BeautifulSoup

################################################################################
### These functions are used to check if a string is a valid json or html string
################################################################################
def is_json(myjson):
    """Checks if a string is a valid json string"""
    try:
        json.loads(myjson)
    except (ValueError, TypeError):
        return False
    return True

def is_html(s):
    """Checks if a string is a valid html string"""
    soup = BeautifulSoup(s, 'html.parser')
    return bool(soup.find())

###############################################
# Helpful utilities for chunking and processing
###############################################
def bytes_to_ascii(b_string):
    """Decodes bytestrings to ascii if possible"""
    try:
        return b_string.decode('ascii')
    except UnicodeDecodeError:
        try:
            return b_string.decode('utf-8')
        except UnicodeDecodeError:
            return False
    except AttributeError:
        return False

def get_last_sentence_and_length(text, tokenizer, prefix = None, method = None):
    """Gets the chunks, last chunk, and length of a too long string."""
    if method is None:
        method = chunk_raw_text
    chunks = method(text, tokenizer, prefix)
    last_chunk = chunks.pop()
    last_sentence = tokenizer.tokenize(last_chunk)
    return chunks, last_sentence, len(last_sentence)


def chunk_raw_text(text, tokenizer, prefix = None, include_middle = False): #This actually needs to work with slicing
    """Breaks a raw string into chunks that are less than the max_length of the tokenizer.
    Tokenizes the string, then slices into chunks of max_length, finally detokenizes to get the original string.
    """
    max_tokens = tokenizer.model_max_length
    prefix_tokenized = tokenizer(prefix )['input_ids'] if prefix is not None else []
    prefix_size = 0 if prefix is None else len(prefix_tokenized)
    chunk_size = max_tokens - prefix_size
    tokenized = tokenizer(text)['input_ids']
    text_length = len(tokenized)
    chunked = [tokenized[i:i + chunk_size] for i in range(0, text_length, chunk_size)]
    if include_middle:
        middle_chunks = [tokenized[i:i + chunk_size] for i in range(chunk_size // 2, text_length, chunk_size)]
        chunked = middle_chunks + chunked
    return [tokenizer.decode(chunk) for chunk in chunked] if prefix is None else [prefix + tokenizer.decode(chunk) for chunk in chunked]


def chunk_builder(splitter_function, long_block_method = None, join_with = None, use_regex = False):
    """Factory function that returns a chunking function that splits a string into chunks.
    For example, with regex: r',(?=(?:[^"]*"[^"]*")*[^"]*$)' as a splitter 
        we can break up json into key, value and objects to chunk together  
    With regex: r'(?<=[.!?])\s+' as a splitter, we can chunk up plaintext documents.
    
    Or you can use a custom function to split the string into constituent parts.
    

    Args:
        splitter_function: Function that splits the string into blocks, or a regex to split on
        long_token_method (optional): Method to deal with blocks that are too long. Defaults to "chunk_raw_text".
        join_with (str, optional): How to join blocks together. Defaults to "."
        use_regex (bool, optional): Set to true if you're using a regular expression to split text. Defaults to False.

    Returns:
        function: A function that takes a string, tokenizer, and prefix as arguments and returns chunks
    """
    if use_regex:
        splitter_function = partial(re.split, splitter_function)
    if long_block_method is None:
        long_block_method = chunk_raw_text
    if join_with is None:
        join_with = ""
    def chunk(string, tokenizer, prefix = None):
        max_tokens = tokenizer.model_max_length
        # This regex will split the string at commas that are not inside quotes
        # https://stackoverflow.com/questions/1757065/java-splitting-a-comma-separated-string-but-ignoring-commas-in-quotes
        # Don't do this at home kids
        sentences = splitter_function(string)
        chunks = []
        current_chunk = []
        prefix_token_count = 0 if prefix is None else len(tokenizer(prefix)["input_ids"])
        current_token_count = prefix_token_count
        # go through each sentence and add it to the current_chunk
        for sentence in sentences:
            token_count = len(tokenizer(sentence)["input_ids"])
            if current_token_count + token_count <= max_tokens:
                if current_token_count == prefix_token_count:
                    current_chunk.append(prefix + sentence)
                else:
                    current_chunk.append(sentence)
                current_token_count += token_count
            else:
                chunks.append(join_with.join(current_chunk))
                if token_count + prefix_token_count >= max_tokens:
                    outputs = get_last_sentence_and_length(sentence, tokenizer, prefix, long_block_method)
                    chunked, last_chunk, length = outputs
                    chunks.extend(chunked)
                    current_chunk = last_chunk
                    current_token_count = length
                else:
                    current_chunk = [sentence] if prefix is None else [prefix + sentence]
                    current_token_count = token_count + prefix_token_count
    
        if current_chunk:
            chunks.append(join_with.join(current_chunk))
        return chunks
    return chunk

###########################################################
### These functions perform actual chunking of the strings
###########################################################

# This regex will find commas, colons, and semicolons with trailing whitespace

def chunk_run_on_sentence(run_on_sentence, tokenizer, prefix = None):
    pass
chunk_run_on_sentence = chunk_builder(chunk_run_on_sentence, r'(?<=[,:;])\s+', use_regex=True)
# This regex will find periods, question marks, and exclamation points with trailing whitespace
#@chunk_builder(r'(?<=[.!?])\s+', long_block_method= chunk_run_on_sentence, use_regex=True)
def chunk_document(text, tokenizer, prefix = None):
    pass
chunk_document = chunk_builder( r'(?<=[.!?])\s+', use_regex=True, long_block_method=chunk_run_on_sentence)
# This regex will split the string at commas that are not inside quotes

def chunk_json(json_string, tokenizer, prefix = None): 
    pass
chunk_json = chunk_builder(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', use_regex=True, join_with=",")

def chunk_html(text, tokenizer, prefix = None):
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text()
    return chunk_raw_text(text, tokenizer, prefix)
