# Ngày 7 — Bài tập

## Nền tảng Dữ liệu: Embedding & Vector Store | Bài tập thực hành

> **Sinh viên:** Đinh Công Tú  
> **Lớp/Nhóm:** L3A  
> **Phạm vi thực hiện:** Bài tập cá nhân. Các phần cần corpus, benchmark query hoặc kết quả chung của nhóm được giữ ở trạng thái chờ dữ liệu nhóm để tránh tự suy đoán.

---

## Phần 1 — Khởi động (Cá nhân)

### Bài tập 1.1 — Cosine Similarity bằng ngôn ngữ đời thường

**Độ tương tự cosine cao nghĩa là gì?**  
Khi hai vector embedding có cosine similarity cao, hướng của hai vector gần nhau. Điều này thường cho thấy hai đoạn văn bản có nội dung hoặc ý nghĩa ngữ nghĩa tương tự nhau, dù cách dùng từ có thể khác nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: `Sinh viên phải hoàn tất đăng ký học phần trước thời hạn.`
- Câu B: `Sinh viên cần đăng ký môn học đúng hạn.`
- Giải thích: Hai câu nói về cùng một hành động là đăng ký học phần và cùng nhấn mạnh yếu tố thời hạn.

**Ví dụ có độ tương tự THẤP:**

- Câu A: `Sinh viên cần nộp đơn phúc khảo điểm trong thời hạn quy định.`
- Câu B: `Hôm nay thời tiết có mưa lớn.`
- Giải thích: Hai câu thuộc hai chủ đề hoàn toàn khác nhau và hầu như không chia sẻ ý nghĩa ngữ nghĩa.

**Tại sao cosine similarity thường phù hợp hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào góc giữa hai vector thay vì độ lớn tuyệt đối. Với text embeddings, hướng vector thường phản ánh thông tin ngữ nghĩa quan trọng hơn độ dài vector; vì vậy cosine similarity ít bị ảnh hưởng bởi scale của vector hơn Euclidean distance.

---

### Bài tập 1.2 — Bài toán tính toán Chunking

**Tài liệu dài 10,000 ký tự, `chunk_size=500`, `overlap=50`.**

Công thức:

```text
số chunk = ceil((document_length - overlap) / (chunk_size - overlap))
```

Thay số:

```text
ceil((10000 - 50) / (500 - 50))
= ceil(9950 / 450)
= ceil(22.111...)
= 23
```

**Đáp án: 23 chunks.**

Nếu tăng `overlap` lên `100`:

```text
ceil((10000 - 100) / (500 - 100))
= ceil(9900 / 400)
= ceil(24.75)
= 25
```

**Đáp án mới: 25 chunks.**  
Overlap lớn hơn làm bước dịch giữa hai chunk nhỏ hơn nên số chunk tăng lên. Đổi lại, nội dung ở ranh giới được lặp lại nhiều hơn, giúp giảm khả năng mất ngữ cảnh khi một ý hoặc câu nằm giữa hai chunk. Nhược điểm là tăng số lượng embedding cần lưu và chi phí truy xuất.

---

## Phần 2 — Lập trình cốt lõi (Cá nhân)

Đã hoàn thiện các TODO trong `src/chunking.py`, `src/store.py` và `src/agent.py`.

### Danh sách cần làm

- [x] `Document` dataclass — đã được cung cấp sẵn
- [x] `FixedSizeChunker` — đã được cung cấp sẵn
- [x] `SentenceChunker`
- [x] `RecursiveChunker`
- [x] `compute_similarity`
- [x] `ChunkingStrategyComparator`
- [x] `EmbeddingStore.__init__`
- [x] `EmbeddingStore.add_documents`
- [x] `EmbeddingStore.search`
- [x] `EmbeddingStore.get_collection_size`
- [x] `EmbeddingStore.search_with_filter`
- [x] `EmbeddingStore.delete_document`
- [x] `KnowledgeBaseAgent.answer`

### Tóm tắt cách triển khai

#### `SentenceChunker`

Dùng regex với positive lookbehind để tách sau dấu kết thúc câu mà vẫn giữ lại dấu câu. Các câu sau khi tách được `strip()` và gom theo `max_sentences_per_chunk`. Text rỗng trả về danh sách rỗng.

