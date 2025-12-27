#!/usr/bin/env python3
"""
Autonomous Claude - Replit Quick Start
דוגמה מהירה להרצה ב-Replit
"""
import sys
sys.path.insert(0, 'autonomous-claude')

def main():
    print("="*70)
    print("🤖 Autonomous Claude - ב-Replit!")
    print("="*70)
    print()

    # Test imports
    print("📦 בודק imports...")
    try:
        from memory import short_term
        print("   ✅ memory module")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 הרץ: pip install -r autonomous-claude/requirements.txt")
        return

    try:
        from decision_loop import DecisionLoop
        print("   ✅ decision_loop module")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    try:
        from browser import BrowserSession
        print("   ✅ browser module")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Test database
    print("💾 בודק database...")
    try:
        short_term.add('action', 'בדיקה ב-Replit')
        recent = short_term.get_recent(5)
        print(f"   ✅ Database עובד! ({len(recent)} זיכרונות)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   💡 הרץ: python3 autonomous-claude/setup_memory.py")
        return

    print()

    # Demo
    print("🎬 הדגמה קצרה:")
    print("-"*70)

    # Add some memories
    short_term.add('goal', 'להריץ Autonomous Claude ב-Replit')
    short_term.add('thought', 'אני צריך לבדוק שהכל עובד')
    short_term.add('action', 'מריץ את הקוד ב-Replit')
    short_term.add('observation', 'המערכת עובדת מצוין!')

    # Show memories
    recent = short_term.get_recent(10)
    print()
    print("📝 זיכרונות אחרונים:")
    icons = {'goal': '🎯', 'thought': '💭', 'action': '⚡', 'observation': '👁️'}

    for m in recent[-4:]:
        icon = icons.get(m['type'], '•')
        print(f"   {icon} [{m['type']:12}] {m['content']}")

    print()
    print("="*70)
    print("✅ המערכת פועלת ב-Replit!")
    print("="*70)
    print()
    print("💡 הוראות נוספות ב: REPLIT_SETUP.md")
    print("📖 תיעוד מלא ב: autonomous-claude/README.md")
    print()
    print("🚀 להרצת הסוכן המלא:")
    print("   python3 autonomous-claude/autonomous_agent.py")
    print()

if __name__ == "__main__":
    main()
