#!/usr/bin/env python3
"""
Hermes Session Rotator - 命令行工具

用法:
    python -m src.cli status    # 查看 context 使用量
    python -m src.cli compress  # 压缩对话
    python -m src.cli monitor   # 启动后台监控

⚠️  当前版本说明:
    由于 Hermes 没有提供读取对话历史的 API，
    摘要生成需要用户手动提供关键信息。
    详见：--help 或 README.md
"""

import click
import sys
import json
from pathlib import Path
from typing import Optional
from .context_monitor import ContextMonitor
from .smart_summarizer import SmartSummarizer
from .session_rotator import SessionRotator


@click.group()
@click.version_option(version="0.2.0", prog_name="Hermes Session Rotator")
def main():
    """🤖 Hermes Session Rotator - Smart context management
    
    ⚠️  当前版本 (v0.2.0) 说明:
    
    由于 Hermes 没有提供读取对话历史的 API，
    摘要生成需要用户手动提供关键信息。
    
    使用方式:
      1. 手动输入关键信息：--input '{"core_tasks": [...]}'
      2. 从文件读取：--file conversation.json
      3. 仅使用模板框架（不提供数据）
    
    详见：README.md - "当前版本限制" 章节
    """
    pass


@main.command()
@click.option("--messages", "-m", default=50, help="当前对话轮数（估算）")
@click.option("--threshold", "-t", default=0.8, help="告警阈值（0.0-1.0）")
@click.option("--model", default="gpt-4", help="模型名称（用于选择 encoding）")
def status(messages: int, threshold: float, model: str):
    """📊 查看当前 context 使用量（估算）
    
    ⚠️  当前版本使用粗略估算（每条消息约 200 tokens）
    
    未来版本 (v0.4.0) 将支持：
    - 准确计数：使用 tiktoken 实时计算
    - 自动检测：从 session_search 读取对话历史
    """
    monitor = ContextMonitor(threshold=threshold, model=model)
    result = monitor.estimate_from_message_count(messages)
    
    click.echo("\n📊 Context 使用量估算（粗略）")
    click.echo("=" * 60)
    click.echo(f"对话轮数：{result['message_count']}")
    click.echo(f"估算 token: {result['estimated_tokens']:,}")
    click.echo(f"使用率：{result['usage_ratio']*100:.1f}%")
    click.echo(f"状态：{result['status']}")
    click.echo(f"方法：{result.get('method', 'rough_estimate')}")
    click.echo()
    click.echo("💡 提示：")
    click.echo("   - 当前使用粗略估算（每条消息 ~200 tokens）")
    click.echo("   - 实际值可能更低（通常 15-20 tokens/消息）")
    click.echo("   - v0.4.0 将支持自动读取对话并准确计数")
    
    if result['should_rotate']:
        click.echo("\n💡 建议：使用 'hermes-rotator compress' 压缩对话")
    else:
        # 使用准确模型的剩余空间计算
        avg_tokens = 200  # 粗略估算用
        remaining = int((threshold - result['usage_ratio']) * result['model_limit'] / avg_tokens)
        click.echo(f"\n✅ 还可以继续对话约 {remaining} 轮")


@main.command()
@click.option("--template", "-t", default="default", 
              type=click.Choice(["default", "minimal", "detailed"]),
              help="摘要模板")
@click.option("--input", "-i", "input_data", 
              help="JSON 格式的关键信息")
@click.option("--file", "-f", "input_file", 
              type=click.Path(exists=True),
              help="从文件读取")
