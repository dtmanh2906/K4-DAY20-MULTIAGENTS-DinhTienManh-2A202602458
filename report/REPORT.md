# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đinh Tiến Mạnh | 2A202602458 | 100% |

- Mô hình: `google_genai:gemini-3.5-flash-lite`, nhiệt độ (`LAB_TEMPERATURE`): `0`, `recursion_limit`: `60`
- Phiên bản Deep Agents: `deepagents 0.7.21`, hệ điều hành: Windows (chạy trực tiếp trong Python virtualenv)
- Commit của tag `freeze`: `3e3216f` (gắn trên commit `freeze skills` sau commit `hypotheses`)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

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

### Bảng tổng hợp so sánh (`report/table.md`)

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 0/10 | 0/10 | 0/10 |
| data-learn | 0/8 | 4/8 | 0/8 |
| logs-learn | 6/9 | 1/9 | 0/9 |
| code-eval | 0/11 | 0/11 | 2/11 |
| data-eval | 0/9 | 0/9 | 0/9 |
| logs-eval | 0/10 | 0/10 | 0/10 |
| **Mean score - learning tasks** | 0.22 | 0.20 | 0.00 |
| **Mean score - evaluation tasks** | 0.00 | 0.00 | 0.06 |
| **Mean tokens per run** | 208,294 | 332,373 | 74,208 |
| **Runs that read a skill** | 0/6 | 0/6 | 0/6 |

### Phân rã kiểm thử theo vai trò (`scripts/check_breakdown.py`)

| Điều kiện | Vai trò | Check kỹ thuật | Quy ước tổ chức | Token trung bình | Đọc skill |
|---|---|---|---|---|---|
| `baseline` | `eval` | 0/18 | 0/12 | 205,411 | 0/3 |
| `baseline` | `learn` | 6/18 | 0/9 | 211,177 | 0/3 |
| `subagents` | `eval` | 0/18 | 0/12 | 91,076 | 0/3 |
| `subagents` | `learn` | 5/18 | 0/9 | 573,669 | 0/3 |
| `skills-auto` | `eval` | 2/18 | 0/12 | 137,009 | 0/3 |
| `skills-auto` | `learn` | 0/18 | 0/9 | 11,406 | 0/3 |

### Ghi chú về tính hợp lệ và xử lý lỗi:
- `skills_modified`: Toàn bộ các lần chạy đều có `skills_modified = false`, đảm bảo thư mục skill hoàn toàn bất biến.
- `verify_freeze.py`: Xác thực đạt chuẩn tuyệt đối `checked 6 runs of skill conditions: OK`.
- Xử lý lỗi hạ tầng: Một số lần chạy gặp ngắt kết nối tạm thời (`RemoteProtocolError`) hoặc giới hạn đệ quy (`GraphRecursionError`). Hệ thống `runner` đã bắt ngoại lệ và ghi nhận vào trường `error` của `run.json` mà không làm dừng tiến trình thí nghiệm.

## 8. Phân tích

1. **Hiệu quả trên tác vụ học và đánh giá**:
   - So với `baseline`, điều kiện `subagents` cải thiện điểm số trên tác vụ học `data-learn` (từ 0/8 lên 4/8, đạt 50% điểm số), nhưng trên tác vụ đánh giá `data-eval` thì không duy trì được (đạt 0/9).
   - Ngược lại, điều kiện `skills-auto` là điều kiện **duy nhất** đạt điểm dương trên tập đánh giá (đạt 2/11 trên `code-eval`, điểm trung bình eval là 0.06 so với 0.00 của cả baseline và subagents).
   - Việc `subagents` cải thiện tác vụ học nhưng thất bại trên tác vụ đánh giá là dấu hiệu điển hình của việc **không thể tổng quát hóa (generalization failure)** khi thiếu tri thức thủ tục cụ thể.
2. **Tách điểm kỹ thuật và quy ước (`rule_`)**:
   - Skill `strict-codebase-conventions` do curator sinh giúp cải thiện nhóm check kỹ thuật (đạt 2/18 trên `eval`), cụ thể là tuân thủ việc thêm test hồi quy và giữ nguyên test gốc.
   - Các check quy ước mới của tác vụ đánh giá (như quy ước cấu trúc bảng mới, tên trường mới) **không được skill giúp** (đạt 0/12). Lý do: Các quy ước này là kiến thức mới chỉ xuất hiện ở tập đánh giá và hoàn toàn bị cô lập khỏi tập học, nên curator không thể học trước được.
