"""SwaadAI Python service: live OpenAI-compatible mode plus transparent local fallback."""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, os, urllib.request

PORT = int(os.getenv("PORT", os.getenv("PYTHON_PORT", "8000")))
API_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

MEALS = [
    {"name":"Masala Moong Bowl","cuisine":"north-indian","description":"A protein-forward bowl with sprouted moong, vegetables, and a bright lemon tadka.","tags":["High protein","20 min","Vegetarian"]},
    {"name":"Paneer Millet Wrap","cuisine":"north-indian","description":"Warm millet roti with spiced paneer, crunchy salad, and mint chutney.","tags":["Filling","30 min","Vegetarian"]},
    {"name":"Lemon Poha","cuisine":"south-indian","description":"Light flattened rice with peanuts, curry leaves, vegetables, and fresh lemon.","tags":["Light","15 min","Budget-friendly"]},
    {"name":"Masala Dosa","cuisine":"south-indian","description":"Crisp dosa with warm potato masala, coconut chutney, and sambar.","tags":["Classic","30 min","Vegetarian"]},
    {"name":"Rajma Rice Bowl","cuisine":"north-indian","description":"Slow-simmered rajma with rice, onion, coriander, and a cooling side salad.","tags":["Comfort","Budget-friendly","Vegetarian"]},
    {"name":"Chana Chaat","cuisine":"north-indian","description":"Chickpeas, tomato, cucumber, pomegranate, and chaat masala with citrus brightness.","tags":["Fresh","Protein","Vegan"]},
    {"name":"Veg Hakka Noodles","cuisine":"chinese","description":"Wok-tossed noodles with crunchy vegetables, ginger, garlic, and a savory soy glaze.","tags":["Wok-tossed","25 min","Vegetarian"]},
    {"name":"Chilli Paneer Bowl","cuisine":"chinese","description":"Crispy paneer, peppers, spring onion, and a glossy sweet-spicy sauce over rice.","tags":["Bold","30 min","Vegetarian"]},
    {"name":"Margherita Pasta","cuisine":"italian","description":"Silky tomato pasta with basil, olive oil, and a gentle parmesan finish.","tags":["Comfort","25 min","Vegetarian"]},
    {"name":"Pesto Veggie Penne","cuisine":"italian","description":"Penne with basil pesto, roasted vegetables, cherry tomatoes, and toasted seeds.","tags":["Fresh","30 min","Vegetarian"]},
    {"name":"Thai Green Curry","cuisine":"thai","description":"Aromatic coconut curry with vegetables, basil, lime, and steamed rice.","tags":["Aromatic","35 min","Vegan"]},
    {"name":"Veg Sushi Platter","cuisine":"japanese","description":"Fresh avocado, cucumber, carrot, and sesame rolls with a light soy dip.","tags":["Fresh","40 min","Vegan"]},
    {"name":"Mexican Bean Tacos","cuisine":"mexican","description":"Soft tacos filled with smoky beans, corn salsa, avocado, and lime.","tags":["High fiber","25 min","Vegan"]},
    {"name":"Garden Grain Salad","cuisine":"continental","description":"Roasted vegetables, grains, greens, and a bright herb-lemon dressing.","tags":["Light","20 min","Vegetarian"]}
]

def local_recommendation(p):
    goal, diet, flavor = p.get("goal","energy"), p.get("diet","vegetarian"), p.get("flavor","homestyle")
    cuisine = p.get("cuisine", "any")
    selected = [m for m in MEALS if cuisine == "any" or m["cuisine"] == cuisine]
    if not selected: selected = MEALS[:]
    if diet == "vegan": selected = [m for m in selected if "Vegan" in m["tags"] or m["cuisine"] in ["chinese","thai","japanese","mexican","continental"]]
    elif diet == "eggetarian": selected = [m for m in selected if "Vegetarian" in m["tags"] or "Vegan" in m["tags"]]
    if goal == "protein": selected = sorted(selected, key=lambda m: ("Protein" not in m["tags"], "High protein" not in m["tags"]))
    elif goal == "light": selected = sorted(selected, key=lambda m: ("Light" not in m["tags"], "Fresh" not in m["tags"]))
    elif goal == "comfort": selected = sorted(selected, key=lambda m: ("Comfort" not in m["tags"], "Filling" not in m["tags"]))
    cuisine_name = cuisine.replace("-", " ").title() if cuisine != "any" else "any cuisine"
    return {"mode":"local-demo","summary":f"A {cuisine_name} shortlist shaped around your moment, not a generic menu.","explanation":f"Because you want {goal.replace('-', ' ')}, prefer {diet} food, and selected {cuisine_name}, the recommender balances fit, preparation time, and everyday practicality. This local fallback is deterministic and uses no private data.","reasons":[goal.replace('-', ' ').title(), diet.title(), cuisine_name, f"{p.get('time','30')} min limit"],"recommendations":selected[:3]}

def live_recommendation(p):
    system = "You are SwaadAI, an explainable food recommendation assistant covering Indian, Chinese, Italian, Mexican, Thai, Japanese, and Continental cuisines. Return only valid JSON with keys mode, summary, explanation, reasons, recommendations. Each recommendation must have name, cuisine, description, tags. Return exactly 3. Avoid medical claims. Keep descriptions concise."
    prompt = "Recommend meals for these preferences: " + json.dumps(p, ensure_ascii=False)
    body = json.dumps({"model":MODEL,"temperature":0.6,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":system},{"role":"user","content":prompt}]}).encode()
    req = urllib.request.Request(API_URL, data=body, headers={"Content-Type":"application/json","Authorization":"Bearer " + os.environ["OPENAI_API_KEY"]}, method="POST")
    with urllib.request.urlopen(req, timeout=25) as response:
        content = json.loads(response.read().decode())["choices"][0]["message"]["content"]
    result = json.loads(content); result["mode"] = "real-ai"; return result

class Handler(BaseHTTPRequestHandler):
    def _send(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Access-Control-Allow-Origin", "*"); self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_OPTIONS(self): self.send_response(204); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    def do_GET(self):
        if self.path == "/health": self._send({"status":"ok","mode":"real-ai" if os.getenv("OPENAI_API_KEY") else "local-demo"})
        else: self._send({"error":"not found"},404)
    def do_POST(self):
        if self.path != "/recommend": self._send({"error":"not found"},404); return
        try:
            length = int(self.headers.get("Content-Length", 0)); prefs = json.loads(self.rfile.read(length) or b"{}")
            result = live_recommendation(prefs) if os.getenv("OPENAI_API_KEY") else local_recommendation(prefs); self._send(result)
        except Exception as exc:
            print("AI fallback:", exc); self._send(local_recommendation(prefs if 'prefs' in locals() else {}))
    def log_message(self, fmt, *args): print("[python]", fmt % args)

if __name__ == "__main__":
    print(f"SwaadAI Python service on 0.0.0.0:{PORT} | mode={'real-ai' if os.getenv('OPENAI_API_KEY') else 'local-demo'}")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
