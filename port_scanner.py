#!/usr/bin/env python3

import socket
import threading
import argparse
import time
from queue import Queue
from datetime import datetime


# ============================================================
# GLOBAL VARIABLES
# ============================================================

print_lock = threading.Lock()
open_ports = []
scanned_ports = 0
total_ports = 0


# ============================================================
# SERVICE DETECTION
# ============================================================

def get_service_name(port, protocol="tcp"):
    try:
        return socket.getservbyport(port, protocol)
    except OSError:
        return "unknown"


# ============================================================
# BANNER GRABBING
# ============================================================

def get_banner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        s.connect((ip, port))

        # HTTP needs a request before it normally sends a response
        if port in [80, 8080, 8000, 8888]:
            request = (
                f"HEAD / HTTP/1.1\r\n"
                f"Host: {ip}\r\n"
                f"Connection: close\r\n\r\n"
            )

            s.sendall(request.encode())

        banner = s.recv(1024).decode(errors="ignore").strip()

        s.close()

        if banner:
            # Keep only the first useful line
            first_line = banner.splitlines()[0]
            return first_line[:100]

        return "No banner"

    except Exception:
        return "No banner"


# ============================================================
# TCP PORT SCANNING
# ============================================================

def scan_tcp_port(ip, port):
    global scanned_ports

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)

        result = s.connect_ex((ip, port))

        if result == 0:

            service = get_service_name(port, "tcp")
            banner = get_banner(ip, port)

            result_data = {
                "port": port,
                "protocol": "TCP",
                "service": service,
                "banner": banner
            }

            with print_lock:
                open_ports.append(result_data)

                print(
                    f"[+] TCP {port:<5} OPEN   "
                    f"| Service: {service:<12} "
                    f"| {banner}"
                )

        s.close()

    except Exception:
        pass

    finally:
        with print_lock:
            scanned_ports += 1


# ============================================================
# UDP PORT SCANNING
# ============================================================

def scan_udp_port(ip, port):
    global scanned_ports

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)

        # Send a small UDP packet
        s.sendto(b"\x00", (ip, port))

        try:
            data, address = s.recvfrom(1024)

            service = get_service_name(port, "udp")

            result_data = {
                "port": port,
                "protocol": "UDP",
                "service": service,
                "banner": "Response received"
            }

            with print_lock:
                open_ports.append(result_data)

                print(
                    f"[+] UDP {port:<5} OPEN/RESP "
                    f"| Service: {service:<12}"
                )

        except socket.timeout:
            # UDP timeout does NOT necessarily mean closed.
            pass

        except ConnectionRefusedError:
            pass

        s.close()

    except Exception:
        pass

    finally:
        with print_lock:
            scanned_ports += 1


# ============================================================
# THREAD WORKER
# ============================================================

def worker(ip, q, protocol):

    while True:

        try:
            port = q.get_nowait()

        except Exception:
            break

        try:

            if protocol == "tcp":
                scan_tcp_port(ip, port)

            elif protocol == "udp":
                scan_udp_port(ip, port)

        finally:
            q.task_done()


# ============================================================
# PROGRESS DISPLAY
# ============================================================

def progress_monitor():

    global scanned_ports
    global total_ports

    while scanned_ports < total_ports:

        with print_lock:

            if total_ports > 0:
                percentage = (scanned_ports / total_ports) * 100

                print(
                    f"\rProgress: {scanned_ports}/{total_ports} "
                    f"({percentage:.1f}%)",
                    end="",
                    flush=True
                )

        time.sleep(0.5)


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(filename, target, start_port, end_port, scan_time):

    try:

        with open(filename, "w", encoding="utf-8") as file:

            file.write("=" * 70 + "\n")
            file.write("PORT SCANNER RESULTS\n")
            file.write("=" * 70 + "\n")

            file.write(f"Target      : {target}\n")
            file.write(f"Port Range  : {start_port} - {end_port}\n")
            file.write(f"Scan Time   : {scan_time:.2f} seconds\n")
            file.write(
                f"Scan Date   : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")

            if open_ports:

                file.write(
                    f"{'PORT':<8}"
                    f"{'PROTOCOL':<12}"
                    f"{'SERVICE':<15}"
                    f"BANNER\n"
                )

                file.write("-" * 70 + "\n")

                for result in sorted(
                    open_ports,
                    key=lambda x: x["port"]
                ):

                    file.write(
                        f"{result['port']:<8}"
                        f"{result['protocol']:<12}"
                        f"{result['service']:<15}"
                        f"{result['banner']}\n"
                    )

            else:
                file.write("No responding open ports found.\n")

        print(f"\nResults saved to: {filename}")

    except Exception as e:

        print(f"\nCould not save results: {e}")


# ============================================================
# CREATE PORT QUEUE
# ============================================================

