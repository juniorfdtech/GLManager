def pause(text='\nEnter para continuar'):
    input('\033[1;32m' + text + '\033[0m')


def get_ip_address():
    import urllib.request as request

    url = 'https://icanhazip.com'
    response = request.urlopen(url)
    ip = response.read().decode('utf-8')
    return '0.0.0.0' # ip.strip()
