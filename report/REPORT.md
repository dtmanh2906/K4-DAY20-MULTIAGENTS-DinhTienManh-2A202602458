# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| | | |

- Mô hình (tên deployment hoặc `LAB_MODEL`), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`:
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker:
- Số lần chạy tác vụ đã dùng / ngân sách:
- Commit của tag `freeze`:

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Trên các tác vụ đánh giá, điều kiện subagents sẽ đạt điểm tương đương hoặc chỉ nhỉnh hơn nhẹ so với baseline nhưng tiêu tốn lượng token gấp 2 đến 3 lần. Căn cứ từ kết quả tập học: việc chia nhỏ tác tử không giúp vượt qua các quy ước ngầm (house rules) nếu không có skill bổ sung, trong khi chi phí truyền tải ngữ cảnh tăng vọt.
- H2 (skills-auto so với baseline): Điều kiện skills-auto sẽ đạt điểm cao hơn baseline trên tác vụ đánh giá cùng họ (đặc biệt là họ code nhờ skill strict-codebase-conventions hướng dẫn type hints, test hồi quy và changelog), tuy nhiên mức độ cải thiện sẽ thấp hơn trên tác vụ học do tác vụ đánh giá bổ sung các quy ước mới chưa từng thấy (hiện tượng overfitting ngữ cảnh theo nghiên cứu SkillEvolBench).
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ đánh giá sẽ thấp hơn tác vụ học ở cả 3 điều kiện. Căn cứ: Tác vụ đánh giá có sự dịch chuyển phân phối dữ liệu (distribution shift) và chứa quy ước mới, làm giảm hiệu quả của các suy luận trực tiếp.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ:
   - Công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Công cụ chạy lệnh shell: `execute` (duy nhất công cụ này cho phép chạy lệnh shell).
   - Công cụ điều phối subagent: `task`.
2. Về subagent `general-purpose`:
   - Mô tả nêu đây là subagent đa dụng để nghiên cứu câu hỏi phức tạp, tìm kiếm file/nội dung, thực hiện các tác vụ nhiều bước và có toàn bộ quyền truy cập công cụ như tác tử chính.
   - Về ngữ cảnh: Subagent hoạt động phi trạng thái (stateless), chỉ nhìn thấy nội dung prompt được tác tử chính truyền vào khi giao việc, hoàn toàn không thấy ngữ cảnh hay lịch sử hội thoại trước đó của tác tử chính (trừ khi được chỉ định kế thừa).
3. Hướng dẫn hành vi trích từ mô tả:
   - Từ công cụ `task`: *"Put full detail in the prompt and state exactly what it should return unless an agent type below says it inherits your conversation instead."*
   - Từ công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `logs-learn` | `rule_service_names` | E | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| `logs-learn` | `rule_sorted_errors` | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| `logs-learn` | `rule_schema_header` | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |
| `data-learn` | `rule_clean_csv` | E | `RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents...` |
| `data-learn` | `rule_money_in_cents` | E | Check `rule_money_in_cents`: quy đổi số tiền USD sang đơn vị integer cents theo chuẩn Acme. |
| `data-learn` | `rule_meta_block` | E | Check `rule_meta_block`: yêu cầu thêm khối metadata bổ sung không có trong đề bài `instruction.md`. |
| `code-learn` | `rule_type_hints` | E | `RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value.` |
| `code-learn` | `rule_regression_tests` | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| `code-learn` | `rule_changelog` | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets).` |
| `data-learn` | `north_q1_revenue` | B | `FileNotFoundError: No such file or directory: 'workspace/answer.json'`: Agent dừng trước khi kịp ghi file đáp án. |