@click.option("--auto", "-a", is_flag=True, help="自动执行切换")
@click.option("--interactive", "-I", is_flag=True, help="交互式输入")
@click.option("--llm", is_flag=True, help="使用 LLM 自动生成（推荐）")
def compress(template: str, input_data: Optional[str], input_file: Optional[str], 
             auto: bool, interactive: bool, llm: bool):
    """📝 压缩对话并切换到新 session
    
    三种方式:
      1. LLM 自动生成：compress --llm
      2. 交互式输入：compress --interactive  
      3. 手动 JSON: compress --input '{...}'
    """
    summarizer = SmartSummarizer(template=template)
    
    # 尝试获取关键信息
    key_info = None
    
    # 方式 1: LLM 自动生成
    if llm:
        click.echo("\n🤖 使用 LLM 自动生成摘要...\n")
        try:
            from hermes_tools import delegate_task
            
            prompt = """请为当前对话生成结构化 JSON 摘要：
{
  "core_tasks": [{"task": "任务", "status": "✅"}],
  "modified_files": ["文件 1"],
  "pending_tasks": ["待办 1"],
  "important_context": {"key": "value"},
  "next_steps": ["下一步"]
}
只输出 JSON。"""
            
            result = delegate_task(goal="生成摘要", context=prompt, role="leaf")
            
            if result and len(result) > 0:
                key_info = result[0]
                click.echo("✅ LLM 摘要生成成功！\n")
            else:
                click.echo("⚠️  LLM 返回为空\n")
        except Exception as e:
            click.echo(f"⚠️  LLM 失败：{e}\n")
    
    # 方式 2: 交互式输入
    if interactive and not key_info:
        click.echo("\n📝 交互式输入\n")
        
        tasks = click.prompt("1️⃣ 完成的任务（逗号分隔）", default="", show_default=False)
        files = click.prompt("2️⃣ 修改的文件（逗号分隔）", default="", show_default=False)
        pending = click.prompt("3️⃣ 待办事项（逗号分隔）", default="", show_default=False)
        
        click.echo("\n4️⃣ 重要上下文（key=value，空行结束）:")
        context = {}
        while True:
            line = click.prompt("   ", default="")
            if not line:
                break
            if "=" in line:
                k, v = line.split("=", 1)
                context[k.strip()] = v.strip()
        
        next_steps = click.prompt("\n5️⃣ 下一步（逗号分隔）", default="", show_default=False)
        
        key_info = {
            "core_tasks": [{"task": t.strip(), "status": "✅"} for t in tasks.split(",") if t.strip()],
            "modified_files": [f.strip() for f in files.split(",") if f.strip()],
            "pending_tasks": [p.strip() for p in pending.split(",") if p.strip()],
            "important_context": context,
            "next_steps": [n.strip() for n in next_steps.split(",") if n.strip()]
        }
        click.echo("\n✅ 已收集信息\n")
    
    # 方式 3: 从参数/文件读取
    elif not key_info:
        if input_data:
            try:
                key_info = json.loads(input_data)
                click.echo("✅ 已从 --input 读取")
            except json.JSONDecodeError as e:
                click.echo(f"❌ JSON 错误：{e}", err=True)
                sys.exit(1)
        
        elif input_file:
            try:
                content = Path(input_file).read_text(encoding='utf-8')
                key_info = json.loads(content)
                click.echo(f"✅ 已从文件读取：{input_file}")
            except Exception as e:
                click.echo(f"❌ 读取失败：{e}", err=True)
                sys.exit(1)
    
    # 创建 rotator 并执行
    rotator = SessionRotator(summarizer=summarizer)
    
    try:
        if key_info:
            # 有数据，生成真实摘要
            summary = summarizer.generate(key_info)
            
            click.echo("\n" + "=" * 80)
            click.echo("📦 Session Compressor - 对话摘要")
            click.echo("=" * 80)
            click.echo()
            click.echo(summary)
            click.echo()
            click.echo("=" * 80)
            click.echo("💡 使用方法:")
            click.echo("   1. 复制上面的摘要")
            click.echo("   2. 输入 /new 创建新 session")
            click.echo("   3. 粘贴摘要到新 session")
            click.echo("=" * 80)
            
            if auto:
                click.echo("\n⚠️  自动切换功能尚未实现，请手动执行 /new")
        else:
            # 没有数据，显示说明
            rotator.compress_and_show()
            
    except KeyboardInterrupt:
        click.echo("\n\n⚠️  操作已取消")
        sys.exit(0)


