from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_session, Document, fuzzy_search_docs

app = Flask(__name__)
CORS(app)

@app.route('/api/index', methods=['POST'])
def index_document():
    data = request.json
    title = data.get('title')
    content = data.get('content')
    
    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400
        
    session = get_session()
    new_doc = Document(title=title, content=content)
    session.add(new_doc)
    session.commit()
    
    doc_id = new_doc.id
    session.close()
    
    return jsonify({'message': 'Document indexed successfully', 'id': doc_id})

@app.route('/api/search', methods=['GET'])
def search_documents():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
        
    session = get_session()
    results = fuzzy_search_docs(session, query)
    session.close()
    
    return jsonify(results)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    session = get_session()
    total_docs = session.query(Document).count()
    session.close()
    
    return jsonify({
        'total_documents': total_docs,
        'status': 'Healthy',
        'active_nodes': 1
    })

if __name__ == '__main__':
    # Initialize DB
    get_session().close()
    app.run(host='0.0.0.0', port=5001, debug=True)
