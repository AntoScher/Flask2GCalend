from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


def get_credentials():
    CLIENT_ID = 'ваш_client_id'
    CLIENT_SECRET = 'ваш_client_secret'
    SCOPE = 'https://www.googleapis.com/auth/calendar'

    storage = Storage('creds.data')  # Локальное хранилище токенов
    creds = storage.get()

    if not creds or creds.invalid:
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        auth_url = flow.step1_get_authorize_url()
        print(f"Перейдите по ссылке: {auth_url}")
        code = input("Введите код: ")
        creds = flow.step2_exchange(code)
        storage.put(creds)
    return creds