def create_queue(start_port, end_port):

    q = Queue()

    for port in range(start_port, end_port + 1):
        q.put(port)

    return q


# ============================================================
# RUN SCAN
# ============================================================

def run_scan(ip, start_port, end_port, threads, protocol):

    global total_ports
    global scanned_ports

    scanned_ports = 0

    total_ports = end_port - start_port + 1

    q = create_queue(start_port, end_port)

    thread_list = []

    start_time = time.time()

    # --------------------------------------------------------
    # Start progress monitor
    # --------------------------------------------------------

    progress_thread = threading.Thread(
        target=progress_monitor
    )

    progress_thread.daemon = True
    progress_thread.start()

    # --------------------------------------------------------
    # Create worker threads
    # --------------------------------------------------------

    for _ in range(threads):

        t = threading.Thread(
            target=worker,
            args=(ip, q, protocol)
        )

        t.daemon = True
        t.start()

        thread_list.append(t)

    # --------------------------------------------------------
    # Wait for queue to finish
    # --------------------------------------------------------

    q.join()

    # Wait until progress reaches 100%
    progress_thread.join(timeout=1)

    end_time = time.time()

    return end_time - start_time


# ============================================================
# MAIN FUNCTION
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="Improved Multi-threaded Network Port Scanner"
    )

    # Target
    parser.add_argument(
        "target",
        help="Target IP address or hostname"
    )

    # Starting port
    parser.add_argument(
        "-s",
        "--start",
        type=int,
        default=1,
        help="Starting port (default: 1)"
    )

    # Ending port
    parser.add_argument(
        "-e",
        "--end",
        type=int,
        default=1024,
        help="Ending port (default: 1024)"
    )

    # Threads
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=100,
        help="Number of threads (default: 100)"
    )

    # UDP
    parser.add_argument(
        "--udp",
        action="store_true",
        help="Perform UDP scan instead of TCP"
    )

    # Quick scan
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Scan common ports only"
    )

    # Output file
    parser.add_argument(
        "-o",
        "--output",
        help="Save results to a text file"
    )

    args = parser.parse_args()

    target = args.target
    threads = args.threads

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if args.quick:

        common_ports = [
            21,
            22,
            23,
            25,
            53,
            80,
            110,
            135,
            139,
            143,
            443,
            445,
            3306,
            3389,
            5432,
            8080
        ]

        start_port = min(common_ports)
        end_port = max(common_ports)

    else:

        start_port = args.start
        end_port = args.end

    if start_port < 1 or end_port > 65535:

        print("Error: Ports must be between 1 and 65535.")
        return

    if start_port > end_port:

        print("Error: Start port cannot be greater than end port.")
        return

    if threads <= 0:

        print("Error: Number of threads must be greater than 0.")
        return

    # Limit threads to avoid excessive resource usage
    if threads > 500:

        print("Error: Maximum allowed threads is 500.")
        return

    # ========================================================
    # RESOLVE TARGET
    # ========================================================

    try:

        ip = socket.gethostbyname(target)

    except socket.gaierror:

        print(f"Error: Could not resolve target '{target}'.")
        return

    protocol = "UDP" if args.udp else "TCP"

    # ========================================================
    # DISPLAY SCAN INFORMATION
    # ========================================================

    print("=" * 70)

    print(" MULTI-THREADED PORT SCANNER")

    print("=" * 70)

    print(f" Target       : {target}")
    print(f" IP Address   : {ip}")
    print(f" Protocol     : {protocol}")
    print(f" Port Range   : {start_port} - {end_port}")
    print(f" Threads      : {threads}")

    if args.quick:
        print(" Scan Mode    : QUICK")

    else:
        print(" Scan Mode    : NORMAL")

    print("=" * 70)

    print("\nScanning started...\n")

    # ========================================================
    # START SCAN
    # ========================================================

    scan_time = run_scan(
        ip,
        start_port,
        end_port,
        threads,
        protocol.lower()
    )

    print("\n")

    # ========================================================
    # RESULTS
    # ========================================================

    print("=" * 70)

    print(f" Scan completed in {scan_time:.2f} seconds")

    print(f" Open ports found: {len(open_ports)}")

    print("=" * 70)

    if open_ports:

        print("\nOPEN PORTS:\n")

        print(
            f"{'PORT':<8}"
            f"{'PROTOCOL':<12}"
            f"{'SERVICE':<15}"
            f"BANNER"
        )

        print("-" * 70)

        for result in sorted(
            open_ports,
            key=lambda x: x["port"]
        ):

            print(
                f"{result['port']:<8}"
                f"{result['protocol']:<12}"
                f"{result['service']:<15}"
                f"{result['banner']}"
            )

    else:

        print("\nNo responding open ports found.")

    print()

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    if args.output:

        save_results(
            args.output,
            target,
            start_port,
            end_port,
            scan_time
        )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    main()