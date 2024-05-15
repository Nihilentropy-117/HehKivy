import runpod
from numpy import ndarray
import logging
import torch
import json
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from torch import Tensor
import torch.nn.functional as F
from typing import List
from tokenizers import Tokenizer

logging.getLogger().setLevel(logging.ERROR)


class Embedder:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError("This method should be overridden by subclasses.")

class LocalSFR(Embedder):
    name = 'Salesforce/SFR-Embedding-Mistral'
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(self.name)
        self.model = AutoModel.from_pretrained(self.name)
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)
        except torch.cuda.OutOfMemoryError as e:
            print(f"{e}\nUsing CPU instead")
            self.device = torch.device("cpu")
            self.model.to(self.device)

        self.max_length = 4096
        print(f"Loaded embedding model Salesforce/SFR-Embedding-Mistral")


    def embed(self, text: str, query=False, task="Given a web search query") -> List[float]:
        with torch.no_grad():
            to_embed = [f'Instruct: {task}\nQuery: {text}'] if query else [text]
            batch_dict = self.tokenizer(to_embed, max_length=self.max_length, padding=True, truncation=True,
                                        return_tensors="pt")
            outputs = self.model(**batch_dict)
            embeddings = self.last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])
            normalized_embeddings = F.normalize(embeddings, p=2, dim=1)
            return normalized_embeddings.squeeze().tolist()

    @staticmethod
    def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])
        if left_padding:
            return last_hidden_states[:, -1]
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]


class GTELargeEnV15(Embedder):
    name ='Alibaba-NLP/gte-large-en-v1.5'

    def __init__(self):
        self.model = SentenceTransformer(self.name, trust_remote_code=True)
        self.tokenizer = Tokenizer.from_pretrained(self.name)
        self.max_tokens = 8192
        self.min_tokens = 512
        self.vector_size = 1024

        print(f"Loaded embedding model Alibaba-NLP/gte-large-en-v1.5")

    def embed(self, text: str) -> list[Tensor] | ndarray | Tensor:
        embeddings = self.model.encode([text])
        return embeddings[0].tolist()


class EmberV1(Embedder):
    name = 'llmrails/ember-v1'
    def __init__(self):
        self.model = SentenceTransformer(self.name)
        self.tokenizer = Tokenizer.from_pretrained(self.name)

        print(f"Loaded embedding model llmrails/ember-v1")

    def embed(self, text: str) -> list[Tensor] | ndarray | Tensor:
        embeddings = self.model.encode([text])
        return embeddings[0]


def main():

    from itertools import combinations
    from sklearn.metrics.pairwise import cosine_similarity

    sentences = [
        "The majestic eagle soared through the clear blue sky, its wings outstretched as it rode the thermals.",
        "High above the ground, the regal raptor glided effortlessly, its keen eyes scanning the landscape below.",
        "The bustling city streets were filled with people hurrying to their destinations, their faces a blur in the crowd.",
        "Amidst the urban chaos, throngs of individuals rushed about their daily lives, anonymity reigning supreme.",
        "The serene lake reflected the vibrant hues of the setting sun, casting a mesmerizing spell over the tranquil scene.",
        "As daylight waned, the placid waters mirrored the brilliant colors of the heavens, creating an enchanting tableau of natural beauty."
    ]

    embedder = GTELargeEnV15()
    _embeddings = [embedder.embed(sentence) for sentence in sentences]

    for (i, sent1), (j, sent2) in combinations(enumerate(sentences), 2):
        sim = cosine_similarity([_embeddings[i]], [_embeddings[j]])[0][0]

        print(f'"{sent1}"\n"{sent2}"\nCosine similarity: {sim:.3f}\n')

        if (i + 1) % 2 == 0 and j == i + 1:
            print("Next set\n")

if __name__ == "__main__":
    main()
