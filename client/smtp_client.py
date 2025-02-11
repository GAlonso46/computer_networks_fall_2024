#!/usr/bin/env python3
import socket
import argparse
import json
import sys
import ast

class SMTPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, self.port))
            response = self._receive()
            return response
        except Exception as e:
            raise Exception(f"Error al conectar con el servidor SMTP: {e}")

    def _send(self, message):
        # Agregamos CRLF al final de cada comando
        full_message = message + "\r\n"
        self.sock.sendall(full_message.encode('utf-8'))

    def _receive(self):
        # Recibimos hasta 1024 bytes (puedes ajustar el buffer según tus necesidades)
        data = self.sock.recv(1024)
        return data.decode('utf-8').strip()

    def send_command(self, command):
        # Envía un comando y retorna la respuesta
        self._send(command)
        response = self._receive()
        return response

    def send_email(self, from_mail, to_mail_list, subject, body, header_dict):
        responses = []

        # 1. Identificarse con HELO o EHLO
        responses.append(self.send_command("HELO localhost"))

        # 2. Especificar el remitente
        responses.append(self.send_command(f"MAIL FROM:<{from_mail}>"))

        # 3. Especificar cada destinatario
        for recipient in to_mail_list:
            responses.append(self.send_command(f"RCPT TO:<{recipient}>"))

        # 4. Iniciar la sección DATA
        responses.append(self.send_command("DATA"))
        # El servidor debe responder con un código 354 para indicar que envíe los datos

        # 5. Preparar el contenido del mensaje (cabeceras y cuerpo)
        email_message = f"Subject: {subject}\r\n"
        # Agregar headers adicionales si existen
        for key, value in header_dict.items():
            email_message += f"{key}: {value}\r\n"
        email_message += "\r\n"  # Separador entre cabeceras y cuerpo
        email_message += f"{body}\r\n"
        email_message += "."  # Indica el final del mensaje según SMTP

        responses.append(self.send_command(email_message))

        # 6. Cerrar la sesión
        responses.append(self.send_command("QUIT"))
        return responses

    def close(self):
        if self.sock:
            self.sock.close()

def main():
    parser = argparse.ArgumentParser(description="Cliente SMTP en Python")
    parser.add_argument("-p", "--port", type=int, required=True, help="Puerto del servidor SMTP (ej. 25)")
    parser.add_argument("-u", "--host", required=True, help="Host del servidor SMTP (ej. 127.0.0.1)")
    parser.add_argument("-f", "--from_mail", required=True, help="Correo del remitente (ej. user1@uh.cu)")
    parser.add_argument("-t", "--to_mail", required=True,
                        help='Lista de correos de destino en formato string (ej. \'["user2@uh.cu", "user3@uh.cu"]\')')
    parser.add_argument("-s", "--subject", required=True, help="Asunto del correo")
    parser.add_argument("-b", "--body", required=True, help="Cuerpo del correo")
    parser.add_argument("-H", "--header", default="{}", help='Headers adicionales en formato JSON (ej. \'{"CC": "cc@example.com"}\')')

    args = parser.parse_args()

    # Parsear la lista de destinatarios y los headers
    try:
        to_mail_list = ast.literal_eval(args.to_mail)
        if not isinstance(to_mail_list, list):
            raise ValueError("El argumento to_mail debe ser una lista.")
    except Exception as e:
        print(json.dumps({"status_code": 500, "message": f"Error al parsear to_mail: {e}"}))
        sys.exit(1)

    try:
        header_dict = json.loads(args.header)
    except Exception as e:
        print(json.dumps({"status_code": 500, "message": f"Error al parsear header: {e}"}))
        sys.exit(1)

    client = SMTPClient(args.host, args.port)

    try:
        # Conectar al servidor SMTP y obtener la respuesta inicial
        initial_response = client.connect()
        # Enviar el correo y recolectar las respuestas de cada comando
        responses = client.send_email(args.from_mail, to_mail_list, args.subject, args.body, header_dict)
        client.close()
        # Combinar todas las respuestas en un solo mensaje (se puede ajustar el formato según se requiera)
        server_output = initial_response + "\n" + "\n".join(responses)
        # Salida en formato JSON con el código de estado esperado
        result = {"status_code": 333, "message": server_output}
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"status_code": 500, "message": f"Error en la ejecución: {e}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
