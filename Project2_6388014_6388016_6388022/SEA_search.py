from flask import Flask, request
from markupsafe import escape
from flask import render_template
from elasticsearch import Elasticsearch
import math

ELASTIC_PASSWORD = "Mm27102544"

es = Elasticsearch("https://localhost:9200", http_auth=("elastic", ELASTIC_PASSWORD), verify_certs=False)
app = Flask(__name__,template_folder='')

@app.route('/')
def homepage():
    return render_template('inde2.html')

@app.route('/search')
def search():
    page_size = 10
    keyword = request.args.get('keyword')
    if request.args.get('page'):
        page_no = int(request.args.get('page'))
    else:
        page_no = 1
    body = {
        'size': page_size,
        'from': page_size * (page_no-1),
        "query":{
            "multi_match": {
                "query": keyword,
                "type": "best_fields",
                "fields": ["Common name","Scientific name","Order and Family","Description"],
                "analyzer": "my_analyzer"
            }
        },
        "sort": [
            { "Common name": "asc" } 
        ]
    }
    res = es.search(index='sea', body=body)
    hits = [{'name': doc['_source']['Common name'], 'description': doc['_source']['Scientific name'], 'created': doc['_source']['Description'], 'image': doc['_source']['img-src'], 'order': doc['_source']['Order and Family']} for doc in res['hits']['hits']]
    page_total = math.ceil(res['hits']['total']['value']/page_size)
    return render_template('search.html',keyword=keyword, hits=hits, page_no=page_no, page_total=page_total)