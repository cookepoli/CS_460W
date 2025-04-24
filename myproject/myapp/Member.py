from Bill import Bill
import psycopg2
from psycopg2 import sql
from datetime import time, datetime, timedelta
from emailer import Emailer

class Member:
    def __init__(self, memberid):
        self.memberid = memberid
        self.my_bill = Bill(self.memberid)

    def getInformation(self):
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT firstname, lastname, email, phonenum, OptIn, guestpass FROM member WHERE member_ID = (%s) ", (self.memberid,))
                information = cur.fetchall()
        return information

    def getBill(self):
        return self.my_bill.getBill()

    def payBill(self,year: int):
        return self.my_bill.payBill(year)

    def updateInformation(self, attribute: str, value: str):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    if attribute == 'password':
                        cur.execute("UPDATE member SET password = crypt(%s, gen_salt('md5')) WHERE member_id = (%s)",
                                (value, self.memberid))
                    else:
                        cur.execute(sql.SQL("UPDATE member SET {} = %s WHERE member_id = %s",).format(sql.Identifier(attribute)),
                    (value, self.memberid))
            return 0
        except psycopg2.Error as e:
            return -1
        except TypeError as e:
            return -1


    def createReservation(self, restype: str, day: int, start: time, end: time, court: int, members: list[int], guests: list[str]):
        try:
            check = self.checkReservationRules(restype, day, start, end, court, members, guests)
            if check != 0:
                return check
            else:
                with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:

                    with conn.cursor() as cur:
                        cur.execute("INSERT INTO reservation (court_num, res_day, start_time, end_time, member_id, type) VALUES "
                            "((%s), (%s), (%s), (%s), (%s), (%s))", (court, day, start, end, self.memberid, restype))


                    with conn.cursor() as cur:
                        cur.execute("SELECT reservation_id FROM reservation WHERE member_ID = (%s) AND start_time = (%s) AND court_num = (%s)",
                            (self.memberid, start, court))
                        res_id = cur.fetchone()

                    for i in range(len(members)):
                        try:
                            with conn.cursor() as cur:
                                cur.execute("SELECT firstname, lastname FROM member WHERE member_ID = (%s)", (members[i],))
                                memname = cur.fetchall()
                                cur.execute("INSERT INTO attendees VALUES ((%s), (%s), (%s), (%s))",
                                    (res_id[0], memname[0][0], memname[0][1],members[i]))
                        except:
                            return 11

                    with conn.cursor() as cur:
                        cur.execute("SELECT guestfee FROM billing_constants")
                        guestfee = cur.fetchall()[0][0]

                    for i in range(len(guests)):
                        guest = guests[i].split()
                        with conn.cursor() as cur:
                            try:
                                cur.execute("INSERT INTO attendees (reservation_id, firstname, lastname) VALUES ((%s), (%s), (%s))",
                                    (res_id[0], guest[0], guest[1]))
                            except IndexError:
                                return 12
                            cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (self.memberid,))
                            rem_passes = cur.fetchall()
                            cur.execute("UPDATE member SET guestpass = (%s) WHERE member_id = (%s)",
                                (rem_passes[0][0]-1, self.memberid))
                        self.my_bill.createCharge(guestfee, "Guest Fee", "Other")
                    with conn.cursor() as cur:
                        cur.execute("SELECT email FROM member WHERE member_id = (%s)", (self.memberid,))
                        email = cur.fetchone()[0]
                try:
                    em = Emailer()
                    em.sendReservationConfirmation(res_id[0], email)
                except:
                   print('yikes')

                return -1
        except psycopg2.Error as e:
            return False

    def deleteReservation(self, res_id: int):
        try:
            res_id = int(res_id)
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT reservation_id FROM reservation WHERE member_id = %s ", (self.memberid,))
                    result = cur.fetchall()
                    check_ids = []
                    for i in range(len(result)):
                        check_ids.append(result[i][0])
                if res_id in check_ids:
                    with conn.cursor() as cur:
                        # Checking Guestpasses
                        cur.execute("SELECT member_id FROM attendees WHERE reservation_id = (%s)", (res_id,))
                        attendees = cur.fetchall()
                        cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (self.memberid,))
                        guestpass = cur.fetchone()[0]
                        cur.execute("SELECT charge_id FROM charges WHERE member_id = (%s) AND description = 'Guest Fee'", (self.memberid,))
                        charges = cur.fetchall()
                        chr_inc = 0
                        for i in range(len(attendees)):
                            if attendees[i][0] is None:
                                guestpass = guestpass+1
                                cur.execute("DELETE FROM charges WHERE charge_id = %s", (charges[chr_inc][0],))
                                chr_inc=chr_inc+1

                        print(guestpass)
                        cur.execute("UPDATE member SET guestpass = %s WHERE member_id = %s", (guestpass, self.memberid))
                        cur.execute("DELETE FROM reservation WHERE reservation_id = %s", (res_id,))

                    return 1
                else:
                    return -2
        except:
            return 0

    def updateReservation(self, res_id, players: list[str]):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT reservation_id FROM reservation WHERE member_id = %s ", (self.memberid,))
                    result = cur.fetchall()
                    check_ids = []
                    for i in range(len(result)):
                        check_ids.append(result[i][0])

                if res_id in check_ids:
                    with conn.cursor() as cur:
                        cur.execute("SELECT type FROM reservation WHERE reservation_id = (%s)", (res_id,))
                        typ = cur.fetchone()[0]
                    if typ == 'singles':
                        if len(players) != 1:
                            return 1
                    elif typ == 'doubles':
                        if len(players) != 3:
                            return 1

                    with conn.cursor() as cur:
                        cur.execute("SELECT member_id FROM attendees WHERE reservation_id = (%s)", (res_id,))
                        attendees = cur.fetchall()
                        cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (self.memberid,))
                        guestpass = cur.fetchone()[0]
                        cur.execute("SELECT charge_id FROM charges WHERE member_id = (%s) AND description = 'Guest Fee'",
                                (self.memberid,))
                        charges = cur.fetchall()
                    chr_inc = 0
                    for i in range(len(attendees)):
                        if attendees[i][0] is None:
                            guestpass = guestpass + 1
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM charges WHERE charge_id = %s", (charges[chr_inc][0],))
                            chr_inc = chr_inc + 1
                    with conn.cursor() as cur:
                        cur.execute("SELECT * FROM attendees WHERE reservation_id = (%s)", (res_id,))
                        old_attendees = cur.fetchall()
                        cur.execute("DELETE FROM attendees WHERE reservation_id = (%s)", (res_id,))
                        cur.execute("UPDATE member SET guestpass = %s WHERE member_id = %s", (guestpass, self.memberid))

                    with conn.cursor() as cur:
                        cur.execute("SELECT guestfee FROM billing_constants")
                        guestfee = cur.fetchall()[0][0]

                    for player in players:
                        with conn.cursor() as cur:
                            try:
                                cur.execute("SELECT member_id FROM member WHERE firstname = %s AND lastname = %s",(player.split(" ")[0],player.split(" ")[1]))
                                member_id = cur.fetchone()[0]
                            except:
                                member_id = None
                        with conn.cursor() as cur:
                            if member_id is None:
                                if guestpass == 0:
                                    for old_attendee in old_attendees:
                                        cur.execute("INSERT INTO attendees VALUES (%s, %s, %s, %s)", (res_id, old_attendee[1], old_attendee[2], old_attendee[3]))
                                    return -1
                                else:
                                    cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (self.memberid,))
                                    guestpass = cur.fetchone()[0]
                                    cur.execute("UPDATE member SET guestpass = %s WHERE member_id = (%s)", (guestpass-1,self.memberid,))
                                    self.my_bill.createCharge(guestfee, "Guest Fee", "Other")
                            cur.execute("INSERT INTO attendees VALUES (%s, %s, %s, %s)", (res_id,player.split(" ")[0],player.split(" ")[1],member_id))

                    return 1
                else:
                    return -2
        except:
            return 0



    def checkReservationRules(self, restype: str, day:int, start: time, end: time, court: int, members: list[int], guests: list[str]):
        try:
            conn = psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432")


            #Rule 1: Overlapping reservation
            with conn.cursor() as cur:
                cur.execute("SELECT start_time, end_time FROM reservation WHERE res_day = (%s) AND court_num = (%s)",
                        (day, court))
                check = cur.fetchall()
            for i in range(len(check)):
                if check[i][0] <= start <= check[i][1]:
                    conn.close()
                    return 1
                if check[i][0] <= end <= check[i][1]:
                    conn.close()
                    return 1

                #Rule 2: Overlapping reservation from same member.
            with conn.cursor() as cur:
                cur.execute("SELECT start_time, end_time FROM reservation WHERE member_ID = (%s) AND res_day = (%s)",
                        (self.memberid,day))
                check = cur.fetchall()
                for i in range(len(check)):
                    if check[i][0] <= start <= check[i][1]:
                        conn.close()
                        return 2
                    if check[i][0] <= end <= check[i][1]:
                        conn.close()
                        return 2

                #Rule 3: Reservation proximity before.
                for i in range(len(check)):
                    if check[i][0] > end and datetime.combine(datetime.now(), check[i][0]) < (datetime.combine(datetime.now(), end) + timedelta(minutes=60)):
                        conn.close()
                        return 3

                #Rule 4: Reservation proximity after.
                for i in range(len(check)):
                    if check[i][1] < start and datetime.combine(datetime.now(), check[i][1]) > (datetime.combine(datetime.now(), start) - timedelta(minutes=60)):
                        conn.close()
                        return 4

                #Rule 5: Checked on front-end.
                if int(day) < 0 or int(day) > 6:
                    return 5

                #Rule 6: Member has enough guest passes.
            with conn.cursor() as cur:
                cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (self.memberid,))
                check = cur.fetchall()
            if len(guests) > check[0][0]:
                conn.close()
                return 6

                #Rule 7: Member has no more than 2 other reservations.
            with conn.cursor() as cur:
                cur.execute("SELECT reservation_id FROM reservation WHERE member_ID = (%s)", (self.memberid,))
                check = cur.fetchall()
            if len(check) >= 3:
                conn.close()
                return 7

                #Rule 8: Check count of accompanying members.
            if restype == "doubles":
                if len(guests) + len(members) != 3:
                    conn.close()
                    return 8
            elif restype == "singles":
                if len(guests) + len(members) != 1:
                    conn.close()
                    return 8
            else:
                conn.close()
                return 8

            #Reservation Length
            if restype == "doubles":
                length = datetime.combine(datetime.today(),end) - datetime.combine(datetime.today(),start)
                if length < timedelta(minutes=90) or length > timedelta(minutes=120):
                    conn.close()
                    return 9
            elif restype == "singles":
                length = datetime.combine(datetime.today(),end) - datetime.combine(datetime.today(),start)
                if length < timedelta(minutes=60) or length > timedelta(minutes=90):
                    conn.close()
                    return 9

            # Guests have another overlapping reservation.
            if type(members) == int:
                members = [members]
            for mem in members:
                with conn.cursor() as cur:
                    cur.execute("SELECT start_time, end_time FROM reservation WHERE member_id = (%s)", (mem,))
                    check = cur.fetchall()

                for i in range(len(check)):
                    if check[i][0] <= start <= check[i][1]:
                        conn.close()
                        return 10
                    if check[i][0] <= end <= check[i][1]:
                        conn.close()
                        return 10


            conn.close()
            return 0
        except psycopg2.Error:
            return False


