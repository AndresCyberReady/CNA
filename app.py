from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import random
import json
import os
from datetime import datetime
from werkzeug.exceptions import BadRequestKeyError

# Data location is overridable via env so Docker volumes can mount
# a persistent directory (e.g. /app/data) without code changes.
_DATA_DIR = os.environ.get(
    'DATA_DIR',
    os.path.dirname(os.path.abspath(__file__))
)
os.makedirs(_DATA_DIR, exist_ok=True)
LEADERBOARD_FILE = os.environ.get(
    'LEADERBOARD_FILE',
    os.path.join(_DATA_DIR, 'leaderboard.json')
)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def add_leaderboard_entry(username, score, correct, total, elapsed_seconds, exam_type):
    entries = load_leaderboard()
    entries.append({
        'username': username,
        'score': round(score, 1),
        'correct': correct,
        'total': total,
        'time': elapsed_seconds,
        'exam_type': exam_type,
        'date': datetime.now().strftime('%Y-%m-%d'),
    })
    entries.sort(key=lambda x: (-x['score'], x['time']))
    entries = entries[:100]
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(entries, f)
    return entries

app = Flask(__name__)
# Use a fixed secret key so sessions persist across restarts.
# In production (e.g. Docker/Portainer), set SECRET_KEY as an env var.
app.secret_key = os.environ.get('SECRET_KEY', 'exam-app-secret-key-2024-production-change-me')

# Configure server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.environ.get(
    'SESSION_FILE_DIR',
    os.path.join(_DATA_DIR, 'flask_session')
)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

Session(app)

