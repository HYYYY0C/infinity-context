#!/usr/bin/env python3
"""
6 小时测试监控脚本

用法:
    python3 tests/test_6hour_monitor.py
    
功能:
- 记录每次压缩的时间、轮数、摘要字数
- 统计成功率
- 生成测试报告
"""

import json
from datetime import datetime
from pathlib import Path


class TestMonitor:
    """测试监控器"""
    
    def __init__(self):
        self.records = []
        self.log_file = Path(__file__).parent / "test_records.json"
        self.load_records()
    
    def load_records(self):
        """加载已有记录"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except:
                self.records = []
    
    def save_records(self):
        """保存记录"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, ensure_ascii=False, indent=2)
    
    def add_record(self, conversation_rounds: int, summary_length: int, 
                   generation_time: float, success: bool, notes: str = ""):
        """添加测试记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "conversation_rounds": conversation_rounds,
            "summary_length": summary_length,
            "generation_time": generation_time,
            "success": success,
            "notes": notes
        }
        self.records.append(record)
        self.save_records()
        
        print(f"\n✅ 测试记录已保存")
        print(f"   时间：{record['timestamp']}")
        print(f"   对话轮数：{conversation_rounds}")
        print(f"   摘要字数：{summary_length}")
        print(f"   生成时间：{generation_time:.2f}秒")
        print(f"   状态：{'✅ 成功' if success else '❌ 失败'}")
    
    def generate_report(self):
        """生成测试报告"""
        if not self.records:
            print("暂无测试记录")
            return
        
        print("\n" + "="*80)
        print("📊 6 小时测试报告")
        print("="*80)
        
        total_tests = len(self.records)
        successful = sum(1 for r in self.records if r['success'])
        success_rate = (successful / total_tests * 100) if total_tests > 0 else 0
        
        avg_rounds = sum(r['conversation_rounds'] for r in self.records) / total_tests
        avg_length = sum(r['summary_length'] for r in self.records) / total_tests
        avg_time = sum(r['generation_time'] for r in self.records) / total_tests
        
        print(f"\n📈 总体统计:")
        print(f"   测试次数：{total_tests}")
        print(f"   成功次数：{successful}")
        print(f"   失败次数：{total_tests - successful}")
        print(f"   成功率：{success_rate:.1f}%")
        
        print(f"\n📊 平均值:")
        print(f"   平均对话轮数：{avg_rounds:.1f}")
        print(f"   平均摘要字数：{avg_length:.1f}")
        print(f"   平均生成时间：{avg_time:.2f}秒")
        
        # 验证是否达到目标
        print(f"\n✅ 目标验证:")
        
        # 目标 1: 生成时间 <3 秒
        time_ok = all(r['generation_time'] < 3.0 for r in self.records)
        print(f"   生成时间 <3 秒：{'✅ 达到' if time_ok else '❌ 未达到'}")
        
        # 目标 2: 摘要字数 300-500
        length_ok = all(300 <= r['summary_length'] <= 500 for r in self.records)
        print(f"   摘要字数 300-500: {'✅ 达到' if length_ok else '❌ 未达到'}")
        
        # 目标 3: 成功率 100%
        success_ok = success_rate == 100
        print(f"   成功率 100%: {'✅ 达到' if success_ok else '❌ 未达到'}")
        
        # 总体评价
        print(f"\n🎯 总体评价:")
        if time_ok and length_ok and success_ok:
            print(f"   🎉 所有目标达成！可以发布！")
        else:
            print(f"   ⚠️  部分目标未达成，需要改进")
        
        print("\n" + "="*80)
        
        # 详细记录
        print(f"\n📋 详细记录:")
        for i, record in enumerate(self.records, 1):
            print(f"\n   记录 {i}:")
            print(f"      时间：{record['timestamp']}")
            print(f"      对话轮数：{record['conversation_rounds']}")
            print(f"      摘要字数：{record['summary_length']}")
            print(f"      生成时间：{record['generation_time']:.2f}秒")
            print(f"      状态：{'✅' if record['success'] else '❌'}")
            if record.get('notes'):
                print(f"      备注：{record['notes']}")


def main():
    """主函数"""
    monitor = TestMonitor()
    
    print("\n" + "="*80)
    print("🧪 6 小时测试监控器")
    print("="*80)
    print("\n选择操作:")
    print("1. 添加测试记录")
    print("2. 生成测试报告")
    print("3. 退出")
    print()
    
    try:
        choice = input("请输入选项 (1/2/3): ").strip()
        
        if choice == "1":
            # 添加记录
            rounds = int(input("对话轮数："))
            length = int(input("摘要字数："))
            time_cost = float(input("生成时间（秒）："))
            success = input("是否成功？(y/n): ").strip().lower() == 'y'
            notes = input("备注（可选）：").strip()
            
            monitor.add_record(rounds, length, time_cost, success, notes)
            
        elif choice == "2":
            # 生成报告
            monitor.generate_report()
            
        elif choice == "3":
            print("\n👋 再见！")
            
        else:
            print("\n❌ 无效选项")
            
    except (ValueError, EOFError, KeyboardInterrupt):
        print("\n\n⚠️  操作已取消")


if __name__ == "__main__":
    main()