class President(Member):
    def __init__(self):
        super().__init__(1)

    def addEventFee(self, fee: float, memo: str, memberid: int):
        bill = Bill(memberid)
        valid = bill.createCharge(fee, memo, "Other")
        return valid

    def createMember(self, firstname: str, lastname: str, email: str, phonenum: str, optin: bool, pw: str):
        #try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO member (firstname, lastname, email, phonenum, optin, password) "
                                "VALUES (%s, %s, %s, %s, %s, crypt(%s, gen_salt('md5')))",
                                (firstname, lastname, email, phonenum, optin, pw))
            return 0
        #except psycopg2.Error:
            #return -1

    def updateInformation(self, member_id: int, attribute: str, value: str):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    if attribute == 'password':
                        cur.execute("UPDATE member SET password = crypt(%s, gen_salt('md5')) WHERE member_id = (%s)", (value,member_id))
                    else:
                        cur.execute(sql.SQL("UPDATE member SET {attr} = %s WHERE member_id = %s").format(attr = sql.Identifier(attribute)),(value,member_id))
            return 0
        except psycopg2.Error as e:
            return -1
        except TypeError as e:
            return -1
        except:
            return -1

    def deactivateMember(self, memberid: int):
        try:
            if int(memberid) == 1 or int(memberid) == 2:
                return -2
            else:
                try:
                    with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                        with conn.cursor() as cur:
                            cur.execute("UPDATE member SET active = FALSE WHERE member_id = %s", (memberid,))
                    return 0
                except psycopg2.Error as e:
                    return -1
        except:
            return -1

    def getBill(self,memberid: int):
        bill = Bill(memberid)
        return bill.getBill()

    def getFullBill(self, memberid: int):
        bill = Bill(memberid)
        return bill.getFullBill()

    def deleteReservation(self, res_id: int):
        try:
            res_id = int(res_id)
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT member_id FROM reservation WHERE reservation_ID = (%s)", (res_id,))
                    member_id = cur.fetchall()[0][0]
                    # Checking Guestpasses
                    cur.execute("SELECT member_id FROM attendees WHERE reservation_id = (%s)", (res_id,))
                    attendees = cur.fetchall()
                    cur.execute("SELECT guestpass FROM member WHERE member_id = (%s)", (member_id,))
                    guestpass = cur.fetchone()[0]
                    cur.execute("SELECT charge_id FROM charges WHERE member_id = (%s) AND description = 'Guest Fee'", (member_id,))
                    charges = cur.fetchall()
                    chr_inc = 0
                    for i in range(len(attendees)):
                        if attendees[i][0] is None:
                            guestpass = guestpass+1
                            cur.execute("DELETE FROM charges WHERE charge_id = %s", (charges[chr_inc][0],))
                            chr_inc=chr_inc+1

                    cur.execute("UPDATE member SET guestpass = %s WHERE member_id = %s", (guestpass, member_id))
                    cur.execute("DELETE FROM reservation WHERE reservation_id = %s", (res_id,))
                return 1
        except:
            return 0

