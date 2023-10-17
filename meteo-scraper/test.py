from datetime import datetime


if __name__ == '__main__':
    now = datetime.now()
    with open('test.txt', 'w', encoding='utf-8') as file:
        file.write(now.strftime("%d/%m/%Y %H:%M:%S"))
