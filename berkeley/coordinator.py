# coordinator.py
import socket
from datetime import datetime, timedelta
from common import *

OFFSET = get_clock_offset()
client_times = {}
client_sockets = {}

def handle_client(conn):
    client_id = conn.recv(1024).decode()
    print(f"[COORDENADOR] Cliente conectado: {client_id}")
    client_sockets[client_id] = conn

def request_times():
    print(f"[COORDENADOR] Hora local: {datetime_to_str(current_time_with_offset(OFFSET))}")
    for client_id, conn in client_sockets.items():
        conn.sendall(b"get_time")
        client_time = str_to_datetime(conn.recv(1024).decode())
        client_times[client_id] = client_time
        print(f"[COORDENADOR] Recebido {client_id}: {datetime_to_str(client_time)}")

def calculate_adjustments():
    local_time = current_time_with_offset(OFFSET)
    all_times = [local_time] + list(client_times.values())
    epoch = datetime(1970, 1, 1)

    # Calcular a média dos segundos desde o Epoch
    total_seconds = sum([(t - epoch).total_seconds() for t in all_times])
    average_seconds = total_seconds / len(all_times)
    average_time = epoch + timedelta(seconds=average_seconds)

    print(f"[COORDENADOR] Média calculada: {datetime_to_str(average_time)}")

    # Enviar ajustes para os clientes
    for client_id, conn in client_sockets.items():
        diff = int((average_time - client_times[client_id]).total_seconds())
        conn.sendall(str(diff).encode())

    # Ajuste do coordenador (só imprime)
    own_adjust = int((average_time - local_time).total_seconds())
    final_time = local_time + timedelta(seconds=own_adjust)
    print(f"[COORDENADOR] Ajuste próprio: {own_adjust} segundos")
    print(f"[COORDENADOR] Hora ajustada: {datetime_to_str(final_time)}")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("localhost", PORT_BASE))
        s.listen()
        print("[COORDENADOR] Aguardando conexões...")

        while len(client_sockets) < NUM_CLIENTS:
            conn, _ = s.accept()
            handle_client(conn)

        print("[COORDENADOR] Todos os clientes conectados.")
        request_times()
        calculate_adjustments()

if __name__ == "__main__":
    start_server()
