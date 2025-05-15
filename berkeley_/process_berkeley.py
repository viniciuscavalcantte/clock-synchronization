import socket
import threading
import time
import random
import json 

from clock_simulation import SimulatedClock

PROCESS_ID = None
IS_COORDINATOR = False
COORDINATOR_HOST = 'localhost'
COORDINATOR_PORT_BASE = 12340 
PROCESS_PORTS = {} 
CLIENT_IDS = [] 

local_clock = None

def initialize_process(pid, is_coord, all_pids):
    global PROCESS_ID, IS_COORDINATOR, local_clock, CLIENT_IDS, PROCESS_PORTS
    PROCESS_ID = pid
    IS_COORDINATOR = is_coord

    for i, p_id in enumerate(all_pids):
        PROCESS_PORTS[p_id] = COORDINATOR_PORT_BASE + i + 1 

    CLIENT_IDS = [p for p in all_pids if p != PROCESS_ID] if IS_COORDINATOR else []

    offset = random.randint(-10, 10)
    local_clock = SimulatedClock(offset)
    print(f"Process {PROCESS_ID} (Coordinator: {IS_COORDINATOR}) initialized. Initial clock offset: {offset}s, Time: {local_clock.get_formatted_time()}")

    if IS_COORDINATOR:
        # O coordenador não precisa de um listener de cliente, ele inicia a comunicação
        # Mas precisa de um meio para os clientes enviarem seus tempos.
        # Para simplificar, o coordenador fará conexões de saída para os clientes.
        pass
    else: 
        threading.Thread(target=client_listener, daemon=True).start()


def client_listener():
    host = 'localhost'
    port = PROCESS_PORTS[PROCESS_ID]
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Client {PROCESS_ID} listening on {host}:{port}")
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    data_bytes = conn.recv(1024)
                    if not data_bytes:
                        continue
                    message = json.loads(data_bytes.decode())
                    
                    print(f"Client {PROCESS_ID} received: {message} from {addr}")

                    if message.get("command") == "GET_TIME":
                        response = {"pid": PROCESS_ID, "time": local_clock.get_time()}
                        conn.sendall(json.dumps(response).encode())
                    elif message.get("command") == "ADJUST_TIME":
                        adjustment = message.get("adjustment")
                        print(f"Process {PROCESS_ID} - Time BEFORE adjustment: {local_clock.get_formatted_time()} ({local_clock.get_time()})")
                        local_clock.adjust_time(adjustment)
                        print(f"Process {PROCESS_ID} - Time AFTER adjustment: {local_clock.get_formatted_time()} ({local_clock.get_time()})")
            except Exception as e:
                print(f"Client {PROCESS_ID} listener error: {e}")
                time.sleep(1) # Evita busy-loop em caso de erro persistente


def send_message_to_client(client_pid, message):
    client_host = 'localhost'
    client_port = PROCESS_PORTS[client_pid]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((client_host, client_port))
            s.sendall(json.dumps(message).encode())
            if message.get("command") == "GET_TIME":
                response_bytes = s.recv(1024)
                if response_bytes:
                    return json.loads(response_bytes.decode())
    except ConnectionRefusedError:
        print(f"Coordinator: Could not connect to client {client_pid} on {client_host}:{client_port}")
    except Exception as e:
        print(f"Coordinator error sending to {client_pid}: {e}")
    return None


def coordinator_synchronize():
    if not IS_COORDINATOR:
        return

    print("\n--- Coordinator starting synchronization ---")
    
    client_times = {}
    threads = []
    
    print("Coordinator: Requesting time from clients...")
    for client_pid in CLIENT_IDS:
        thread = threading.Thread(target=lambda p: client_times.update({p: send_message_to_client(p, {"command": "GET_TIME"})}), args=(client_pid,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join() 

    
    coordinator_current_time = local_clock.get_time()
    print(f"Coordinator (PID {PROCESS_ID}) - Time BEFORE adjustment: {local_clock.get_formatted_time()} ({coordinator_current_time})")
    
    all_times = [coordinator_current_time] 

    valid_client_responses = 0
    for pid, response in client_times.items():
        if response and "time" in response:
            all_times.append(response["time"])
            valid_client_responses +=1
            print(f"Coordinator: Received time {response['time']} from client {pid}")
        else:
            print(f"Coordinator: No valid time response from client {pid}")
            
    if not all_times or len(all_times) < (len(CLIENT_IDS) * 0.5): 
        print("Coordinator: Not enough time responses to calculate average. Aborting sync.")
        return

    average_time = sum(all_times) / len(all_times)
    print(f"Coordinator: Calculated average time: {average_time}")

   
    coord_adjustment = int(round(average_time - coordinator_current_time))
    local_clock.adjust_time(coord_adjustment)
    print(f"Coordinator (PID {PROCESS_ID}) - Time AFTER adjustment: {local_clock.get_formatted_time()} ({local_clock.get_time()})")

    threads_adjust = []
    for client_pid, response_data in client_times.items():
        if response_data and "time" in response_data:
            client_original_time = response_data["time"]
            adjustment = int(round(average_time - client_original_time))
            print(f"Coordinator: Sending adjustment {adjustment}s to client {client_pid}")
            msg = {"command": "ADJUST_TIME", "adjustment": adjustment}
            thread = threading.Thread(target=send_message_to_client, args=(client_pid, msg))
            threads_adjust.append(thread)
            thread.start()
            
    for thread in threads_adjust:
        thread.join()
        
    print("--- Coordinator synchronization finished ---")


if __name__ == "__main__":
    num_processes = 5 
    all_pids_list = [f"P{i}" for i in range(num_processes)]
    
    # Determina o ID e se é coordenador a partir de um argumento de linha de comando
    # Ex: python process_berkeley.py P0 coordinator
    #     python process_berkeley.py P1 client
    import sys
    if len(sys.argv) < 3:
        print("Usage: python process_berkeley.py <PROCESS_ID> <client|coordinator>")
        print("Example: python process_berkeley.py P0 coordinator")
        sys.exit(1)

    current_pid = sys.argv[1]
    role = sys.argv[2].lower()

    if current_pid not in all_pids_list:
        print(f"Error: Process ID {current_pid} is not in the defined list: {all_pids_list}")
        sys.exit(1)

    is_coordinator_role = (role == "coordinator")
    
    initialize_process(current_pid, is_coordinator_role, all_pids_list)

    if is_coordinator_role:
        print("Coordinator waiting for clients to start...")
        time.sleep(5) 
        coordinator_synchronize()
        
        print("Coordinator finished. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("Coordinator shutting down.")
    else:
        print(f"Client {PROCESS_ID} running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"Client {PROCESS_ID} shutting down.")
    
    if local_clock:
        local_clock.stop()