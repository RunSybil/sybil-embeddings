from sentence_transformers import SentenceTransformer
from typing import Optional

class Instructor:
    def __init__(self, model_name: Optional[str] = None):
        if model_name is None:
            model_name = 'hkunlp/instructor-base'
            #alt_model = 'paraphrase-xlm-r-multilingual-v1'
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer

    def encode(self, text: str, **kwargs):
        return self.model.encode(text, **kwargs)
    
    def get_tokenizer(self):
        return self.model.tokenizer