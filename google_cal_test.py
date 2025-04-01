import os
import httplib2
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import json

load_dotenv()


def debug_print_request(http):
    """Промежуточное ПО для логирования HTTP-запросов"""

    def _request(*args, **kwargs):
        response, content = http.request(*args, **kwargs)
        print(f"\n[DEBUG] HTTP Request:")
        print(f"URL: {args[0]}")
        print(f"Method: {args[1]}")
        print(f"Status: {response.status}")
        print(f"Response Body:\n{content.decode()[:500]}")
        return response, content

    return _request


def create_calendar_event(summary, start_datetime, end_datetime):
    try:
        sa_path = os.getenv('SERVICE_ACCOUNT_JSON')
        calendar_id = os.getenv('CALENDAR_ID')

        # Валидация параметров
        if not sa_path or not os.path.exists(sa_path):
            raise FileNotFoundError(f"Service account file not found: {sa_path}")

        if not calendar_id or '@' not in calendar_id:
            raise ValueError(f"Invalid Calendar ID: {calendar_id}")

        # Создаем кастомный HTTP-клиент с логированием
        http = httplib2.Http()
        http = debug_print_request(http)

        credentials = service_account.Credentials.from_service_account_file(
            sa_path,
            scopes=['https://www.googleapis.com/auth/calendar'],
        )

        service = build(
            'calendar',
            'v3',
            credentials=credentials,
            cache_discovery=False,
            http=http
        )

        event_body = {
            'summary': summary,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': 'UTC'},
        }

        print("\n[INFO] Отправка запроса к Google Calendar API...")
        event = service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()

        print(f"\n✅ Событие успешно создано!")
        print(f"ID: {event['id']}")
        print(f"Ссылка: {event.get('htmlLink', 'N/A')}")
        return True

    except Exception as e:
        print("\n❌ Критическая ошибка:")
        print(f"Тип: {type(e).__name__}")
        print(f"Сообщение: {str(e)}")

        if hasattr(e, 'content'):
            try:
                error_details = json.loads(e.content.decode())
                print("Детали ошибки:")
                print(json.dumps(error_details, indent=2))
            except:
                print("Raw Error Content:")
                print(e.content.decode()[:500])

        return False


if __name__ == '__main__':
    # Проверка окружения
    print("=" * 50)
    print("Google Calendar API Debugger")
    print("=" * 50)

    print("\n[Шаг 1] Проверка переменных окружения:")
    print(f"SERVICE_ACCOUNT_JSON: {os.path.exists(os.getenv('SERVICE_ACCOUNT_JSON'))}")
    print(f"CALENDAR_ID: {os.getenv('CALENDAR_ID', 'NOT SET!')}")

    print("\n[Шаг 2] Инициализация тестового события...")
    now = datetime.now(timezone.utc)
    test_event = {
        'summary': '[TEST] Python API Event',
        'start_datetime': now + timedelta(hours=1),
        'end_datetime': now + timedelta(hours=2)
    }
    print(f"Начало: {test_event['start_datetime'].isoformat()}")
    print(f"Окончание: {test_event['end_datetime'].isoformat()}")

    print("\n[Шаг 3] Запуск теста...")
    result = create_calendar_event(**test_event)

    print("\n[Шаг 4] Результат:")
    print("УСПЕХ" if result else "НЕУДАЧА")