Một hạn chế đã biết là cách tách câu đơn giản có thể xử lý chưa hoàn hảo các trường hợp viết tắt như `TS.`, `PGS.` hoặc số thập phân.

#### `RecursiveChunker`

Chiến lược ưu tiên separator theo thứ tự:

```python
["\n\n", "\n", ". ", " ", ""]
```

Nếu một đoạn vẫn dài hơn `chunk_size`, thuật toán tiếp tục đệ quy xuống separator nhỏ hơn. Khi không còn separator, thuật toán fallback sang cắt cứng theo số ký tự. Sau khi tách, các mảnh nhỏ liền kề được gom lại nếu tổng độ dài chưa vượt quá `chunk_size` để tránh sinh quá nhiều chunk vụn.

#### `compute_similarity`

Áp dụng công thức cosine similarity:

```text
cos(a, b) = dot(a, b) / (||a|| * ||b||)
```

Nếu một trong hai vector có độ lớn bằng 0, hàm trả về `0.0` để tránh `ZeroDivisionError`.

#### `ChunkingStrategyComparator`

Chạy cùng một văn bản qua ba chiến lược:

```text
fixed_size
by_sentences
recursive
```

Mỗi chiến lược trả về:

```text
count
avg_length
chunks
```

Text rỗng được xử lý để không chia cho 0 khi tính độ dài trung bình.

#### `EmbeddingStore`

Store được triển khai theo hướng in-memory để đảm bảo hành vi nhất quán với bộ test. Mỗi `Document` được chuyển thành record gồm `id`, `content`, `metadata`, `embedding`. Metadata được copy và đảm bảo có `doc_id`.

`search()` embedding truy vấn, tính dot product với từng record rồi sắp xếp score giảm dần. Vì mock embedder chuẩn hóa vector về norm 1 nên dot product tương đương cosine similarity.

`search_with_filter()` thực hiện metadata filtering **trước** khi similarity search. Cách này tránh trường hợp top-k bị chiếm bởi các tài liệu không đúng filter rồi mới bị loại bỏ.

`delete_document()` xóa tất cả record có `metadata['doc_id']` khớp với tài liệu cần xóa và trả `True` nếu thực sự xóa được ít nhất một record.

#### `KnowledgeBaseAgent`

Agent thực hiện pipeline RAG theo ba bước:

```text
Question
  ↓
Retrieve top-k chunks
  ↓
Build grounded context
  ↓
Call llm_fn
```

Các chunk được đánh số `[1]`, `[2]`, ... kèm nguồn để câu trả lời có khả năng truy vết. Prompt yêu cầu LLM chỉ trả lời dựa trên context và nói rõ khi không đủ thông tin.

### Kết quả kiểm thử

Bản implementation cá nhân đã được chạy bằng bộ test chính thức:

```text
pytest tests/ -v
```

Kết quả:

```text
42 passed
```

**Số test vượt qua: 42 / 42.**

---

## Phần 3 — So Sánh Chiến Lược Truy Xuất

### Bài tập 3.0 — Chuẩn Bị Tài Liệu (Nhóm)

L3A bắt buộc sử dụng domain **dịch vụ/quy định đại học**. Corpus cuối cùng phải gồm 5–10 tài liệu và mỗi tài liệu cần metadata tối thiểu:

```yaml
source_url:
retrieved_at:
document_version:
audience: student | faculty | staff | all
```

Ngoài ra nên có ít nhất một trường hữu ích như:

```yaml
department:
category:
language:
```

**Trạng thái:** Chờ nhóm thống nhất corpus chính thức. Không tự điền URL hoặc phiên bản tài liệu khi chưa có nguồn thật.

