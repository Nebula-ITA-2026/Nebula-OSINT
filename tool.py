#!/usr/bin/env python3
# NEBULA - OSINT Tool
# 
# MIT License
# 
# Copyright (c) 2024 Principale
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import socket
import requests
import whois
import dns.resolver
import ssl
import os
import subprocess
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Inizializzazione per Windows CMD
init(autoreset=True)

class Nebula:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def banner(self):
        print(f"""
{Fore.CYAN}  _   _ _____ ____  _   _ _        _    
{Fore.CYAN} | \\ | | ____| __ )| | | | |      / \\   
{Fore.CYAN} |  \\| |  _| |  _ \\| | | | |     / _ \\  
{Fore.CYAN} | |\\  | |___| |_) | |_| | |___ / ___ \\ 
{Fore.CYAN} |_| \\_|_____|____/ \___/|_____/_/   \\_\\
        """)

    def get_whois_info(self, domain):
        print(f"\n{Fore.YELLOW}[+] Info WHOIS: {domain}")
        try:
            w = whois.whois(domain)
            print(f"{Fore.GREEN}Registrar: {w.registrar}\nData Creazione: {w.creation_date}\nEmail: {w.emails}")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def get_dns_records(self, domain):
        print(f"\n{Fore.YELLOW}[+] Record DNS: {domain}")
        for r_type in ['A', 'MX', 'NS', 'TXT']:
            try:
                answers = dns.resolver.resolve(domain, r_type)
                for rdata in answers: print(f"{Fore.GREEN}[{r_type}] {rdata}")
            except: print(f"{Fore.RED}[-] Nessun record {r_type}")

    def geo_ip(self, ip):
        print(f"\n{Fore.YELLOW}[+] Geolocalizzazione: {ip}")
        try:
            data = requests.get(f"http://ip-api.com/json/{ip}").json()
            if data['status'] == 'success':
                print(f"{Fore.GREEN}Paese: {data['country']}\nCittà: {data['city']}\nISP: {data['isp']}")
            else: print(f"{Fore.RED}[!] IP non trovato.")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def check_username(self, username):
        print(f"\n{Fore.YELLOW}[+] Ricerca Username: {username}")
        socials = {
            "GitHub": f"https://github.com/{username}",
            "Twitter": f"https://twitter.com/{username}",
            "Instagram": f"https://instagram.com/{username}",
            "Reddit": f"https://www.reddit.com/user/{username}"
        }
        for p, url in socials.items():
            try:
                if requests.get(url, headers=self.headers, timeout=5).status_code == 200:
                    print(f"{Fore.GREEN}[FOUND] {p}: {url}")
                else: print(f"{Fore.WHITE}[NOT FOUND] {p}")
            except: pass

    def port_scan(self, target):
        print(f"\n{Fore.YELLOW}[+] Scan porte comuni su: {target}")
        for port in [21, 22, 23, 25, 53, 80, 110, 443, 3306, 8080]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((target, port)) == 0:
                print(f"{Fore.GREEN}[OPEN] Porta {port}")
            s.close()

    def ssl_check(self, domain):
        print(f"\n{Fore.YELLOW}[+] Verifica SSL: {domain}")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    print(f"{Fore.GREEN}Scadenza: {cert['notAfter']}")
        except Exception as e: print(f"{Fore.RED}[!] Errore SSL: {e}")

    def get_links(self, url):
        if not url.startswith("http"): url = "http://" + url
        print(f"\n{Fore.YELLOW}[+] Estrazione Link da: {url}")
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            links = set([a.get('href') for a in soup.find_all('a') if a.get('href')])
            for link in list(links)[:15]: print(f"{Fore.GREEN}-> {link}")
            print(f"{Fore.WHITE}... visualizzati i primi 15 link.")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def reverse_dns(self, ip):
        print(f"\n{Fore.YELLOW}[+] Reverse DNS per: {ip}")
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            print(f"{Fore.GREEN}Hostname: {hostname}")
        except Exception as e: print(f"{Fore.RED}[!] Nessun hostname trovato.")

    def get_security_headers(self, url):
        if not url.startswith("http"): url = "http://" + url
        print(f"\n{Fore.YELLOW}[+] Analisi Header di Sicurezza: {url}")
        security_headers = [
            "Strict-Transport-Security", "Content-Security-Policy",
            "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy"
        ]
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            for header in security_headers:
                status = f"{Fore.GREEN}[SICURO]" if header in res.headers else f"{Fore.RED}[MANCANTE]"
                print(f"{status} {header}")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def subdomain_enum(self, domain):
        print(f"\n{Fore.YELLOW}[+] Enumerazione Sottodomini per: {domain}")
        subs = ['www', 'dev', 'api', 'mail', 'test', 'admin', 'vpn', 'shop', 'blog']
        for sub in subs:
            target = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(target)
                print(f"{Fore.GREEN}[FOUND] {target} -> {ip}")
            except: pass

    def scan_sensitive_files(self, url):
        if not url.startswith("http"): url = "http://" + url
        if url.endswith("/"): url = url[:-1]
        print(f"\n{Fore.YELLOW}[+] Ricerca File Sensibili su: {url}")
        files = ['/robots.txt', '/.env', '/.git/config', '/sitemap.xml', '/.vscode/', '/config.php', '/wp-config.php', '/.htaccess']
        for f in files:
            try:
                res = requests.get(url + f, headers=self.headers, timeout=5)
                if res.status_code == 200:
                    print(f"{Fore.GREEN}[VULN?] Trovato: {url + f} (Dim: {len(res.text)})")
                else: print(f"{Fore.WHITE}[-] Non trovato: {f}")
            except: pass

    def detect_tech(self, url):
        if not url.startswith("http"): url = "http://" + url
        print(f"\n{Fore.YELLOW}[+] Rilevamento Tecnologie: {url}")
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            server = res.headers.get('Server', 'Sconosciuto')
            powered = res.headers.get('X-Powered-By', 'Sconosciuto')
            print(f"{Fore.GREEN}Server: {server}")
            print(f"{Fore.GREEN}Tecnologia: {powered}")
            if "wp-content" in res.text: print(f"{Fore.GREEN}CMS: WordPress rilevato")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def check_email_mx(self, email):
        print(f"\n{Fore.YELLOW}[+] Verifica MX Record per Email: {email}")
        try:
            domain = email.split('@')[1]
            answers = dns.resolver.resolve(domain, 'MX')
            for rdata in answers:
                print(f"{Fore.GREEN}[MX] {rdata.exchange}")
        except: print(f"{Fore.RED}[!] Dominio email non valido o nessun server MX.")

    def ping_host(self, host):
        print(f"\n{Fore.YELLOW}[+] Ping verso: {host}")
        param = "-n" if os.name == "nt" else "-c"
        command = ["ping", param, "1", host]
        if subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            print(f"{Fore.GREEN}[UP] Host raggiungibile")
        else: print(f"{Fore.RED}[DOWN] Host non risponde")

    def traceroute_host(self, host):
        print(f"\n{Fore.YELLOW}[+] Traceroute verso: {host} (Potrebbe richiedere tempo...)")
        cmd = "tracert" if os.name == "nt" else "traceroute"
        try:
            # Su Linux traceroute spesso richiede privilegi o parametri specifici
            if os.name != "nt":
                output = subprocess.check_output([cmd, "-m", "20", host], stderr=subprocess.STDOUT, universal_newlines=True)
            else:
                output = subprocess.check_output([cmd, host], stderr=subprocess.STDOUT, universal_newlines=True)
            print(f"{Fore.WHITE}{output}")
        except: print(f"{Fore.RED}[!] Errore durante il traceroute.")

