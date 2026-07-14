#!/usr/bin/env python3
"""
Session Rotator - 无缝切换到新 Session

执行压缩流程：生成摘要 → 创建新 session → 注入摘要
"""

from typing import Dict, Optional
from .smart_summarizer import SmartSummarizer


class SessionRotator:
    """Session 无缝切换器"""
    
    def __init__(self, summarizer: Optional[SmartSummarizer] = None):
        """
        初始化切换器
        
        Args:
            summarizer: 摘要生成器（可选，不提供则创建默认）
        """
        self.summarizer = summarizer or SmartSummarizer()
    
    def rotate(self, reason: str = "manual", auto: bool = False) -> Dict:
        """
        执行 session 切换
        
        Args:
            reason: 切换原因（manual/context_limit/scheduled）
            auto: 是否自动执行（False=只生成摘要，让用户手动确认）
            
        Returns:
            切换结果字典
        """
        print("\n🔄 开始 Session 切换流程...")
        print("=" * 60)
        
        # 步骤 1: 生成摘要
        print("\n📝 步骤 1: 生成摘要...")
        summary = self.summarizer.generate()
        print(f"   ✅ 已生成 {len(summary)} 字摘要")
        
        # 步骤 2: 显示摘要（让用户确认）
        print("\n📋 摘要内容:")
        print("-" * 60)
        print(summary)
        print("-" * 60)
        
        if not auto:
            # 手动模式：等待用户确认
            print("\n💡 下一步操作:")
            print("1. 复制上面的摘要")
            print("2. 在 Hermes 中输入 /new 创建新 session")
            print("3. 粘贴摘要到新 session")
            print()
            print("或者输入 'auto' 自动执行切换（实验性功能）: ", end="")
            
            try:
                choice = input().strip().lower()
                if choice == "auto":
                    return self._auto_rotate(summary)
                else:
                    return {
                        "success": True,
                        "auto": False,
                        "summary": summary,
                        "message": "请手动执行 /new 并粘贴摘要"
                    }
            except (EOFError, KeyboardInterrupt):
                return {
                    "success": False,
                    "error": "用户中断"
                }
        else:
            # 自动模式
            return self._auto_rotate(summary)
    
    def _auto_rotate(self, summary: str) -> Dict:
        """
        自动执行切换（需要 Hermes API 支持）
        
        注意：当前 Hermes 没有直接的 API 执行 /new，
        这里只是演示流程，实际需要用户手动操作
        """
        print("\n🔄 步骤 2: 创建新 session...")
        print("   ⚠️  当前 Hermes 版本不支持自动 /new")
        print("   💡 请手动输入 /new 创建新 session")
        
        print("\n🔄 步骤 3: 注入摘要...")
        print("   ✅ 摘要已生成，请在新 session 中粘贴:")
        print()
        print(summary)
        
        return {
            "success": True,
            "auto": False,  # 当前不支持全自动
            "summary": summary,
            "message": "Hermes API 限制：需要手动执行 /new"
        }
    
    def compress_and_show(self) -> str:
        """
        压缩并显示摘要（不切换）
        
        Returns:
            生成的摘要文本
        """
        summary = self.summarizer.generate()
        
        print("\n" + "=" * 80)
        print("📦 Session Compressor - 对话摘要")
        print("=" * 80)
        print()
        print(summary)
        print()
        print("=" * 80)
        print("💡 使用方法:")
        print("   1. 复制上面的摘要")
        print("   2. 输入 /new 创建新 session")
        print("   3. 粘贴摘要到新 session")
        print("=" * 80)
        
        return summary


def main():
    """命令行入口"""
    rotator = SessionRotator()
    
    print("\n🎯 Hermes Session Rotator - 无缝切换工具")
    print("=" * 60)
    print("\n选择操作模式:")
    print("1. 仅生成摘要（推荐）")
    print("2. 尝试自动切换（实验性）")
    print()
    
    try:
        choice = input("请输入选项 (1/2): ").strip()
        
        if choice == "2":
            result = rotator.rotate(auto=True)
        else:
            result = rotator.compress_and_show()
        
        print(f"\n✅ 操作完成")
        
    except (EOFError, KeyboardInterrupt):
        print("\n\n⚠️  操作已取消")


if __name__ == "__main__":
    main()
