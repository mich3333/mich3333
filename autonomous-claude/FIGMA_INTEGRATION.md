# 🎨 Figma Integration Guide

## מה זה עושה?

האינטגרציה מאפשרת לך לייבא עיצובים ישירות מ-Figma ולהמיר אותם לקוד אוטומטית!

### תכונות:
- ✅ קריאת קבצי Figma דרך API
- ✅ חילוץ צבעים אוטומטי
- ✅ חילוץ טיפוגרפיה (פונטים וגדלים)
- ✅ חילוץ קומפוננטות
- ✅ יצירת Tailwind Config אוטומטית
- ✅ יצירת CSS Variables
- ✅ המרת Frames ל-HTML

---

## 🚀 איך להתחיל?

### שלב 1: קבל Personal Access Token

1. היכנס ל-Figma: https://www.figma.com
2. לך להגדרות: **Settings → Account Settings**
3. גלול ל-**Personal Access Tokens**
4. לחץ **Generate new token**
5. תן שם לtoken ותעתיק אותו!

### שלב 2: הגדר את ה-Token

```bash
export FIGMA_TOKEN='your-token-here'
```

### שלב 3: קבל File Key

מה-URL של הקובץ ב-Figma:
```
https://www.figma.com/file/ABC123XYZ/My-Design
                              ↑
                         זה ה-File Key!
```

---

## 📡 שימוש ב-API

### ייבוא עיצוב מFigma:

```bash
curl -X POST http://localhost:5000/api/figma/import \
  -H "Content-Type: application/json" \
  -d '{
    "file_key": "ABC123XYZ",
    "token": "your-figma-token"  # אופציונלי אם יש FIGMA_TOKEN
  }'
```

### תגובה:

```json
{
  "success": true,
  "file_name": "My Awesome Design",
  "colors": [
    {
      "name": "Primary",
      "rgb": "rgb(99, 102, 241)",
      "rgba": {...}
    }
  ],
  "text_styles": [
    {
      "name": "Heading",
      "fontFamily": "Inter",
      "fontSize": 48,
      "fontWeight": 700
    }
  ],
  "components": 15,
  "tailwind_config": "...",
  "css_variables": "..."
}
```

---

## 💻 שימוש ב-Python

```python
from figma_integration import FigmaClient

# יצירת client
client = FigmaClient(token='your-figma-token')

# קריאת קובץ
file_data = client.get_file('ABC123XYZ')

# חילוץ צבעים
colors = client.extract_colors(file_data)
print(f"Found {len(colors)} colors!")

# חילוץ טיפוגרפיה
text_styles = client.extract_text_styles(file_data)
print(f"Found {len(text_styles)} text styles!")

# חילוץ קומפוננטות
components = client.extract_components(file_data)
print(f"Found {len(components)} components!")

# יצירת Tailwind Config
tailwind = client.generate_tailwind_config(file_data)
with open('tailwind.config.js', 'w') as f:
    f.write(tailwind)

# יצירת CSS Variables
css = client.generate_css_variables(file_data)
with open('variables.css', 'w') as f:
    f.write(css)
```

---

## 🎨 המרה ל-HTML

```python
from figma_integration import FigmaClient, FigmaToHTML

client = FigmaClient(token='your-token')
converter = FigmaToHTML(client)

file_data = client.get_file('ABC123XYZ')

# המרת frame ראשון ל-HTML
first_frame = file_data['document']['children'][0]['children'][0]
html = converter.frame_to_html(first_frame)

print(html)
```

---

## 📦 דוגמה מלאה