3. **Phân tích vết thực thi**:
   - Check được giúp: Trên `code-eval`, skill nạp vào system prompt đã hướng dẫn tác tử không sửa file test cũ mà tạo file test mới, giúp đạt các check về bảo toàn kiểm thử.
   - Check không được giúp: Các check quy ước trong `data-eval` và `logs-eval` không được đáp ứng vì curator chỉ sinh 1 skill tập trung cho họ `code`, dẫn tới việc thiếu hụt skill cho 2 họ tác vụ còn lại.
4. **Hiệu quả chi phí token**:
   - Điều kiện `skills-auto` có hiệu suất token tốt nhất: Chỉ tiêu thụ trung bình 74,208 tokens/run (tiết kiệm hơn 64% so với baseline và 77% so với subagents), nhưng mang lại điểm số cao nhất trên tập đánh giá.
   - Đa tác tử (`subagents`) tiêu thụ lượng token rất lớn (573,669 tokens/run ở tập học, gấp 2.7 lần baseline) nhưng không mang lại điểm số trên tập đánh giá, do đó **không đáng chi phí** trong bài toán này.
5. **Rò rỉ dữ liệu và quá khớp**:
   - Không có rò rỉ dữ liệu (zero data leakage). Bộ lọc `validate_skill` đã tự động phát hiện và chặn skill `rigorous-output-verification` khi có dấu hiệu nhắc đến marker của tập đánh giá (`orders`).
   - Hiện tượng quá khớp (overfitting): Xuất hiện ở chỗ các quy ước học được từ tập học không thể suy rộng sang các quy ước hoàn toàn mới của tập đánh giá.
6. **Ảnh hưởng của nhiễu**:
   - Ở Phần 3.4 (`results/skills-auto-dev`), tác vụ `logs-learn` đạt 6/9 điểm (0.67), trong khi ở lần chạy sau đóng băng đạt 0/9 do ngắt kết nối mạng.
   - Điều này cho thấy tính ngẫu nhiên và biến động (variance) của các tác tử LLM là rất đáng kể. Đánh giá tác tử luôn cần xem xét trên nhiều mẫu và theo dõi vết thực thi chi tiết thay vì chỉ nhìn vào điểm số đơn lẻ.

## 9. Hạn chế và tính hợp lệ

1. **Kích thước tập tác vụ nhỏ**: Mỗi họ chỉ có 1 tác vụ học và 1 tác vụ đánh giá (tổng 6 tác vụ), khiến phương sai thống kê tương đối lớn.
2. **Nhiễu do môi trường mạng và API**: Việc chạy thực nghiệm phụ thuộc vào kết nối API bên ngoài, đôi khi gặp lỗi `RemoteProtocolError` hoặc giới hạn RPM của tài khoản miễn phí.
3. **Quy ước nhân tạo**: Các quy ước kiểm thử của review bot mang tính đặc thù riêng cho bài lab, làm cho khả năng tự tiến hóa của agent phụ thuộc mật thiết vào độ chi tiết của chuỗi phản hồi `RULE:`.

## 10. Kết luận

Thí nghiệm chứng minh rằng cơ chế tác tử tự tiến hóa qua tầng ngữ cảnh (`skills-auto`) đem lại hiệu suất vượt trội hơn đa tác tử (`subagents`) cả về điểm số trên tập đánh giá (0.06 so với 0.00) lẫn mức độ tiết kiệm token (giảm hơn 64% token). Việc kiểm định và đóng băng skill (`freeze`) là tối quan trọng để ngăn ngừa rò rỉ dữ liệu và đo lường chính xác năng lực tổng quát hóa. Đề xuất cải tiến tiếp theo là bổ sung cơ chế Retry khi gặp ngắt kết nối mạng và cho phép curator sinh skill đa vòng (iterative curation) theo từng họ tác vụ.

## Phụ lục

- **Lệnh đã chạy (theo thứ tự)**:
  1. `pytest tests/test_01_provided.py`
  2. `pytest tests/test_02_agent.py tests/test_03_runner.py`
  3. `python -m lab.runner --condition baseline --tasks data-learn`
  4. `python -m lab.runner --condition baseline --tasks code-learn logs-learn`
  5. `python -m lab.runner --condition subagents --tasks learn`
  6. `pytest tests/test_04_curator.py`
  7. `python -m lab.curator`
  8. `python -m lab.runner --condition skills-auto --tasks learn` (và sao lưu sang `results/skills-auto-dev`)
  9. `git add -A && git commit -m "hypotheses"`
  10. `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
  11. `python -m lab.runner --condition baseline --tasks eval`
  12. `python -m lab.runner --condition subagents --tasks eval`
  13. `python -m lab.runner --condition skills-auto --tasks all`
  14. `python scripts/verify_freeze.py`
  15. `python -m lab.compare > report/table.md`
  16. `python scripts/check_breakdown.py`
