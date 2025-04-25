from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.application import MIMEApplication 
from email.mime.multipart import MIMEMultipart
import smtplib 
import os

class Emailer:
    def __init__(self):
        self.smtp = None

    def connect(self):
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587) #server and port of your SMTP server
        self.smtp.ehlo() 
        self.smtp.starttls() 
        self.smtp.login('ACED.Tennis.Team@gmail.com', 'psmgnqwgvxaxzxou') #login email and password

    def sendEmail(self, text, subject, email):
        msg = MIMEMultipart() 
        msg['Subject'] = subject 
        msg.attach(MIMEText(text)) 
        self.smtp.sendmail(from_addr="Your Login Email", to_addrs=email, msg=msg.as_string()) 
        self.smtp.quit()

    def sendReservationConfirmation(self,res_id, email):
        subject = "ACED Reservation Confirmation"
        text = ("You scheduled a reservation!" + '\n'
                + "Reservation ID: " + str(res_id) +'\n'
                + "Please use the scheduler if you need to delete or change your reservation!")
        self.connect()
        self.sendEmail(text, subject, email)

    def sendReservationConfirmationAdded(self, res_id, email):
        subject = "ACED Reservation Confirmation"
        text = ("You were added to a reservation!" + '\n'
                + "Reservation ID: " + str(res_id) + '\n')
        self.connect()
        self.sendEmail(text, subject, email)

    def sendBillEmail(self, bill, email):
        subject = "ACED Bill"
        billstr = 'Amount   Date    Description     Type'
        for i in range(len(bill)):
            billstr = billstr + "\n"
            billstr = billstr + str(bill[i][1]) + "     " + str(bill[i][2]) + "     " + bill[i][3] + "      " + bill[i][4]

        text = ("Your bill is due! Please pay via the Billing page before January 31st. Your bill is below:" +
                "\n" + billstr +
                "\n" + "Thank You!" + "\n" + "ACED Billing Staff")

        self.connect()
        self.sendEmail(text, subject, email)

    def lateBillEmail(self, email):
        subject = "Late Bill"
        text = "NOTICE: Your bill is late and a late fee has been added to your account. Please pay your bill by March 31st to avoid deactivation!"

        self.connect()
        self.sendEmail(text, subject, email)
        
#emailer testing (must have SMPTP server set up)
#emailer = Emailer()
#emailer.connect()
#emailer.sendEmail("Hello World", "Test", "cookepoli@hartford.edu")