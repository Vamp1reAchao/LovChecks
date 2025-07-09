api_id = 'blant'  # Ваш апи айди. Получать тут: https://my.telegram.org/apps
api_hash = 'blant'  # Ваш апи ключ. Получать тут: https://my.telegram.org/apps

channel = '-12341234'  # Айди канала с логами об активированных чеках. Если вы хотите указать публичный канал, то введите 'тег без @', Например channel = 'ChequeCatcher'

avto_vivod = False  # Если данные параметр True, то скрипт раз в сутки будет переводить деньги с помощью чека на указанный аккаунт. Чтобы отключить укажите False, например avto_vivod = False
avto_vivod_tag = 'username'  # Тег аккаунта(без @), куда раз в сутки будет отправляться чеки со всеми собранными средствами. Например avto_vivod_tag = 'ChequeCatcher'

anti_captcha = True  # Если параметр True, то скрипт будет автоматически разгадывать каптчу для CryptoBot. Чтобы отключить укажите False, например anti_captcha = False
ocr_api_key = 'ABCD1234'