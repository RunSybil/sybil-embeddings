from .models import Instructor
from sybil_embeddings.preprocessing import default_sql_preprocess, default_reshape
from .preprocessing.preprocess_models import chunk_string
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingSearch:
    reshape = default_reshape

    def __init__(self, pre_processing = None, EmbeddingModel = None, **kwargs):
        if pre_processing is None:
            self.pre_processing = default_sql_preprocess
        if EmbeddingModel is None:
            self.model = Instructor()
        elif isinstance(EmbeddingModel, str):
            try:
                self.model = Instructor(EmbeddingModel)
            except:
                self.model = AutoModel.from_pretrained(EmbeddingModel)
                self.tokenizer = AutoTokenizer.from_pretrained(EmbeddingModel)

        self.tokenizer = self.model.tokenizer
        self.reshape = default_reshape
    
    def embed_query_results(self, sql_results, drop_ids: list[str], prefix = None, **kwargs):
        chunks = self.pre_processing(sql_results, **kwargs)
        chunks = [x for x in chunks if x[0] not in drop_ids]
        reshaped = self.reshape(chunks, self.tokenizer, prefix=prefix, **kwargs)
        self.ids, to_encode = list(zip(*reshaped))
        self.encode(to_encode, **kwargs)

    def encode(self, to_encode, normalize_embeddings = True, batch_size = 128, **kwargs):
        embeddings = self.model.encode(to_encode, 
                normalize_embeddings = normalize_embeddings, 
                batch_size = batch_size, 
                **kwargs)
        self.embeddings = embeddings
        return self.embeddings


    def search(self, query, prefix, top_k = 10, **kwargs):
        processed_query = chunk_string(query, self.tokenizer, prefix=prefix)
        to_find = self.model.encode(processed_query, normalize_embeddings=True)
        if len(to_find.shape) > 1:
            print("I DON'T KNOW WHAT TO DO, QUERY IS TOO LONG. I'M JUST GOING TO USE THE FIRST CHUNK.")
            to_find = to_find[0]
        if len(to_find.shape) == 1:
            to_find = to_find.reshape(1, -1)
        similarities = cosine_similarity(self.embeddings, to_find).flatten()
        top_k_indices = similarities.argsort()[-top_k:][::-1]
        output_ids = [self.ids[i] for i in top_k_indices]
        return output_ids


    def get_embeddings(self, **kwargs):
        return self.embeddings