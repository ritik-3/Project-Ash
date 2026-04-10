# Voice And Natural Language Design (Planning Spec)

## Purpose
Define how Project Ash should understand normal human language and voice commands in daily usage.

## Product Intent
The assistant should work when the user speaks naturally, including casual and mixed phrasing, and should answer in simple, useful language.

## Supported Input Styles
- Direct command style: Open Chrome and search for budget template.
- Conversational style: Can you quickly open my mail and draft a follow-up?
- Mixed-language style: Open sheet and add today ka expense 220.
- Imperfect grammar style: go browser and find best ai notes.

## Voice Interaction Goals
- Reliable wake and listen behavior.
- Fast speech-to-text for common commands.
- Clarification when speech is unclear.
- Natural spoken confirmations for risky actions.

## Step-By-Step Interaction Pipeline
1. Capture user voice input.
2. Run speech-to-text transcription.
3. Normalize text (handle filler words, casual grammar, mixed phrasing).
4. Detect intent, entities, and constraints.
5. Build task plan and risk classification.
6. Ask follow-up question if ambiguity remains.
7. Execute approved steps.
8. Return response in text and optional speech.
9. Log transcript, intent, plan, and result.

## Normal Language Understanding Rules
- Handle synonyms: open/start/launch.
- Handle indirect requests: Can you do this means execute task, not just explain.
- Handle pronouns from context: send it, open that, add this.
- Handle casual sequence words: then/after that/also.
- Handle mixed-language phrases for common productivity actions.

## Response Style Rules
- Keep responses concise and practical.
- Confirm understanding in one line before action.
- Explain current step while executing multi-step tasks.
- Ask short clarification questions when needed.
- Avoid over-technical wording unless user requests detail.

## Confirmation Voice Patterns
- Medium risk: single confirmation.
  - Example: I am about to edit your sheet. Should I continue?
- High risk: strict confirmation.
  - Example: This action may be irreversible. Please confirm yes to proceed.

## Error Handling For Voice
- If transcription confidence is low, ask user to repeat.
- If intent confidence is low, propose top 2 interpretations.
- If environment noise is high, suggest text input fallback.
- If action fails, explain reason and offer next best action.

## MVP Voice Scope
- Push-to-talk voice command input.
- Text response always available.
- Optional text-to-speech output toggle.
- Voice supported for P1 task set only.

## Post-MVP Voice Scope
- Always-on wake word mode.
- Speaker adaptation for better personalization.
- Faster streaming speech response.

## Acceptance Criteria
- Assistant can complete P1 tasks from voice input with at least 85 percent command understanding in controlled tests.
- Clarification is triggered for low-confidence voice commands.
- User can switch between voice and text in same session without losing context.
- Risk confirmations are clearly spoken and logged.
