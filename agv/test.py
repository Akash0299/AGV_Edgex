import smtplib

# creates SMTP session
print('Inside smtp session test code')
s = smtplib.SMTP('smtp.gmail.com', 25)

print('SMTP session created')
 
# start TLS for security
#print('Inside start tls')
#s.starttls()
 
#print('TLS started') 

# Authentication
print('Authenticating..')
s.login("akash0299@gmail.com", "sathyasaibaba")
 
print('Login success')
 
# sending the mail
print('Sending mail')
s.sendmail("akash0299@gmail.com", "sirisatwikakotha29@gmail.com", message)
 
print('Mail successfully sent')
# terminating the session
print('Quitting')
s.quit()
