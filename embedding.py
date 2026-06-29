
import ollama

def build_embedding_text(chunk):
    content_text ="\n".join(chunk["Content"])
    
    embedding_text = f"""Customer: {chunk["Customer"]}

Subject : {chunk["Subject"]}

Content : 
{content_text}
"""
    return embedding_text

def build_metadata(chunk):
    metadata_dict = {
        "Customer":chunk["Customer"],
        "Section":chunk["Section"],
        "Subject":chunk["Subject"],
    }
    return metadata_dict

def generate_embedding(text):
        response = ollama.embed(
            model = "mxbai-embed-large",
            input = text
        )
        return response.embeddings[0]
