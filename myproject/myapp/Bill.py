import psycopg2
from datetime import datetime

class Bill:
    def __init__(self, memberID):
        self.memberID = memberID

    def getTotal(self):
        total = 0
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT amount FROM charges WHERE member_id = (%s) AND isPaid = False",(self.memberID,))
                bill = cur.fetchall()

        for i in range(len(bill)):
            total += bill[i][0]

        return total

    def createCharge(self, value: float, memo: str, type: str):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO charges (member_id, amount, description, type) "
                        "VALUES (%s, %s, %s, %s)", (self.memberID, value, memo, type))
        except psycopg2.errors.ForeignKeyViolation:
            return -1
        except psycopg2.Error as e:
            return False

    def payBill(self, year: int):
        if int(year) == int(datetime.now().year):
            return False
        else:
            ystring = str(year)+'%'
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE charges SET isPaid = True WHERE date::varchar(10) LIKE %s AND member_id = %s", (ystring,self.memberID))
            return True

    def getBill(self):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT charge_id, amount, date, description, type  FROM charges where member_id = (%s) AND isPaid = FALSE ORDER BY date",
                            (self.memberID,))
                    bill = cur.fetchall()

            bill.append(("",self.getTotal(),"","Total Bill",""))

            return bill
        except:
            return False

    def getFullBill(self):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute(
                    "SELECT charge_id, amount, date, description, type, ispaid  FROM charges where member_id = (%s) ORDER BY date",
                    (self.memberID,))
                    bill = cur.fetchall()

            bill.append(("", self.getTotal(), "", "Total Bill", "", ""))

            return bill
        except:
            return False