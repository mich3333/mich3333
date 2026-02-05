#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGPT Brain - חיבור המערכת ל-OpenAI
המערכת האוטונומית עם ChatGPT כמוח המקבל החלטות
"""
import os
import json
from typing import List, Dict, Optional
from memory import short_term, long_term
from logging_config import setup_logging

# Initialize logger
logger = setup_logging('chatgpt_brain')

# Check if openai is installed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️  OpenAI not installed. Install with: pip install openai")


class ChatGPTBrain:
    """
    ChatGPT כמוח המערכת האוטונומית.
    משתמש ב-OpenAI API לקבלת החלטות חכמות.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        אתחול ChatGPT Brain.

        Args:
            api_key: OpenAI API key (או מ-OPENAI_API_KEY env var)
            model: GPT model to use (gpt-3.5-turbo, gpt-4, etc.)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed")

        # Get API key
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter"
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history = []

        print(f"✅ ChatGPT Brain initialized (model: {model})")

    def think(self, situation: str, context: Dict = None) -> str:
        """
        חושב על מצב נתון ומחליט מה לעשות.

        Args:
            situation: תיאור המצב הנוכחי
            context: הקשר נוסף (זיכרונות, מטרות וכו')

        Returns:
            החלטה של ChatGPT
        """
        # Build prompt with context
        prompt = self._build_prompt(situation, context)

        # Record thought process
        short_term.add('thought', f'שואל את ChatGPT: {situation[:50]}...')

        try:
            # Call ChatGPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            decision = response.choices[0].message.content
            short_term.add('observation', f'ChatGPT החליט: {decision[:50]}...')

            return decision

        except Exception as e:
            error_msg = f"ChatGPT error: {str(e)}"
            short_term.add('observation', error_msg)
            return f"Error: {error_msg}"

    def analyze_and_decide(self, goal: str, observations: List[str]) -> Dict:
        """
        מנתח מצב ומחליט על פעולה הבאה.

        Args:
            goal: המטרה הנוכחית
            observations: תצפיות אחרונות

        Returns:
            החלטה מובנית: {action, reasoning, priority}
        """
        # Build context
        context_text = f"""
מטרה נוכחית: {goal}

תצפיות אחרונות:
{chr(10).join(f"- {obs}" for obs in observations[-5:])}

מה הפעולה הבאה שכדאי לבצע?
ענה בפורמט JSON:
{{
    "action": "תיאור הפעולה",
    "reasoning": "הסבר למה",
    "priority": "high/medium/low"
}}
"""

        response = self.think(context_text)

        # Try to parse JSON with robust error handling
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Try to extract JSON from response if embedded in text
            import re
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            # Log warning about JSON parsing failure
            logger.warning(f"ChatGPT did not return valid JSON. Error: {e}")
            logger.debug(f"Response: {response[:200]}...")

            # Fallback with original response
            return {
                "action": response[:500],  # Limit length
                "reasoning": "Failed to parse JSON response",
                "priority": "medium",
                "parse_error": True
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing ChatGPT response: {e}", exc_info=True)
            return {
                "action": "Error occurred",
                "reasoning": f"Unexpected error: {str(e)}",
                "priority": "low",
                "parse_error": True
            }

    def ask_for_help(self, question: str, context: str = "") -> str:
        """
        שואל את ChatGPT לעזרה.

        Args:
            question: השאלה
            context: הקשר נוסף

        Returns:
            תשובת ChatGPT
        """
        full_question = f"{context}\n\n{question}" if context else question
        return self.think(full_question)

    def learn_from_experience(self, experience: str, outcome: str) -> str:
        """
        לומד מניסיון ומייצר לקח.

        Args:
            experience: מה ניסינו לעשות
            outcome: מה קרה

        Returns:
            לקח שנלמד
        """
        prompt = f"""
ניסיון: {experience}
תוצאה: {outcome}

מה הלקח שאפשר ללמוד מזה? (תשובה קצרה)
"""
        lesson = self.think(prompt)

        # Store in long-term memory if available
        if long_term.qdrant_available:
            long_term.add(
                content=lesson,
                memory_type="lesson",
                tags=["chatgpt", "learned", "experience"],
                importance=7
            )

        return lesson

    def _build_prompt(self, situation: str, context: Dict = None) -> str:
        """בונה prompt עם הקשר."""
        if not context:
            return situation

        prompt_parts = [situation, ""]

        if context.get('memories'):
            prompt_parts.append("זיכרונות רלוונטיים:")
            for m in context['memories'][-3:]:
                prompt_parts.append(f"- [{m['type']}] {m['content']}")
            prompt_parts.append("")

        if context.get('goal'):
            prompt_parts.append(f"מטרה נוכחית: {context['goal']}")

        return "\n".join(prompt_parts)

    def _get_system_prompt(self) -> str:
        """System prompt שמגדיר את התפקיד של ChatGPT."""
        return """אתה המוח של מערכת AI אוטונומית בשם Autonomous Claude.

התפקיד שלך:
- לקבל החלטות חכמות על סמך המידע שניתן לך
- לנתח מצבים ולהציע פעולות
- להיות תמציתי ומעשי
- לתת החלטות ברורות וניתנות לביצוע

עקרונות:
- תחשוב לוגית ושיטתי
- שקול סיכונים ויתרונות
- תן עדיפות למטרות שהוגדרו
- למד מטעויות

ענה בעברית בצורה קצרה ומעשית."""


class AutonomousAgentWithChatGPT:
    """
    סוכן אוטונומי עם ChatGPT כמוח.
    משלב את כל המערכות: זיכרון, decision loop, ChatGPT.
    """

    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.brain = ChatGPTBrain(api_key=api_key, model=model)
        self.current_goal = None
        self.iteration = 0

    def set_goal(self, goal: str):
        """הגדר מטרה חדשה."""
        self.current_goal = goal
        short_term.add('goal', goal)
        print(f"🎯 מטרה חדשה: {goal}")

    def run_cycle(self):
        """הרץ מחזור החלטה אחד."""
        self.iteration += 1

        print(f"\n{'='*70}")
        print(f"🤖 מחזור #{self.iteration} - ChatGPT Brain")
        print(f"{'='*70}\n")

        # 1. Read context
        print("1️⃣  קורא זיכרונות...")
        recent = short_term.get_recent(20)
        observations = [m['content'] for m in recent if m['type'] == 'observation']
        print(f"   מצאתי {len(observations)} תצפיות אחרונות\n")

        # 2. Ask ChatGPT to decide
        print("2️⃣  שואל את ChatGPT מה לעשות...")
        if not self.current_goal:
            self.current_goal = "לחקור ולהבין את הסביבה"

        decision = self.brain.analyze_and_decide(self.current_goal, observations)

        print(f"   💡 החלטה: {decision.get('action', 'N/A')}")
        print(f"   🤔 נימוק: {decision.get('reasoning', 'N/A')}")
        print(f"   ⚡ עדיפות: {decision.get('priority', 'N/A')}\n")

        # 3. Record the decision
        print("3️⃣  מתעד החלטה...")
        short_term.add('thought', f"ChatGPT החליט: {decision['action']}")
        short_term.add('action', f"מבצע: {decision['action']}")

        # 4. Simulate execution (in real use, actually do the action)
        print("4️⃣  מבצע פעולה...")
        result = f"ביצעתי: {decision['action']}"
        short_term.add('observation', result)
        print(f"   ✅ {result}\n")

        # 5. Learn
        if self.iteration % 3 == 0:  # Learn every 3 iterations
            print("5️⃣  לומד מניסיון...")
            lesson = self.brain.learn_from_experience(
                decision['action'],
                result
            )
            print(f"   📚 לקח: {lesson}\n")

        print(f"{'='*70}")
        print(f"✅ מחזור #{self.iteration} הושלם")
        print(f"{'='*70}\n")

    def run(self, cycles: int = 3):
        """הרץ כמה מחזורים."""
        print("\n🚀 מתחיל הרצה אוטונומית עם ChatGPT Brain\n")

        for i in range(cycles):
            self.run_cycle()

            if i < cycles - 1:
                import time
                time.sleep(1)

        print("\n🏁 הרצה הושלמה!")
        print(f"📊 סה\"כ מחזורים: {self.iteration}")


def demo():
    """הדגמה של ChatGPT Brain."""
    print("="*70)
    print("🤖 ChatGPT Brain Demo")
    print("="*70)
    print()

    # Check if API key exists
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY לא נמצא!")
        print()
        print("💡 הגדר את ה-API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print()
        print("או:")
        print("   brain = ChatGPTBrain(api_key='your-key-here')")
        print()
        return

    try:
        # Create agent
        agent = AutonomousAgentWithChatGPT(model="gpt-3.5-turbo")

        # Set a goal
        agent.set_goal("לחקור GitHub API ולמצוא repositories מעניינים")

        # Run
        agent.run(cycles=2)

    except Exception as e:
        print(f"❌ שגיאה: {e}")
        print()
        print("💡 וודא שה-API key תקין וש-openai מותקן:")
        print("   pip install openai")


if __name__ == "__main__":
    demo()
