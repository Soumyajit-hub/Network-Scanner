import socket
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class NetworkScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Port Scanner - Pro Edition")
        self.root.geometry("650, 600" if False else "650x620")
        self.root.resizable(False, False)

        self.q = queue.Queue()
        self.stop_event = threading.Event()
        self.is_scanning = False

        # --- UI Layout ---
        frame_input = ttk.LabelFrame(root, text=" Target & Port Settings ", padding=12)
        frame_input.pack(fill="x", padx=15, pady=10)

        # Target IP Input
        ttk.Label(frame_input, text="Target IP / Hostname:").grid(row=0, column=0, sticky="w", pady=4)
        self.entry_target = ttk.Entry(frame_input, width=28)
        self.entry_target.insert(0, "127.0.0.1")
        self.entry_target.grid(row=0, column=1, padx=5, pady=4)

        # Start Port Input
        ttk.Label(frame_input, text="Start Port (1-65535):").grid(row=1, column=0, sticky="w", pady=4)
        self.entry_start = ttk.Entry(frame_input, width=12)
        self.entry_start.insert(0, "1")
        self.entry_start.grid(row=1, column=1, sticky="w", padx=5, pady=4)

        # End Port Input
        ttk.Label(frame_input, text="End Port (1-65535):").grid(row=2, column=0, sticky="w", pady=4)
        self.entry_end = ttk.Entry(frame_input, width=12)
        self.entry_end.insert(0, "1024")
        self.entry_end.grid(row=2, column=1, sticky="w", padx=5, pady=4)

        # Buttons Frame
        btn_frame = ttk.Frame(frame_input)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.btn_scan = ttk.Button(btn_frame, text="Start Scan", command=self.start_scan)
        self.btn_scan.pack(side="left", padx=5)

        self.btn_stop = ttk.Button(btn_frame, text="Stop Scan", command=self.stop_scan, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=5)

        # Output Results Area
        frame_output = ttk.LabelFrame(root, text=" Scan Output ", padding=10)
        frame_output.pack(fill="both", expand=True, padx=15, pady=5)

        self.text_output = tk.Text(frame_output, state="disabled", wrap="word", bg="#1e1e1e", font=("Consolas", 10))
        self.text_output.pack(fill="both", expand=True)

        # Color tags
        self.text_output.tag_configure("normal", foreground="#87ceeb")   # Sky blue
        self.text_output.tag_configure("open", foreground="#ff4444")     # Red
        self.text_output.tag_configure("success", foreground="#00ff00")  # Green

    def log(self, text, tag="normal"):
        self.text_output.config(state="normal")
        self.text_output.insert(tk.END, text + "\n", tag)
        self.text_output.see(tk.END)
        self.text_output.config(state="disabled")

    def validate_inputs(self):
        target_raw = self.entry_target.get().strip()
        if not target_raw:
            messagebox.showerror("Error", "Target hostname or IP cannot be empty.")
            return None, None, None

        try:
            resolved_ip = socket.gethostbyname(target_raw)
        except socket.gaierror:
            messagebox.showerror("Error", f"Could not resolve hostname: '{target_raw}'")
            return None, None, None

        try:
            start_port = int(self.entry_start.get().strip())
            end_port = int(self.entry_end.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Ports must be valid integers.")
            return None, None, None

        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535):
            messagebox.showerror("Error", "Port numbers must be between 1 and 65535.")
            return None, None, None

        if start_port > end_port:
            messagebox.showerror("Error", "Start port cannot be greater than end port.")
            return None, None, None

        return resolved_ip, start_port, end_port

    def start_scan(self):
        resolved_ip, start_port, end_port = self.validate_inputs()
        if not resolved_ip:
            return

        self.stop_event.clear()
        self.is_scanning = True
        self.btn_scan.config(state="disabled")
        self.btn_stop.config(state="normal")
        
        self.text_output.config(state="normal")
        self.text_output.delete("1.0", tk.END)
        self.text_output.config(state="disabled")

        total_ports = (end_port - start_port) + 1
        self.progress["maximum"] = total_ports
        self.progress["value"] = 0

        # Start background thread
        threading.Thread(target=self.worker_scan, args=(resolved_ip, start_port, end_port), daemon=True).start()
        
        # Start queue polling loop
        self.root.after(100, self.process_queue)

    def stop_scan(self):
        self.stop_event.set()
        self.log("[!] Stop signal sent. Finishing active workers...", "normal")

    def worker_scan(self, target, start_port, end_port):
        self.q.put(("log", f"[*] Target resolved IP: {target}", "normal"))
        self.q.put(("log", f"[*] Starting scan ({start_port}-{end_port}) with 100 workers...", "normal"))
        self.q.put(("log", f"[*] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "-" * 50, "normal"))

        from concurrent.futures import ThreadPoolExecutor
        open_ports = 0
        scanned_count = 0

        def scan_single_port(port):
            nonlocal open_ports, scanned_count
            if self.stop_event.is_set():
                return
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                res = s.connect_ex((target, port))
                if res == 0:
                    try:
                        service = socket.getservbyport(port)
                    except:
                        service = "Unknown service"
                    self.q.put(("open_port", port, service))
                    open_ports += 1
                s.close()
            except Exception:
                pass
            finally:
                self.q.put(("progress", 1))

        with ThreadPoolExecutor(max_workers=100) as executor:
            executor.map(scan_single_port, range(start_port, end_port + 1))

        self.q.put(("done", open_ports))

    def process_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                msg_type = msg[0]
                if msg_type == "log":
                    self.log(msg[1], msg[2])
                elif msg_type == "open_port":
                    self.log(f"[+] Port {msg[1]:<5} OPEN  --> {msg[2]}", "open")
                elif msg_type == "progress":
                    self.progress["value"] += msg[1]
                elif msg_type == "done":
                    self.log("-" * 50, "normal")
                    if self.stop_event.is_set():
                        self.log("[*] Scan stopped by user.", "success")
                    else:
                        self.log(f"[*] Scan finished. Found {msg[1]} open port(s).", "success")
                    self.btn_scan.config(state="normal")
                    self.btn_stop.config(state="disabled")
                    self.is_scanning = False
                    return
        except queue.Empty:
            pass

        if self.is_scanning:
            self.root.after(100, self.process_queue)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkScannerGUI(root)
    root.mainloop()