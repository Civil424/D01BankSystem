from datetime import datetime
import json

class Account:
    def __init__(self,login,password,account,balance,history):
        self.login = login
        self.password = password
        self.account = account
        self.balance = balance
        self.history = history

    def deposit(self,amount):
        if amount <= 0:
            raise InvalidAmountError("Число должно быть положительным")
        self.balance += amount
        transaction = Transaction("Пополнение",self.account,amount,datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        self.history.append(transaction)
        Bank.logging_operations(transaction)

    def withdraw(self,amount):
        if amount <= 0:
            raise InvalidAmountError("Число должно быть положительным")
        if amount > self.balance:
            raise InsufficientFundsError("Не достаточно средств")
        self.balance -= amount
        transaction = Transaction("Снятие",self.account,amount,datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        self.history.append(transaction)
        Bank.logging_operations(transaction)

    def transaction(self,amount,account,accounts):
        ac = None
        for acc in accounts:
            if acc.account == account:
                ac = acc
                break
        if ac == None:
            raise NoneAccountError("Счет не найден")                
        if amount <= 0:
            raise InvalidAmountError("Число должно быть положительным")
        if amount > self.balance:
            raise InsufficientFundsError("Не достаточно средств")
        self.balance -= amount
        transaction_to = Transaction("Перевод",account,amount,datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        self.history.append(transaction_to)
        ac.balance += amount
        Bank.logging_operations(transaction_to)
        transaction_from = Transaction("Перевод",self.account,amount,datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        ac.history.append(transaction_from)
        Bank.logging_operations(transaction_from)

class Bank:
    acc_log = 1000

    def __init__(self,accounts):
        self.accounts = accounts

    def autorization(self):
        print("Введите или придумайте логин")
        login = is_str_correct()

        for acc in self.accounts:
            if acc.login == login:
                flag = False
                while flag == False:
                    print("Введите пароль")
                    pas = is_str_correct()
                    if self.check_pass(login,pas) == True:
                        flag = True
                return acc
        else:
            acc = self.registration(login)
            return acc

    def check_pass(self,login,password):
        for acc in self.accounts:
            if acc.login == login and acc.password == password:
                return True
        else:
            print("Не верный пароль, попробуйте еще раз")
            return False

    def registration(self,login):
        print("Придумайте пароль")
        pas = is_str_correct()
        acc = Account(login,pas,Bank.acc_log,0,[])
        self.accounts.append(acc)
        Bank.acc_log += 1
        return acc
    
    def visual(self,acc):
        print("-----------------")
        print(f"Логин: {acc.login}")
        print(f"Счет: {acc.account}")
        print(f"Баланс: {acc.balance}")
        print("----------")
        print(f"История: {acc.history}")
        print("-----------------")
        print("1 - Пополнение счета")
        print("2 - Снятие со счета")
        print("3 - Перевод на другой счет")
        print("4 - Выйти из аккаунта")
        print("5 - Выйти из приложения")

    def json_importer(self):
        try:
            with open("bank_data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            print("Файл не найден\nСоздание нового файла 'bank_data.json'")
            with open("bank_data.json","w",encoding="utf-8") as file:
                json.dump({},file)
        else:

            acc_logs = []
            for account,info in data.items():
                
                history = []
                for transaction in info["history"]:

                    history.append(
                        Transaction(
                            transaction["type"],
                            transaction["account"],
                            transaction["sum"],
                            transaction["date"]
                        )
                    )

                acc_logs.append(int(account))
                acc = Account(
                    info["login"],
                    info["password"],
                    int(account),
                    info["balance"],
                    history
                )
                self.accounts.append(acc)
            Bank.acc_log = self.max_of_list(acc_logs) + 1


    def json_loader(self):
        data = {}

        for acc in bank.accounts:
            history = []

            for transaction in acc.history:
                history.append({
                    "type": transaction.type,
                    "account": transaction.account,
                    "sum": transaction.summ,
                    "date": transaction.date
                })

            data[str(acc.account)] = {
                "login" : acc.login,
                "password" : acc.password,
                "balance" : acc.balance,
                "history" : history
            }
    
        with open("bank_data.json","w",encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def max_of_list(self,list):
        max = 0
        for i in list:
            if i > max:
                max = i
        return max
    
    def logging_operations(transaction):
        with open("transactions.log","a",encoding="utf-8") as file:
            file.write(f"\naccount: {transaction.account}, type: {transaction.type}, sum: {transaction.summ}, {transaction.date}")

class Transaction:
    def __init__(self,type,account,summ,date):
        self.type = type
        self.account = account
        self.summ = summ
        self.date = date
    
    def __str__(self):
        return f"\n| Операция: {self.type} | Счет: {self.account} | Сумма: {self.summ} | {self.date} |"
        
    def __repr__(self):
        return str(self)

class InvalidAmountError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class NoneAccountError(Exception):
    pass
    
def is_str_correct():
    x = input()
    if x == "":
        print("Ошибка, ввод не может быть пустым")
        return None
    else:
        return x
    
def is_int_correct():
    try:
        x = int(input())
    except ValueError:
        print("Ошибка ввода")
        return 0
    else:
        return x

current_account = None
is_active = False
run = True
bank = Bank([])

bank.json_importer()

while(run):
    if current_account == None:
        acc = bank.autorization()
        current_account = acc
        Bank.json_loader(bank)
        is_active = True

    if is_active == True and current_account != None:
        bank.visual(current_account)
        is_active = False

    inp = is_int_correct()
    if inp == 1:
        print("Введите сумму")
        try:
            amount = is_int_correct()
            current_account.deposit(amount)
        except InvalidAmountError as e:
            print("Число должно быть положительным")
            print(f"Ошибка {e}")
        except InsufficientFundsError as e:
            print("Не достаточно средств")
            print(f"Ошибка {e}")
        Bank.json_loader(bank)
        is_active = True
    
    if inp == 2:
        print("Введите сумму")
        try:
            amount = is_int_correct()
            current_account.withdraw(amount)
        except InvalidAmountError as e:
            print("Число должно быть положительным")
            print(f"Ошибка {e}")
        except InsufficientFundsError as e:
            print("Не достаточно средств")
            print(f"Ошибка {e}")
        Bank.json_loader(bank)
        is_active = True

    if inp == 3:
        try:
            print("Введите счет для перевода")
            account = is_int_correct()
            print("Введите сумму")
            amount = is_int_correct()
            current_account.transaction(amount,account,bank.accounts)
        except InvalidAmountError as e:
            print("Число должно быть положительным")
            print(f"Ошибка {e}")
        except InsufficientFundsError as e:
            print("Не достаточно средств")
            print(f"Ошибка {e}")
        except NoneAccountError as e:
            print("Счет не найден")
            print(f"Ошибка {e}")
        Bank.json_loader(bank)
        is_active = True
    
    if inp == 4:
        current_account = None

    if inp == 5:
        run = False