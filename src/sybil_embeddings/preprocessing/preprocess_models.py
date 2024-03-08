from base64 import b64decode
from sybil_embeddings.preprocessing.chunking import is_json, is_html, chunk_json, chunk_html, chunk_raw_text, bytes_to_ascii

def chunk_string(text, tokenizer, prefix = None):  
    if is_json(text):
        return chunk_json(text, tokenizer, prefix)
    elif is_html(text):
        return chunk_html(text, tokenizer, prefix)
    else:
        return chunk_raw_text(text, tokenizer, prefix, include_middle = True)
    
def preprocess_sql_return(sql_results, request_index = 3, response_index = 4, url_index = 1, id_index = 0, **kwargs):
    decoded = [(*x[:request_index], b64decode(x[request_index]), *x[request_index +1:]) if x[request_index] is not None else (*x[:request_index], None, *x[request_index+1:]) for x in sql_results]
    decoded = [(*x[:response_index], b64decode(x[response_index]), *x[response_index+1:]) if x[response_index] is not None else (*x[:response_index], None, *x[response_index+1:]) for x in decoded]
    #If you replace the else None clause, you can end up getting some PDFs or other horrible formats. Please send help.
    decoded = [(*x[:request_index], output, *x[request_index +1:]) if x[request_index] is not None and (output := bytes_to_ascii(x[request_index])) else (*x[:request_index], None, *x[request_index+1:]) for x in decoded]
    decoded = [(*x[:response_index], output, *x[response_index+1:]) if x[response_index] is not None and (output := bytes_to_ascii(x[response_index])) else (*x[:response_index], None, *x[response_index+1:]) for x in decoded]
    #decoded = [(*x[:request_index], output, *x[4:]) if (output := bytes_to_ascii(x[request_index])) else (output := None) for x in decoded ]
    #decoded = [(*x[:4], output, *x[5:]) if (output := bytes_to_ascii(x[4])) else (output := None) for x in decoded ]
    request_bodies = [(x[id_index], x[request_index]) for x in decoded if x[request_index] is not None ]
    response_bodies = [(x[id_index], x[4]) for x in decoded if x[response_index] is not None]
    urls = [(x[id_index], x[url_index]) for x in decoded if x[url_index] is not None]
    rr_bodies = request_bodies + response_bodies + urls
    return rr_bodies

def chunk_and_reshape(rr_bodies, tokenizer, prefix = None, method = chunk_string, **kwargs):
    chunked = [(x, method(y, tokenizer, prefix)) for x, y in rr_bodies]
    reshaped = [[u,z] for u,v in chunked for z in v]
    return reshaped