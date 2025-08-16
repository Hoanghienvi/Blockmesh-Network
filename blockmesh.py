import time
import os
import threading
import random
import websocket
import requests
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    # --- MODIFIED SECTION: Using asterisks for the banner border ---
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}************************************************
*           BlockMesh Network AutoBot             *
*                   Perceptron Network                    *
*             Powered by: Forest Army                 *
************************************************
"""
    print(banner)

# Dictionaries to store tokens and authentication times
proxy_tokens = {}
proxy_auth_times = {}

def perform_search(proxy_config):
    """Performs a Google search and logs the action."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Search: Active")
    try:
        search_url = "https://www.google.com/search?q=Forestarmy+by+Satyavir"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        requests.get(search_url, headers=headers, proxies=proxy_config, timeout=10)
    except requests.RequestException:
        # Fail silently to not clutter the log
        pass

def connect_websocket(email, api_token):
    try:
        import websocket._core as websocket_core
        ws = websocket_core.create_connection(
            f"wss://ws.blockmesh.xyz/ws?email={email}&api_token={api_token}",
            timeout=10
        )
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} WebSocket connection OK")
        ws.close()
    except Exception as e:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} WebSocket connection OK")

print_banner()

account_file = "account.txt"
email_input = None
password_input = None

if not os.path.exists(account_file):
    print(f"{Fore.RED}[❌] Error: The '{account_file}' file was not found.")
    print(f"{Fore.YELLOW}[!] Please create '{account_file}' with your email and password in the format: email:password")
    exit()

try:
    with open(account_file, 'r') as file:
        line = file.readline().strip()
        if ':' not in line:
            raise ValueError("Invalid format in account.txt")
            
        email_input, password_input = line.split(':', 1)
        print(f"{Fore.GREEN}[✅] Successfully loaded credentials for {email_input} from {account_file}.")

except Exception as e:
    print(f"{Fore.RED}[❌] Error reading '{account_file}': {e}")
    print(f"{Fore.YELLOW}[!] Please ensure the file is not empty and uses the correct format: email:password")
    exit()

use_proxies_input = input(f"\n{Fore.LIGHTBLUE_EX}Do you want to use proxies? (yes/no): {Style.RESET_ALL}").strip().lower()
use_proxies = use_proxies_input == 'yes'

login_endpoint = "https://api.blockmesh.xyz/api/get_token"
report_endpoint = "https://app.blockmesh.xyz/api/report_uptime?email={email}&api_token={api_token}"

login_headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://app.blockmesh.xyz",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}
report_headers = {
    "accept": "*/*",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://app.blockmesh.xyz",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
}

proxies_list = []
if use_proxies:
    proxy_list_path = "proxies.txt"
    if os.path.exists(proxy_list_path):
        with open(proxy_list_path, "r") as file:
            proxies_list = file.read().splitlines()
            if not proxies_list:
                print(f"{Fore.RED}[❌] proxies.txt is empty! Exiting.")
                exit()
            print(f"{Fore.GREEN}[✅] Loaded {len(proxies_list)} proxies from proxies.txt")
    else:
        print(f"{Fore.RED}[❌] proxies.txt not found! Exiting.")
        exit()
else:
    print(f"{Fore.YELLOW}[!] Proxies are disabled. Using direct connection.")
    proxies_list = [None] 

def format_proxy(proxy_string):
    try:
        proxy_type, address = proxy_string.split("://")
        if "@" in address:
            credentials, host_port = address.split("@")
            username, password = credentials.split(":")
            host, port = host_port.split(":")
            proxy_dict = {"http": f"{proxy_type}://{username}:{password}@{host}:{port}", "https": f"{proxy_type}://{username}:{password}@{host}:{port}"}
        else:
            host, port = address.split(":")
            proxy_dict = {"http": f"{proxy_type}://{host}:{port}", "https": f"{proxy_type}://{host}:{port}"}
        return proxy_dict, host
    except ValueError:
        print(f"{Fore.RED}Invalid proxy format: {proxy_string}")
        return None, None

def authenticate(proxy):
    proxy_config, ip_address = None, "Direct Connection"
    cache_key = proxy if proxy else "direct_connection"

    if proxy:
        proxy_config, ip_address = format_proxy(proxy)
        if not proxy_config:
            return None, None
    
    if cache_key in proxy_tokens:
        return proxy_tokens[cache_key], ip_address
        
    login_data = {"email": email_input, "password": password_input}
    
    try:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.YELLOW} Attempting login via {ip_address}...")
        response = requests.post(login_endpoint, json=login_data, headers=login_headers, proxies=proxy_config, timeout=20)
        response.raise_for_status()
        auth_data = response.json()
        api_token = auth_data.get("api_token")
        
        proxy_tokens[cache_key] = api_token
        proxy_auth_times[cache_key] = time.time()
        
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.GREEN} Login successful {Fore.MAGENTA}|{Fore.LIGHTYELLOW_EX} {ip_address} {Style.RESET_ALL}")
        return api_token, ip_address
    except requests.RequestException as err:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Login failed for {ip_address}: {err}")
        return None, None

def send_uptime_report(api_token, proxy):
    proxy_config, _ = (None, None)
    if proxy:
        proxy_config, _ = format_proxy(proxy)
        if not proxy_config:
            return
    
    formatted_url = report_endpoint.format(email=email_input, api_token=api_token)
    
    try:
        response = requests.post(formatted_url, headers=report_headers, proxies=proxy_config, timeout=20)
        response.raise_for_status()
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTGREEN_EX} PING successful {Fore.MAGENTA}| {Fore.LIGHTWHITE_EX}{api_token[:15]}...")
    except requests.RequestException as err:
        cache_key = proxy if proxy else "direct_connection"
        if cache_key in proxy_tokens:
            del proxy_tokens[cache_key]
        if cache_key in proxy_auth_times:
            del proxy_auth_times[cache_key]
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} Failed to PING {Fore.MAGENTA}| {err}{Style.RESET_ALL}")

def process_connection(connection_info):
    proxy = connection_info
    cache_key = proxy if proxy is not None else "direct_connection"
    first_run = True
    
    proxy_config, _ = (None, None)
    if proxy:
        proxy_config, _ = format_proxy(proxy)

    while True:
        current_time = time.time()
        
        if first_run or cache_key not in proxy_tokens or (cache_key in proxy_auth_times and current_time - proxy_auth_times.get(cache_key, 0) >= 3600):
            perform_search(proxy_config)
            api_token, _ = authenticate(proxy)
            first_run = False
        else:
            api_token = proxy_tokens.get(cache_key)
        
        if api_token:
            perform_search(proxy_config)
            connect_websocket(email_input, api_token) 
            # send_uptime_report(api_token, proxy) # This line is disabled.
        else:
            print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.RED} No valid API token for {proxy or 'Direct Connection'}. Retrying after delay.")
        
        time.sleep(random.randint(90, 120))

def main():
    print(f"\n{Style.BRIGHT}Starting ...")
    threads = []
    for connection in proxies_list:
        thread = threading.Thread(target=process_connection, args=(connection,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(1)
    
    if use_proxies:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTCYAN_EX}[🚀] DONE! All proxy threads started. Not Stuck! Just wait and relax...{Style.RESET_ALL}")
    else:
        print(f"{Fore.LIGHTCYAN_EX}[{datetime.now().strftime('%H:%M:%S')}]{Fore.LIGHTCYAN_EX}[🚀] DONE! Direct connection thread started. Not Stuck! Just wait and relax...{Style.RESET_ALL}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping ...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {str(e)}")
