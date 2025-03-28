from sentence_transformers import SentenceTransformer


class Embeddings:
    def __init__(self) -> None:
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            prompts={
                "classification": "Classify the following text: ",
                "retrieval": "Retrieve semantically similar text: ",
                "clustering": "Identify the topic or theme based on the text: ",
            },
            default_prompt_name="retrieval",
        )

    def encode(self, sentences: str | list[str]):
        return self.model.encode(sentences, show_progress_bar=False)


embeddings = Embeddings()
