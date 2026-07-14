# 🤝 贡献指南

**欢迎为 Infinity Context 做出贡献！**

---

## 🎯 如何贡献

### **1. 报告问题**

发现 Bug？有功能建议？

- 📝 [创建 Issue](https://github.com/HYYYY0C/infinity-context/issues/new)
- 📋 提供详细信息：
  - 问题描述
  - 重现步骤
  - 预期行为
  - 实际行为
  - 环境信息（Python 版本、Hermes 版本等）

### **2. 提交代码**

#### **Fork 项目**
```bash
# 1. Fork 项目
# 2. Clone 到本地
git clone https://github.com/YOUR_USERNAME/infinity-context.git
cd infinity-context

# 3. 创建分支
git checkout -b feature/your-feature-name
```

#### **开发**
```bash
# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black mypy

# 运行测试（确保通过）
bash run_tests.sh

# 运行代码检查
flake8 scripts/ tests/
black scripts/ tests/
mypy scripts/ --ignore-missing-imports
```

#### **提交**
```bash
# 提交更改
git add .
git commit -m "feat: 添加你的功能

- 详细描述你的改动
- 关联 Issue（如果有）
- 说明测试情况"

# 推送到 GitHub
git push origin feature/your-feature-name
```

#### **创建 Pull Request**
- 📝 填写 PR 描述
- ✅ 确保所有测试通过
- 🔗 关联相关 Issue
- 👀 等待代码审查

---

## 📋 代码规范

### **Python 代码风格**

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# ✅ 好的命名
def check_and_rotate():
    """检查并自动切换"""
    total_tokens = calculate_tokens(messages)
    if usage_rate > 0.8:
        generate_summary()

# ❌ 避免的命名
def check():  # 太模糊
    t = calculate(m)  # 缩写
```

### **类型注解**

鼓励使用类型注解：

```python
from typing import List, Dict, Optional

def extract_messages(
    session_id: str,
    limit: int = 100
) -> List[Dict[str, str]]:
    """提取会话消息"""
    ...
```

### **文档字符串**

所有公共函数必须有文档字符串：

```python
def generate_summary(messages: List[Dict]) -> str:
    """
    生成会话摘要
    
    Args:
        messages: 会话消息列表
        
    Returns:
        结构化的摘要文本
        
    Raises:
        ValueError: 当消息列表为空时
    """
    ...
```

---

## 🧪 测试要求

### **编写测试**

- ✅ 新增功能必须添加测试
- ✅ 修复 Bug 必须添加回归测试
- ✅ 测试覆盖率不能降低

**示例测试**:
```python
def test_token_counting():
    """测试 Token 计数准确性"""
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    
    tokens = calculate_tokens(messages)
    assert tokens > 0
    assert isinstance(tokens, int)
```

### **运行测试**

```bash
# 运行所有测试
bash run_tests.sh

# 运行特定测试
pytest tests/test_basic.py -v

# 查看覆盖率
pytest tests/ -v --cov=scripts --cov-report=html
```

---

## 📝 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

### **类型**

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具配置

### **示例**

```bash
# ✅ 好的提交信息
feat: 添加 LLM 摘要生成
fix: 修复 Token 计数误差问题
docs: 更新 README 安装说明
test: 添加集成测试用例
refactor: 优化摘要生成逻辑

# ❌ 避免的提交信息
update code
fix bug
changes
```

---

## 🔍 代码审查

### **审查标准**

- ✅ 代码功能正确
- ✅ 测试覆盖完整
- ✅ 代码风格一致
- ✅ 文档清晰完整
- ✅ 性能影响可接受

### **审查流程**

1. 自动检查（CI/CD）
2. 维护者审查
3. 反馈和修改
4. 合并到主分支

---

## 💬 社区行为准则

### **我们的承诺**

为了营造一个开放和友好的环境，我们承诺：

- ✅ 尊重不同观点和经验
- ✅ 接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表示同理心

### **不可接受的行为**

- ❌ 使用性别化的语言或图像
- ❌ 人身攻击或侮辱性评论
- ❌ 公开或私下骚扰
- ❌ 未经许可发布他人信息
- ❌ 其他不道德或不专业的行为

---

## 🚀 开发环境设置

### **1. 克隆项目**

```bash
git clone https://github.com/HYYYY0C/infinity-context.git
cd infinity-context
```

### **2. 创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### **3. 安装依赖**

```bash
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black mypy
```

### **4. 验证安装**

```bash
# 运行测试
bash run_tests.sh

# 运行代码检查
flake8 scripts/ tests/
black --check scripts/ tests/
```

---

## 📚 资源

- [Hermes Agent 文档](https://hermes-agent.nousresearch.com/docs)
- [Python 风格指南](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest 文档](https://pytest.org/)
- [Black 文档](https://black.readthedocs.io/)

---

## 🙏 致谢

感谢所有为 Infinity Context 做出贡献的开发者！

**每一个贡献都让我们的项目更好！** ❤️

---

*"Infinite context, small model"*
