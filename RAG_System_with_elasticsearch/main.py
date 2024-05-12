import json
from elasticsearch import Elasticsearch

with open('RAG_System_with_elasticsearch/documents.json', 'rt') as f_in:
    documents_file = json.load(f_in)

documents = []

for course in documents_file:
    course_name = course['course']

    for doc in course['documents']:
        doc['course'] = course_name
        documents.append(doc)

es = Elasticsearch("http://localhost:9200")
#print(es.info())

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "section": {"type": "text"},
            "question": {"type": "text"},
            "course": {"type": "keyword"} 
        }
    }
}

index_name = "questions_1"
response = es.indices.create(index=index_name, body=index_settings)

#print(response)
from tqdm.auto import tqdm

for doc in tqdm(documents):
    es.index(index=index_name, document=doc)

user_question = "When will the course start?"

search_query = {
    "size": 5,
    "query": {
        "bool": {
            "must": {
                "multi_match": {
                    "query": user_question,
                    "fields": ["question^3", "text", "section"],
                    "type": "best_fields"
                }
            },
            "filter": {
                "term": {
                    "course": "'data-engineering-zoomcamp"
                }
            }
        }
    }
}

response = es.search(index=index_name, body=search_query)

for hit in response['hits']['hits']:
    doc = hit['_source']
    print(f"Section: {doc['section']}\nQuestion: {doc['question']}\nAnswer: {doc['text']}\n\n")
print(response)