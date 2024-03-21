# sybil-embeddings

This is the repository for embedding models for various NLP based downstream tasks, such as:
- Semantic Similarity
- Asymmetric Semantic Search
- Classification
- Regression

At the current moment this repository is designed for semantic similarity on Write/Read alignment. Such that, if there is a vulnerability (like changing a user's address), we can find the associated read with that write. The vision is to be able to:
1. Assign a user address
2. Find the read associated with the address (with embedding model).
3. Exploit the potential vulnerability in whatever way.
4. Utilize the read (headers/content/authtokens/whatever) to verify that an exploitation has taken place.


The model utilized is the [INSTRUCTOR-base, a 325M parameter model](https://arxiv.org/pdf/2212.09741.pdf) designed for various tasks, where you can change the embeddings for downstream tasks by changing the prefix. For asymmetric search, you have different prefixes.

The general structure of a prefix must take the following form:

```Represent the {domain} {text type} {text objective}: ```

An example for http messages:

`Represent the HTTP write document for retrieving supporting HTTP read document: `
And for embedding the query for retrieval

`Represent the HTTP read document for retrieval: `

It should be noted that INSTRUCTOR has not been fine tuned for HTTP requests/response tasks generally. There were many simplifying assumptions made in chunking/processing text, such as grabbing all the innermost text on an HTML body. Chunking JSON responses on commas not inside quotes, etc, etc. Those simplifying assumptions can be found in src/sybil_embeddings/preprocessing/chunking.py.


Here are some example domain/text type/text objectives that you can include in a prefix.

|  | Examples |
| --------- | ----------- |
| Domain         | wikipedia, news, medicine, biology,<br>reddit, stackoverflow, science, quora, <br>coronavirus, math, physics |
| Text type      | question, query, answer, summary,<br> sentence, review, post, comment, <br>statement, paragraph, passage, document |
| Text objective | classify the sentence as positive or negative, <br>retrieve a duplicate sentence, <br>retrieve the supporting document |


Here were the query instructions and tasks presented in the paper that the model was trained on/with:

| Task Type | # of Datasets| Task | Instruction  |
| --------- | --- |---- | ------------|
| Retrieval |15| Natural Question (BEIR) | **Query instruction:** Represent the Wikipedia question for retrieving supporting documents: <br>**Doc instruction:** Represent the Wikipedia document for retrieval|
|Reranking| 14 | MindSmallReranking| **Query instruction:** Represent the News query for retrieving articles: <br>**Doc instruction:** Represent the News article for retrieval:|
|Clustering| 11|  MedrxivClusteringS2S| Represent the Medicine statement for retrieval:|
|Pair Classification | 3 |TwitterSemEval2015 |Represent the Tweet post for retrieving duplicate comments:|
|Classification| 12 | ImdbClassification |Represent the Review sentence for classifying emotion as positive or negative: |
| STS | 10 | STS12 |Represent the statement: |
| Summarization | 1 | SummEval | Represent the Biomedical summary for retrieving duplicate summaries: |
| Text Evaluation | 3 | Mscoco | Represent the caption for retrieving duplicate captions:
|Prompt Retrieval | 11 | GeoQuery | Represent the Geography example for retrieving duplicate examples: |



## Future Dataset Collection

This is the general structure of data that we want to collect from future datasets for further finetuning.

For classification tasks: Class labels of inputs -- either ones computed, or further verified.

For semantic similarity: Pairs of similar text, ideally all "positive" pairs -- this allows for hard negative mining which provides a great performance boost during training. 

Asymmetric Semantic similarity: Query question (such as, "does this http response contain sensitive user information?" should probably be transformed into a simple question like "What documents contain sensitive user information?"). Just whatever asymmetric queries that you are interested in.