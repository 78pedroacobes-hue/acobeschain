import http.server
import socketserver
import json
import os

PORT = 8080
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>ACOBESCHAIN VIVA</title></head>
            <body style="background-color: black; color: white; font-family: sans-serif; text-align: center;">
                <h1>ACOBESCHAIN VIVA</h1>
                <br>
                <a href="/musica" style="color: #8A2BE2; text-decoration: underline; font-size: 24px;">MUSICA</a>
                <br><br>
                <a href="/health" style="color: #8A2BE2; text-decoration: underline; font-size: 24px;">HEALTH</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        elif self.path == '/health' or self.path == '/he':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            data = {"cadena":"viva","musica_files":0,"status":"ok"}
            self.wfile.write(json.dumps(data).encode())
        elif self.path == '/musica':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
            <head><title>ACOBESCHAIN MUSICA</title></head>
            <body style="background-color: black; color: white; font-family: sans-serif; text-align: center;">
                <h1>MUSICA</h1>
                <p>Sección en construcción.</p>
                <br>
                <a href="/" style="color: #8A2BE2;">VOLVER</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Servidor corriendo en puerto {PORT}")
    httpd.serve_forever()
