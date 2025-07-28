# phishing_detection/feature_extractor.py

import re
import socket
import ssl
import whois
import requests
from urllib.parse import urlparse
from datetime import datetime

    """
    Extracts 30 features from a URL for KNN phishing detection.
    Returns a list of numeric values representing the features.
    """
def has_ip_address(url):
    try:
        ip = socket.gethostbyname(urlparse(url).netloc)
        return -1 if re.match(r"\d+\.\d+\.\d+\.\d+", ip) else 1
    except:
        return 1

def url_length(url):
    return -1 if len(url) >= 75 else (0 if len(url) >= 54 else 1)

def url_shortening_service(url):
    shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|tinyurl|tr\.im|is\.gd|cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc"
    return -1 if re.search(shortening_services, url) else 1

def has_at_symbol(url):
    return -1 if "@" in url else 1

def double_slash_redirecting(url):
    return -1 if url.rfind("//") > 6 else 1

def prefix_suffix(url):
    domain = urlparse(url).netloc
    return -1 if "-" in domain else 1

def sub_domains(url):
    domain = urlparse(url).netloc
    dots = domain.split(".")
    return -1 if len(dots) > 3 else (0 if len(dots) == 3 else 1)

def ssl_final_state(url):
    try:
        if urlparse(url).scheme != "https":
            return -1
        return 1
    except:
        return -1

def domain_registration_length(domain_name):
    try:
        w = whois.whois(domain_name)
        expiration_date = w.expiration_date
        creation_date = w.creation_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        age = (expiration_date - creation_date).days
        return -1 if age <= 365 else 1
    except:
        return -1

def favicon(url):
    return 1  # Skipping favicon check logic for now

def port_check(url):
    parsed = urlparse(url)
    port = parsed.port
    return -1 if port not in [80, 443, None] else 1

def https_token(url):
    domain = urlparse(url).netloc
    return -1 if 'https' in domain else 1

def request_url(): return 1
def url_of_anchor(): return 1
def links_in_tags(): return 1
def sfh(): return 1
def submitting_to_email(): return 1
def abnormal_url(): return 1
def redirect(): return 1
def on_mouseover(): return 1
def right_click(): return 1
def popup_window(): return 1
def iframe(): return 1
def age_of_domain(domain_name): return 1
def dns_record(domain): return 1
def web_traffic(): return 1
def page_rank(): return 1
def google_index(): return 1
def links_pointing_to_page(): return 1
def statistical_report(): return 1

def extract_features(url):
    domain_name = urlparse(url).netloc

    features = [
        has_ip_address(url),
        url_length(url),
        url_shortening_service(url),
        has_at_symbol(url),
        double_slash_redirecting(url),
        prefix_suffix(url),
        sub_domains(url),
        ssl_final_state(url),
        domain_registration_length(domain_name),
        favicon(url),
        port_check(url),
        https_token(url),
        request_url(),
        url_of_anchor(),
        links_in_tags(),
        sfh(),
        submitting_to_email(),
        abnormal_url(),
        redirect(),
        on_mouseover(),
        right_click(),
        popup_window(),
        iframe(),
        age_of_domain(domain_name),
        dns_record(domain_name),
        web_traffic(),
        page_rank(),
        google_index(),
        links_pointing_to_page(),
        statistical_report()
    ]

    return features
