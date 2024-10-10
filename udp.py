import socket
import threading
import argparse
import time
from bcc import BPF

# Global variable to control the interval for sending periodic messages
report_send_interval = 5
# Set to keep track of connected clients
clients = set()

articipating_machines = ['','']

def get_local_ip():
    """
    Get the local IP address of the machine.

    This function creates a UDP socket and connects to a public DNS server (8.8.8.8) to determine the local IP address.
    It does not actually send any data to the DNS server; the connection is used solely to determine the local IP address.
    If an error occurs, it returns the loopback address "127.0.0.1".
    """
    try:
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS server to determine the local IP address
        sock.connect(("8.8.8.8", 80))
        # Get the local IP address from the socket
        ip = sock.getsockname()[0]
        # Close the socket
        sock.close()
        return ip
    except Exception as e:
        # Print the error and return the loopback address if an exception occurs
        print(f"Error trying to get local IP: {e}")
        return "127.0.0.1"

def is_server_running(server_ip, port):
    """
    Check if the server is already running by sending a ping message.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(b'ping', (server_ip, port))
        sock.settimeout(2)
        data, address = sock.recvfrom(1024)
        if data:
            print(f"The server is already running at {server_ip}:{port}")
            return True
    except Exception as e:
        print(f"Server not found. Error: {e}")
        return False
    finally:
        sock.close()

def server(server_ip, port):
    """
    Start the UDP server to listen for incoming messages.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, port))
    print(f"UDP server is waiting for messages at {server_ip}:{port}...")

    while True:
        data, address = sock.recvfrom(1024)
        response = data.decode()
        response = f"{address} Sent: \n {response}"
        if address not in clients:
            clients.add(address)
        for client in clients:
            sock.sendto(response.encode(), client)

def receive_messages(sock):
    """
    Function to receive messages from the server.
    Updates the report_send_interval if an integer is received.
    """
    global report_send_interval
    while True:
        data, address = sock.recvfrom(1024)
        data = data.decode()

        try:
            metrics = process_metrics(data)
            print(f"{metrics}")
        except ValueError:
            print(f"Error processing metric: {data}")

def process_metrics(data):
    if "CPU Usage" in data or "Context Switches" in data:
        return f"Received: {data}\n"
    return "Unknown metric"

def send_periodic_message(sock, server_ip, port):
    global report_send_interval
    while True:
        time.sleep(report_send_interval)
        cpu_usage, num_processes, context_switches = collect_metrics()
        message = f"CPU Usage: {cpu_usage:.2f}%, Processes: {num_processes}, Context Switches: {context_switches}"
        sock.sendto(message.encode(), (server_ip, port))

def client(server_ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receive_thread = threading.Thread(target=receive_messages, args=(sock,))
    receive_thread.daemon = True
    receive_thread.start()

    periodic_thread = threading.Thread(target=send_periodic_message, args=(sock, server_ip, port))
    periodic_thread.daemon = True
    periodic_thread.start()

    while True:
        message = input("")
        sock.sendto(message.encode(), (server_ip, port))

def start_server_with_check(server_ip, port):
    if not is_server_running(server_ip, port):
        server_thread = threading.Thread(target=server, args=(server_ip, port))
        server_thread.daemon = True
        server_thread.start()
        print("Server started.")
    else:
        print("The server is already running, it will not be started again.")

def collect_metrics():
    # Define BPF program for CPU usage and context switch collection
    bpf_program = """
    BPF_HASH(start, u32);
    BPF_HASH(total, u32);
    BPF_HASH(context_switches, u64);  // Changed to u64 to avoid overflow

    TRACEPOINT_PROBE(sched, sched_switch) {
        u32 pid = bpf_get_current_pid_tgid();
        u64 ts = bpf_ktime_get_ns();

        // Increment context switch count
        u64 zero = 0;
        u64 *cs = context_switches.lookup_or_init(&zero, &zero);  // Use u64 here
        (*cs)++;

        // Calculate CPU usage
        u64 *tsp = start.lookup(&pid);
        if (tsp) {
            u64 delta = ts - *tsp;
            u64 *total_time = total.lookup_or_init(&pid, &delta);
            *total_time += delta;
        }
        
        start.update(&pid, &ts);
        return 0;
    }
    """

    # Load eBPF program
    b = BPF(text=bpf_program)

    while True:
        try:
            total_cpu_usage = 0
            process_count = 0
            context_switches = 0

            # Process CPU usage
            for pid, val in b["total"].items():
                cpu_usage = val.value / (5 * 1e9) * 100
                total_cpu_usage += cpu_usage
                process_count += 1

            # Process context switches
            for _, val in b["context_switches"].items():
                context_switches = val.value

            # Calculate average CPU usage
            if process_count > 0:
                average_cpu_usage = total_cpu_usage / process_count
            else:
                average_cpu_usage = 0

            # Clear BPF maps for next cycle
            b["total"].clear()
            b["context_switches"].clear()

            return average_cpu_usage, process_count, context_switches
        except KeyboardInterrupt:
            break

def main(args):
    server_ip = args.ip if args.ip else get_local_ip()
    port = args.port

    start_server_with_check(server_ip, port)

    client_thread = threading.Thread(target=client, args=(server_ip, port))
    client_thread.daemon = True
    client_thread.start()
    client_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP server and client")
    parser.add_argument('--ip', type=str, help='Server IP')
    parser.add_argument('--port', type=int, default=5005, help='Server port')
    args = parser.parse_args()

    main(args)