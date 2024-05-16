from numpy import ndarray
import logging
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
from torch import Tensor
import torch.nn.functional as F
from typing import List
from tokenizers import Tokenizer

# Set logging level to ERROR to suppress excessive logging
logging.getLogger().setLevel(logging.ERROR)


# Base class for all Embedders
class Embedder:
    def __init__(self):
        self.model = None  # Placeholder for model

    def embed(self, text: str) -> List[float]:
        # To be implemented by subclasses
        raise NotImplementedError("This method should be overridden by subclasses.")

    def unload(self):
        if self.model is not None:
            del self.model  # Delete model to free memory
            torch.cuda.empty_cache()  # Clear CUDA cache
            print(f"Unloaded embedding model {self.name}")
        else:
            print("No model to unload.")


# Local Salesforce/SFR Embedding Model
class LocalSFR(Embedder):
    name = 'Salesforce/SFR-Embedding-Mistral'

    def __init__(self):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(self.name)  # Load tokenizer
        self.model = AutoModel.from_pretrained(self.name)  # Load model
        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)  # Move model to GPU if available
        except torch.cuda.OutOfMemoryError as e:
            print(f"{e}\nUsing CPU instead")
            self.device = torch.device("cpu")
            self.model.to(self.device)  # Move model to CPU if GPU memory is insufficient

        self.max_length = 4096  # Set max token length
        print(f"Loaded embedding model Salesforce/SFR-Embedding-Mistral")

    def embed(self, text: str, query=False, task="Given a web search query") -> List[float]:
        with torch.no_grad():  # Disable gradient computation
            to_embed = [f'Instruct: {task}\nQuery: {text}'] if query else [text]
            batch_dict = self.tokenizer(to_embed, max_length=self.max_length, padding=True, truncation=True,
                                        return_tensors="pt")  # Tokenize input
            outputs = self.model(**batch_dict)  # Get model outputs
            embeddings = self.last_token_pool(outputs.last_hidden_state, batch_dict['attention_mask'])  # Pool embeddings
            normalized_embeddings = F.normalize(embeddings, p=2, dim=1)  # Normalize embeddings
            return normalized_embeddings.squeeze().tolist()  # Convert to list

    @staticmethod
    def last_token_pool(last_hidden_states: Tensor, attention_mask: Tensor) -> Tensor:
        left_padding = (attention_mask[:, -1].sum() == attention_mask.shape[0])  # Check for left padding
        if left_padding:
            return last_hidden_states[:, -1]  # Return last token embedding
        else:
            sequence_lengths = attention_mask.sum(dim=1) - 1  # Calculate sequence lengths
            batch_size = last_hidden_states.shape[0]
            return last_hidden_states[torch.arange(batch_size, device=last_hidden_states.device), sequence_lengths]  # Return embeddings


# Alibaba GTE Large Embedding Model
class GTELargeEnV15(Embedder):
    name ='Alibaba-NLP/gte-large-en-v1.5'

    def __init__(self):
        super().__init__()
        self.model = SentenceTransformer(self.name, trust_remote_code=True)  # Load SentenceTransformer model
        self.tokenizer = Tokenizer.from_pretrained(self.name)  # Load tokenizer
        self.max_tokens = 8192  # Set max tokens
        self.min_tokens = 512  # Set min tokens
        self.vector_size = 1024  # Set vector size

        print(f"Loaded embedding model Alibaba-NLP/gte-large-en-v1.5")

    def embed(self, text: str) -> list[Tensor] | ndarray | Tensor:
        embeddings = self.model.encode([text])  # Encode text
        return embeddings[0].tolist()  # Convert to list


# LLMRails EmberV1 Embedding Model
class EmberV1(Embedder):
    name = 'llmrails/ember-v1'

    def __init__(self):
        super().__init__()
        self.model = SentenceTransformer(self.name)  # Load SentenceTransformer model
        self.tokenizer = Tokenizer.from_pretrained(self.name)  # Load tokenizer

        print(f"Loaded embedding model llmrails/ember-v1")

    def embed(self, text: str) -> list[Tensor] | ndarray | Tensor:
        embeddings = self.model.encode([text])  # Encode text
        return embeddings[0]  # Return embeddings



if __name__ == "__main__":
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

    embedder = GTELargeEnV15()  # Initialize embedder
    _embeddings = [embedder.embed(sentence) for sentence in sentences]  # Get embeddings for sentences

    # Compare pairs of sentences and compute cosine similarity
    for (i, sent1), (j, sent2) in combinations(enumerate(sentences), 2):
        sim = cosine_similarity([_embeddings[i]], [_embeddings[j]])[0][0]  # Compute cosine similarity

        print(f'"{sent1}"\n"{sent2}"\nCosine similarity: {sim:.3f}\n')  # Print similarity

        if (i + 1) % 2 == 0 and j == i + 1:  # Print "Next set" after every pair
            print("Next set\n")

