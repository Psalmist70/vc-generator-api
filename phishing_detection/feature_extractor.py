# phishing_detection/feature_extractor.py

import re
import urllib.parse
import ipaddress

def extract_features(url):
    """
    Extracts 30 features from a URL for KNN phishing detection.
    Returns a list of numeric values representing the features.
    """

    features = []

    # 1. URL Length
    features.append(len(url))

    # 2. Having IP Address
    try:
        ipaddress.ip_address(url)
        features.append(1)
    except:
        features.append(0)

    # 3. Presence of @ symbol
    features.append(1 if "@" in url else 0)

    # 4. Number of subdomains
    domain = urllib.parse.urlparse(url).netloc
    features.append(domain.count('.'))

    # 5. Presence of hyphen in domain
    features.append(1 if "-" in domain else 0)

    # 6. Uses HTTPS
    features.append(1 if url.startswith("https") else 0)

    # 7. Uses TinyURL (or similar shortener)
    shorteners = ["bit.ly", "tinyurl", "goo.gl", "ow.ly", "t.co", "is.gd"]
    features.append(1 if any(s in url for s in shorteners) else 0)

    # 8. Length of domain
    features.append(len(domain))

    # 9. Count of `.` in URL
    features.append(url.count('.'))

    # 10. Count of `//` in URL
    features.append(url.count('//'))

    # 11. Count of `?` in URL
    features.append(url.count('?'))

    # 12. Count of `=` in URL
    features.append(url.count('='))

    # 13. Count of `&` in URL
    features.append(url.count('&'))

    # 14. Count of `%` in URL
    features.append(url.count('%'))

    # 15. Count of digits
    features.append(len(re.findall(r'\d', url)))

    # 16. Count of letters
    features.append(len(re.findall(r'[a-zA-Z]', url)))

    # 17. Presence of suspicious words
    suspicious_words = ["secure", "account", "webscr", "login", "ebayisapi", "banking"]
    features.append(1 if any(word in url.lower() for word in suspicious_words) else 0)

    # 18. URL path length
    features.append(len(urllib.parse.urlparse(url).path))

    # 19. URL query length
    features.append(len(urllib.parse.urlparse(url).query))

    # 20. Has 'http' in domain (phishy trick)
    features.append(1 if 'http' in domain else 0)

    # 21. Has 'https' in domain
    features.append(1 if 'https' in domain else 0)

    # 22. URL contains "//" in path (not after protocol)
    path = urllib.parse.urlparse(url).path
    features.append(1 if '//' in path else 0)

    # 23. Count of slashes `/`
    features.append(url.count('/'))

    # 24. TLD length (e.g. .com → 3)
    tld = domain.split('.')[-1]
    features.append(len(tld))

    # 25. Count of subdomain segments (e.g. 3 in mail.google.com)
    features.append(len(domain.split('.')))

    # 26. Is domain in all lowercase
    features.append(1 if domain == domain.lower() else 0)

    # 27. Has repeated characters
    features.append(1 if re.search(r'(.)\1{2,}', url) else 0)

    # 28. Uses port number explicitly
    features.append(1 if ':' in domain else 0)

    # 29. Query string contains suspicious keywords
    query = urllib.parse.urlparse(url).query.lower()
    features.append(1 if any(k in query for k in ["login", "password", "token"]) else 0)

    # 30. Length of entire URL
    features.append(len(url))

    return features
