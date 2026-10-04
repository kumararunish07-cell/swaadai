# SwaadAI free deployment plan

## Recommended platform

Use Render free web services with the root `render.yaml` Blueprint. It creates:

1. `swaadai-python` — Python recommendation and optional live-AI service.
2. `swaadai-java` — Java gateway and public frontend.

Render's free web services sleep after 15 minutes without inbound traffic, and the first request after sleep can take about a minute. The free allowance is 750 instance-hours per workspace per month; if the allowance is exhausted, free services are suspended until the next month.

## Before deployment

- Create or select a GitHub repository containing this project.
- Do not commit an OpenAI key, `.env` file, password, or token.
- Confirm the project is public if using the simplest free GitHub-to-Render workflow.

## Deploy

1. Open Render and choose **New > Blueprint**.
2. Connect the GitHub repository containing `render.yaml`.
3. Confirm that Render detects two services: `swaadai-python` and `swaadai-java`.
4. Keep both services on the **Free** plan.
5. Deploy the Blueprint.
6. Wait for both services to show **Live**.
7. Open the Java service URL. This is the public SwaadAI website.
8. Test the cuisine selector with Chinese, Italian, and South Indian.
9. Submit the form and confirm that the recommendation cards and AI reasoning panel render.

## Optional live AI mode

The website works without an API key using the local deterministic fallback. To enable live AI:

1. Open the `swaadai-python` service in Render.
2. Add `OPENAI_API_KEY` as a secret environment variable in the Render dashboard.
3. Keep `OPENAI_MODEL=gpt-4o-mini` or choose another compatible model.
4. Redeploy the Python service.
5. Submit a recommendation and confirm the badge changes to **Live AI mode**.

The hosting can remain within the free service limits, but model/API usage is a separate possible cost from the model provider. Never put the key in frontend JavaScript or GitHub.

## Cost and reliability notes

- Hosting: intended to remain free within Render's free limits.
- Cold starts: expected after idle sleep.
- Database: not needed for this demo.
- Images: the UI has curated photo URLs and a local SVG fallback so cards remain usable if an image cannot load.
- Payments: none.
- User accounts: none.
- Medical advice: none.

## Rollback

If a deployment fails, inspect the Render deploy log. The most common checks are:

- Python service health check: `/health`
- Python start command: `python ai_service.py`
- Java service must listen on Render's `$PORT`
- Java `PYTHON_RECOMMEND_URL` must end with `/recommend`
- `OPENAI_API_KEY` must be set only on the Python service for live mode