| #   | Tên tài liệu | Nguồn    | Ngày lấy / Phiên bản | Số ký tự | Metadata |
| --- | ------------ | -------- | -------------------- | -------- | -------- |
| 1   | Chờ nhóm     | Chờ nhóm | Chờ nhóm             | Chờ nhóm | Chờ nhóm |
| 2   | Chờ nhóm     | Chờ nhóm | Chờ nhóm             | Chờ nhóm | Chờ nhóm |
| 3   | Chờ nhóm     | Chờ nhóm | Chờ nhóm             | Chờ nhóm | Chờ nhóm |
| 4   | Chờ nhóm     | Chờ nhóm | Chờ nhóm             | Chờ nhóm | Chờ nhóm |
| 5   | Chờ nhóm     | Chờ nhóm | Chờ nhóm             | Chờ nhóm | Chờ nhóm |

---

### Bài tập 3.1 — Thiết Kế Chiến Lược Truy Xuất (Phần cá nhân)

**Chiến lược cá nhân lựa chọn:** `RecursiveChunker`.

**Lý do:**  
Các tài liệu quy định đại học thường có nhiều đoạn, mục và câu với độ dài không đồng đều. Recursive chunking ưu tiên các ranh giới ngữ nghĩa lớn như đoạn văn và dòng mới trước, sau đó mới giảm xuống câu, từ hoặc ký tự. Cách này có khả năng giữ cấu trúc tự nhiên của tài liệu tốt hơn fixed-size chunking trong nhiều trường hợp.

Cấu hình dự kiến:

```python
RecursiveChunker(
    separators=["\n\n", "\n", ". ", " ", ""],
    chunk_size=500,
)
```

**Baseline cần so sánh:**

```text
FixedSizeChunker
SentenceChunker
RecursiveChunker
```

**Trạng thái benchmark:** Chờ corpus chung của nhóm. Sau khi nhóm chốt 5–10 tài liệu, chạy `ChunkingStrategyComparator().compare()` trên cùng 2–3 tài liệu để có số liệu `count`, `avg_length` và đánh giá coherence.

---

### Bài tập 3.2 — Chuẩn Bị Câu Hỏi Đánh Giá (Nhóm)

Yêu cầu chính thức là **đúng 5 query** và gold answer phải kiểm chứng được từ corpus thật. L3A còn yêu cầu ít nhất một query cần:

```python
metadata_filter={"audience": "student"}
```

**Trạng thái:** Chờ nhóm thống nhất 5 query và gold answer; không tự tạo câu trả lời quy định đại học khi chưa có tài liệu nguồn.

| #   | Query    | Gold Answer | Chunk chứa thông tin |
| --- | -------- | ----------- | -------------------- |
| 1   | Chờ nhóm | Chờ nhóm    | Chờ nhóm             |
| 2   | Chờ nhóm | Chờ nhóm    | Chờ nhóm             |
| 3   | Chờ nhóm | Chờ nhóm    | Chờ nhóm             |
| 4   | Chờ nhóm | Chờ nhóm    | Chờ nhóm             |
| 5   | Chờ nhóm | Chờ nhóm    | Chờ nhóm             |

---

### Bài tập 3.3 — Dự Đoán Độ Tương Tự Cosine (Cá nhân)

Trước khi chạy, dự đoán dựa trên **ý nghĩa ngôn ngữ**. Kết quả bên dưới được tính với `MockEmbedder` đi kèm lab.

> Lưu ý: `MockEmbedder` sinh vector xác định từ MD5 và số giả ngẫu nhiên, không phải semantic embedding thật. Vì vậy điểm thực tế dưới đây không phản ánh tốt độ tương đồng ngữ nghĩa; đây chính là một quan sát quan trọng của bài lab.

| Cặp | Câu A                                             | Câu B                                             | Dự đoán | Điểm thực tế với MockEmbedder | Nhận xét                                          |
| --- | ------------------------------------------------- | ------------------------------------------------- | ------- | ----------------------------: | ------------------------------------------------- |
| 1   | Sinh viên cần đăng ký học phần trước thời hạn.    | Sinh viên phải hoàn tất đăng ký môn học đúng hạn. | Cao     |                       -0.0315 | Không khớp dự đoán vì mock không mã hóa ngữ nghĩa |
| 2   | Thư viện mở cửa từ 8 giờ sáng.                    | Thư viện bắt đầu phục vụ lúc 8 giờ.               | Cao     |                        0.0150 | Score gần 0 dù hai câu gần nghĩa                  |
| 3   | Học phí phải được thanh toán trước ngày quy định. | Sinh viên cần đóng học phí đúng hạn.              | Cao     |                        0.0327 | Score dương nhưng rất thấp                        |
| 4   | Quy trình phúc khảo điểm gồm nhiều bước.          | Hôm nay trời có mưa lớn.                          | Thấp    |                       -0.0314 | Phù hợp về hướng dự đoán thấp                     |
| 5   | Ký túc xá dành cho sinh viên nội trú.             | Mô hình học máy sử dụng dữ liệu để học.           | Thấp    |                       -0.0624 | Phù hợp về hướng dự đoán thấp                     |

