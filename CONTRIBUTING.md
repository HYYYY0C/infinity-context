# 🤝 贡献指南

欢迎为 **Infinity Context** 做贡献！🎉

---

## 🚀 快速开始

### 1. Fork 仓库

点击右上角的 "Fork" 按钮。

### 2. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/infinity-context.git
cd infinity-context
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
```

### 4. 安装开发依赖

```bash
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

---

## 💡 可以贡献什么？

### 代码类

- ✅ 新功能实现
- ✅ Bug 修复
- ✅ 性能优化
- ✅ 单元测试
- ✅ 代码重构

### 文档类

- ✅ README 改进
- ✅ 教程和示例
- ✅ 翻译（多语言支持）
- ✅ 常见问题解答

### 社区类

- ✅ 报告 Bug
- ✅ 提出功能建议
- ✅ 分享使用案例
- ✅ 帮助回答 Issues

---

## 📝 开发流程

### 1. 开发新功能

```python
# src/your_feature.py
def your_new_feature():
    """
    清晰的功能说明
    
    Args:
        param1: 参数说明
    
    Returns:
        返回值说明
    """
    pass
```

### 2. 编写测试

```python
# tests/test_your_feature.py
def test_your_feature():
    result = your_new_feature()
    assert result == expected_value
```

### 3. 代码格式化

```bash
# 使用 black 格式化代码
black src/ tests/

# 使用 flake8 检查代码风格
flake8 src/ tests/
```

### 4. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: 添加你的功能

- 功能描述 1
- 功能描述 2
- 功能描述 3

Closes #123"
```

### 6. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

---

## 📋 代码规范

### 命名规范

- **文件名**: 小写，下划线分隔 (`your_file.py`)
- **函数名**: 小写，下划线分隔 (`your_function()`)
- **类名**: 驼峰命名 (`YourClass`)
- **常量**: 大写，下划线分隔 (`MAX_VALUE = 100`)

### 文档字符串

所有公共函数和类必须有文档字符串：

```python
def compress_context(messages: list, template: str = "default") -> dict:
    """
    压缩对话上下文生成摘要
    
    Args:
        messages: 对话消息列表
        template: 摘要模板名称 (default: "default")
    
    Returns:
        包含摘要的字典
    
    Raises:
        ValueError: 当模板不存在时
    """
    pass
```

### 类型注解

使用 Python 类型注解：

```python
from typing import List, Dict, Optional

def process_messages(
    messages: List[Dict],
    max_tokens: Optional[int] = None
) -> Dict:
    pass
```

---

## 🧪 测试规范

### 单元测试

```python
import pytest
from src.token_counter import TokenCounter

def test_token_counter_gpt4():
    counter = TokenCounter(model="gpt-4")
    tokens = counter.count("Hello, world!")
    assert tokens > 0

def test_token_counter_invalid_model():
    with pytest.raises(ValueError):
        TokenCounter(model="invalid-model")
```

### 集成测试

```python
def test_full_rotation_workflow():
    """测试完整的 session 轮换流程"""
    # 1. 监控 context
    # 2. 生成摘要
    # 3. 创建新 session
    # 4. 验证连续性
    pass
```

---

## 📝 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

### 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具/配置

### 示例

```bash
feat: 添加交互式 CLI 模式

- 实现 --interactive 参数
- 添加用户输入验证
- 更新帮助文档

Closes #45
```

```bash
fix: 修复 tiktoken 计数错误

- 修正 f-string 转义问题
- 添加边界测试用例

Fixes #67
```

```bash
docs: 更新快速开始指南

- 添加安装步骤截图
- 补充常见问题
- 优化示例代码
```

---

## 🔍 Code Review 清单

### 提交前自查

- [ ] 代码已格式化 (black)
- [ ] 代码风格检查通过 (flake8)
- [ ] 所有测试通过 (pytest)
- [ ] 测试覆盖率 > 80%
- [ ] 文档字符串完整
- [ ] 类型注解完整
- [ ] 提交信息规范

### Reviewer 检查

- [ ] 代码逻辑正确
- [ ] 无性能问题
- [ ] 无安全隐患
- [ ] 测试充分
- [ ] 文档完整

---

## 🐛 报告 Bug

### Bug 报告模板

```markdown
**描述问题**
简洁描述问题

**复现步骤**
1. 执行 '...'
2. 点击 '...'
3. 看到错误 '...'

**预期行为**
应该发生什么

**截图**
如有，添加截图

**环境信息**
- OS: [e.g. Ubuntu 22.04]
- Python: [e.g. 3.11]
- Version: [e.g. v0.3.0]

**日志**
```
错误日志内容
```
```

---

## 💡 功能建议

### 功能建议模板

```markdown
**功能描述**
简洁描述建议的功能

**使用场景**
这个功能解决什么问题？

**实现建议**
如何实现？（可选）

**替代方案**
有其他解决方案吗？

**额外信息**
截图、示例等
```

---

## 🎯 当前优先任务

查看 [Issues](https://github.com/HYYYY0C/infinity-context/issues) 中标记为：

- 🔴 `high priority` - 高优先级
- 🟢 `good first issue` - 适合新手
- 💡 `enhancement` - 功能改进

### 特别欢迎

- ✅ 单元测试覆盖
- ✅ 文档改进
- ✅ 使用示例
- ✅ 性能优化
- ✅ 多语言翻译

---

## 📞 联系方式

- **GitHub Issues**: [提问/讨论](https://github.com/HYYYY0C/infinity-context/issues)
- **GitHub Discussions**: [一般讨论](https://github.com/HYYYY0C/infinity-context/discussions)
- **Email**: hyyyy0c@gmail.com

---

## 🙏 致谢

感谢所有贡献者！🎉

<a href="https://github.com/HYYYY0C/infinity-context/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=HYYYY0C/infinity-context" />
</a>

---

**Made with ❤️ by the Infinity Context Team**

*"Infinite context, small model"*
