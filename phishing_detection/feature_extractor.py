import re
import socket
import ssl
import whois
import requests
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup

def having_ip_address(url):
    try:
        ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', url)
        return -1 if ip else 1
    except:
        return -1

def url_length(url):
    if len(url) < 54:
        return 1
    elif 54 <= len(url) <= 75:
        return 0
    else:
        return -1

def shortening_service(url):
    shorteners = r"(bit\.ly|goo\.gl|tinyurl\.com|ow\.ly|is\.gd|buff\.ly|adf\.ly|t\.co)"
    return -1 if re.search(shorteners, url) else 1

def having_at_symbol(url):
    return -1 if "@" in url else 1

def double_slash_redirecting(url):
    return -1 if url.rfind('//') > 6 else 1

def prefix_suffix(domain):
    return -1 if '-' in domain else 1

def having_sub_domain(url):
    domain = urlparse(url).netloc
    dots = domain.split('.')
    if len(dots) <= 2:
        return 1
    elif len(dots) == 3:
        return 0
    else:
        return -1

def ssl_final_state(url):
    try:
        domain = urlparse(url).netloc
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain, 443))
        return 1
    except:
        return -1

def domain_registration_length(domain):
    try:
        whois_info = whois.whois(domain)
        exp_date = whois_info.expiration_date
        if isinstance(exp_date, list):
            exp_date = exp_date[0]
        if exp_date is not None:
            days = (exp_date - datetime.now()).days
            return -1 if days <= 365 else 1
        return -1
    except:
        return -1

def favicon(url):
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        for link in soup.find_all('link', rel='icon'):
            href = link.get('href')
            if href and domain not in href:
                return -1
        return 1
    except:
        return -1

def port(url):
    try:
        domain = urlparse(url).netloc
        ports = [80, 443]
        for p in ports:
            s = socket.socket()
            s.settimeout(2)
            try:
                s.connect((domain, p))
            except:
                return -1
        return 1
    except:
        return -1

def https_token(url):
    domain = urlparse(url).netloc
    return -1 if 'https' in domain else 1

def request_url(url):
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        imgs = soup.find_all('img', src=True)
        total = len(imgs)
        outside = sum(1 for img in imgs if domain not in img['src'])
        return -1 if total > 0 and (outside / total) > 0.5 else 1
    except:
        return -1

def url_of_anchor(url):
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        anchors = soup.find_all('a', href=True)
        total = len(anchors)
        unsafe = sum(1 for a in anchors if '#' in a['href'] or 'javascript' in a['href'].lower() or domain not in a['href'])
        return -1 if total > 0 and (unsafe / total) > 0.5 else 1
    except:
        return -1

def links_in_tags(url):
    try:
        domain = urlparse(url).netloc
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        metas = soup.find_all('meta', content=True)
        links = soup.find_all('link', href=True)
        scripts = soup.find_all('script', src=True)
        total = len(metas) + len(links) + len(scripts)
        unsafe = sum(1 for tag in links+scripts if domain not in tag.get('href', '') and domain not in tag.get('src', ''))
        return -1 if total > 0 and (unsafe / total) > 0.5 else 1
    except:
        return -1

def sfh(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        forms = soup.find_all('form', action=True)
        for form in forms:
            action = form.get('action')
            if action == "" or action == "about:blank":
                return -1
            elif urlparse(url).netloc not in action:
                return 0
        return 1
    except:
        return -1

def submitting_to_email(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if re.findall(r"[mail\(\)|mailto:?]", response.text) else 1
    except:
        return -1

def abnormal_url(url):
    try:
        whois_info = whois.whois(urlparse(url).netloc)
        return 1 if whois_info.domain_name else -1
    except:
        return -1

def redirect(url):
    try:
        response = requests.get(url, timeout=5)
        if len(response.history) <= 1:
            return 1
        elif len(response.history) <= 4:
            return 0
        else:
            return -1
    except:
        return -1

def on_mouseover(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if "onmouseover" in response.text else 1
    except:
        return -1

def right_click(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if re.search(r'event.button ?== ?2', response.text) else 1
    except:
        return -1

def popup_window(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if "alert(" in response.text else 1
    except:
        return -1

def iframe(url):
    try:
        response = requests.get(url, timeout=5)
        return -1 if "<iframe" in response.text.lower() else 1
    except:
        return -1

def age_of_domain(domain):
    try:
        whois_info = whois.whois(domain)
        creation_date = whois_info.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age = (datetime.now() - creation_date).days
        return -1 if age < 180 else 1
    except:
        return -1

def dns_record(domain):
    try:
        socket.gethostbyname(domain)
        return 1
    except:
        return -1

def web_traffic(domain):
    # Stubbed realistically – real Alexa/API required
    return 0

def page_rank():
    return 0

def google_index(url):
    try:
        response = requests.get(f"https://www.google.com/search?q=site:{url}", headers={'User-Agent': 'Mozilla/5.0'})
        return 1 if "did not match any documents" not in response.text else -1
    except:
        return -1

def links_pointing_to_page(url):
    return 0

def statistical_report():
    return 0

def extract_features(url):
    domain = urlparse(url).netloc
    return [
        having_ip_address(url),
        url_length(url),
        shortening_service(url),
        having_at_symbol(url),
        double_slash_redirecting(url),
        prefix_suffix(domain),
        having_sub_domain(url),
        ssl_final_state(url),
        domain_registration_length(domain),
        favicon(url),
        port(url),
        https_token(url),
        request_url(url),
        url_of_anchor(url),
        links_in_tags(url),
        sfh(url),
        submitting_to_email(url),
        abnormal_url(url),
        redirect(url),
        on_mouseover(url),
        right_click(url),
        popup_window(url),
        iframe(url),
        age_of_domain(domain),
        dns_record(domain),
        web_traffic(domain),
        page_rank(),
        google_index(url),
        links_pointing_to_page(url),
        statistical_report()
    ]
