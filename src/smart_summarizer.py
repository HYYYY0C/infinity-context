#!/usr/bin/env python3
"""
Smart Summarizer - 智能生成 Session 摘要

从对话历史中提取关键信息，生成结构化的精简摘要（300-500 字）

⚠️ 当前版本说明：
由于 Hermes 没有提供读取当前对话历史的 API，
本模块提供框架和模板系统，真正的对话提取需要：
1. 用户手动提供对话内容
2. 或等待 Hermes 官方开放相关 API
3. 或通过 session_search 间接获取（需要额外配置）
"""

from datetime import datetime
from typing import Dict, List, Optional
import json


class SmartSummarizer:
    """智能摘要生成器"""
    
    def __init__(self, template: str = "default"):
        """
        初始化摘要生成器
        
        Args:
            template: 模板名称（default/minimal/detailed）
        """
        self.template = self._load_template(template)
        self.max_length = 500
        self.min_length = 300
    
    def _load_template(self, template_name: str) -> str:
        """加载模板"""
        templates = {
            "default": self._default_template(),
            "minimal": self._minimal_template(),
            "detailed": self._detailed_template(),
        }
        return templates.get(template_name, templates["default"])
    
    def _default_template(self) -> str:
        """默认模板"""
        return """## 📝 Session 摘要 ({timestamp})

### 🎯 核心任务
{core_tasks}

### 🔧 关键操作
{key_operations}

### ⏳ 待办事项
{pending_tasks}

### 📎 重要上下文
{important_context}

### 💡 下一步建议
{next_steps}
"""
    
    def _minimal_template(self) -> str:
        """精简模板"""
        return """## 📝 Session 摘要 ({timestamp})

**核心任务**: {core_tasks}
**待办**: {pending_tasks}
**关键上下文**: {important_context}
"""
    
    def _detailed_template(self) -> str:
        """详细模板"""
        return """## 📝 Session 摘要 ({timestamp})

### 🎯 核心任务完成情况
{core_tasks}

### 🔧 技术操作详情
- **修改文件**: {modified_files}
- **配置变更**: {config_changes}
- **解决问题**: {solved_issues}

### ⏳ 待办事项清单
{pending_tasks}

### 📎 重要上下文与参数
{important_context}

### 🔗 相关资源
{references}

### 💡 下一步建议
{next_steps}
"""
    
    def extract_from_conversation(self, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """
        从对话历史中提取关键信息
        
        ⚠️ 重要说明：
        当前 Hermes 版本没有提供读取当前对话历史的 API。
        
        使用方法：
        1. 手动提供对话历史（通过参数）
        2. 或提供已提取的关键信息（通过 key_info 参数）
        3. 或等待未来版本集成 session_search
        
        Args:
            conversation_history: 对话历史列表（可选，当前版本不支持自动获取）
            
        Returns:
            提取的关键信息字典
            
        Raises:
            NotImplementedError: 当尝试使用未实现的功能时
        """
        # 如果没有提供对话历史，返回空结构（而不是硬编码假数据）
        if not conversation_history:
            # 返回空结构，让用户知道需要提供数据
            return {
                "core_tasks": [],
                "modified_files": [],
                "config_changes": [],
                "pending_tasks": [],
                "important_context": {},
                "next_steps": [],
                "_note": "⚠️ 当前 Hermes 版本无法自动读取对话历史。请手动提供关键信息，或使用 CLI 的 --input 参数。详见 README.md。"
            }
        
        # TODO: 实现真正的智能提取逻辑
        # 需要：
        # 1. NLP 分析对话内容
        # 2. 识别任务、操作、待办事项
        # 3. 提取关键参数和配置
        # 4. 结构化输出
        
        # 当前版本：简单的启发式提取（未来会改进）
        return self._simple_extract(conversation_history)
    
    def _simple_extract(self, conversation_history: List[Dict]) -> Dict:
        """
        简单的启发式提取（临时方案）
        
        未来会被基于 LLM 的智能提取替代
        """
        core_tasks = []
        pending_tasks = []
        modified_files = set()
        config_changes = []
        important_context = {}
        
        # 简单的关键词匹配（非常基础，未来会改进）
        task_keywords = ["任务", "目标", "要做的", "需要", "计划"]
        file_patterns = ["/opt/data/", "~/", ".py", ".yaml", ".json", ".md"]
        
        for msg in conversation_history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            # 提取可能的任务
            if role == "user":
                for keyword in task_keywords:
                    if keyword in content:
                        core_tasks.append({
                            "task": content[:50] + "..." if len(content) > 50 else content,
                            "status": "⏳",
                            "result": "进行中"
                        })
                        break
            
            # 提取可能的文件修改
            if "修改文件" in content or "写入文件" in content:
                for pattern in file_patterns:
                    if pattern in content:
                        # 简单提取文件路径
                        import re
                        paths = re.findall(r'[/~][\w/.-]+\.(py|yaml|json|md|txt)', content)
                        modified_files.update(paths)
        
        return {
            "core_tasks": core_tasks if core_tasks else [{"task": "未检测到明确任务", "status": "⚠️", "result": "请手动提供"}],
            "modified_files": list(modified_files),
            "config_changes": config_changes,
            "pending_tasks": pending_tasks,
            "important_context": important_context,
            "next_steps": ["请手动补充下一步计划"] if not pending_tasks else pending_tasks,
        }
    
    def generate(self, key_info: Optional[Dict] = None) -> str:
        """
        生成摘要
        
        Args:
            key_info: 关键信息字典（可选，不提供则返回说明信息）
            
        Returns:
            生成的摘要文本
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 如果没有提供关键信息，返回说明而不是假数据
        if key_info is None:
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            return """## 📝 Session 摘要 (""" + timestamp_str + """)

⚠️ **需要用户提供信息**

当前 Hermes 版本无法自动读取对话历史。请通过以下方式之一提供信息：

1. **手动输入**: 使用 `--input` 参数提供关键信息
2. **文件导入**: 从文件读取对话历史
3. **等待 API**: 未来版本将支持自动获取

**示例用法**:
```bash
# 手动提供关键信息
python -m src.cli compress --input '{"core_tasks": ["开发功能 A"], "pending_tasks": ["测试"]}'

# 从文件读取
python -m src.cli compress --file conversation.json
```

详见：README.md - "当前版本限制" 章节
"""
        
        # 检查是否有说明标记
        if "_note" in key_info:
            # 这是一个空结构，返回友好提示
            return f"""## 📝 Session 摘要 ({timestamp})

⚠️ **当前版本限制**

{key_info['_note']}

**解决方案**:
1. 手动提供关键信息
2. 使用 `--input` 参数
3. 从文件导入对话历史

详见 README.md 获取详细指导。
"""
        
        # 正常生成摘要
        return self._format_summary(key_info, timestamp)
    
    def _format_summary(self, key_info: Dict, timestamp: str) -> str:
        """格式化摘要内容"""
        # 格式化核心任务
        core_tasks_list = key_info.get("core_tasks", [])
        if core_tasks_list:
            core_tasks = "\n".join([
                f"- {t.get('task', '未知任务')}: {t.get('status', '⏳')} {t.get('result', '')}"
                for t in core_tasks_list
            ])
        else:
            core_tasks = "未提供核心任务"
        
        # 格式化关键操作
        modified_files = key_info.get("modified_files", [])
        config_changes = key_info.get("config_changes", [])
        
        if modified_files or config_changes:
            key_operations = []
            if modified_files:
                key_operations.append(f"- 修改文件:\n  - " + "\n  - ".join(modified_files))
            if config_changes:
                key_operations.append(f"- 配置变更:\n  - " + "\n  - ".join(config_changes))
            key_operations_str = "\n".join(key_operations)
        else:
            key_operations_str = "未记录关键操作"
        
        # 格式化待办事项
        pending_tasks_list = key_info.get("pending_tasks", [])
        if pending_tasks_list:
            pending_tasks = "\n".join([
                f"- [ ] {task}" for task in pending_tasks_list
            ])
        else:
            pending_tasks = "未记录待办事项"
        
        # 格式化重要上下文
        context_items = key_info.get("important_context", {})
        if context_items:
            important_context = "\n".join([
                f"- {k}: {v}" for k, v in context_items.items()
            ])
        else:
            important_context = "未记录重要上下文"
        
        # 格式化下一步建议
        next_steps_list = key_info.get("next_steps", [])
        if next_steps_list:
            next_steps = "\n".join([
                f"{i+1}. {step}" for i, step in enumerate(next_steps_list)
            ])
        else:
            next_steps = "未提供下一步建议"
        
        # 填充模板
        summary = self.template.format(
            timestamp=timestamp,
            core_tasks=core_tasks,
            key_operations=key_operations_str,
            pending_tasks=pending_tasks,
            important_context=important_context,
            next_steps=next_steps,
            modified_files=", ".join(modified_files) if modified_files else "无",
            config_changes=", ".join(config_changes) if config_changes else "无",
            solved_issues=key_info.get("solved_issues", "无"),
            references=key_info.get("references", "无"),
        )
        
        return summary
    
    def validate_length(self, summary: str) -> bool:
        """验证摘要长度是否在合理范围内"""
        length = len(summary)
        # 允许 50% 浮动：min_length*0.5 到 max_length*1.5
        min_allowed = self.min_length * 0.5
        max_allowed = self.max_length * 1.5
        return min_allowed <= length <= max_allowed


def main():
    """测试摘要生成"""
    print("=" * 80)
    print("📝 Smart Summarizer - 测试模式")
    print("=" * 80)
    print()
    print("⚠️  当前版本说明:")
    print("   由于 Hermes 没有提供读取对话历史的 API，")
    print("   本测试将展示空输入时的行为。")
    print()
    
    summarizer = SmartSummarizer()
    
    # 测试 1: 空输入
    print("-" * 80)
    print("测试 1: 不提供任何输入")
    print("-" * 80)
    summary = summarizer.generate()
    print(summary)
    print()
    
    # 测试 2: 提供真实数据
    print("-" * 80)
    print("测试 2: 提供真实关键信息")
    print("-" * 80)
    test_data = {
        "core_tasks": [
            {"task": "开发用户认证模块", "status": "✅", "result": "完成"},
            {"task": "编写单元测试", "status": "⏳", "result": "进行中"},
        ],
        "modified_files": ["src/auth.py", "tests/test_auth.py"],
        "config_changes": ["max_iterations: 50→30"],
        "pending_tasks": ["完成测试覆盖", "更新文档"],
        "important_context": {
            "Python 版本": "3.11",
            "框架": "FastAPI",
        },
        "next_steps": ["运行测试套件", "提交 PR"],
    }
    summary = summarizer.generate(test_data)
    print(summary)
    print()
    print("=" * 80)
    print(f"字数：{len(summary)}")
    print(f"长度验证：{'✅ 通过' if summarizer.validate_length(summary) else '⚠️  超出范围'}")
    print("=" * 80)


if __name__ == "__main__":
    main()
