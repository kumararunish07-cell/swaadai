import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.concurrent.Executors;

/** Minimal Java 17+ gateway: static files plus a proxy to the Python AI service. */
public class FoodGateway {
  private static final int PORT = 8080;
  private static final String PYTHON_URL = "http://localhost:8000/recommend";
  private static Path frontend;

  public static void main(String[] args) throws Exception {
    frontend = Paths.get(args.length > 0 ? args[0] : "../frontend").toAbsolutePath().normalize();
    HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", PORT), 0);
    server.createContext("/api/recommend", FoodGateway::recommend);
    server.createContext("/", FoodGateway::staticFile);
    server.setExecutor(Executors.newCachedThreadPool());
    server.start();
    System.out.println("SwaadAI Java gateway on http://localhost:" + PORT);
  }

  private static void recommend(HttpExchange exchange) throws IOException {
    if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) { send(exchange, 405, "{\"error\":\"POST required\"}", "application/json"); return; }
    byte[] requestBody = exchange.getRequestBody().readAllBytes();
    try {
      HttpURLConnection connection = (HttpURLConnection) new URL(PYTHON_URL).openConnection();
      connection.setRequestMethod("POST"); connection.setDoOutput(true); connection.setRequestProperty("Content-Type", "application/json");
      try (OutputStream out = connection.getOutputStream()) { out.write(requestBody); }
      int status = connection.getResponseCode(); InputStream stream = status >= 400 ? connection.getErrorStream() : connection.getInputStream();
      String response = new String(stream.readAllBytes(), StandardCharsets.UTF_8); send(exchange, status, response, "application/json; charset=utf-8");
    } catch (IOException error) {
      String message = "{\"error\":\"Python AI service is offline. Start ai_service.py first.\"}";
      send(exchange, 503, message, "application/json");
    }
  }

  private static void staticFile(HttpExchange exchange) throws IOException {
    String requestPath = URLDecoder.decode(exchange.getRequestURI().getPath(), StandardCharsets.UTF_8);
    if (requestPath.equals("/")) requestPath = "/index.html";
    Path file = frontend.resolve(requestPath.substring(1)).normalize();
    if (!file.startsWith(frontend) || !Files.exists(file) || Files.isDirectory(file)) { send(exchange, 404, "Not found", "text/plain"); return; }
    String type = Files.probeContentType(file); if (type == null) type = "application/octet-stream";
    byte[] content = Files.readAllBytes(file); exchange.getResponseHeaders().set("Content-Type", type + (type.startsWith("text/") ? "; charset=utf-8" : "")); exchange.sendResponseHeaders(200, content.length); try (OutputStream out = exchange.getResponseBody()) { out.write(content); }
  }

  private static void send(HttpExchange exchange, int status, String body, String contentType) throws IOException { byte[] data = body.getBytes(StandardCharsets.UTF_8); exchange.getResponseHeaders().set("Content-Type", contentType); exchange.getResponseHeaders().set("Access-Control-Allow-Origin", "*"); exchange.sendResponseHeaders(status, data.length); try (OutputStream out = exchange.getResponseBody()) { out.write(data); } }
}
