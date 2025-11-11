from sentence_transformers import SentenceTransformer
import numpy as np
model = SentenceTransformer("all-MiniLM-L6-v2")


def encode_note(title, description, tags):
    tags = [t.strip().lower() for t in (tags or '').split(',') if t.strip()]
    text = f"{title or ''} {description or ''} {tags}"
    embedding = model.encode(text, convert_to_numpy=True)
    print('Encodin note to embedding')
    return embedding.tolist()

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))