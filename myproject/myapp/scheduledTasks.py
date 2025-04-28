import schedule
import threading
import psycopg2
import datetime
import time
from Bill import Bill
from emailer import Emailer
import pandas as pd


def run_continouously(interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()

    return cease_continuous_run



def addYearlyFee():
    if datetime.datetime.now().day == 1 and datetime.datetime.now().month == 1:
        year = datetime.datetime.now().year - 1

        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT member_id FROM member WHERE active = True")
                members = cur.fetchall()
            with conn.cursor() as cur:
                cur.execute("SELECT annualfee FROM billing_constants")
                annualfee = cur.fetchall()[0][0]

            em = Emailer()

            for member in members:
                if member[0] != 1 and member[0] != 2:
                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO charges (member_id, amount, date, description, type) VALUES (%s, %s, %s, %s, %s)",
                                (member[0], annualfee, datetime.date(year, 1, 1),'Annual Dues', 'Annual'))

        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            for member in members:
                if member[0] != 1 and member[0] != 2:
                    with conn.cursor() as cur:
                        cur.execute("SELECT email FROM member WHERE member_id = %s", (member[0],))
                        email = cur.fetchall()[0][0]
                        bill = Bill(member[0])
                        print(bill.getBill())
                        try:
                            em.sendBillEmail(bill.getBill(), email)
                            pass
                        except:
                            pass
        return 0


def getUnpaid():
    year = str(datetime.datetime.now().year - 1)
    date = ''+year+'-01-01'
    with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT charge_id, member_id FROM charges WHERE isPaid = False AND date = %s AND type = 'Annual'",(date,))
            result = cur.fetchall()
    return result


def addLateFee():
    if datetime.datetime.now().day == 1:
        month = datetime.datetime.now().month
        year = datetime.datetime.now().year - 1
        unpaid = getUnpaid()
        em = Emailer()
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            if month == 2:
                for i in range(len(unpaid)):
                    with conn.cursor() as cur:
                        cur.execute("SELECT amount FROM charges WHERE charge_id = %s", (unpaid[i][0],))
                        annualfee = cur.fetchall()[0]
                        annualfee = annualfee[0]
                    with conn.cursor() as cur:
                        cur.execute("UPDATE charges SET amount = %s WHERE charge_id = %s", (annualfee+annualfee*0.1, unpaid[i][0]))
                        cur.execute("SELECT email FROM member WHERE member_id = %s", (unpaid[i][1],))
                        email = cur.fetchone()[0]
                        try:
                            em.lateBillEmail(email)
                        except:
                            pass

            if month == 3:
                for i in range(len(unpaid)):
                    with conn.cursor() as cur:
                        cur.execute("SELECT amount FROM charges WHERE charge_id = %s", (unpaid[i][0],))
                        annualfee = cur.fetchall()[0]
                        annualfee = annualfee[0]/1.1
                    with conn.cursor() as cur:
                        cur.execute("UPDATE charges SET amount = %s WHERE charge_id = %s", (round(annualfee+annualfee*0.2,2), unpaid[i][0]))
                        cur.execute("SELECT email FROM member WHERE member_id = %s", (unpaid[i][1],))
                        email = cur.fetchone()[0]
                        try:
                            em.lateBillEmail(email)
                        except:
                            pass
    elif datetime.datetime.now.day() == 31 and datetime.datetime.now.month() == 3:
        unpaid = getUnpaid()
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                for member in unpaid:
                    cur.execute("UPDATE member SET active = false WHERE member_id = %s",(member[1],))

def refreshReservation():
    day = datetime.datetime.today().weekday()
    with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM reservation WHERE res_day = %s", (day,))

def resetGuestPass():
    if datetime.datetime.today().weekday() == 1:
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE member SET guastpass = 4")

def backupDB():
    if datetime.datetime.today.weekday() == 4:
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM member")
                member = cur.fetchall()

                cur.execute("SELECT * FROM reservation")
                reservation = cur.fetchall()

                cur.execute("SELECT * FROM charges")
                charges = cur.fetchall()

                cur.execute("SELECT * FROM attendees")
                attendees = cur.fetchall()

                cur.execute("SELECT * FROM billing_constants")
                billing_constants = cur.fetchall()
        member = pd.DataFrame(member)
        reservation = pd.DataFrame(reservation)
        charges = pd.DataFrame(charges)
        attendees = pd.DataFrame(attendees)
        billing_constants = pd.DataFrame(billing_constants)

        member.to_csv('Backups/member.csv')
        reservation.to_csv('Backups/reservation.csv')
        charges.to_csv('Backups/charges.csv')
        attendees.to_csv('Backups/attendees.csv')
        billing_constants.to_csv('Backups/billing_constants.csv')

def loadBackup():
    member = pd.read_csv('Backups/member.csv', index_col=0).to_dict('records')
    reservation = pd.read_csv('Backups/reservation.csv', index_col=0).to_dict('records')
    charges = pd.read_csv('Backups/charges.csv', index_col=0).to_dict('records')
    attendees = pd.read_csv('Backups/attendees.csv', index_col=0).to_dict('records')
    billing_constants = pd.read_csv('Backups/billing_constants.csv', index_col=0).to_dict('records')

    with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
        for mem in member:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO member VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (mem['0'],mem['1'], mem['2'], mem['3'], mem['4'],mem['5'],mem['6'],mem['7'],mem['8']))
        for res in reservation:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO reservation VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (res['0'], res['1'], res['2'], res['3'], res['4'], res['5'], res['6']))
        for chrg in charges:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO charges VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (chrg['0'], chrg['1'], chrg['2'], chrg['3'], chrg['4'], chrg['5'], chrg['6']))
        for attn in attendees:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO attendees VALUES (%s, %s, %s, %s)",
                            (attn['0'], attn['1'], attn['2'], attn['3']))

        for bill in billing_constants:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO billing_constants VALUES (%s, %s)",
                            (bill['0'], bill['1']))


#schedule.every().day.at("05:30").do(lambda: addYearlyFee())
#schedule.every().day.at("05:30").do(lambda: addLateFee())
#schedule.every().day.at("22:00").do(lambda: refreshReservation())
#schedule.every().Monday.at("22:00").do(lambda: backupDB())



#stop_run_continuously = run_continouously(43200)

