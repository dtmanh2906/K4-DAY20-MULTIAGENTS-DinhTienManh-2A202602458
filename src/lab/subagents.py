"""GUIDE Phần 1 - Định nghĩa subagent (tác tử con).   >>> SINH VIÊN CÀI ĐẶT <<<

Pseudo-code: guides/pseudocode/02_subagents.md
Kiểm tra:    pytest tests/test_02_agent.py
"""


def get_subagents() -> list[dict]:
    """Trả về danh sách subagent (ít nhất 2, tên khác nhau).

    Mỗi phần tử là một dict có các khóa bắt buộc:
      "name":          tên duy nhất (chữ thường, có thể có dấu gạch ngang)
      "description":   khi nào tác tử chính nên giao việc cho subagent này (viết như một hướng dẫn hành động)
      "system_prompt": chỉ dẫn cho subagent
    Gợi ý vai trò: explorer (đọc và báo cáo), implementer (thực hiện), reviewer (kiểm tra độc lập).
    """
    return [
        {
            "name": "explorer",
            "description": (
                "Use to explore the workspace, inspect data files, read documentation or docstrings, "
                "and report facts without modifying any files."
            ),
            "system_prompt": (
                "You are an exploration subagent. Inspect files, read code and data samples, "
                "and report exact facts and findings. Never modify or delete any files. "
                "Report your observations concisely."
            ),
        },
        {
            "name": "implementer",
            "description": (
                "Use to implement code changes, clean data, run tests or scripts, and report the execution outcomes."
            ),
            "system_prompt": (
                "You are an implementation subagent. Make precise code edits, write clean scripts, "
                "run tests and shell commands, and verify your changes. Report what actions were taken and the results."
            ),
        },
        {
            "name": "reviewer",
            "description": (
                "Use to independently review the implementation, check edge cases, "
                "verify deliverables against instructions, and run checks without modifying files."
            ),
            "system_prompt": (
                "You are a review and verification subagent. Check existing files and verification rules "
                "against the specification. Run test scripts to verify compliance. Do not edit source files."
            ),
        },
    ]
