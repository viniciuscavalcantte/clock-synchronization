# client.py
import socket
import threading
from common import *

CLIENT_ID = int(input("ID do cliente (1 a 4): "))
OFFSET = get_clock_offset()

def handle_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("localhost", PORT_BASE))
            s.sendall(f"client_{CLIENT_ID}".encode())

            current = current_time_with_offset(OFFSET)
            print(f"[CLIENT {CLIENT_ID}] Hora atual: {datetime_to_str(current)}")

            data = s.recv(1024)
            if not data:
                print(f"[CLIENT {CLIENT_ID}] Erro: nenhuma mensagem recebida.")
                return
            if data.decode() != "get_time":
                print(f"[CLIENT {CLIENT_ID}] Erro: mensagem inesperada.")
                return

            s.sendall(datetime_to_str(current).encode())

            # Espera o ajuste
            adjustment_data = s.recv(1024)
            if not adjustment_data:
                print(f"[CLIENT {CLIENT_ID}] Erro: nenhuma mensagem de ajuste recebida.")
                return
            adjustment_str = adjustment_data.decode()
            if not adjustment_str.strip().lstrip("-").isdigit():
                print(f"[CLIENT {CLIENT_ID}] Erro ao receber ajuste.")
                return

            adjustment = int(adjustment_str)
            print(f"[CLIENT {CLIENT_ID}] Ajuste recebido: {adjustment} segundos")

            final_time = current + timedelta(seconds=adjustment)
            print(f"[CLIENT {CLIENT_ID}] Hora ajustada: {datetime_to_str(final_time)}")

    except Exception as e:
        print(f"[CLIENT {CLIENT_ID}] Erro: {e}")

if __name__ == "__main__":
    threading.Thread(target=handle_server).start()
