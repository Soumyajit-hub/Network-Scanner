This is a Multi Threaded Python Port Scanner with a simple GUI, built to understand how network scanning works.

**_Preview Images:_**

**1st Image: Scan in progress**
<br>
<img width="790" height="812" alt="image" src="https://github.com/user-attachments/assets/058453b8-f2a8-47af-bf5e-853b16cd0591" />

<br>

**2nd Image:  Scan results**
<br>
<img width="400" height="797" alt="image" src="https://github.com/user-attachments/assets/48961b30-67bd-44fc-946f-11da57932bde" />


<br>

**About the Project:**
- Port scanning is one of the first steps in network security testing, because it shows which services a system exposes. I built this tool to learn how TCP connections work at the socket level and how to make a scanner fast and easy to use. The scanner checks each port by attempting a TCP connection. It uses multiple threads so many ports are checked at the same time, and the GUI stays responsive while the scan runs. Open ports are shown live in colors, along with the service name.

**Features:**
- Fast scanning with multiple threads
- Simple GUI built with tkinter
- Color-coded live results
- Custom port range
- Input validation with clear error messages

**What I Learned**
- How TCP connections work using Python sockets
- How to use threads to speed up network tasks
- How to keep a GUI responsive during background work
- Why scanning should only be done with permission

**Tools Used:**
Python, tkinter, socket, threading

**How to Run?**
1. Install Python 3
2. Download this project
3. Run: `python main.py`

**Legal Note:**
Use only on your own computer or on systems you have permission to test, such as `127.0.0.1` or `scanme.nmap.org`.

**Author:**
Soumyajit Roy
B.Tech Data Science | Cybersecurity Enthusiast
