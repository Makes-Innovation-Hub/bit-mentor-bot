import requests


def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip = response.json()['ip']
        # logger.info(f"Fetched public IP: {ip}")
        return ip
    except Exception as e:
        # logger.error("Error fetching public IP", exc_info=True)
        raise