import re

def format_phone_number(phone):
    phone = re.sub(r'[^0-9]', '', phone)

    if phone.startswith('8') and len(phone) == 11:
        phone = phone[1:]
    elif phone.startswith('7') and len(phone) == 11:
        phone = phone[1:]
    elif phone.startswith('0') and len(phone) == 11:
        phone = phone[1:]
    elif len(phone) == 10:
        pass

    return f"+7 ({phone[:3]}) {phone[3:6]}-{phone[6:8]}-{phone[8:10]}"

def sort_and_format_phones(phones):
    def get_sort_key(phone):
        digits = re.sub(r'[^0-9]', '', phone)
        if digits.startswith('8') and len(digits) == 11:
            return digits[1:]
        elif digits.startswith('7') and len(digits) == 11:
            return digits[1:]
        elif digits.startswith('0') and len(digits) == 11:
            return digits[1:]
        return digits[-10:] if len(digits) >= 10 else digits

    sorted_phones = sorted(phones, key=get_sort_key)
    return [format_phone_number(p) for p in sorted_phones]

if __name__ == '__main__':
    n = int(input())
    phones = [input().strip() for _ in range(n)]
    formatted = sort_and_format_phones(phones)
    for p in formatted:
        print(p)
