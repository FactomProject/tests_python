import smtplib


def send_email(msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    #Next, log in to the server
    server.login("factomtesting@gmail.com", "welcome01")
    #Send the mail
    #msg = "Hello!" # The /n separates the message from the headers
    #print msg
    server.sendmail("factomtesting@gmail.com", "factomtesting@gmail.com", msg)
    server.quit()

