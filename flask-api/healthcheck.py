import sys
import requests

if __name__ == '__main__':
    try:
        r = requests.get('http://127.0.0.1:5000')
        if r.ok:
            sys.exit(0)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)
