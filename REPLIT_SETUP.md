# 🚀 הרצה ב-Replit

## התקנה מהירה

### שלב 1: העלה את הפרויקט ל-Replit

1. לך ל-[Replit.com](https://replit.com)
2. צור Repl חדש (New Repl)
3. בחר: **Import from GitHub**
4. הדבק את ה-URL של הרפוזיטורי שלך

או:
1. צור Python Repl
2. העלה את התיקייה `autonomous-claude/`

### שלב 2: התקן תלויות

```bash
pip install -r autonomous-claude/requirements.txt
```

או פשוט לחץ על כפתור **Run** - Replit יתקין אוטומטית!

### שלב 3: אתחל את המערכת

```bash
python3 autonomous-claude/setup_memory.py
```

### שלב 4: הרץ!

```bash
python3 autonomous-claude/autonomous_agent.py
```

---

## 🎮 דוגמאות שימוש

### 1. מערכת זיכרון בסיסית

```python
from autonomous-claude.memory import short_term

# הוסף זיכרון
short_term.add('goal', 'ללמוד Python')
short_term.add('action', 'קראתי tutorial')
short_term.add('observation', 'למדתי על lists')

# קרא זיכרונות
recent = short_term.get_recent(10)
for m in recent:
    print(f"[{m['type']}] {m['content']}")
```

### 2. גלישה באינטרנט

```python
import sys
sys.path.insert(0, 'autonomous-claude')

import requests
from memory import short_term
from browser import BrowserSession

# צור session
browser = BrowserSession()
short_term.add('goal', 'לחקור GitHub API')

# גלוש
response = requests.get('https://api.github.com/users/torvalds')
data = response.json()

print(f"User: {data['login']}")
print(f"Followers: {data['followers']}")

# תעד
short_term.add('observation', f"מצאתי {data['followers']} followers")
```

### 3. סוכן אוטונומי

```python
from autonomous-claude.autonomous_agent import AutonomousAgent

agent = AutonomousAgent(
    initial_goal='לחקור repositories פופולריים ב-GitHub'
)

agent.run(max_cycles=3)
```

---

## ⚙️ הגדרות Replit

הפרויקט מגיע עם:
- `.replit` - הגדרות הרצה
- `replit.nix` - תלויות מערכת
- `autonomous-claude/requirements.txt` - חבילות Python

---

## 🌐 גלישה באינטרנט ב-Replit

Replit תומך בגישה לאינטרנט! אתה יכול:

✅ לגלוש ב-GitHub API
✅ לשלוף נתונים מ-REST APIs
✅ לקרוא מאתרים ציבוריים
✅ להשתמש ב-requests, urllib

**דוגמה:**
```python
import requests
r = requests.get('https://api.github.com')
print(r.json())
```

---

## 💾 בסיס הנתונים

SQLite עובד מצוין ב-Replit!

המערכת תיצור אוטומטית:
```
autonomous-claude/data/memory/short_term.db
```

הנתונים יישמרו בין הרצות! 🎉

---

## 📸 צילומי מסך

צילומי מסך יישמרו ב:
```
autonomous-claude/data/screenshots/
```

אתה יכול להוריד אותם או לראות אותם ב-Replit Files.

---

## 🔧 Qdrant (זיכרון ארוך טווח - אופציונלי)

ב-Replit **לא** תוכל להריץ Qdrant בקלות (זה דורש Docker).

**אבל אין בעיה!** המערכת עובדת מצוין בלי זה:
- ✅ זיכרון קצר טווח (SQLite) - עובד
- ✅ Decision loop - עובד
- ✅ Browser automation - עובד
- ⚠️ זיכרון ארוך טווח (Qdrant) - לא זמין

---

## 🚨 הגבלות Replit

1. **זמן ריצה**: Free tier מוגבל לכמה שעות
2. **CPU/Memory**: מוגבל בתכנית חינמית
3. **Docker**: לא זמין (אז אין Qdrant)
4. **Storage**: מוגבל, אבל מספיק לפרויקט הזה

---

## 💡 טיפים ל-Replit

### הרצה ראשונה:
```bash
# התקנה
pip install requests pillow

# אתחול
python3 autonomous-claude/setup_memory.py

# בדיקה
python3 -c "from autonomous-claude.memory import short_term; print('Works!')"
```

### דוגמה מהירה:
```python
# main.py
import sys
sys.path.insert(0, 'autonomous-claude')

from memory import short_term

print("🤖 Autonomous Claude ב-Replit!")
print()

# הוסף מטרה
short_term.add('goal', 'להריץ את המערכת ב-Replit')
short_term.add('action', 'התקנתי את הפרויקט')
short_term.add('observation', 'הכל עובד!')

# הצג
recent = short_term.get_recent(10)
print("📝 זיכרונות אחרונים:")
for m in recent[-3:]:
    print(f"  [{m['type']}] {m['content']}")
```

---

## 📦 מה כלול בפרויקט?

```
autonomous-claude/
├── memory.py              # מערכת זיכרון
├── decision_loop.py       # לולאת החלטות
├── autonomous_agent.py    # סוכן אוטונומי
├── browser.py             # כלי גלישה
├── setup_memory.py        # התקנת DB
├── README.md              # תיעוד מלא
├── install.sh             # התקנה (Linux/Mac)
└── requirements.txt       # תלויות Python
```

---

## 🎯 להתחיל עכשיו!

1. **צור Repl חדש** ב-Replit
2. **העלה את התיקייה** `autonomous-claude/`
3. **לחץ Run** - זהו!

או:
```bash
git clone [YOUR-REPO-URL]
cd mich3333
python3 autonomous-claude/autonomous_agent.py
```

---

## ✅ המערכת תעבוד!

Replit תומך ב:
- ✅ Python 3.11
- ✅ SQLite
- ✅ Internet access
- ✅ File storage
- ✅ pip packages

**כל מה שהמערכת צריכה!** 🚀

---

## 📞 תמיכה

אם משהו לא עובד:
1. בדוק שההתקנה הושלמה: `pip list | grep requests`
2. אתחל את הזיכרון: `python3 autonomous-claude/setup_memory.py`
3. קרא את README: `autonomous-claude/README.md`

---

**תהנה מהמערכת האוטונומית שלך ב-Replit!** 🎉
