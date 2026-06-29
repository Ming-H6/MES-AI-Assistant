import chromadb
from embedding import generate_embedding

embedding_cache = {}

def get_collection():
    
    client = chromadb.PersistentClient(path = './data/chromadb')

    collection = client.get_or_create_collection(name = 'mes_manual')

    return collection

def reset_collection():
    client = chromadb.PersistentClient(path = './data/chromadb')
    try :
        client.delete_collection('mes_manual')
    except:
        pass
    return client.get_or_create_collection(name= "mes_manual")

def add_document(
        collection,
        doc_id,
        text,
        vector,
        metadata,        
):
    collection.add(
        ids = [doc_id],
        documents =[text],
        embeddings = [vector],
        metadatas= [metadata]
    )

def extract_filter(question):
    question_lower = question.lower()

    if 'mazda' in question_lower:
        return {"Customer":"Mazda Customer"}
    if 'tesla' in question_lower:
        return {"Customer":"Tesla Customer"}
    if 'bmw' in question_lower:
        return {"Customer":"BMW Customer"}
    if 'gm' in question_lower:
        return {"Customer":"GM Customer"}
    return None

def retrieve(collection,question,n_results = 5):

    filter_condition = extract_filter(question)
    
    if question in embedding_cache:
        print("="*50)
        print("CACHE HIT")
        query_vector = embedding_cache[question]
    else:
        print("="*50)
        print("CACHE MISS")
        query_vector = generate_embedding(question)
        embedding_cache[question] = query_vector
    print(f"Cache size: {len(embedding_cache)}")
    
    if filter_condition:
        result = collection.query(
        query_embeddings = [query_vector],
        n_results = n_results,
        where = filter_condition
        )
    else:
        result = collection.query(
        query_embeddings= [query_vector],
        n_results = n_results
        )
    DEBUG = False
    if DEBUG:
        for i in range(len(result["metadatas"][0])):
            print(result["distances"][0][i])
            print(result["metadatas"][0][i])


    best_distance = result["distances"][0][0]

    threshold = min(best_distance + 0.1,0.8)

    candidate_docs = []
    candidate_meta = []
    candidate_distances = []

    for doc,meta,distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0]
    ):
        
        if distance <= threshold:
            candidate_docs.append(doc)
            candidate_meta.append(meta)
            candidate_distances.append(distance)


    scored_results = []

    for doc,meta,distance in zip(
        candidate_docs,
        candidate_meta,
        candidate_distances
    ):
            
        keywords = question.lower().split()

        keyword_score = 0

        for word in keywords:
            if word in doc.lower():
                keyword_score += 1

        final_score = keyword_score*2 - distance

        scored_results.append(
            (
                final_score,
                doc,
                meta,
                distance
            )
        )

    scored_results.sort(reverse= True, key = lambda x:x[0])
    scored_results = scored_results[:3]

    filtered_score =[]
    filtered_docs = []
    filtered_meta = []
    filtered_distances = []

    for final_score,doc,meta,distance in scored_results:
        filtered_score.append(final_score)
        filtered_docs.append(doc)
        filtered_meta.append(meta)
        filtered_distances.append(distance)
       
    return{
        "documents":[filtered_docs],
        "metadatas":[filtered_meta],
        "distances":[filtered_distances],
        "scores":[filtered_score]
    }
            




 



















    


