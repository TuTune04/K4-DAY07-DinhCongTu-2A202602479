# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Đinh Công Tú  
**Nhóm:** L3A  
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**  
Độ tương tự cosine cao nghĩa là hai vector biểu diễn văn bản có hướng gần giống nhau trong không gian embedding. Trong thực tế, điều này thường cho thấy hai đoạn văn bản có nội dung hoặc ý nghĩa tương đối gần nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần đăng ký học phần trước thời hạn.
- Câu B: Người học phải hoàn tất đăng ký môn học đúng hạn.
- Tại sao tương đồng: Hai câu diễn đạt cùng một yêu cầu về việc đăng ký học phần đúng thời hạn, dù sử dụng từ ngữ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Quy định học bổng yêu cầu điểm trung bình tối thiểu.
- Câu B: Xe điện sử dụng pin lithium-ion.
- Tại sao khác: Hai câu thuộc hai chủ đề gần như không liên quan: quy định học bổng và công nghệ xe điện.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector thay vì độ lớn tuyệt đối, nên phù hợp khi cần so sánh mức độ giống nhau về ngữ nghĩa. Euclidean distance chịu ảnh hưởng trực tiếp bởi độ lớn vector, trong khi với embedding đã chuẩn hóa, hướng vector thường quan trọng hơn cho bài toán truy xuất văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Công thức:

`ceil((document_length - overlap) / (chunk_size - overlap))`

Thay số:

`ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.11...) = 23`

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi `overlap=100`, số chunk là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ lại ngữ cảnh ở biên giữa hai chunk, làm giảm nguy cơ một câu hoặc một ý quan trọng bị tách rời hoàn toàn; đổi lại sẽ tạo nhiều chunk hơn, tăng dung lượng lưu trữ và chi phí embedding/retrieval.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk` — hướng tiếp cận:**  
Tôi dùng regex `(?<=[.!?])(?:\s+|\n+)` để tách tại khoảng trắng hoặc xuống dòng nằm sau dấu kết thúc câu, nhờ đó vẫn giữ lại dấu câu trong kết quả. Các câu sau đó được gom tối đa theo `max_sentences_per_chunk`; văn bản rỗng hoặc chỉ chứa khoảng trắng trả về danh sách rỗng. Cách tách này vẫn có hạn chế với chữ viết tắt hoặc một số cấu trúc dấu chấm đặc biệt.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**  
Thuật toán thử separator theo thứ tự ưu tiên từ ranh giới lớn đến nhỏ: đoạn văn, dòng, câu, từ, rồi cuối cùng là cắt cứng theo ký tự. Nếu một phần vẫn vượt `chunk_size`, hàm `_split` gọi đệ quy với các separator còn lại; sau khi tách, các mảnh nhỏ liền kề được gom lại tới gần giới hạn `chunk_size` để tránh sinh quá nhiều chunk vụn. Base case là text rỗng, text đã đủ ngắn, hết separator, hoặc separator cuối là chuỗi rỗng.

### Lớp EmbeddingStore

**`add_documents` + `search` — hướng tiếp cận:**  
Mỗi `Document` được chuẩn hóa thành một record gồm `id`, `content`, bản sao `metadata`, `embedding` và chỉ số chèn. Khi thêm tài liệu, nội dung được embedding một lần và lưu trong bộ nhớ; khi search, query được embedding rồi tính dot product với từng vector tài liệu, sau đó sắp xếp giảm dần theo score và lấy `top_k`.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**  
`search_with_filter` lọc metadata trước khi tính similarity để các slot top-k chỉ được cạnh tranh bởi tài liệu phù hợp điều kiện lọc. `delete_document` loại bỏ toàn bộ record có `metadata['doc_id']` trùng với id tài liệu gốc; nếu metadata chưa có `doc_id`, `_make_record` tự bổ sung bằng `Document.id`.

### Tác tử KnowledgeBaseAgent

**`answer` — hướng tiếp cận:**  
Agent thực hiện ba bước: retrieve top-k chunk, ghép chúng thành context có đánh số nguồn `[1]`, `[2]`, ... rồi đưa context cùng câu hỏi vào prompt của LLM. Prompt yêu cầu chỉ trả lời dựa trên context và nói rõ khi không đủ thông tin, giúp giảm hallucination và tăng khả năng truy vết nguồn. Nếu store không trả về kết quả, agent trả thông báo trực tiếp thay vì gọi LLM không cần thiết.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```text
..........................................                               [100%]
42 passed in 0.09s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

Các phần đã hoàn thiện:
- `SentenceChunker`
- `RecursiveChunker`
- `compute_similarity`
- `ChunkingStrategyComparator`
- `EmbeddingStore` (`_make_record`, `_search_records`, `add_documents`, `search`, `get_collection_size`, `search_with_filter`, `delete_document`)
- `KnowledgeBaseAgent.answer`

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi dự đoán dựa trên ý nghĩa câu trước khi tính điểm. Điểm thực tế dưới đây dùng `MockEmbedder` mặc định của lab rồi gọi `compute_similarity()`; vì MockEmbedder sinh vector xác định từ hash chứ không mã hóa ngữ nghĩa, điểm chỉ dùng để kiểm tra pipeline chứ không phải thước đo semantic similarity thực tế.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Sinh viên cần đăng ký học phần trước thời hạn. | Người học phải hoàn tất đăng ký môn học đúng hạn. | cao | 0.243729 | Tương đối |
| 2 | Học phí phải được thanh toán trước ngày quy định. | Sinh viên cần nộp học phí đúng thời hạn. | cao | -0.186110 | Không |
| 3 | Thư viện mở cửa từ thứ Hai đến thứ Sáu. | Ký túc xá có quy định về giờ ra vào. | thấp | 0.132302 | Tương đối |
| 4 | Sinh viên có thể nộp đơn phúc khảo kết quả thi. | Giảng viên cập nhật điểm sau khi chấm bài. | thấp | -0.040816 | Có |
| 5 | Quy định học bổng yêu cầu điểm trung bình tối thiểu. | Xe điện sử dụng pin lithium-ion. | thấp | -0.160334 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**  
Cặp 2 bất ngờ nhất vì hai câu gần như cùng nghĩa nhưng score lại âm. Nguyên nhân là lab mặc định dùng `MockEmbedder`, vốn sinh vector từ MD5 và số giả ngẫu nhiên nên không biểu diễn ngữ nghĩa; điều này cho thấy muốn đánh giá semantic similarity hoặc retrieval quality thực tế thì cần dùng một embedding model thật như multilingual Sentence Transformers, OpenAI hoặc Gemini.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Phần này cần chạy **đúng 5 benchmark query chung của nhóm L3A**. Tại thời điểm hoàn thiện phần cá nhân, `REPORT_NHOM.md` chưa có 5 query và gold answer đã thống nhất, vì vậy tôi chưa tự tạo query riêng để tránh làm sai yêu cầu “cùng bộ câu hỏi với nhóm”.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---|---|---|
| 1 | Chờ benchmark chung của nhóm | | | | |
| 2 | Chờ benchmark chung của nhóm | | | | |
| 3 | Chờ benchmark chung của nhóm | | | | |
| 4 | Chờ benchmark chung của nhóm | | | | |
| 5 | Chờ benchmark chung của nhóm | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** Chưa đánh giá.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**  
Sẽ bổ sung sau phần demo/so sánh của nhóm để phản ánh đúng trải nghiệm thực tế thay vì suy đoán trước.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | Chưa chấm / 10 |
| **Tổng phần cá nhân hiện hoàn thành** | **50 / 60 trước benchmark nhóm** |