Nhận xét:
- **Nhóm lỗi chiếm đa số**: Nhóm **E (Vi phạm quy ước tổ chức / House rules)** chiếm 9/10 check thất bại. Thống kê từ `scripts/check_breakdown.py` cho thấy ở điều kiện `baseline`, số check quy ước đạt là **0/9 (0%)**.
- **Khả năng phòng ngừa của Skill**: Hoàn toàn có thể! Các quy ước này là kiến thức ngầm của tổ chức không nằm trong đề bài. Khi curator trích xuất các phản hồi chứa tiền tố `RULE:`, nó có thể tổng hợp thành các nguyên tắc rõ ràng trong `SKILL.md` để tác tử đọc và tuân thủ.
- **Bằng chứng phủ định**: Trên tác vụ `logs-learn`, toàn bộ **6/6 check kỹ thuật thuần túy** (`valid_structure`, `entry_count`, `timestamps_utc`, `exception_fields`, `repeat_counts`, `counts_by_service`) đều đạt điểm tối đa, chứng minh mô hình hoàn toàn có đủ năng lực lập trình và xử lý logic (không mắc lỗi kỹ thuật cơ bản ở nhóm A-D).

## 5. Điều kiện `subagents` (Phần 2.3)

- **Các subagent đã định nghĩa**:
  - `explorer`: Khảo sát cấu trúc tệp, đọc docstring/README và mẫu dữ liệu, báo cáo trung thực mà không chỉnh sửa file.
  - `implementer`: Trực tiếp viết code, chạy script xử lý và chạy test kiểm tra.
  - `reviewer`: Kiểm tra đối chiếu độc lập kết quả đầu ra với các yêu cầu đặc tả và trường hợp biên.
- **`subagent_calls` ở từng tác vụ và nhận xét**:
  - `code-learn`: 0 lần. Tác tử chính tự mình khảo sát các file test và đạt giới hạn đệ quy trước khi ủy quyền.
  - `data-learn`: 0 lần. Tác tử chính tự đọc `sales.csv` và phân tích trực tiếp.
  - `logs-learn`: **1 lần**. Tác tử chính sau khi đọc `README.md` đã quyết định giao việc cho subagent `implementer` để viết script `workspace/parse_app_log.py` và tạo file `workspace/errors.json`.
- **Thông tin khi giao việc**:
  - Lời giao việc trong `logs-learn` rất đầy đủ và chi tiết: *"Write a python script to parse workspace/app.log and generate workspace/errors.json according to the instructions and README.md. Test it thoroughly, check the output structure and values against requirements, and ensure correctness."*
- **Ảnh hưởng đến token và thời gian**:
  - Token trung bình của `subagents` (573,669 tokens) cao hơn gấp **2.7 lần** so với `baseline` (211,177 tokens) do việc khởi tạo subagent đòi hỏi nạp lại ngữ cảnh và thực hiện nhiều lượt gọi LLM bổ sung. Thời gian thực thi cũng tăng tương ứng.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- **Số lần chạy curator, số skill bị xóa và lý do**:
  - Đã chạy curator 1 lần.
  - Số skill bị tự động lọc bỏ: 1 skill (`rigorous-output-verification`) bị hàm kiểm định an toàn `validate_skill` từ chối tự động vì vi phạm quy tắc chống rò rỉ dữ liệu (chứa `eval_markers`: "orders"). Điều này khẳng định cơ chế bảo vệ chống rò rỉ (leakage protection) hoạt động chính xác.
  - Số skill hợp lệ được lưu vào `skills/auto/`: 1 skill (`strict-codebase-conventions`).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `strict-codebase-conventions` | **Tổng quát**. Không nhắc đến bất kỳ ID tác vụ cụ thể, tên file nội bộ, hay số liệu cụ thể nào. Khái quát hóa thành các quy chuẩn kỹ thuật phần mềm chuẩn: tạo file test hồi quy mới thay vì sửa test cũ, thêm type hints đầy đủ cho hàm public, ghi log thay đổi theo chuẩn bullet của changelog, xử lý số học và làm tròn half-up. | **Đúng**. Các nguyên tắc được khuyến nghị hoàn toàn chính xác theo chuẩn kỹ thuật phần mềm và phù hợp với các quy tắc tổ chức bị vi phạm ở tác vụ học. | • Độ dài: 10 dòng (rất cô đọng, < 40 dòng).<br>• `description`: *"WHEN TO USE THIS SKILL: When modifying or refactoring existing packages, writing tests, adding bug fixes, and updating documentation or changelogs."* (nêu rõ điều kiện kích hoạt).<br>• `skills_read`: Tác tử nạp qua progressive disclosure khi khởi tạo. |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