# Exam questions covering Network+ and Security+ topics
QUESTIONS = [
    {
        "id": 1,
        "question": "Which port does HTTPS typically use?",
        "options": ["21", "443", "80", "8080"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 2,
        "question": "What does VPN stand for?",
        "options": ["Virtual Private Network", "Very Private Network", "Virtual Public Network", "Verified Private Network"],
        "correct": 0,
        "topic": "Network+/Security+"
    },
    {
        "id": 3,
        "question": "Which type of attack involves sending false data to a DNS server?",
        "options": ["SQL Injection", "Cross-Site Scripting", "DNS Spoofing", "Brute Force"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 4,
        "question": "What is the default subnet mask for a Class B network?",
        "options": ["255.255.0.0", "255.0.0.0", "255.255.255.0", "255.255.255.255"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 5,
        "question": "Which protocol is used for secure email communication?",
        "options": ["SMTP", "S/MIME", "POP3", "IMAP"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 6,
        "question": "What does WPA3 provide over WPA2?",
        "options": ["Higher speed", "Better password management", "Enhanced security", "All of the above"],
        "correct": 3,
        "topic": "Security+"
    },
    {
        "id": 7,
        "question": "Which device operates at Layer 2 of the OSI model?",
        "options": ["Router", "Switch", "Hub", "Firewall"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 8,
        "question": "What type of malware replicates itself across a network?",
        "options": ["Virus", "Worm", "Trojan", "Spyware"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 9,
        "question": "What is the purpose of a firewall?",
        "options": ["Block unwanted network traffic", "Speed up internet", "Encrypt data", "Route packets"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 10,
        "question": "Which protocol is connection-oriented?",
        "options": ["UDP", "TCP", "ICMP", "ARP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 11,
        "question": "What does MFA stand for?",
        "options": ["Multi-Function Authentication", "Multi-Factor Authentication", "Multiple File Access", "Multi-Framework Access"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 12,
        "question": "What is the maximum cable length for standard Ethernet?",
        "options": ["100 meters", "50 meters", "200 meters", "150 meters"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 13,
        "question": "Which encryption algorithm is considered most secure currently?",
        "options": ["DES", "3DES", "AES-256", "RC4"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 14,
        "question": "What port does SSH use by default?",
        "options": ["21", "22", "23", "443"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 15,
        "question": "What does RADIUS provide in network security?",
        "options": ["File encryption", "Centralized authentication", "Malware detection", "DDoS protection"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 16,
        "question": "Which command is used to display the routing table on Windows?",
        "options": ["route print", "ipconfig /showroutes", "netstat -r", "ip route show"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 17,
        "question": "What is a zero-day vulnerability?",
        "options": ["A bug with no known fix", "A vulnerability with no known exploit", "A vulnerability with no patch", "A vulnerability requiring zero knowledge to exploit"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 18,
        "question": "What does NAT stand for?",
        "options": ["Network Address Translation", "Network Access Test", "Network Authentication Token", "Network Adapter Type"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 19,
        "question": "Which protocol provides end-to-end encryption for VoIP?",
        "options": ["SIP", "SRTP", "RTP", "H.323"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 20,
        "question": "What is the purpose of a DMZ?",
        "options": ["Isolate internal networks", "Provide an isolated subnet for public-facing services", "Encrypt all traffic", "Block all external access"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 21,
        "question": "Which wireless standard operates at 5 GHz?",
        "options": ["802.11b", "802.11g", "802.11n", "802.11ac"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 22,
        "question": "What does DDoS stand for?",
        "options": ["Distributed Denial of Service", "Dynamic Data Operating System", "Direct Disk Operating System", "Domain Directory Operating System"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 23,
        "question": "Which layer of the OSI model does IP operate at?",
        "options": ["Layer 2", "Layer 3", "Layer 4", "Layer 5"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 24,
        "question": "What is social engineering?",
        "options": ["Physical security measures", "Manipulating people to reveal sensitive information", "Hacking through social media", "Network architecture"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 25,
        "question": "What does VLAN stand for?",
        "options": ["Virtual LAN", "Variable LAN", "Verified LAN", "Value LAN"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 26,
        "question": "Which protocol provides dynamic routing in IPv4 networks?",
        "options": ["OSPF", "ARP", "ICMP", "FTP"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 27,
        "question": "What is the default subnet mask for a Class C network?",
        "options": ["255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.255"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 28,
        "question": "Which port does FTP use by default?",
        "options": ["20", "21", "22", "25"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 29,
        "question": "What does SSL/TLS encrypt at the transport layer?",
        "options": ["Application data", "Network headers", "Both application data and headers", "Only email"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 30,
        "question": "Which wireless security standard uses TKIP?",
        "options": ["WEP", "WPA", "WPA2", "WPA3"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 31,
        "question": "What is the purpose of a MAC address?",
        "options": ["Route packets", "Identify devices on a local network", "Encrypt data", "Authenticate users"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 32,
        "question": "Which attack intercepts communication between two parties?",
        "options": ["Replay attack", "Man-in-the-middle attack", "Brute force attack", "SQL injection"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 33,
        "question": "What is a honeypot?",
        "options": ["A wireless access point", "A decoy system to detect attacks", "A type of firewall", "A VPN server"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 34,
        "question": "Which protocol is used for network time synchronization?",
        "options": ["SNTP", "NTP", "SMTP", "HTTP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 35,
        "question": "What does HTTPS ensure over HTTP?",
        "options": ["Faster transmission", "Better compression", "Encryption and authentication", "Lower latency"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 36,
        "question": "Which cable type is used for Ethernet connections?",
        "options": ["Coaxial", "Twisted pair", "Fiber optic", "All of the above"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 37,
        "question": "What is a ping flood attack?",
        "options": ["Overwhelming a target with ICMP packets", "Password cracking", "Website defacement", "Email spoofing"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 38,
        "question": "Which port does SMTP use for email sending?",
        "options": ["25", "80", "143", "993"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 39,
        "question": "What does IDS stand for?",
        "options": ["Intrusion Detection System", "Internet Domain Service", "Internal Data Storage", "Integrated Directory Service"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 40,
        "question": "Which network topology connects all devices to a central point?",
        "options": ["Bus", "Ring", "Star", "Mesh"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 41,
        "question": "What type of security control is antivirus software?",
        "options": ["Administrative", "Physical", "Technical", "None of the above"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 42,
        "question": "Which protocol provides link-state routing?",
        "options": ["RIP", "EIGRP", "OSPF", "BGP"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 43,
        "question": "What is ransomware?",
        "options": ["A type of firewall", "Malware that encrypts files for ransom", "Network monitoring tool", "VPN protocol"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 44,
        "question": "Which bandwidth technology uses copper telephone lines?",
        "options": ["Cable", "DSL", "Fiber", "Satellite"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 45,
        "question": "What does CSRF stand for?",
        "options": ["Cross-Site Request Forgery", "Computer System Resource Framework", "Centralized Security Response Function", "Cybersecurity Risk Framework"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 46,
        "question": "Which layer of the OSI model handles routing?",
        "options": ["Transport", "Network", "Data Link", "Physical"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 47,
        "question": "What is a botnet?",
        "options": ["A type of network cable", "Network of compromised devices", "Cloud storage service", "Email protocol"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 48,
        "question": "Which command shows active network connections?",
        "options": ["ping", "tracert", "netstat", "ipconfig"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 49,
        "question": "What does PKI provide?",
        "options": ["Network routing", "Digital certificates and encryption", "Email services", "DNS resolution"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 50,
        "question": "Which wireless frequency does 802.11n support?",
        "options": ["2.4 GHz only", "5 GHz only", "Both 2.4 and 5 GHz", "900 MHz"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 51,
        "question": "What is the CIA triad in security?",
        "options": ["Control, Integrity, Access", "Central Intelligence Agency", "Confidentiality, Integrity, Availability", "Certificate, Identity, Authority"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 52,
        "question": "Which protocol does VoIP typically use?",
        "options": ["HTTP", "SIP", "FTP", "DNS"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 53,
        "question": "What does NAC stand for?",
        "options": ["Network Access Control", "Network Authentication Certificate", "National Advisory Council", "Network Address Configuration"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 54,
        "question": "Which port does DHCP use?",
        "options": ["53", "67", "80", "443"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 55,
        "question": "What is privilege escalation?",
        "options": ["Improving network speed", "Gaining higher access than authorized", "Updating firmware", "Configuring routers"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 56,
        "question": "Which device operates at Layer 3 of the OSI model?",
        "options": ["Switch", "Hub", "Router", "Repeater"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 57,
        "question": "What does ARP poisoning involve?",
        "options": ["Sending malicious ARP messages", "Blocking ARP traffic", "Disabling ARP", "Encrypting ARP packets"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 58,
        "question": "Which IPv6 address type is similar to IPv4 private addresses?",
        "options": ["Link-local", "Unique local", "Global unicast", "Multicast"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 59,
        "question": "What is two-factor authentication?",
        "options": ["Two passwords", "Two user accounts", "Two different authentication methods", "Two logins required"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 60,
        "question": "Which cable type is immune to EMI?",
        "options": ["UTP", "STP", "Coaxial", "Fiber optic"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 61,
        "question": "What does SIEM provide?",
        "options": ["Network performance monitoring", "Security event aggregation and analysis", "Email encryption", "Cloud storage"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 62,
        "question": "Which DNS record type maps hostname to IPv4?",
        "options": ["A", "AAAA", "CNAME", "MX"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 63,
        "question": "What is a rainbow table used for?",
        "options": ["Network diagramming", "Password cracking", "Data visualization", "Traffic analysis"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 64,
        "question": "Which protocol provides secure file transfer?",
        "options": ["FTP", "SFTP", "TFTP", "HTTP"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 65,
        "question": "What is asymmetric encryption?",
        "options": ["Same key for encryption and decryption", "Different keys for encryption and decryption", "No encryption", "Weak encryption"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 66,
        "question": "Which wireless standard has the fastest theoretical speed?",
        "options": ["802.11b", "802.11g", "802.11n", "802.11ac"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 67,
        "question": "What does IPS stand for?",
        "options": ["Intrusion Prevention System", "Internet Protocol Service", "Internal Process Security", "Integrated Platform Service"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 68,
        "question": "Which port does Telnet use?",
        "options": ["21", "22", "23", "25"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 69,
        "question": "What is defense in depth?",
        "options": ["Multiple layers of security", "Single firewall", "Anti-virus only", "Network segmentation only"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 70,
        "question": "Which command tests network connectivity?",
        "options": ["nslookup", "ping", "tracert", "ipconfig"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 71,
        "question": "What does OWASP focus on?",
        "options": ["Network protocols", "Web application security", "Hardware security", "Email security"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 72,
        "question": "Which protocol provides automatic IP configuration?",
        "options": ["DNS", "DHCP", "SNMP", "FTP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 73,
        "question": "What is a backdoor in security?",
        "options": ["Firewall rule", "Unauthorized access method", "VPN tunnel", "Proxy server"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 74,
        "question": "Which port does POP3 use for email retrieval?",
        "options": ["110", "143", "993", "995"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 75,
        "question": "What does hashing provide?",
        "options": ["Encryption", "Data integrity verification", "Network routing", "File compression"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 76,
        "question": "Which network device regenerates signals?",
        "options": ["Hub", "Switch", "Router", "Repeater"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 77,
        "question": "What is shoulder surfing?",
        "options": ["Physical eavesdropping", "Looking over someone's shoulder to steal information", "Network monitoring", "Social engineering attack"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 78,
        "question": "Which IPv6 address is link-local?",
        "options": ["2001:db8::1", "fe80::1", "ff02::1", "::1"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 79,
        "question": "What does XSS stand for?",
        "options": ["External System Security", "Cross-Site Scripting", "Extended Security Standard", "X.509 Security Service"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 80,
        "question": "Which protocol resolves hostnames to IP addresses?",
        "options": ["DHCP", "DNS", "ARP", "SNMP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 81,
        "question": "What is a certificate authority?",
        "options": ["Network router", "Entity that issues digital certificates", "Firewall", "Server"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 82,
        "question": "Which port does LDAP use?",
        "options": ["88", "389", "443", "636"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 83,
        "question": "What is penetration testing?",
        "options": ["Simulated attack on a system", "Network monitoring", "Firewall configuration", "Antivirus scanning"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 84,
        "question": "Which cable standard supports 10 Gbps over copper?",
        "options": ["Cat 5e", "Cat 6", "Cat 6a", "Cat 7"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 85,
        "question": "What does RBAC stand for?",
        "options": ["Role-Based Access Control", "Router-Based Authentication Certificate", "Remote Backup and Archive", "Real-time Bandwidth Allocation Control"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 86,
        "question": "Which protocol is used for remote desktop access?",
        "options": ["VNC", "RDP", "SSH", "Telnet"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 87,
        "question": "What is bluejacking?",
        "options": ["WiFi attack", "Bluetooth spam", "Email phishing", "DNS spoofing"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 88,
        "question": "Which wireless encryption is weakest?",
        "options": ["WEP", "WPA", "WPA2", "WPA3"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 89,
        "question": "What does MTTR stand for?",
        "options": ["Mean Time To Resolution", "Maximum Throughput Transfer Rate", "Multi-Tenant Transaction Record", "Message Type Transfer Request"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 90,
        "question": "Which port does SNMP use?",
        "options": ["161", "162", "445", "514"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 91,
        "question": "What is a logic bomb?",
        "options": ["Physical device", "Malware triggered by specific conditions", "Network protocol", "Firewall rule"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 92,
        "question": "Which WAN technology uses cell towers?",
        "options": ["DSL", "Cable", "Cellular", "Satellite"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 93,
        "question": "What does TLS provide?",
        "options": ["File transfer", "Encrypted communication", "Network routing", "DNS resolution"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 94,
        "question": "Which port does IMAP secure (IMAPS) use?",
        "options": ["143", "993", "995", "110"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 95,
        "question": "What is whaling in cybersecurity?",
        "options": ["Attacking executives", "Large-scale DDoS", "Mass malware distribution", "Database attacks"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 96,
        "question": "Which network topology has no single point of failure?",
        "options": ["Star", "Bus", "Ring", "Mesh"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 97,
        "question": "What does APIPA provide?",
        "options": ["Public IP addresses", "Automatic private IP addressing when DHCP fails", "Routed networks", "DNS resolution"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 98,
        "question": "Which algorithm provides digital signatures?",
        "options": ["AES", "RSA", "MD5", "SHA-1"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 99,
        "question": "What port does LDAPS use?",
        "options": ["389", "636", "3268", "3269"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 100,
        "question": "What is a Trojan horse?",
        "options": ["Malware disguised as legitimate software", "Network scanner", "Encryption tool", "Proxy server"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 101,
        "question": "Which port does RDP use for remote desktop?",
        "options": ["21", "23", "3389", "443"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 102,
        "question": "What is a rootkit?",
        "options": ["Network monitoring tool", "Malware that hides its presence", "Firewall configuration", "Encryption standard"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 103,
        "question": "Which IPv4 class is used for multicast?",
        "options": ["Class A", "Class B", "Class C", "Class D"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 104,
        "question": "What does MAC flooding attack a switch with?",
        "options": ["ICMP packets", "DNS queries", "Fake MAC addresses", "HTTP requests"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 105,
        "question": "Which protocol provides QoS for VoIP?",
        "options": ["ICMP", "IGMP", "RTP", "FTP"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 106,
        "question": "What is a keylogger?",
        "options": ["Firewall", "Hardware or software that records keystrokes", "VPN server", "Proxy"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 107,
        "question": "Which command traces the path packets take?",
        "options": ["ping", "ipconfig", "tracert", "netstat"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 108,
        "question": "What does DLP stand for?",
        "options": ["Data Loss Prevention", "Dynamic Link Protocol", "Distributed Load Proxy", "Domain Level Policy"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 109,
        "question": "Which wireless standard operates only at 2.4 GHz?",
        "options": ["802.11a", "802.11b", "802.11ac", "802.11n"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 110,
        "question": "What is session hijacking?",
        "options": ["Stealing cookies to impersonate a user", "Breaking into physical server room", "Changing DNS records", "Blocking network traffic"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 111,
        "question": "Which network device is also called a multiport repeater?",
        "options": ["Router", "Hub", "Switch", "Bridge"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 112,
        "question": "What does IOC stand for in security?",
        "options": ["Internet of Connections", "Indicators of Compromise", "Internal Operations Center", "Integrated Operations Control"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 113,
        "question": "Which protocol provides secure remote access to network devices?",
        "options": ["Telnet", "SSH", "FTP", "HTTP"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 114,
        "question": "What is a watering hole attack?",
        "options": ["Infecting a website frequented by targets", "DNS cache poisoning", "Port scanning", "Brute force attack"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 115,
        "question": "Which IPv6 transition technology tunnels IPv6 over IPv4?",
        "options": ["Dual-stack", "6to4", "Teredo", "All of the above"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 116,
        "question": "What does BYOD stand for?",
        "options": ["Bring Your Own Device", "Backup Your Own Data", "Build Your Own Database", "Buy Your Own Domain"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 117,
        "question": "Which wireless security issue does weak IV vectors affect?",
        "options": ["WPA2", "WEP", "WPA3", "WPA"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 118,
        "question": "What is a VLAN trunk?",
        "options": ["Point-to-point link carrying multiple VLANs", "Physical cable", "Network topology", "Security protocol"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 119,
        "question": "What does GDPR regulate?",
        "options": ["Network protocols", "Data privacy and protection", "Encryption standards", "Router configurations"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 120,
        "question": "Which DNS record maps domain to another domain?",
        "options": ["A", "MX", "CNAME", "PTR"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 121,
        "question": "What is tailgating in physical security?",
        "options": ["Following an authorized person through access control", "Network attack", "Email spoofing", "DNS poisoning"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 122,
        "question": "Which protocol provides neighbor discovery in IPv6?",
        "options": ["ARP", "NDP", "ICMP", "IGMP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 123,
        "question": "What does SDN stand for?",
        "options": ["Secure Data Network", "Software Defined Network", "System Defense Network", "Structured Database Network"],
        "correct": 1,
        "topic": "Network+/Security+"
    },
    {
        "id": 124,
        "question": "Which attack uses AI or automated tools to bypass CAPTCHA?",
        "options": ["Social engineering", "CAPTCHA bypass", "SQL injection", "DDoS"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 125,
        "question": "What is BGP?",
        "options": ["Border Gateway Protocol for internet routing", "Basic Gateway Protocol", "Broadcast Gateway Protocol", "Backup Gateway Protocol"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 126,
        "question": "What does NIST provide for security?",
        "options": ["Network hardware", "Security frameworks and standards", "Firewall software", "VPN solutions"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 127,
        "question": "Which port does TFTP use?",
        "options": ["20", "21", "69", "22"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 128,
        "question": "What is a baseline in security?",
        "options": ["Network cable type", "Accepted security configuration standard", "Firewall rule", "Router firmware"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 129,
        "question": "Which wireless standard has the longest range?",
        "options": ["802.11ac", "802.11n", "802.11g", "802.11b"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 130,
        "question": "What does SOAR stand for?",
        "options": ["Secure Operations and Response", "Security Orchestration, Automation and Response", "System Operations and Recovery", "Structured Operations and Roles"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 131,
        "question": "Which routing protocol uses hop count as metric?",
        "options": ["OSPF", "RIP", "BGP", "EIGRP"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 132,
        "question": "What is a Faraday cage used for?",
        "options": ["EMI shielding", "Network wiring", "Cable organization", "Physical security"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 133,
        "question": "Which protocol provides load balancing?",
        "options": ["RIP", "HSRP", "BGP", "OSPF"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 134,
        "question": "What does IR stand for in incident response?",
        "options": ["Internal Response", "Incident Response", "Intrusion Recovery", "Information Retrieval"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 135,
        "question": "Which network topology uses a token passing method?",
        "options": ["Bus", "Ring", "Star", "Mesh"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 136,
        "question": "What is tarpitting in network security?",
        "options": ["Delaying malicious connections", "Encrypting data", "Firewall configuration", "VPN setup"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 137,
        "question": "Which IPv4 address range is Class A?",
        "options": ["128-191", "192-223", "1-126", "224-239"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 138,
        "question": "What does CSP stand for in web security?",
        "options": ["Content Security Policy", "Computer Security Protocol", "Centralized Security Platform", "Cryptographic Security Process"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 139,
        "question": "Which wireless encryption uses CCMP?",
        "options": ["WEP", "WPA", "WPA2", "WPA3"],
        "correct": 2,
        "topic": "Security+"
    },
    {
        "id": 140,
        "question": "What is a collision domain?",
        "options": ["Network where frames can collide", "Security zone", "VLAN segment", "Firewall rule"],
        "correct": 0,
        "topic": "Network+"
    },
    {
        "id": 141,
        "question": "What does MITM stand for?",
        "options": ["Man-In-The-Middle", "Machine Interoperability Testing Module", "Modern Internet Technology Management", "Multi-Instance Transaction Manager"],
        "correct": 0,
        "topic": "Security+"
    },
    {
        "id": 142,
        "question": "Which protocol provides port mirroring on switches?",
        "options": ["SNMP", "SPAN", "RSPAN", "ERSPAN"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 143,
        "question": "What is a secure coding practice?",
        "options": ["Hard-coding passwords", "Input validation", "Disabling authentication", "Using plain text protocols"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 144,
        "question": "Which IPv6 address type is multicast?",
        "options": ["Unicast", "Multicast", "Anycast", "Broadcast"],
        "correct": 1,
        "topic": "Network+"
    },
    {
        "id": 145,
        "question": "What does SCADA control?",
        "options": ["Network protocols", "Industrial control systems", "Firewall rules", "DNS records"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 146,
        "question": "Which cable type has the best distance performance?",
        "options": ["Cat 5", "Cat 5e", "Cat 6", "Cat 6a"],
        "correct": 3,
        "topic": "Network+"
    },
    {
        "id": 147,
        "question": "What is a buffer overflow attack?",
        "options": ["Network flooding", "Exploiting memory allocation", "Password cracking", "DNS spoofing"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 148,
        "question": "Which wireless standard has beamforming?",
        "options": ["802.11b", "802.11g", "802.11n", "802.11ac"],
        "correct": 2,
        "topic": "Network+"
    },
    {
        "id": 149,
        "question": "What does SOX compliance regulate?",
        "options": ["Network security", "Financial data integrity", "Email encryption", "VPN configurations"],
        "correct": 1,
        "topic": "Security+"
    },
    {
        "id": 150,
        "question": "Which protocol provides proxy auto-configuration?",
        "options": ["PPTP", "PAC", "L2TP", "SSL"],
        "correct": 1,
        "topic": "Network+/Security+"
    }
]

# PenTest+ focused question bank
PENTEST_QUESTIONS = [
    {
        "id": 1,
        "question": "Which Nmap flag performs a SYN (half-open) scan?",
        "options": ["-sT", "-sS", "-sU", "-sA"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 2,
        "question": "What does OSINT stand for?",
        "options": ["Open Source Intelligence", "Operational Security Intelligence", "Online Security Information Tool", "Offensive Security Intercept Network"],
        "correct": 0,
        "topic": "Reconnaissance"
    },
    {
        "id": 3,
        "question": "Which tool is primarily used for web application proxy and interception?",
        "options": ["Wireshark", "Metasploit", "Burp Suite", "Nessus"],
        "correct": 2,
        "topic": "Web Application"
    },
    {
        "id": 4,
        "question": "What is the purpose of a pentest scoping document?",
        "options": ["List all known vulnerabilities", "Define boundaries and rules of engagement", "Document post-exploitation findings", "Enumerate network hosts"],
        "correct": 1,
        "topic": "Planning"
    },
    {
        "id": 5,
        "question": "Which Metasploit command searches for a specific exploit module?",
        "options": ["use", "search", "find", "exploit"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 6,
        "question": "What type of SQL injection sends different queries to infer data without direct output?",
        "options": ["Error-based", "Union-based", "Blind", "Out-of-band"],
        "correct": 2,
        "topic": "Web Application"
    },
    {
        "id": 7,
        "question": "Which tool is used to crack password hashes offline?",
        "options": ["Hydra", "John the Ripper", "Aircrack-ng", "Nikto"],
        "correct": 1,
        "topic": "Password Attacks"
    },
    {
        "id": 8,
        "question": "What does pivoting allow a pentester to do?",
        "options": ["Escalate privileges locally", "Access internal networks through a compromised host", "Capture network traffic", "Scan for open ports"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 9,
        "question": "Which reconnaissance technique gathers information without directly interacting with the target?",
        "options": ["Active reconnaissance", "Passive reconnaissance", "Social engineering", "Port scanning"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 10,
        "question": "What is the default port for the Metasploit listener (reverse TCP meterpreter)?",
        "options": ["4444", "1337", "8080", "443"],
        "correct": 0,
        "topic": "Exploitation"
    },
    {
        "id": 11,
        "question": "Which tool is used for automated web vulnerability scanning?",
        "options": ["Nmap", "Nikto", "Netcat", "Nessus"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 12,
        "question": "What is a reverse shell?",
        "options": ["The attacker connects to the target", "The target connects back to the attacker", "A shell protected by encryption", "A shell running as root"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 13,
        "question": "Which command in Meterpreter elevates privileges on Windows?",
        "options": ["privesc", "getsystem", "elevate", "sudo"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 14,
        "question": "What does CVE stand for?",
        "options": ["Common Vulnerability Enumeration", "Common Vulnerabilities and Exposures", "Cyber Vulnerability Exploit", "Critical Vulnerability Entry"],
        "correct": 1,
        "topic": "Vulnerability Management"
    },
    {
        "id": 15,
        "question": "Which Nmap flag detects service versions running on open ports?",
        "options": ["-O", "-sV", "-A", "-p"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 16,
        "question": "What is the purpose of a Rules of Engagement (ROE) document?",
        "options": ["List exploits to use", "Define what is and isn't allowed during the pentest", "Summarize findings", "Document network topology"],
        "correct": 1,
        "topic": "Planning"
    },
    {
        "id": 17,
        "question": "Which tool performs online password brute-forcing against services like SSH and FTP?",
        "options": ["John the Ripper", "Hashcat", "Hydra", "Mimikatz"],
        "correct": 2,
        "topic": "Password Attacks"
    },
    {
        "id": 18,
        "question": "What is a buffer overflow vulnerability?",
        "options": ["Too much data sent to a network buffer", "Writing data beyond a buffer's boundary into adjacent memory", "Overloading a server with requests", "Corrupting a firewall's buffer table"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 19,
        "question": "Which OWASP Top 10 category covers SQL injection?",
        "options": ["Broken Authentication", "Injection", "Security Misconfiguration", "Sensitive Data Exposure"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 20,
        "question": "What does the Nmap flag -O attempt to determine?",
        "options": ["Open ports", "Operating system", "Output format", "Owner of the IP"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 21,
        "question": "Which tool extracts credentials from Windows memory?",
        "options": ["Mimikatz", "Hashcat", "Responder", "BloodHound"],
        "correct": 0,
        "topic": "Post-Exploitation"
    },
    {
        "id": 22,
        "question": "What is the goal of privilege escalation?",
        "options": ["Gain access to more systems", "Obtain higher permission levels on a compromised system", "Exfiltrate data faster", "Bypass network firewalls"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 23,
        "question": "Which attack captures NTLMv2 hashes by poisoning LLMNR/NBT-NS traffic?",
        "options": ["Pass-the-hash", "Responder", "Kerberoasting", "ARP spoofing"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 24,
        "question": "What does XSS allow an attacker to do?",
        "options": ["Execute code on the server", "Inject malicious scripts into pages viewed by other users", "Bypass SQL authentication", "Intercept encrypted traffic"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 25,
        "question": "Which phase of a pentest involves running exploits against identified vulnerabilities?",
        "options": ["Reconnaissance", "Scanning", "Exploitation", "Reporting"],
        "correct": 2,
        "topic": "Methodology"
    },
    {
        "id": 26,
        "question": "What is a bind shell?",
        "options": ["The attacker's machine opens a port and listens", "The target opens a port and the attacker connects to it", "A shell bound to a specific user", "An encrypted reverse shell"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 27,
        "question": "Which tool maps Active Directory relationships to identify attack paths?",
        "options": ["Mimikatz", "BloodHound", "Responder", "CrackMapExec"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 28,
        "question": "What is Kerberoasting?",
        "options": ["Brute forcing Kerberos passwords", "Requesting and cracking service tickets offline", "Passing Kerberos tickets to authenticate", "Forging Kerberos tickets"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 29,
        "question": "Which file on Linux stores hashed passwords?",
        "options": ["/etc/passwd", "/etc/shadow", "/etc/creds", "/var/passwords"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 30,
        "question": "What is a Golden Ticket attack?",
        "options": ["Forging a Kerberos TGT using the KRBTGT hash", "Stealing a domain admin password", "Escalating privileges via misconfigured services", "Forging SAML assertions"],
        "correct": 0,
        "topic": "Active Directory"
    },
    {
        "id": 31,
        "question": "Which tool is commonly used for network packet capture and analysis?",
        "options": ["Metasploit", "Wireshark", "Nikto", "sqlmap"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 32,
        "question": "What does LFI (Local File Inclusion) allow an attacker to do?",
        "options": ["Upload files to the server", "Read local files on the server via the web application", "Execute remote code directly", "Bypass authentication"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 33,
        "question": "Which Nmap scan type is used for UDP ports?",
        "options": ["-sS", "-sT", "-sU", "-sX"],
        "correct": 2,
        "topic": "Scanning"
    },
    {
        "id": 34,
        "question": "What is the purpose of a pentest report's executive summary?",
        "options": ["Technical vulnerability details for IT staff", "High-level risk overview for non-technical stakeholders", "Step-by-step exploit instructions", "Full network topology diagram"],
        "correct": 1,
        "topic": "Reporting"
    },
    {
        "id": 35,
        "question": "Which tool is used to automate SQL injection testing?",
        "options": ["Nikto", "sqlmap", "Burp Suite", "Nessus"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 36,
        "question": "What is a pass-the-hash attack?",
        "options": ["Cracking a hash offline", "Using a captured NTLM hash to authenticate without knowing the plaintext password", "Sending hashed data over the network", "Bypassing hash verification"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 37,
        "question": "Which Nmap script engine category checks for known vulnerabilities?",
        "options": ["discovery", "safe", "vuln", "default"],
        "correct": 2,
        "topic": "Scanning"
    },
    {
        "id": 38,
        "question": "What does enumeration involve in a pentest?",
        "options": ["Cracking passwords", "Extracting detailed information about systems and services", "Delivering payloads", "Writing the final report"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 39,
        "question": "Which wireless attack captures a WPA2 handshake to crack offline?",
        "options": ["Deauthentication attack", "WPS pin attack", "Evil twin attack", "PMKID attack"],
        "correct": 0,
        "topic": "Wireless"
    },
    {
        "id": 40,
        "question": "What is the purpose of a C2 (Command and Control) server?",
        "options": ["Host exploit code", "Manage and communicate with compromised hosts", "Store stolen credentials", "Scan for vulnerabilities"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 41,
        "question": "Which technique involves sending a phishing email with a malicious attachment?",
        "options": ["Vishing", "Spear phishing", "Smishing", "Tailgating"],
        "correct": 1,
        "topic": "Social Engineering"
    },
    {
        "id": 42,
        "question": "What does RFI (Remote File Inclusion) do?",
        "options": ["Reads files stored locally", "Includes a remote file from an attacker-controlled server", "Redirects file downloads", "Injects code into local files"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 43,
        "question": "Which tool cracks WPA/WPA2 wireless passwords using a wordlist?",
        "options": ["Wireshark", "Kismet", "Aircrack-ng", "Nmap"],
        "correct": 2,
        "topic": "Wireless"
    },
    {
        "id": 44,
        "question": "What is the CVSS score range for a Critical severity vulnerability?",
        "options": ["7.0–8.9", "9.0–10.0", "4.0–6.9", "0.1–3.9"],
        "correct": 1,
        "topic": "Vulnerability Management"
    },
    {
        "id": 45,
        "question": "What does 'living off the land' mean in post-exploitation?",
        "options": ["Using custom malware", "Using built-in OS tools to avoid detection", "Exfiltrating data via DNS", "Exploiting physical access"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 46,
        "question": "Which protocol does Responder abuse to capture credentials?",
        "options": ["DNS", "LLMNR/NBT-NS", "ICMP", "Kerberos"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 47,
        "question": "What is the purpose of the /etc/passwd file on Linux?",
        "options": ["Store password hashes", "Store user account information", "List sudo permissions", "Define network interfaces"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 48,
        "question": "Which attack type targets a specific individual or organization with customized phishing?",
        "options": ["Whaling", "Spear phishing", "Clone phishing", "Vishing"],
        "correct": 1,
        "topic": "Social Engineering"
    },
    {
        "id": 49,
        "question": "What is the purpose of Nmap's -A flag?",
        "options": ["Scan all ports", "Enable OS detection, version detection, script scanning, and traceroute", "Anonymous scan", "Aggressive UDP scan"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 50,
        "question": "Which Metasploit payload type provides an interactive session over the network?",
        "options": ["singles", "stagers", "meterpreter", "shellcode"],
        "correct": 2,
        "topic": "Exploitation"
    },
    {
        "id": 51,
        "question": "What is IDOR (Insecure Direct Object Reference)?",
        "options": ["Injecting malicious code into a database", "Accessing resources by manipulating object references without authorization", "Redirecting HTTP to HTTPS", "Overflowing a memory buffer"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 52,
        "question": "Which tool is used for subdomain enumeration during reconnaissance?",
        "options": ["Metasploit", "Gobuster", "Nessus", "CrackMapExec"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 53,
        "question": "What does SSRF (Server-Side Request Forgery) allow an attacker to do?",
        "options": ["Steal session cookies", "Make the server perform requests to internal resources", "Forge digital signatures", "Bypass TLS certificates"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 54,
        "question": "Which Windows command lists current user privileges?",
        "options": ["net user", "whoami /priv", "ipconfig", "tasklist"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 55,
        "question": "What is a Silver Ticket attack?",
        "options": ["Forging a TGT using KRBTGT hash", "Forging a service ticket using a service account hash", "Stealing plaintext credentials from memory", "Dumping the NTDS.dit database"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 56,
        "question": "Which tool performs SMB enumeration and exploitation on Windows networks?",
        "options": ["CrackMapExec", "Gobuster", "Aircrack-ng", "Nikto"],
        "correct": 0,
        "topic": "Network Exploitation"
    },
    {
        "id": 57,
        "question": "What is directory traversal?",
        "options": ["Listing all directories on a web server", "Navigating outside the web root using ../ sequences", "Brute forcing directory names", "Mapping the web app sitemap"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 58,
        "question": "Which hashcat attack mode uses a wordlist?",
        "options": ["Mode 1 (Combination)", "Mode 0 (Straight)", "Mode 3 (Brute force)", "Mode 6 (Hybrid)"],
        "correct": 1,
        "topic": "Password Attacks"
    },
    {
        "id": 59,
        "question": "What is the purpose of Netcat in a pentest?",
        "options": ["Crack passwords", "Establish connections, transfer files, and create shells", "Scan for vulnerabilities", "Enumerate Active Directory"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 60,
        "question": "Which technique involves adding a legitimate user to the local admin group after exploitation?",
        "options": ["Persistence", "Privilege escalation", "Lateral movement", "Exfiltration"],
        "correct": 0,
        "topic": "Post-Exploitation"
    },
    {
        "id": 61,
        "question": "What does the acronym TTP stand for in threat intelligence?",
        "options": ["Tactics, Techniques, and Procedures", "Threat, Target, and Profile", "Tools, Testing, and Penetration", "Technical Threat Parameters"],
        "correct": 0,
        "topic": "Methodology"
    },
    {
        "id": 62,
        "question": "Which attack exploits trust relationships between domains in Active Directory?",
        "options": ["Pass-the-hash", "Kerberoasting", "Domain trust abuse", "LLMNR poisoning"],
        "correct": 2,
        "topic": "Active Directory"
    },
    {
        "id": 63,
        "question": "What is the purpose of the MITRE ATT&CK framework?",
        "options": ["Document network configurations", "Catalog adversary tactics and techniques", "Rate vulnerability severity", "Define pentest legal requirements"],
        "correct": 1,
        "topic": "Methodology"
    },
    {
        "id": 64,
        "question": "Which tool creates malicious payloads for various platforms?",
        "options": ["Nmap", "msfvenom", "Nikto", "BloodHound"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 65,
        "question": "What is an evil twin attack?",
        "options": ["Cloning a MAC address", "Creating a rogue wireless AP mimicking a legitimate one", "Spoofing a DNS server", "Duplicating a web login page"],
        "correct": 1,
        "topic": "Wireless"
    },
    {
        "id": 66,
        "question": "Which Windows file contains the local SAM database hashes?",
        "options": ["C:\\Windows\\System32\\config\\SAM", "C:\\Windows\\System32\\credentials.db", "C:\\Users\\All Users\\passwords.txt", "C:\\Windows\\NTDS\\ntds.dit"],
        "correct": 0,
        "topic": "Post-Exploitation"
    },
    {
        "id": 67,
        "question": "What does a pentest debrief involve?",
        "options": ["Running final scans", "Presenting findings to the client after the engagement", "Cleaning up backdoors", "Submitting a bug bounty"],
        "correct": 1,
        "topic": "Reporting"
    },
    {
        "id": 68,
        "question": "Which technique abuses scheduled tasks or cron jobs for persistence?",
        "options": ["Token impersonation", "Scheduled task/cron persistence", "DLL injection", "Kernel exploitation"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 69,
        "question": "What is the purpose of recon-ng?",
        "options": ["Exploit framework", "OSINT and web reconnaissance framework", "Password cracking", "Wireless packet injection"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 70,
        "question": "Which HTTP method is most commonly tested for CSRF vulnerabilities?",
        "options": ["GET", "POST", "DELETE", "OPTIONS"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 71,
        "question": "What is lateral movement in a pentest?",
        "options": ["Escalating local privileges", "Moving from one compromised system to others in the network", "Exfiltrating data to an external server", "Establishing a reverse shell"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 72,
        "question": "Which tool enumerates web directories and files via brute force?",
        "options": ["Wireshark", "Gobuster", "Responder", "Impacket"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 73,
        "question": "What is a stored XSS attack?",
        "options": ["Script injected into a URL parameter", "Script permanently stored on the server and executed by all visitors", "Script injected into a DOM element client-side", "Script embedded in a PDF"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 74,
        "question": "Which document formally authorizes a pentest engagement?",
        "options": ["NDA", "Statement of Work / Authorization letter", "CVE report", "Pentest report"],
        "correct": 1,
        "topic": "Planning"
    },
    {
        "id": 75,
        "question": "What does Impacket's secretsdump.py extract?",
        "options": ["SSL certificates", "Password hashes from SAM, LSA, and NTDS.dit", "Network traffic captures", "Browser cookies"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 76,
        "question": "Which attack sends crafted packets to crash or gain control of an application?",
        "options": ["Buffer overflow", "SQL injection", "CSRF", "Clickjacking"],
        "correct": 0,
        "topic": "Exploitation"
    },
    {
        "id": 77,
        "question": "What is the purpose of a deauthentication attack in wireless testing?",
        "options": ["Crack WPA passwords directly", "Force clients to reconnect to capture the handshake", "Bypass MAC filtering", "Inject traffic into a WPA2 network"],
        "correct": 1,
        "topic": "Wireless"
    },
    {
        "id": 78,
        "question": "Which Linux command finds SUID binaries that could be abused for privilege escalation?",
        "options": ["find / -perm -4000 2>/dev/null", "ls -la /etc/shadow", "ps aux | grep root", "cat /etc/sudoers"],
        "correct": 0,
        "topic": "Post-Exploitation"
    },
    {
        "id": 79,
        "question": "What is the Lockheed Martin Cyber Kill Chain's first stage?",
        "options": ["Weaponization", "Reconnaissance", "Delivery", "Installation"],
        "correct": 1,
        "topic": "Methodology"
    },
    {
        "id": 80,
        "question": "Which tool from Impacket facilitates SMB relay attacks?",
        "options": ["secretsdump.py", "ntlmrelayx.py", "psexec.py", "GetSPN.py"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 81,
        "question": "What type of pentest provides no prior knowledge of the target environment?",
        "options": ["White box", "Gray box", "Black box", "Crystal box"],
        "correct": 2,
        "topic": "Methodology"
    },
    {
        "id": 82,
        "question": "Which attack intercepts and potentially alters communication between two parties?",
        "options": ["Replay attack", "Man-in-the-middle (MITM)", "Brute force", "SQL injection"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 83,
        "question": "What is a pentest finding's remediation section used for?",
        "options": ["Demonstrate impact of the vulnerability", "Provide steps to fix the identified issue", "Rate the vulnerability severity", "List affected systems"],
        "correct": 1,
        "topic": "Reporting"
    },
    {
        "id": 84,
        "question": "Which tool captures 802.11 wireless traffic for analysis?",
        "options": ["Aircrack-ng", "Airodump-ng", "Aireplay-ng", "Airbase-ng"],
        "correct": 1,
        "topic": "Wireless"
    },
    {
        "id": 85,
        "question": "What does the Nmap flag --script=smb-vuln-ms17-010 check for?",
        "options": ["SMB brute force", "EternalBlue vulnerability (MS17-010)", "SMB signing status", "Open SMB shares"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 86,
        "question": "Which post-exploitation technique hides malicious processes in legitimate ones?",
        "options": ["DLL hijacking", "Process hollowing", "Token impersonation", "Scheduled tasks"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 87,
        "question": "What is WHOIS used for during reconnaissance?",
        "options": ["Scan open ports", "Look up domain registration and ownership information", "Enumerate DNS records", "Map network routes"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 88,
        "question": "Which type of XSS is triggered by manipulating the browser DOM without hitting the server?",
        "options": ["Stored XSS", "Reflected XSS", "DOM-based XSS", "Persistent XSS"],
        "correct": 2,
        "topic": "Web Application"
    },
    {
        "id": 89,
        "question": "What is the purpose of an NDA in a pentest engagement?",
        "options": ["Grant legal authorization", "Protect confidential information shared between parties", "Define payment terms", "List the testing methodology"],
        "correct": 1,
        "topic": "Planning"
    },
    {
        "id": 90,
        "question": "Which attack uses precomputed hash tables to crack passwords?",
        "options": ["Brute force", "Dictionary attack", "Rainbow table attack", "Credential stuffing"],
        "correct": 2,
        "topic": "Password Attacks"
    },
    {
        "id": 91,
        "question": "Which tool is used for SMTP enumeration to find valid email addresses?",
        "options": ["smtp-user-enum", "Gobuster", "Nessus", "BloodHound"],
        "correct": 0,
        "topic": "Reconnaissance"
    },
    {
        "id": 92,
        "question": "What is the purpose of token impersonation in Windows post-exploitation?",
        "options": ["Dump password hashes", "Steal another user's authentication token to act as them", "Inject into LSASS", "Create a reverse shell"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 93,
        "question": "Which Nmap timing template is the fastest and most aggressive?",
        "options": ["-T3", "-T4", "-T5", "-T2"],
        "correct": 2,
        "topic": "Scanning"
    },
    {
        "id": 94,
        "question": "What does UAC (User Account Control) bypass allow on Windows?",
        "options": ["Crack passwords without hashes", "Execute code with elevated privileges without a UAC prompt", "Disable Windows Firewall", "Access the SAM database"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 95,
        "question": "Which protocol is commonly exploited in PrintNightmare (CVE-2021-34527)?",
        "options": ["SMB", "Windows Print Spooler (MS-RPRN)", "RDP", "WMI"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 96,
        "question": "What does the acronym IOC stand for in incident response?",
        "options": ["Indicators of Compromise", "Internet Operations Center", "Intrusion Object Capture", "Incident Operations Command"],
        "correct": 0,
        "topic": "Methodology"
    },
    {
        "id": 97,
        "question": "Which tool is used to enumerate DNS records including subdomains?",
        "options": ["theHarvester", "dnsenum", "Gobuster", "Responder"],
        "correct": 1,
        "topic": "Reconnaissance"
    },
    {
        "id": 98,
        "question": "What is credential stuffing?",
        "options": ["Using random passwords to brute force", "Using leaked username/password pairs from other breaches to gain access", "Injecting credentials into memory", "Sniffing credentials off the wire"],
        "correct": 1,
        "topic": "Password Attacks"
    },
    {
        "id": 99,
        "question": "Which exploit was used in the WannaCry ransomware attack?",
        "options": ["BlueKeep", "EternalBlue (MS17-010)", "Heartbleed", "Shellshock"],
        "correct": 1,
        "topic": "Exploitation"
    },
    {
        "id": 100,
        "question": "What does a gray box pentest provide to the tester?",
        "options": ["No prior information", "Full source code and credentials", "Partial knowledge such as network diagrams or user-level credentials", "Physical access to hardware"],
        "correct": 2,
        "topic": "Methodology"
    },
    {
        "id": 101,
        "question": "Which command checks for sudo privileges on a Linux system?",
        "options": ["id", "sudo -l", "cat /etc/shadow", "ps aux"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 102,
        "question": "What is the purpose of port knocking?",
        "options": ["Scan all ports quickly", "Obscure open ports until a correct sequence of packets is sent", "Perform banner grabbing", "Enumerate SMB shares"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 103,
        "question": "Which attack forges ARP replies to associate the attacker's MAC with a legitimate IP?",
        "options": ["DNS spoofing", "ARP poisoning/spoofing", "VLAN hopping", "ICMP redirect"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 104,
        "question": "What is a WAF (Web Application Firewall) bypass technique?",
        "options": ["Using encrypted payloads only", "Encoding, obfuscation, or case manipulation to evade signature detection", "Sending requests over IPv6", "Using a VPN connection"],
        "correct": 1,
        "topic": "Web Application"
    },
    {
        "id": 105,
        "question": "Which Linux privilege escalation vector involves writable files in the PATH?",
        "options": ["SUID binary abuse", "PATH hijacking", "Cron job exploitation", "Kernel exploitation"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 106,
        "question": "What does the acronym CVSS stand for?",
        "options": ["Cyber Vulnerability Scoring System", "Common Vulnerability Scoring System", "Critical Vulnerability Security Standard", "Centralized Vulnerability Scan Score"],
        "correct": 1,
        "topic": "Vulnerability Management"
    },
    {
        "id": 107,
        "question": "Which DNS record type is commonly targeted to perform a zone transfer?",
        "options": ["A", "MX", "NS", "CNAME"],
        "correct": 2,
        "topic": "Reconnaissance"
    },
    {
        "id": 108,
        "question": "What is the purpose of the Metasploit 'post' modules?",
        "options": ["Set up listeners", "Perform post-exploitation tasks on a compromised session", "Generate payloads", "Scan for open services"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 109,
        "question": "Which technique injects a DLL into a running process?",
        "options": ["Process hollowing", "DLL injection", "Token impersonation", "Heap spray"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 110,
        "question": "What is the goal of data exfiltration in a pentest?",
        "options": ["Destroy target data", "Demonstrate that sensitive data can be removed from the environment", "Encrypt the target's files", "Maintain persistent access"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 111,
        "question": "Which tool performs password spraying against Active Directory?",
        "options": ["Hydra", "Kerbrute", "Mimikatz", "BloodHound"],
        "correct": 1,
        "topic": "Active Directory"
    },
    {
        "id": 112,
        "question": "What is vishing?",
        "options": ["Email phishing", "Voice-based social engineering over the phone", "SMS-based phishing", "Visual deception on a screen"],
        "correct": 1,
        "topic": "Social Engineering"
    },
    {
        "id": 113,
        "question": "Which Windows registry key is commonly checked for persistence mechanisms?",
        "options": ["HKLM\\System\\CurrentControlSet", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", "HKLM\\Software\\Policies", "HKCU\\System\\Services"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 114,
        "question": "What does the 'hashdump' Meterpreter command do?",
        "options": ["Dump browser history", "Extract Windows password hashes from the SAM database", "List running processes", "Capture keystrokes"],
        "correct": 1,
        "topic": "Post-Exploitation"
    },
    {
        "id": 115,
        "question": "Which scan type is used to identify hosts on a network without port scanning?",
        "options": ["SYN scan", "Ping sweep (-sn)", "UDP scan", "Version scan"],
        "correct": 1,
        "topic": "Scanning"
    },
    {
        "id": 116,
        "question": "What is SMB signing and why is it relevant to pentesting?",
        "options": ["Encrypts SMB sessions; prevents exploitation", "Validates SMB packet integrity; disabled by default allows relay attacks", "Authenticates SMB users with certificates", "Signs all SMB data with NTLM"],
        "correct": 1,
        "topic": "Network Exploitation"
    },
    {
        "id": 117,
        "question": "Which tool is used for phishing simulation and social engineering campaigns?",
        "options": ["SET (Social-Engineer Toolkit)", "Metasploit", "Burp Suite", "Nessus"],
        "correct": 0,
        "topic": "Social Engineering"
    },
    {
        "id": 118,
        "question": "What is the purpose of a proof of concept (PoC) in a pentest report?",
        "options": ["Define remediation steps", "Demonstrate that a vulnerability is exploitable", "List all open ports found", "Summarize the engagement scope"],
        "correct": 1,
        "topic": "Reporting"
    },
    {
        "id": 119,
        "question": "Which attack targets weak WPS PINs to retrieve the WPA key?",
        "options": ["Deauthentication attack", "WPS brute force (Reaver)", "Evil twin", "KRACK attack"],
        "correct": 1,
        "topic": "Wireless"
    },
    {
        "id": 120,
        "question": "What is the Cyber Kill Chain stage after 'Weaponization'?",
        "options": ["Reconnaissance", "Delivery", "Exploitation", "Installation"],
        "correct": 1,
        "topic": "Methodology"
    },
]

# Number of questions to randomly select for the exam
EXAM_SIZE = 20
FULL_EXAM_SIZE = 120
PENTEST_EXAM_SIZE = 85

@app.route('/')
def index():
    return render_template('index.html', exam_size=EXAM_SIZE, full_exam_size=FULL_EXAM_SIZE, pentest_exam_size=PENTEST_EXAM_SIZE)

@app.route('/start_pentest_exam', methods=['POST'])
def start_pentest_exam():
    exam_questions = random.sample(PENTEST_QUESTIONS, min(PENTEST_EXAM_SIZE, len(PENTEST_QUESTIONS)))
    session['exam_questions'] = exam_questions
    session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session['answers'] = {}
    session['exam_type'] = 'PenTest+'
    return redirect(url_for('exam'))

@app.route('/start_full_exam', methods=['POST'])
def start_full_exam():
    exam_questions = random.sample(QUESTIONS, min(FULL_EXAM_SIZE, len(QUESTIONS)))
    session['exam_questions'] = exam_questions
    session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session['answers'] = {}
    session['exam_type'] = 'Net+/Sec+ Full'
    return redirect(url_for('exam'))

@app.route('/start_exam', methods=['POST'])
def start_exam():
    exam_questions = random.sample(QUESTIONS, min(EXAM_SIZE, len(QUESTIONS)))
    session['exam_questions'] = exam_questions
    session['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    session['answers'] = {}
    session['exam_type'] = 'Net+/Sec+'
    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    if 'exam_questions' not in session:
        return redirect(url_for('index'))
    
    return render_template('exam.html', questions=session['exam_questions'])

@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    print("\n=== SUBMIT EXAM DEBUG ===")
    print(f"Method: {request.method}")
    print(f"Form data: {dict(request.form)}")
    print(f"Session before: {session.get('answers')}")
    
    if 'exam_questions' not in session:
        print("ERROR: No exam questions in session!")
        return redirect(url_for('index'))
    
    # Get user's answers
    user_answers = {}
    print(f"Form keys: {list(request.form.keys())}")
    for question_id in request.form.keys():
        try:
            user_answers[int(question_id)] = int(request.form[question_id])
            print(f"Saved: Q{question_id} = {request.form[question_id]}")
        except (ValueError, KeyError) as e:
            print(f"Error processing Q{question_id}: {e}")
            continue
    
    print(f"Total answers collected: {len(user_answers)}")
    session['answers'] = user_answers
    print(f"Session after: {session.get('answers')}")
    print("=== END DEBUG ===\n")
    
    return redirect(url_for('results'))

@app.route('/results')
def results():
    if 'exam_questions' not in session or 'answers' not in session:
        return redirect(url_for('index'))

    exam_questions = session['exam_questions']
    user_answers   = session['answers']

    # Calculate elapsed time server-side
    elapsed_seconds = 0
    if 'start_time' in session:
        start_dt = datetime.strptime(session['start_time'], '%Y-%m-%d %H:%M:%S')
        elapsed_seconds = max(0, int((datetime.now() - start_dt).total_seconds()))

    # Calculate score
    correct = 0
    total = len(exam_questions)
    question_results = []

    for question in exam_questions:
        q_id = question['id']
        user_answer = user_answers.get(q_id, None)
        is_correct = user_answer == question['correct']
        if is_correct:
            correct += 1
        question_results.append({
            'question': question['question'],
            'options': question['options'],
            'correct_answer': question['options'][question['correct']],
            'user_answer': question['options'][user_answer] if user_answer is not None else "Not answered",
            'is_correct': is_correct
        })

    score  = (correct / total) * 100
    passed = score >= 70

    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    time_display = f"{minutes:02d}:{seconds:02d}"

    # Store for leaderboard submission
    session['pending_score'] = {
        'score': score,
        'correct': correct,
        'total': total,
        'elapsed_seconds': elapsed_seconds,
        'exam_type': session.get('exam_type', 'Unknown'),
    }

    # Clear exam session data
    session.pop('exam_questions', None)
    session.pop('answers', None)
    session.pop('start_time', None)
    session.pop('exam_type', None)

    leaderboard = load_leaderboard()

    return render_template('results.html',
                           score=score,
                           correct=correct,
                           total=total,
                           passed=passed,
                           question_results=question_results,
                           time_display=time_display,
                           elapsed_seconds=elapsed_seconds,
                           leaderboard=leaderboard[:20])


@app.route('/save_score', methods=['POST'])
def save_score():
    if 'pending_score' not in session:
        return redirect(url_for('index'))

    raw = request.form.get('username', '').upper()
    username = ''.join(c for c in raw if c.isalpha())[:3]
    username = username.ljust(3, 'A')

    pending = session.pop('pending_score')
    add_leaderboard_entry(
        username,
        pending['score'],
        pending['correct'],
        pending['total'],
        pending['elapsed_seconds'],
        pending['exam_type'],
    )

    return redirect(url_for('leaderboard'))


@app.route('/leaderboard')
def leaderboard():
    entries = load_leaderboard()
    return render_template('leaderboard.html', entries=entries[:20])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

