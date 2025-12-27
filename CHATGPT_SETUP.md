# 🧠 הרצה עם ChatGPT Brain

## מה זה?

במקום שהמערכת תקבל החלטות בעצמה, **ChatGPT יהיה המוח!**

ChatGPT יקבל:
- ✅ את המטרה שהגדרת
- ✅ את כל הזיכרונות
- ✅ את התצפיות האחרונות

ויחליט:
- 🤔 מה לעשות הבא
- 🎯 איך להתקדם למטרה
- 📚 מה ללמוד מהניסיון

---

## התקנה מהירה

### 1. התקן OpenAI

```bash
pip install openai
```

### 2. קבל API Key

1. לך ל-[OpenAI Platform](https://platform.openai.com)
2. התחבר / הרשם
3. לך ל-API Keys
4. צור key חדש
5. העתק אותו!

### 3. הגדר את ה-Key

**Linux/Mac:**
```bash
export OPENAI_API_KEY='sk-your-key-here'
```

**Windows:**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**או בקוד:**
```python
brain = ChatGPTBrain(api_key='sk-your-key-here')
```

### 4. הרץ!

```bash
python3 autonomous-claude/chatgpt_brain.py
```

---

## דוגמאות שימוש

### דוגמה 1: ChatGPT מחליט מה לעשות

```python
from autonomous-claude.chatgpt_brain import ChatGPTBrain

# צור מוח
brain = ChatGPTBrain(model="gpt-3.5-turbo")

# תן לו מצב והוא יחליט
decision = brain.think(
    situation="אני רוצה לחקור את GitHub API של Python",
    context={
        'goal': 'למצוא repositories מעניינים',
        'memories': []
    }
)

print(decision)
# ChatGPT ישיב: "כדאי להתחיל מ-repos/python/cpython..."
```

### דוגמה 2: סוכן אוטונומי מלא

```python
from autonomous-claude.chatgpt_brain import AutonomousAgentWithChatGPT

# צור סוכן עם ChatGPT כמוח
agent = AutonomousAgentWithChatGPT(model="gpt-4")  # או gpt-3.5-turbo

# הגדר מטרה
agent.set_goal("לחקור GitHub ולמצוא פרויקטים מגניבים ב-Python")

# הרץ 5 מחזורים
agent.run(cycles=5)
```

### דוגמה 3: למידה מניסיון

```python
brain = ChatGPTBrain()

# ניסית משהו
experience = "ניסיתי לגשת ל-API ללא authentication"
outcome = "קיבלתי שגיאת 401 Unauthorized"

# ChatGPT ילמד ויגיד מה הלקח
lesson = brain.learn_from_experience(experience, outcome)
print(lesson)
# "צריך להוסיף API key לכל request"
```

### דוגמה 4: שאל לעזרה

```python
brain = ChatGPTBrain()

answer = brain.ask_for_help(
    question="איך אני מחפש repositories לפי כמות stars?",
    context="אני משתמש ב-GitHub API"
)

print(answer)
# ChatGPT יסביר בדיוק איך!
```

---

## המודלים הזמינים

### GPT-3.5 Turbo (מומלץ להתחלה)
```python
brain = ChatGPTBrain(model="gpt-3.5-turbo")
```
- ✅ מהיר
- ✅ זול ($0.002 לכל 1K tokens)
- ✅ טוב מאוד

### GPT-4 (החזק ביותר)
```python
brain = ChatGPTBrain(model="gpt-4")
```
- ✅ החכם ביותר
- ⚠️ יקר יותר
- ✅ מומלץ למשימות מורכבות

### GPT-4 Turbo
```python
brain = ChatGPTBrain(model="gpt-4-turbo-preview")
```
- ✅ מאזן טוב
- ✅ context window גדול

---

## דוגמה מלאה - צעד אחר צעד

```python
#!/usr/bin/env python3
"""
סוכן שחוקר GitHub עם ChatGPT כמוח
"""
import os
from autonomous-claude.chatgpt_brain import ChatGPTBrain
from autonomous-claude.memory import short_term
import requests

# 1. הגדר API key
os.environ['OPENAI_API_KEY'] = 'sk-your-key-here'

# 2. צור ChatGPT Brain
brain = ChatGPTBrain(model="gpt-3.5-turbo")
print("🧠 ChatGPT Brain מוכן!\n")

# 3. הגדר מטרה
goal = "למצוא את 3 ה-repositories הכי פופולריים של Python"
short_term.add('goal', goal)

# 4. שאל את ChatGPT איך להתחיל
print("🤔 שואל את ChatGPT איך להתחיל...\n")
plan = brain.think(f"המטרה שלי: {goal}\nאיך כדאי להתחיל?")
print(f"📋 תכנית: {plan}\n")

# 5. בצע את מה ש-ChatGPT אמר
print("⚡ מבצע...")
r = requests.get('https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc')
data = r.json()

# 6. תן ל-ChatGPT לנתח את התוצאות
print("🔍 ChatGPT מנתח תוצאות...\n")
analysis = brain.think(
    f"מצאתי {len(data['items'])} repositories.\n"
    f"3 הראשונים: {[r['name'] for r in data['items'][:3]]}\n"
    f"מה אני צריך לעשות עכשיו?"
)
print(f"💡 ניתוח: {analysis}\n")

# 7. למד מהניסיון
lesson = brain.learn_from_experience(
    experience="חיפשתי repositories ב-GitHub API",
    outcome=f"מצאתי {len(data['items'])} תוצאות"
)
print(f"📚 לקח: {lesson}")
```

---

## עלויות

### GPT-3.5 Turbo
- $0.002 / 1K tokens
- מחזור טיפוסי: ~500 tokens = $0.001
- 1000 מחזורים = ~$1

### GPT-4
- $0.03 / 1K tokens (input)
- $0.06 / 1K tokens (output)
- יקר יותר פי 15-30

### טיפים לחיסכון:
1. התחל עם GPT-3.5
2. השתמש ב-GPT-4 רק למשימות קשות
3. הגבל את max_tokens
4. שמור בזיכרון החלטות טובות

---

## שילוב עם המערכת הקיימת

```python
from autonomous-claude.chatgpt_brain import ChatGPTBrain
from autonomous-claude.decision_loop import DecisionLoop
from autonomous-claude.memory import short_term

# החלף את ה-decision logic ב-ChatGPT
brain = ChatGPTBrain()
loop = DecisionLoop()

# במקום החלטה ידנית
situation = "צריך לבחור איזה repository לחקור"
decision = brain.think(situation)

# המשך עם ה-decision loop הרגיל
loop.record('thought', decision)
loop.act(decision)
```

---

## Troubleshooting

### ❌ "OpenAI API key not found"

```bash
# Linux/Mac
export OPENAI_API_KEY='sk-...'

# Windows
set OPENAI_API_KEY=sk-...

# או בקוד
brain = ChatGPTBrain(api_key='sk-...')
```

### ❌ "Module 'openai' not found"

```bash
pip install openai
```

### ❌ "Rate limit exceeded"

אתה עושה יותר מדי requests. חכה קצת או שדרג תכנית.

### ❌ "Invalid API key"

בדוק שה-key תקין ב-[OpenAI Dashboard](https://platform.openai.com/api-keys)

---

## יתרונות של ChatGPT Brain

✅ **החלטות חכמות** - ChatGPT מבין context ומקבל החלטות טובות

✅ **למידה** - יכול ללמוד מטעויות ולהשתפר

✅ **גמישות** - מתאים את עצמו למצבים חדשים

✅ **הסברים** - נותן נימוקים להחלטות

✅ **שפה טבעית** - אפשר לדבר איתו בעברית!

---

## דוגמה מתקדמת: Multi-Agent

```python
# צור כמה agents עם תפקידים שונים
explorer = ChatGPTBrain(model="gpt-3.5-turbo")
analyzer = ChatGPTBrain(model="gpt-4")

# Explorer מחפש
repos = explorer.think("מצא repositories מגניבים ב-AI")

# Analyzer מנתח לעומק
analysis = analyzer.think(f"נתח את הrepos האלה: {repos}")

print(analysis)
```

---

## סיכום

1. **התקן**: `pip install openai`
2. **API Key**: קבל מ-OpenAI
3. **הגדר**: `export OPENAI_API_KEY='...'`
4. **הרץ**: `python3 autonomous-claude/chatgpt_brain.py`

**עכשיו יש לך סוכן AI אוטונומי עם ChatGPT כמוח!** 🧠🚀

---

**מחיר משוער**: $0.001-0.01 למחזור (תלוי במודל)

**מומלץ**: התחל עם GPT-3.5 Turbo, שדרג ל-GPT-4 רק אם צריך
