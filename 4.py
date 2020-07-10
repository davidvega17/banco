import random
import sqlite3


class Banco:

    def generar_pin(self):
        pin = random.randint(0, 9999)
        pin = '{:04d}'.format(pin)
        return pin

    def luhn(self, numero_de_cuenta):
        acumulador = 0
        for i in range(1, len(numero_de_cuenta) + 1):
            numero = int(numero_de_cuenta[i - 1])
            if i % 2 != 0:
                numero = numero * 2
            if numero > 9:
                numero = numero - 9
            acumulador = acumulador + numero
        acumulador = 10 - acumulador % 10
        if acumulador == 10:
            return "0"
        else:
            return str(acumulador)

    @property
    def generar_numero_cuenta(self):

        numero_de_cuenta = random.randint(0, 999999999)
        numero_de_cuenta = '{:09d}'.format(numero_de_cuenta)
        numero_de_tarjeta = "{}{}".format(400000, numero_de_cuenta)
        check_sum = self.luhn(numero_de_tarjeta)
        numero_de_tarjeta = numero_de_tarjeta + str(check_sum)
        t = (int(numero_de_tarjeta),)
        cur.execute('SELECT id FROM card WHERE id=?', t)
        cuenta = cur.fetchone()
        while cuenta is not None:
            numero_de_cuenta = random.randint(0, 999999999)
            numero_de_cuenta = '{:09d}'.format(numero_de_cuenta)
            numero_de_tarjeta = "{}{}".format(400000, numero_de_cuenta)
            check_sum = self.luhn(numero_de_tarjeta)
            numero_de_tarjeta = numero_de_tarjeta + str(check_sum)

        else:
            return numero_de_tarjeta

    def crear_cuenta(self, numero_de_tarjeta, pin):
        # "345656754675" : {"pin":0000,"balance":0}
        cur.execute(
            "insert into card(id, number, pin) values({},{},'{}');".format(numero_de_tarjeta, numero_de_tarjeta, pin))
        conn.commit()

    def comparar_lhun(self, numero):
        ultimo_numero = self.luhn(numero[0:len(numero) - 1])
        if str(ultimo_numero) == str(numero[-1]):
            return True
        else:
            return False


banco = Banco()
conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
try:
    cur.execute("create table card(id integer, number text, pin text, balance integer default 0 );")
    conn.commit()
except:
    pass

while True:
    menu = input("""1. Create an account
    2. Log into account
    0. Exit""")
    if menu == "1":
        cuenta = banco.generar_numero_cuenta
        pin = banco.generar_pin()
        banco.crear_cuenta(cuenta, pin)
        print('Your card has been created')
        print('Your card number:')
        print("{}".format(cuenta))
        print("Your card PIN:")
        print('{}'.format(pin))
    elif menu == "2":
        card_number = input("Enter your card number:")
        pin = input("Enter your PIN:")
        t = (int(card_number),)
        cur.execute("select * from card where id = ?", t)
        card = cur.fetchone()
        if card is None:
            print("Wrong card number or PIN!")
        elif card_number == card[1] and pin == card[2]:
            print("You have successfully logged in!")

            while True:
                menu2 = input("1. Balance \n2. Add income \n3. Do transfer \n4. close acount \n5. log out \n0. exit")
                if menu2 == "1":
                    print("Balance: {}".format(card[3]))
                elif menu2 == "5":
                    print("You have successfully logged out!")
                    break
                elif menu2 == "3":
                    tarjeta_destino = input("Enter card number:")
                    if card_number == tarjeta_destino:
                        print("You can't transfer money to the same account!")
                        continue
                    elif not banco.comparar_lhun(tarjeta_destino):
                        print("Probably you made mistake in the card number. Please try again!")
                        continue
                    else:
                        t = (tarjeta_destino,)
                        cur.execute("SELECT id FROM card WHERE number =  ?;", t)
                        tar = cur.fetchone()
                        if tar is None:
                            print("Such card does not exist.")
                            continue
                        billete = input("Enter how much money you want to transfer:")
                        t = (card_number,)
                        cur.execute("SELECT Balance FROM card WHERE number = ?;", t)
                        saldo_usuario = cur.fetchone()
                        if saldo_usuario[0] < int(billete):
                            print("Not enough money!")
                            continue
                        t = (billete, card_number)
                        cur.execute("UPDATE card SET balance = balance - ? where number = ?;", t)
                        t = (billete, tarjeta_destino)
                        cur.execute("UPDATE card SET balance = balance + ? where number = ?;", t)
                        conn.commit()
                        print("Success!")
                        continue

                elif menu2 == "4":
                    t = (card_number,)
                    cur.execute("DELETE FROM card WHERE number = ?;",t)
                    conn.commit()
                    print("The account has been closed!")
                    break
                elif menu2 == "2":
                    plata_agg = input("Enter income:")
                    t = (plata_agg, card_number,)
                    cur.execute("UPDATE card SET Balance = Balance + ? WHERE number = ?;", t)
                    conn.commit()
                    continue

                elif menu2 == "0":
                    print("bye")
                    exit()

        else:
            print("Wrong card number or PIN!")

    elif menu == "0":
        print("bye")
        exit()