```python
#!/usr/bin/env python3
import os
from figma_integration import FigmaClient

# הגדר token
os.environ['FIGMA_TOKEN'] = 'your-token-here'

# יצירת client
client = FigmaClient()

# קריאת העיצוב שלך
FILE_KEY = 'ABC123XYZ'  # מה-URL
file_data = client.get_file(FILE_KEY)

print(f"📄 File: {file_data['name']}")

# חילוץ כל הצבעים
colors = client.extract_colors(file_data)
print(f"\n🎨 Colors ({len(colors)}):")
for color in colors[:5]:
    print(f"  - {color['name']}: {color['rgb']}")

# חילוץ טקסטים
text_styles = client.extract_text_styles(file_data)
print(f"\n📝 Text Styles ({len(text_styles)}):")
for style in text_styles[:5]:
    print(f"  - {style['name']}: {style['fontFamily']} {style['fontSize']}px")

# יצירת Tailwind Config
print("\n⚙️  Generating Tailwind config...")
tailwind = client.generate_tailwind_config(file_data)
with open('figma-tailwind.config.js', 'w') as f:
    f.write(tailwind)
print("✅ Saved to: figma-tailwind.config.js")

# יצירת CSS Variables
print("\n🎨 Generating CSS variables...")
css = client.generate_css_variables(file_data)
with open('figma-variables.css', 'w') as f:
    f.write(css)
print("✅ Saved to: figma-variables.css")

print("\n🎉 Done! Your Figma design is now code!")
```

---

## 🔗 API Endpoints

### `POST /api/figma/import`

ייבוא עיצוב מFigma.

**Request:**
```json
{
  "file_key": "ABC123XYZ",
  "token": "optional-if-env-set"
}
```

**Response:**
```json
{
  "success": true,
  "file_name": "My Design",
  "colors": [...],
  "text_styles": [...],
  "components": 15,
  "tailwind_config": "...",
  "css_variables": "..."
}
```

---

## 🎯 Use Cases

### 1. ייבוא Color Palette

```python
colors = client.extract_colors(file_data)
# השתמש בצבעים ב-Tailwind או CSS
```

### 2. העתקת Typography System

```python
text_styles = client.extract_text_styles(file_data)
# צור פונטים תואמים לעיצוב
```

### 3. יצוא תמונות

```python
# קבל IDs של frames
node_ids = ['node-id-1', 'node-id-2']

# יצא כPNG
images = client.get_images('ABC123XYZ', node_ids, scale=2.0, format='png')

# URLs לתמונות
for node_id, url in images['images'].items():
    print(f"Download: {url}")
```

### 4. בניית Design System

```python
# חלץ כל מה שצריך
colors = client.extract_colors(file_data)
text_styles = client.extract_text_styles(file_data)
components = client.extract_components(file_data)

# בנה design system tokens
design_system = {
    'colors': colors,
    'typography': text_styles,
    'components': components
}

import json
with open('design-system.json', 'w') as f:
    json.dump(design_system, f, indent=2)
```

---

## 🐛 Troubleshooting

### ❌ "Figma token required"

הגדר את ה-token:
```bash
export FIGMA_TOKEN='your-token'
```

### ❌ "Figma API error: 403"

Token לא תקין או אין לך גישה לקובץ. ודא:
1. Token נכון
2. יש לך access לקובץ ב-Figma

### ❌ "Figma API error: 404"

File Key שגוי. בדוק את ה-URL.

---

## 📚 Figma API Documentation

- **Figma API Docs**: https://www.figma.com/developers/api
- **Get Personal Token**: https://www.figma.com/settings
- **API Reference**: https://www.figma.com/developers/api#files

---

## ✨ תכונות מתקדמות

### Export Specific Frames

```python
# קבל רשימת frames
file_data = client.get_file('ABC123XYZ')

# חפש frame ספציפי
def find_frame(node, name):
    if node.get('name') == name:
        return node
    if 'children' in node:
        for child in node['children']:
            result = find_frame(child, name)
            if result:
                return result
    return None

# מצא frame
hero_section = find_frame(file_data['document'], 'Hero Section')

# המר ל-HTML
from figma_integration import FigmaToHTML
converter = FigmaToHTML(client)
html = converter.frame_to_html(hero_section)
```

### Auto-Generate Components

```python
components = client.extract_components(file_data)

for comp in components:
    print(f"Component: {comp['name']}")
    # Generate React component
    # Generate Vue component
    # Generate HTML
```

---

## 🎉 סיכום

עכשיו יש לך:
- ✅ אינטגרציה מלאה עם Figma
- ✅ חילוץ צבעים וטיפוגרפיה
- ✅ יצירת Tailwind Config אוטומטית
- ✅ המרת עיצובים לקוד
- ✅ API endpoints מוכנים

**תהנה! 🚀**