**Kết quả bất ngờ nhất:**  
Các cặp 1 và 2 có ý nghĩa rất gần nhau nhưng score của mock embedding lại gần 0 hoặc âm. Điều này cho thấy một hệ thống retrieval chỉ tốt khi embedding backend thực sự mã hóa được ngữ nghĩa. MockEmbedder phù hợp cho unit test về cấu trúc và luồng xử lý, nhưng không phù hợp để kết luận chất lượng semantic retrieval.

Khi nhóm chạy benchmark chính thức nên dùng một embedding backend thật, ví dụ:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

vì corpus L3A chủ yếu là tiếng Việt.

---

### Bài tập 3.4 — Chạy Đánh Giá & So Sánh Trong Nhóm

Phần cá nhân sẽ chạy đúng 5 benchmark query do nhóm thống nhất trên strategy cá nhân.

Cần ghi lại với mỗi query:

```text
Top-1
Top-2
Top-3
similarity score
relevant / not relevant
agent answer
```

Đồng thời ít nhất một query cần chạy A/B:

```text
search(query)
vs
search_with_filter(query, metadata_filter={"audience": "student"})
```

**Trạng thái:** Chưa chạy vì `REPORT_NHOM.md` hiện chưa có 5 benchmark query và gold answer chính thức.

---

### Bài tập 3.5 — Phân Tích Lỗi

Failure case phải lấy từ benchmark thực tế, không tự dựng kết quả giả.

Khung phân tích sẽ dùng:

```text
Query gặp lỗi:
Top-3 trả về:
Expected chunk:
Nguyên nhân:
- chunk quá lớn / quá nhỏ?
- semantic embedding chưa tốt?
- metadata filter quá chặt?
- query mơ hồ?
- đúng document nhưng sai section?

Đề xuất cải thiện:
- đổi chunking strategy
- điều chỉnh chunk_size/overlap
- cải thiện metadata
- tăng top_k
- dùng reranker
- dùng embedding backend tốt hơn
```

**Trạng thái:** Chờ benchmark nhóm để chọn một failure case thật.

---

## Danh Sách Kiểm Tra Nộp Bài

### Phần cá nhân

- [x] Hoàn thành core implementation trong `src/`
- [x] `pytest tests/ -v` → **42 passed**
- [x] Hoàn thành Warm-up
- [x] Hoàn thành hướng tiếp cận implementation
- [x] Hoàn thành Similarity Predictions
- [ ] Chạy 5 benchmark query chung của nhóm
- [ ] Điền Competition Results vào `REPORT_CANHAN.md`

### Phần phụ thuộc nhóm

- [ ] Nhóm chốt corpus L3A 5–10 tài liệu
- [ ] Mỗi tài liệu đủ metadata bắt buộc
- [ ] Nhóm chốt đúng 5 benchmark query + gold answer
- [ ] Có ít nhất 1 query dùng `audience=student`
- [ ] Hoàn thiện `REPORT_NHOM.md`
- [ ] Chạy benchmark và failure analysis

---

## Kết luận cá nhân

Phần implementation cá nhân đã hoàn thành và vượt qua toàn bộ 42 test. Qua bài lab, điểm quan trọng nhất là chất lượng RAG không chỉ phụ thuộc vào LLM mà phụ thuộc mạnh vào pipeline phía trước: cách chunk dữ liệu, chất lượng embedding, metadata và chiến lược retrieval. Unit test xác nhận code hoạt động đúng contract, nhưng benchmark trên corpus thật mới là bước xác nhận retrieval có hữu ích về mặt ngữ nghĩa hay không.
