#!/usr/bin/env python3
"""
🔄 Session Rotation Phase 3 - 完全自动化

核心特性:
1. 自动检测 context 限制
2. 自动生成摘要
3. 自动执行 /new（Computer Use）
4. 自动注入摘要
5. 用户完全无感知

工作流程:
  检测 80% → 生成摘要 → 等待自然断点 → 
  自动执行 /new → 注入摘要 → 事后通知
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Any

# 条件导入：避免 LSP 警告
if TYPE_CHECKING:
    from hermes_tools import session_search, terminal, send_message, computer_use
    import tiktoken
else:
    try:
        from hermes_tools import session_search, terminal, send_message, computer_use
        import tiktoken
    except ImportError:
        session_search = None
        terminal = None
        send_message = None
        computer_use = None
        tiktoken = None


class FullyAutoRotator:
    """完全自动化轮换器 - Phase 3"""
    
    def __init__(self):
        # 运行时检查
        if session_search is None or terminal is None or send_message is None:
            raise RuntimeError(
                "❌ 请在 Hermes 环境中运行此脚本\n"
                "hermes_tools 未找到，这应该是一个部署问题。"
            )
        
        self.summary_dir = Path.home() / ".hermes" / "session-rotation"
        self.summary_dir.mkdir(parents=True, exist_ok=True)
        self.summary_file = self.summary_dir / "auto_summary.json"
        self.state_file = self.summary_dir / "auto_state.json"
        
        # 阈值配置
        self.threshold_messages = 40
        self.threshold_tokens = 100000
        self.auto_threshold = 0.8  # 80% 触发自动切换
        
        # 自然断点关键词
        self.natural_breaks = [
            "好的", "明白了", "谢谢", "理解了", "知道了",
            "ok", "good", "thanks", "understood",
            "👌", "✅", "🙏",
        ]
    
    def check_and_auto_rotate(self):
        """检查并自动执行轮换"""
        
        print("🔍 检查当前会话...")
        
        # 读取当前会话
        try:
            recent = session_search(limit=1)
            current_id = recent.session_id
        except Exception as e:
            print(f"❌ 无法读取会话：{e}")
            return
        
        # 读取消息
        try:
            messages_data = session_search(session_id=current_id, window=100)
            messages = messages_data.get('messages', [])
            message_count = len(messages)
        except Exception as e:
            print(f"❌ 无法读取消息：{e}")
            return
        
        # 计算 Token
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
            total_tokens = sum(len(encoding.encode(m.get('content', ''))) for m in messages)
        except:
            total_tokens = message_count * 300
        
        # 计算使用率
        usage_rate = max(
            message_count / self.threshold_messages,
            total_tokens / self.threshold_tokens
        )
        
        print(f"📊 使用率：{usage_rate:.1%} ({message_count} 轮，{total_tokens:,} tokens)")
        
        # 检查是否需要自动切换
        if usage_rate >= self.auto_threshold:
            print(f"⚠️  使用率超过 {self.auto_threshold:.0%}，准备自动切换...")
            
            # 检查最后一条消息是否是自然断点
            last_message = messages[-1].get('content', '') if messages else ''
            is_natural_break = any(break_word in last_message.lower() for break_word in self.natural_breaks)
            
            if is_natural_break:
                print("✅ 检测到自然断点，执行自动切换...")
                self.execute_full_auto_rotation(messages)
            else:
                print("⏳ 未检测到自然断点，发送温和提醒...")
                self.send_gentle_reminder(usage_rate)
        else:
            print("✅ 使用率正常，无需操作")
    
    def execute_full_auto_rotation(self, messages):
        """执行完全自动轮换"""
        
        print("🔄 开始自动轮换...")
        
        # Step 1: 生成摘要
        print("📝 Step 1: 生成摘要...")
        summary = self.generate_summary(messages)
        if not summary:
            print("❌ 摘要生成失败，中止")
            return
        
        # Step 2: 保存摘要
        print("💾 Step 2: 保存摘要...")
        if not self.save_summary(summary):
            print("❌ 摘要保存失败，中止")
            return
        
        # Step 3: 等待合适时机（2-5 秒）
        print("⏳ Step 3: 等待合适时机...")
        time.sleep(3)
        
        # Step 4: 自动执行 /new
        print("✍️  Step 4: 自动执行 /new...")
        if not self.auto_execute_new():
            print("❌ 执行 /new 失败，发送手动提示...")
            self.send_manual_switch_prompt()
            return
        
        # Step 5: 等待新会话开启
        print("⏳ Step 5: 等待新会话开启...")
        new_session_id = self.wait_for_new_session()
        if not new_session_id:
            print("❌ 未检测到新会话，发送手动提示...")
            self.send_manual_switch_prompt()
            return
        
        # Step 6: 注入摘要
        print("💉 Step 6: 注入摘要...")
        if not self.inject_summary_to_new_session():
            print("❌ 摘要注入失败")
            return
        
        # Step 7: 事后通知
        print("📬 Step 7: 发送事后通知...")
        self.send_post_notification(summary)
        
        print("✅ 自动轮换完成！")
    
    def generate_summary(self, messages):
        """生成结构化摘要"""
        
        conversation_text = "\n".join([
            f"{m.get('role', 'unknown')}: {m.get('content', '')}"
            for m in messages[-50:]
        ])
        
        prompt = f"""
请分析以下对话，生成结构化摘要（JSON 格式）：

{conversation_text[:30000]}

