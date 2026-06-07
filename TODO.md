- [ ] Inspect current CHATBOT.py AI integration paths.
- [ ] Add Gemini direct connection using google-generativeai (read-only prompt constraints maintained: electronics-only + safety warnings).
- [ ] Keep existing email login unchanged.
- [ ] Update backend endpoint /api/chat to call Gemini and return Gemini output.
- [ ] Keep fallback to local electronics_answer if Gemini fails.
- [ ] Update .env.example with GEMINI_API_KEY and GEMINI_MODEL (if needed).
- [ ] Test: run server, login, submit an electronics question; verify response is Gemini text.

