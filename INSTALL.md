============================================================
MULTI-THREADED PORT SCANNER
INSTALLATION AND USAGE GUIDE
============================================================


1. REQUIREMENTS
------------------------------------------------------------

Before running this project, make sure you have:

- Python 3.9 or newer
- Git (optional, only required if you want to clone the project)
- VS Code or another Python editor (optional)

No external Python packages are required.

The project uses only Python standard-library modules:

- socket
- threading
- argparse
- time
- queue
- datetime


2. PROJECT STRUCTURE
------------------------------------------------------------

The project folder should look like:

multithreaded-port-scanner/
│
├── port_scanner.py
├── requirements.txt
├── install.txt
├── README.md
├── .gitignore
└── LICENSE


3. INSTALLATION
------------------------------------------------------------

STEP 1: Install Python

Download and install Python from:

https://www.python.org/

During Windows installation, make sure to enable:

"Add Python to PATH"


STEP 2: Verify Python installation

Open PowerShell or Command Prompt and run:

python --version

Example:

Python 3.12.5


STEP 3: Download or clone the project

If using Git:

git clone https://github.com/adithya79359/multithreaded-port-scanner.git

Move into the project folder:

cd multithreaded-port-scanner


If the project is already downloaded, simply open the
project folder in PowerShell or VS Code.


4. INSTALL PYTHON PACKAGES
------------------------------------------------------------

No external packages are required.

Therefore, you do NOT need to run:

pip install socket
pip install threading
pip install argparse

These modules are already included with Python.

The requirements.txt file is included only to document
that the project has no external dependencies.


5. HOW TO RUN
------------------------------------------------------------

Open PowerShell inside the project folder.

Example:

cd D:\projects_2026\port_scanner


6. BASIC SCAN
------------------------------------------------------------

To scan your own computer:

python port_scanner.py 127.0.0.1

The program scans ports 1 to 1024 by default.

IMPORTANT:
127.0.0.1 means the local computer on which the scanner
is running.


7. SCAN A SPECIFIC PORT RANGE
------------------------------------------------------------

Example:

python port_scanner.py 127.0.0.1 -s 1 -e 100

This means:

Target  : 127.0.0.1
Start   : Port 1
End     : Port 100


8. CHANGE NUMBER OF THREADS
------------------------------------------------------------

Example:

python port_scanner.py 127.0.0.1 -s 1 -e 1024 -t 50

This uses 50 threads.

The default number of threads is 100.


9. SCAN A LOCAL NETWORK DEVICE
------------------------------------------------------------

Example:

python port_scanner.py 192.168.0.1 -s 1 -e 1024

IMPORTANT:
Only scan devices that you own or have explicit permission
to test.

The IP address above is an example of a local router.

* Replace the IP address with the IP address of your own
  authorized device.


10. QUICK SCAN
------------------------------------------------------------

The improved scanner supports a quick scan of commonly used
ports.

Run:

python port_scanner.py 192.168.0.1 --quick

The quick scan checks commonly used ports such as:

21
22
23
25
53
80
135
139
443
445
3306
3389
8080


11. UDP SCAN
------------------------------------------------------------

To perform a UDP scan:

python port_scanner.py 192.168.0.1 -s 1 -e 100 --udp

IMPORTANT:
UDP scanning works differently from TCP scanning.

A UDP timeout does not always mean that a port is closed.


12. SAVE SCAN RESULTS
------------------------------------------------------------

To save the results to a text file:

python port_scanner.py 192.168.0.1 -s 1 -e 1024 -o results.txt

A results.txt file will be created in the project folder.


13. VIEW HELP
------------------------------------------------------------

To see all available options:

python port_scanner.py --help

Available options include:

-s, --start
Starting port

-e, --end
Ending port

-t, --threads
Number of scanning threads

--udp
Perform UDP scan

--quick
Perform a quick scan of common ports

-o, --output
Save scan results to a text file


14. SAMPLE OUTPUT — LOCAL COMPUTER
------------------------------------------------------------

Command:

python port_scanner.py 127.0.0.1


Example output:

======================================================================
 MULTI-THREADED PORT SCANNER
======================================================================
 Target       : 127.0.0.1
 IP Address   : 127.0.0.1
 Protocol     : TCP
 Port Range   : 1 - 1024
 Threads      : 100
 Scan Mode    : NORMAL
======================================================================

Scanning started...

Progress: 203/1024 (19.8%)
[+] TCP 135   OPEN   | Service: epmap
[+] TCP 445   OPEN   | Service: microsoft-ds

======================================================================
 Scan completed in 6.04 seconds
 Open ports found: 2
======================================================================

OPEN PORTS:

PORT    PROTOCOL    SERVICE        BANNER
----------------------------------------------------------------------
135     TCP         epmap           No banner
445     TCP         microsoft-ds    No banner


15. SAMPLE OUTPUT — ROUTER
------------------------------------------------------------

Command:

python port_scanner.py 192.168.0.1 -s 1 -e 1024


Example output:

======================================================================
 MULTI-THREADED PORT SCANNER
======================================================================
 Target       : 192.168.0.1
 IP Address   : 192.168.0.1
 Protocol     : TCP
 Port Range   : 1 - 1024
 Threads      : 100
 Scan Mode    : NORMAL
======================================================================

Scanning started...

[+] TCP 22    OPEN   | Service: ssh
[+] TCP 53    OPEN   | Service: domain
[+] TCP 80    OPEN   | Service: http

======================================================================
 Scan completed in 6.00 seconds
 Open ports found: 3
======================================================================

OPEN PORTS:

PORT    PROTOCOL    SERVICE        BANNER
----------------------------------------------------------------------
22      TCP         ssh             SSH-2.0-dropbear_2012.55
53      TCP         domain          No banner
80      TCP         http            No banner


16. UNDERSTANDING THE OUTPUT
------------------------------------------------------------

OPEN means that the scanner successfully established a
TCP connection to that port.

Example:

Port 22 → SSH

Port 53 → DNS

Port 80 → HTTP

Port 135 → Windows RPC

Port 445 → Windows SMB/File Sharing


17. PERSONAL INFORMATION IN SAMPLE OUTPUT
------------------------------------------------------------

The following information may be personal or specific to
the user's computer/network:

* IP addresses such as 192.168.0.101
* Local router IP addresses such as 192.168.0.1
* Hostnames
* MAC addresses
* Device-specific service information
* Scan times or other environment-specific information

When publishing screenshots or output on GitHub, replace
personal/local information with examples where appropriate.

For example:

192.168.0.101 → YOUR_LOCAL_IP

192.168.0.1 → YOUR_ROUTER_IP


18. SECURITY NOTICE
------------------------------------------------------------

This tool is intended for educational purposes, network
troubleshooting, and authorized security testing.

Only scan systems, devices, and networks that you own or
have explicit permission to test.

Do not use this scanner to scan unauthorized systems.


19. BASIC WORKING
------------------------------------------------------------

The scanner works using the following process:

1. Accept target and port range from the user.
2. Create a queue containing the ports.
3. Create multiple worker threads.
4. Each thread takes a port from the queue.
5. The scanner attempts a TCP or UDP connection.
6. If a TCP connection succeeds, the port is reported as open.
7. The scanner attempts banner grabbing.
8. The service name is identified when possible.
9. Results are displayed.
10. Scan time and open ports are displayed.
11. Results can optionally be saved to a text file.


============================================================
END OF INSTALLATION AND USAGE GUIDE
============================================================