@main.command()
@click.option("--interval", "-i", default=120, help="检查间隔（秒）")
@click.option("--threshold", "-t", default=0.8, help="告警阈值")
def monitor(interval: int, threshold: float):
    """⏰ 启动后台监控（每 N 秒检查一次）"""
    import time
    import schedule
    
    monitor = ContextMonitor(threshold=threshold)
    
    def check():
        click.echo("\n🔍 自动检查 context 使用量...")
        click.echo("💡 当前对话是否超过 40 轮？")
        click.echo("   是 → 输入 'y' 压缩对话")
        click.echo("   否 → 输入 'n' 继续监控")
        click.echo("   退出 → 输入 'q'")
        click.echo("   帮助 → 输入 'h'")
        
        try:
            choice = input("\n   你的选择：").strip().lower()
            
            if choice == 'y':
                click.echo("\n📝 正在生成摘要...")
                click.echo("💡 提示：使用 --input 或 --file 提供关键信息可获得更好的摘要")
                compress()
            elif choice == 'q':
                click.echo("\n👋 监控已停止")
                schedule.clear()
            elif choice == 'h':
                click.echo("\n📖 帮助:")
                click.echo("   - 使用 --input 参数提供关键信息")
                click.echo("   - 使用 --file 参数从文件读取")
                click.echo("   - 详见：hermes-rotator compress --help")
        except (EOFError, KeyboardInterrupt):
            click.echo("\n\n⚠️  监控已停止")
            schedule.clear()
    
    click.echo(f"\n⏰ 启动后台监控（每{interval}秒检查一次）")
    click.echo("按 Ctrl+C 停止监控\n")
    
    schedule.every(interval).seconds.do(check)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n\n👋 监控已停止")


@main.command()
def config():
    """⚙️ 显示/编辑配置文件"""
    click.echo("⚙️  配置文件位置：~/.hermes-session-rotator/config.yaml")
    click.echo("\n💡 当前使用默认配置:")
    click.echo("   - 告警阈值：80%")
    click.echo("   - 检查间隔：120 秒")
    click.echo("   - 摘要模板：default")
    click.echo("\n📝 创建自定义配置:")
    click.echo("   mkdir -p ~/.hermes-session-rotator")
    click.echo("   vim ~/.hermes-session-rotator/config.yaml")


@main.command()
def examples():
    """📖 显示使用示例"""
    click.echo("""
📖 Hermes Session Rotator - 使用示例
=====================================

1️⃣  查看 context 使用量:
   hermes-rotator status --messages 60

2️⃣  生成摘要（手动输入关键信息）:
   hermes-rotator compress --input '{"core_tasks": ["开发功能 A"], "pending_tasks": ["测试"]}'

3️⃣  生成摘要（从文件读取）:
   hermes-rotator compress --file conversation.json
   
   文件格式:
   {
     "core_tasks": [
       {"task": "开发用户认证模块", "status": "✅", "result": "完成"}
     ],
     "modified_files": ["src/auth.py"],
     "pending_tasks": ["完成测试"],
     "next_steps": ["运行测试"]
   }

4️⃣  使用不同模板:
   hermes-rotator compress --template minimal --input '...'
   hermes-rotator compress --template detailed --input '...'

5️⃣  启动后台监控:
   hermes-rotator monitor --interval 120

6️⃣  查看帮助:
   hermes-rotator --help
   hermes-rotator compress --help

⚠️  当前版本说明:
   由于 Hermes 没有提供读取对话历史的 API，
   摘要生成需要用户手动提供关键信息。
   
   详见：README.md - "当前版本限制" 章节
""")


if __name__ == "__main__":
    main()
