# University corpus — L3A

Chủ đề: Quy định đào tạo và đăng ký học phần tại Đại học Quốc gia Hà Nội.

Bộ dữ liệu gồm 7 tài liệu Markdown đã được tóm tắt/paraphrase từ nguồn công khai chính thức.
Mỗi file có YAML frontmatter phục vụ metadata filtering.

## Quy tắc sử dụng
- Đây là corpus phục vụ bài lab retrieval/RAG, không thay thế văn bản pháp quy gốc.
- Khi cần câu trả lời chính thức, luôn đối chiếu `source_url`.
- Không chỉnh sửa `source_url`, `retrieved_at`, `document_version` nếu chưa kiểm tra lại nguồn.

## Benchmark gợi ý
1. Sinh viên phải hoàn thành đăng ký học phần chậm nhất khi nào?
2. Học phần bắt buộc bị điểm F thì sinh viên phải làm gì?
3. Sinh viên được rút học phần trong thời hạn nào?
4. Khối lượng tín chỉ được công nhận/chuyển đổi tối đa là bao nhiêu?
5. Người dùng cần làm gì khi tổ chức/đăng ký học phần? 
   - chạy không filter;
   - chạy với `metadata_filter={"audience": "student"}` để kiểm tra hiệu quả lọc.
