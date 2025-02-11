#!/usr/bin/env python3
import socketserver

class SMTPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"220 Servidor SMTP de ejemplo\r\n")
        while True:
            line = self.rfile.readline().decode('utf-8').strip()
            if not line:
                break
            print("Cliente:", line)
            if line.upper().startswith("HELO") or line.upper().startswith("EHLO"):
                self.wfile.write(b"250 Hola\r\n")
            elif line.upper().startswith("MAIL FROM:"):
                self.wfile.write(b"250 OK\r\n")
            elif line.upper().startswith("RCPT TO:"):
                self.wfile.write(b"250 OK\r\n")
            elif line.upper().startswith("DATA"):
                self.wfile.write(b"354 End data with <CRLF>.<CRLF>\r\n")
            elif line == ".":
                self.wfile.write(b"250 OK, mensaje recibido\r\n")
            elif line.upper().startswith("QUIT"):
                self.wfile.write(b"221 Adios\r\n")
                break
            else:
                self.wfile.write(b"500 Comando no reconocido\r\n")

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 2525  # Puedes ajustar el puerto para pruebas
    with socketserver.TCPServer((HOST, PORT), SMTPHandler) as server:
        print(f"Servidor SMTP corriendo en {HOST}:{PORT}")
        server.serve_forever()