class BillingStaff(Member):
    def __init__(self):
        super().__init__(2)

    def addEventFee(self, fee: float, memo: str, memberid: int):
        bill = Bill(memberid)
        valid = bill.createCharge(fee, memo, "Other")
        return valid

    def modifyBill(self, charge_id: int, attribute: str, value: float):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute(sql.SQL("UPDATE charges SET {attr} = %s WHERE charge_id = (%s)").format(attr = sql.Identifier(attribute)),
                                (value, charge_id))
            return True
        except psycopg2.Error as e:
            return False
        except TypeError as e:
            return False

    def deleteCharge(self, charge_id:int):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM charges WHERE charge_id = %s", (charge_id,))
            return True
        except psycopg2.Error as e:
            return False

    def getBill(self,memberid: int):
        bill = Bill(memberid)
        return bill.getBill()

    def modifyGuestFee(self, guestfee: int):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE billing_constants SET guestfee = %s", (guestfee,))
            return True
        except psycopg2.Error as e:
            return False

    def modifyAnnualFee(self, annualfee: int):
        try:
            with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
                with conn.cursor() as cur:
                    cur.execute("UPDATE billing_constants SET annualfee = %s", (annualfee,))
            return True
        except psycopg2.Error as e:
            return False

    def getBillingScheme(self):
        with psycopg2.connect(dbname="aced", user="aceduser", password="acedpassword", port="5432") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM billing_constants")
                return cur.fetchall()

    def getFullBill(self, memberid: int):
        bill = Bill(memberid)
        return bill.getFullBill()



