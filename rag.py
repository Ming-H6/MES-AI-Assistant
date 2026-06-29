from vectorstore import retrieve
import ollama

def ask(collection, question, history = None):

    history_text =""

    if history:

        for msg in history[-6:]:

            history_text += (f"{msg['role']}: "
                             f"{msg['content']}\n")
            
    # version 1:
    # search_query = question

    # if history:

    #     recent_questions =[]

    #     for msg in reversed(history):
    #         if msg["role"] == "user":
    #             recent_questions.append(msg["content"])
    #         if len(recent_questions) >= 2:
    #             break

    #     recent_questions.reverse()
    #     search_query = (
    #         "\n".join(recent_questions)
    #         +"\n"
    #         +question
    #     )
    #  DEBUG_MEMORY = False
    #  if DEBUG_MEMORY:
    #      print("Search query")
    #      print(search_query)

    result =  retrieve(collection, question)
    
    docs = result["documents"][0]

    context = ""

    for i,doc in enumerate(docs):

        context += f"""

        Document{i+1}

        {doc}

        ----------------------------------
        """

    prompt = f"""
You are a MES documentation assistant.

Use ONLY the information provided in the context:

Rules:
1. Answer only using the provided context.
2. Do not use your own knowledge.
3. Do NOT say:
   - According to the documentation
   - Based on the provided context
   - The document states
   - The documentation mentions
4. If the answer is not contained in the context, say:
   "I cannot find relevant information in the MES documentation."
5. If the answer is a procedure, use numbered steps.
6. Be concise and professional.

Conversation history:
{history_text}

context:
{context}

question:
{question}
"""

    stream = ollama.chat(
        model = "llama3",
        messages = [
            {
                "role" : "user",
                "content" : prompt,
            }
    ],
        options = {
            "temperature": 0
        },
        stream = True
    )    

    unique_sources = []

    seen = set()

    for source in result["metadatas"][0]:
        key = (
            source["Customer"],
            source["Section"],
            source["Subject"]
        )

        if key not in seen:
            seen.add(key)
            unique_sources.append(source)
    
    print("="*50)
    print(history_text)
    print(question)

    return {
        "stream": stream,
        "sources":unique_sources,
        "debug":{
            "distances":result["distances"][0],
            "metadatas":result["metadatas"][0]
        },
        "scores":result["scores"][0]
    }

    