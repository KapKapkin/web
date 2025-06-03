import re

def format_phone_number(phone):
    phone = re.sub(r'[^0-9]', '', phone)
    if phone.startswith('8') or phone.startswith('7'):
        phone = phone[1:]
    elif phone.startswith('0'):
        phone = phone[1:]
    return f"+7 ({phone[:3]}) {phone[3:6]}-{phone[6:8]}-{phone[8:10]}"

if __name__ == '__main__':
    n = int(input())
    phones = [input().strip() for _ in range(n)]
    formatted = [format_phone_number(p) for p in sorted(phones)]
    for p in formatted:
        print(p)