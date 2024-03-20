def format_indian_currency(number):
    if not number:
        return '\u20B9 ' + '0'
    if isinstance(number, float):
        integer_part, *fractional_part = str(number).split('.')
        integer_part_formatted = ",".join(integer_part[::-1][i:i+3] for i in range(0, len(integer_part), 3))[::-1]
        formatted_number = integer_part_formatted + ('.' + fractional_part[0] if fractional_part else '')
    else:
        formatted_number = ",".join(str(number)[::-1][i:i+3] for i in range(0, len(str(number)), 3))[::-1]
    return '\u20B9 ' + formatted_number


if __name__ == '__main__':
    pass