import requests

def whatsmyip():
    try:
        raw: dict[str] = requests.get('https://api.duckduckgo.com/?q=ip&format=json').json()
    except Exception as e:
        return False
    else:
        return raw['Answer'].split()[4].strip()
