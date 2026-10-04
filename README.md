# SwaadAI — AI Food Recommendation Website

SwaadAI is a portfolio-ready India-first food recommendation demo. It explains how AI improves food discovery by combining a person's goal, diet, spice preference, available time, and budget instead of showing the same generic list to everyone.

## Architecture

- `frontend/` — responsive browser UI with recommendation cards, AI explanation, nutrition trade-offs, and an AI importance section.
- `ai-python/ai_service.py` — Python recommendation service. It uses an OpenAI-compatible API when `OPENAI_API_KEY` is set, and falls back to a transparent local demo recommender when it is not.
- `backend-java/FoodGateway.java` — Java 17+ HTTP gateway. It serves the frontend and forwards `/api/recommend` to Python, demonstrating Java backend integration.

No payment, account, or health diagnosis functionality is included. Food and nutrition notes are educational and should not replace professional medical advice.

## Run locally

1. Start the Python AI service:

   ```powershell
   cd ai-python
   python ai_service.py
   ```

   Optional real AI mode:

   ```powershell
   $env:OPENAI_API_KEY = "your-key-in-your-local-shell-only"
   $env:OPENAI_MODEL = "gpt-4o-mini"
   python ai_service.py
   ```

2. In another terminal, compile and start the Java gateway:

   ```powershell
   cd backend-java
   javac FoodGateway.java
   java FoodGateway ..\frontend
   ```

3. Open `http://localhost:8080`.

The Java gateway expects Python on `http://localhost:8000`. The browser can also use the UI's demo mode if the services are not running.

## Why AI matters here

Traditional food menus can filter by category, but AI can interpret intent and explain trade-offs: for example, it can prioritize high-protein vegetarian meals under a time limit, adapt to regional preferences, learn from feedback, and give a human-readable reason for each suggestion. The interface makes these benefits visible instead of hiding them behind a black box.

## Cuisine coverage and visual fallback

The preference form supports North Indian, South Indian, Chinese, Italian, Mexican, Thai, Japanese, Continental, and surprise-me recommendations. Recommendation cards use curated food photography when available and a built-in SVG illustration fallback when an image cannot load.

## Free Render deployment

The root `render.yaml` defines two free Docker web services: `swaadai-python` for recommendations and `swaadai-java` for the public website/gateway. To deploy, push this folder to a GitHub repository, create a Render Blueprint from that repository, and set `OPENAI_API_KEY` only in the Python service environment if live AI is desired. Keep the key out of GitHub and frontend files. Render free services sleep after inactivity, so the first request after a quiet period may be slower.

## Safety and privacy

- Demo data only; no live ordering or payment.
- The API key is read only from the local environment and is never placed in frontend code.
- The recommender does not provide medical diagnosis or treatment.
- The local fallback keeps the website useful for demos without any key.