def main():
    tool = Nebula()
    while True:
        tool.clear_screen()
        tool.banner()
        print(f"{Fore.CYAN}1.{Fore.WHITE} Analisi WHOIS & DNS")
        print(f"{Fore.CYAN}2.{Fore.WHITE} Geolocalizzazione IP")
        print(f"{Fore.CYAN}3.{Fore.WHITE} Ricerca Username Social")
        print(f"{Fore.CYAN}4.{Fore.WHITE} Scansione Porte TCP")
        print(f"{Fore.CYAN}5.{Fore.WHITE} Verifica SSL")
        print(f"{Fore.CYAN}6.{Fore.WHITE} Estrazione Link Web")
        print(f"{Fore.CYAN}7.{Fore.WHITE} Reverse DNS")
        print(f"{Fore.CYAN}8.{Fore.WHITE} Header di Sicurezza")
        print(f"{Fore.CYAN}9.{Fore.WHITE} Enumerazione Sottodomini")
        print(f"{Fore.CYAN}10.{Fore.WHITE} Scanner File Sensibili")
        print(f"{Fore.CYAN}11.{Fore.WHITE} Rilevamento Tecnologie/CMS")
        print(f"{Fore.CYAN}12.{Fore.WHITE} Verifica Email (MX)")
        print(f"{Fore.CYAN}13.{Fore.WHITE} Ping Host")
        print(f"{Fore.CYAN}14.{Fore.WHITE} Traceroute")
        print(f"{Fore.CYAN}0.{Fore.WHITE} Esci")

        choice = input(f"\n{Fore.YELLOW}Seleziona un'opzione > ")

        if choice == '1':
            dom = input("Dominio: ")
            tool.get_whois_info(dom)
            tool.get_dns_records(dom)
        elif choice == '2':
            ip = input("IP: ")
            tool.geo_ip(ip)
        elif choice == '3':
            user = input("Username: ")
            tool.check_username(user)
        elif choice == '4':
            target = input("IP o Dominio: ")
            tool.port_scan(target)
        elif choice == '5':
            dom = input("Dominio: ")
            tool.ssl_check(dom)
        elif choice == '6':
            url = input("URL: ")
            tool.get_links(url)
        elif choice == '7':
            ip = input("IP: ")
            tool.reverse_dns(ip)
        elif choice == '8':
            url = input("URL/Dominio: ")
            tool.get_security_headers(url)
        elif choice == '9':
            dom = input("Dominio: ")
            tool.subdomain_enum(dom)
        elif choice == '10':
            url = input("URL: ")
            tool.scan_sensitive_files(url)
        elif choice == '11':
            url = input("URL: ")
            tool.detect_tech(url)
        elif choice == '12':
            email = input("Email: ")
            tool.check_email_mx(email)
        elif choice == '13':
            host = input("Host/IP: ")
            tool.ping_host(host)
        elif choice == '14':
            host = input("Host/IP: ")
            tool.traceroute_host(host)
        elif choice == '0':
            print(f"{Fore.MAGENTA}Chiusura...")
            break
        else:
            print(f"{Fore.RED}Scelta non valida.")

        input(f"\n{Fore.WHITE}Premi Invio per continuare...")

if __name__ == "__main__":
    main()