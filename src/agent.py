from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_blocks = []
        for index, result in enumerate(results, start=1):
            source = result.get("metadata", {}).get("source") or result.get("metadata", {}).get("doc_id") or result.get("id")
            context_blocks.append(f"[{index}] Nguồn: {source}\n{result['content']}")

        context = "\n\n".join(context_blocks)
        prompt = (
            "Bạn là trợ lý hỏi đáp dựa trên cơ sở tri thức. "
            "Chỉ sử dụng thông tin trong phần NGỮ CẢNH để trả lời. "
            "Nếu ngữ cảnh không đủ thông tin, hãy nói rõ rằng không tìm thấy câu trả lời. "
            "Khi phù hợp, hãy trích dẫn nguồn bằng ký hiệu [1], [2], ...\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI:\n{question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