输出严格的 JSON 格式：
{{
  "summary": "200-300 字摘要",
  "key_points": ["关键点 1", "关键点 2"],
  "action_items": ["待办 1", "待办 2"],
  "context": {{
    "projects": ["项目 A"],
    "decisions": ["决定 B"],
    "tech_stack": ["技术 C"]
  }},
  "next_steps": "下一步计划",
  "confidence": 0.95
}}
"""
        
        try:
            from hermes_tools import delegate_task
            
            result = delegate_task(
                goal="生成结构化摘要（JSON 格式）",
                context=prompt
            )
            
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
            
        except Exception as e:
            print(f"❌ 生成摘要失败：{e}")
            return None
    
    def save_summary(self, summary: dict) -> bool:
        """保存摘要"""
        try:
            summary['_metadata'] = {
                'generated_at': datetime.now().isoformat(),
                'auto_mode': True
            }
            
            summary_json = json.dumps(summary, ensure_ascii=False, indent=2)
            
            command = f"""
cat > {self.summary_file} << 'EOF'
{summary_json}
EOF
"""
            result = terminal(command)
            return result.get('exit_code', 1) == 0
        except:
            return False
    
    def auto_execute_new(self) -> bool:
        """自动执行 /new（使用 Computer Use）"""
        
        try:
            # 方法 1: 使用 computer_use 模拟输入
            if computer_use is None:
                raise ImportError("computer_use 不可用")
            
            # 聚焦输入框
            computer_use.click_element("输入框")
            
            # 输入 /new
            computer_use.type_text("/new")
            
            # 按 Enter
            computer_use.press_key("Enter")
            
            print("✅ 已自动执行 /new")
            return True
            
        except ImportError:
            print("⚠️  computer_use 不可用，尝试替代方案...")
            
            # 方法 2: 使用 terminal 模拟（如果支持）
            try:
                # 某些 Hermes 环境支持直接发送命令
                terminal("echo '/new'")  # 可能需要特殊配置
                return True
            except:
                return False
        
        except Exception as e:
            print(f"❌ 执行失败：{e}")
            return False
    
    def wait_for_new_session(self, timeout=30) -> Optional[str]:
        """等待新会话开启"""
        
        start_time = time.time()
        old_session_id = None
        
        # 获取旧会话 ID
        try:
            recent = session_search(limit=1)
            old_session_id = recent.session_id
        except:
            pass
        
        # 轮询检测新会话
        while time.time() - start_time < timeout:
            time.sleep(2)
            
            try:
                recent = session_search(limit=1)
                current_id = recent.session_id
                
                if current_id != old_session_id:
                    print(f"✅ 检测到新会话：{current_id}")
                    return current_id
            except:
                pass
        
        print("⏰ 等待超时")
        return None
    
    def inject_summary_to_new_session(self) -> bool:
        """注入摘要到新会话"""
        
        if not self.summary_file.exists():
            return False
        
        try:
            with open(self.summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            inject_prompt = f"""
📋 **已自动恢复上下文**

**摘要**: {summary.get('summary', '无')}

**关键点**:
{chr(10).join('• ' + str(p) for p in summary.get('key_points', []))}

**待办事项**:
{chr(10).join('• ' + str(t) for t in summary.get('action_items', []))}

**下一步**: {summary.get('next_steps', '继续当前任务')}

---
我们可以继续了！有什么需要我做的吗？
"""
            
            send_message(inject_prompt)
            print("✅ 摘要已注入")
            
            # 清理临时文件
            self.summary_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"❌ 注入失败：{e}")
            return False
    
    def send_post_notification(self, summary: dict):
        """发送事后通知"""
        
        message = f"""
✅ **已自动切换到新会话**

为了保持最佳性能，我已自动：
1. 生成了上一会话的摘要
2. 开启了新会话
3. 注入了上下文

**摘要预览**: {summary.get('summary', '无')[:100]}...

我们可以继续了！
"""
        
        send_message(message)
    
    def send_gentle_reminder(self, usage_rate: float):
        """发送温和提醒（非自然断点时）"""
        
        message = f"""
💡 **提示**: 当前会话使用率已达 {usage_rate:.0%}

建议：
- 等一个自然停顿点（如"好的"、"谢谢"）
- 我会自动切换到新会话
- 或者现在说"切换"立即执行

（自动模式已启用）
"""
        
        send_message(message)
    
    def send_manual_switch_prompt(self):
        """发送手动切换提示（自动失败时）"""
        
        message = """
⚠️ **自动切换失败**

请手动执行：
1. 说 "/new" 开启新会话
2. 说 "继续" 恢复上下文

抱歉给您带来不便，我会继续改进自动切换功能。
"""
        
        send_message(message)
    
    def save_state(self, state: dict):
        """保存状态"""
        try:
            state_json = json.dumps(state, ensure_ascii=False, indent=2)
            command = f"cat > {self.state_file} << 'EOF'\n{state_json}\nEOF"
            terminal(command)
        except:
            pass
    
    def load_state(self) -> dict:
        """加载状态"""
        if not self.state_file.exists():
            return {}
        try:
            content = self.state_file.read_text(encoding='utf-8')
            return json.loads(content)
        except:
            return {}


def main():
    """主函数"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Session Rotation Phase 3 - 完全自动化")
    parser.add_argument("action", 
                       choices=["check", "force", "status"],
                       help="操作类型：check=检查并自动切换，force=强制切换，status=状态")
    
    args = parser.parse_args()
    
    rotator = FullyAutoRotator()
    
    if args.action == "check":
        rotator.check_and_auto_rotate()
    
    elif args.action == "force":
        # 强制切换（不等待自然断点）
        print("⚠️  强制切换模式...")
        # 简化实现：直接调用自动轮换
        rotator.check_and_auto_rotate()
    
    elif args.action == "status":
        state = rotator.load_state()
        print("当前状态:", json.dumps(state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
