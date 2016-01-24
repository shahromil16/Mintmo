from flask import Flask, request, redirect
import twilio.twiml
import json, requests
import urllib.request as urllib2
from twilio.rest import TwilioRestClient
from nltk.tag import pos_tag
import re
 
app = Flask(__name__)

account_sid = "AC77c5f4b3c7bb0d4f2e92e982cefd6dbe"
auth_token = "e90ccf9a885aa2455faa47689a14289a"
client = TwilioRestClient(account_sid, auth_token)

# Accounts
urlac = 'http://api.reimaginebanking.com/enterprise/accounts?key=1e2b66d04760ccd17a94100593d21961'
r1 = requests.get(urlac)
with open('accounts.txt','w') as accounts:
    accounts.write(r1.text)
with open('accounts.txt') as accounts:
    data_ac = json.load(accounts)
    
# Bills
urlbi = 'http://api.reimaginebanking.com/enterprise/bills?key=1e2b66d04760ccd17a94100593d21961'
r2 = requests.get(urlbi)
with open('bills.txt','w') as bills:
    bills.write(r2.text)
with open('bills.txt') as bills:
    data_bi = json.load(bills)

### Customers
##urlcu = 'http://api.reimaginebanking.com/enterprise/customers?key=1e2b66d04760ccd17a94100593d21961'
##r3 = requests.get(urlcu)
##with open('customers.txt','w') as customers:
##    customers.write(r3.text)
with open('customers.txt') as customers:
    data_cu = json.load(customers)

# Deposits
urlde = 'http://api.reimaginebanking.com/enterprise/deposits?key=1e2b66d04760ccd17a94100593d21961'
r4 = requests.get(urlde)
with open('deposits.txt','w') as deposits:
    deposits.write(r4.text)
with open('deposits.txt') as deposits:
    data_de = json.load(deposits)

# Merchants
urlme = 'http://api.reimaginebanking.com/enterprise/merchants?key=1e2b66d04760ccd17a94100593d21961'
r5 = requests.get(urlme)
with open('merchants.txt','w') as merchants:
    merchants.write(r5.text)
with open('merchants.txt') as merchants:
    data_me = json.load(merchants)

# Tranfers
urltr = 'http://api.reimaginebanking.com/enterprise/transfers?key=1e2b66d04760ccd17a94100593d21961'
r6 = requests.get(urltr)
with open('transfers.txt','w') as transfers:
    transfers.write(r6.text)
with open('transfers.txt') as transfers:
    data_tr = json.load(transfers)

# Withdrawals
urlwi = 'http://api.reimaginebanking.com/enterprise/withdrawals?key=1e2b66d04760ccd17a94100593d21961'
r7 = requests.get(urlwi)
with open('withdrawals.txt','w') as withdrawals:
    withdrawals.write(r7.text)
with open('withdrawals.txt') as withdrawals:
    data_wi = json.load(withdrawals)

# Try adding your own number to this list!
callers = {
    "+18579197147": "56241a13de4bf40b17112864",
    "+18579197161": "56a088d63921211200ef22aa",
    }


 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond and greet the caller by name."""
         
    from_id = request.values.get('From', None)
    from_body = request.values.get('Body', None)

    words = ['accounts','ac','customers','zip','state'
             'farmers','cloth','shop','recurring',
             'payment','pending',
             'cancelled','completed'
             'restaurant','food','book','deposit','send','transfer','withdraw']
    from_body = from_body.lower()
    rcvdmsg = []
    mainword = []
    for word in words:
        if word in from_body:
            if word == 'ac':
                mainword = 'accounts'
            elif word == 'customers':
                mainword = 'customers'
            elif word == ('restaurant'or'food'or'book'or'merchants'):
                mainword = 'merchants'
            else:
                rcvdmsg.append(word)     
    subword = []
    message = "Hey! "
    if from_id in callers:
        if mainword == 'accounts':
        
            urlsub = "http://api.reimaginebanking.com/enterprise/accounts/"+callers[from_id]+"?key=1e2b66d04760ccd17a94100593d21961"
            rsub = requests.get(urlsub)
            with open('asub.txt','w') as asub:
                asub.write(rsub.text)
            with open('asub.txt') as asub:
                a = json.load(asub)
            
            n = 0
            print(rcvdmsg)
            if 'pending' in rcvdmsg:
                for i in range(0,len(data_bi['results'])):
                    if data_bi['results'][i]['account_id'] == callers[from_id]:
                        n = n + 1
                        urlsubsub = "http://api.reimaginebanking.com/enterprise/bills/"+data_bi['results'][i]['_id']+"?key=1e2b66d04760ccd17a94100593d21961"
                        rsubsub = requests.get(urlsubsub)
                        
                        with open('bsub.txt','w') as bsub:
                            bsub.write(rsubsub.text)
                        with open('bsub.txt') as bsub:
                            b = json.load(bsub)
                        message = message + " Your " + b["payee"] + " amount of $" + str(b["payment_amount"]) + " is " + b["status"] + "."
            
            elif 'deposit' in rcvdmsg:
                phone = re.findall('\d+', from_body)
                phone = phone[0]
                
                for i in range(0,len(data_de['results'])):
                    if data_de['results'][i]['payee_id'] == callers["+1"+phone]:
                        n = n + 1
                        urlsubsub = "http://api.reimaginebanking.com/enterprise/deposits/"+data_de['results'][i]['_id']+"?key=1e2b66d04760ccd17a94100593d21961"
                        rsubsub = requests.get(urlsubsub)
                        
                        with open('bsub.txt','w') as bsub:
                            bsub.write(rsubsub.text)
                        with open('bsub.txt') as bsub:
                            b = json.load(bsub)
                        if b["status"] == "executed":
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]+b["amount"]) + " for the reason of " + b["description"] + "."
                        else:
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]) + " for the reason of " + b["description"] + "."
                        
            elif 'transfer' in rcvdmsg:
                phone = re.findall('\d+', from_body)
                phone = phone[0]
                
                for i in range(0,len(data_tr['results'])):
                    if data_tr['results'][i]['payee_id'] == callers["+1"+phone]:
                        n = n + 1
                        urlsubsub = "http://api.reimaginebanking.com/enterprise/transfers/"+data_tr['results'][i]['_id']+"?key=1e2b66d04760ccd17a94100593d21961"
                        rsubsub = requests.get(urlsubsub)
                        
                        with open('bsub.txt','w') as bsub:
                            bsub.write(rsubsub.text)
                        with open('bsub.txt') as bsub:
                            b = json.load(bsub)
                        if b["status"] == "executed":
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]-b["amount"]) + " for the reason of " + b["description"] + "."
                        else:
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]) + " for the reason of " + b["description"] + "."
                        
            elif 'withdraw' in rcvdmsg:
                phone = re.findall('\d+', from_body)
                phone = phone[0]
                
                for i in range(0,len(data_wi['results'])):
                    if data_wi['results'][i]['payer_id'] == callers["+1"+phone]:
                        n = n + 1
                        urlsubsub = "http://api.reimaginebanking.com/enterprise/withdrawals/"+data_wi['results'][i]['_id']+"?key=1e2b66d04760ccd17a94100593d21961"
                        rsubsub = requests.get(urlsubsub)
                        
                        with open('bsub.txt','w') as bsub:
                            bsub.write(rsubsub.text)
                        with open('bsub.txt') as bsub:
                            b = json.load(bsub)
                        if b["status"] == "executed":
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]-b["amount"]) + " for the reason of " + b["description"] + "."
                        else:
                            message = message + " Your payment of " + str(b["amount"]) + " is " + b["status"] + ". Total amount in balance: " + str(a["balance"]) + " for the reason of " + b["description"] + "."
                       
      
            elif 'send' in rcvdmsg:
                for i in range(0,len(data_ac['results'])):
                    if data_ac['results'][i]['_id'] == callers[from_id]:
                        n = n + 1
                        urlsubsub = "http://api.reimaginebanking.com/enterprise/accounts/"+data_ac['results'][i]['_id']+"?key=1e2b66d04760ccd17a94100593d21961"
                        rsubsub = requests.get(urlsubsub)
                        
                        with open('bsub.txt','w') as bsub:
                            bsub.write(rsubsub.text)
                        with open('bsub.txt') as bsub:
                            b = json.load(bsub)
                        amt = re.findall('\d+', from_body)
                        amt = amt[0]
                        
                        message = message + " You paid " + amt + " to. Remaining amount in your account is: " + str(a["balance"]-int(amt))
                        
                        payload = {"balance": a["balance"]-int(amt)}
                        response = requests.post(urlsub,
                                                 data=json.dumps(payload),
                                                 headers={'content-type':'application/json'},
                                                 )
                        print(response)
            else:
                message = "Nothing"
                
            from_status = request.values.get('SmsStatus', None)
            from_zip = request.values.get('FromZip', None)
            with open("analysis.txt", "a") as analysis:
                analysis.write(from_body)
                analysis.write(",")
                analysis.write(from_status)
                analysis.write(",")
                analysis.write(from_zip)
                analysis.write(",")
                analysis.write(from_id)
                analysis.write("\n")

        
        elif mainword == 'customers':
            message = "Hi! "
            urlsub = "http://api.reimaginebanking.com/enterprise/customers?key=1e2b66d04760ccd17a94100593d21961"
            rsub = requests.get(urlsub)
            with open('asub.txt','w') as asub:
                asub.write(rsub.text)
            with open('asub.txt') as asub:
                a = json.load(asub)
            n = 0
            if 'zip' in rcvdmsg:
                amt = re.findall('\d+', from_body)
                amt = amt[0]
                count = 0
                for i in range(0,len(data_cu['results'])):
                    if data_cu['results'][i]['address']['zip'] == amt:
                        count = count + 1
                    with open("zipc.txt", "a") as zipc:
                        if len(data_cu['results'][i]['address']['state'])==2:
                            zipc.write(data_cu['results'][i]['address']['state'])
                            zipc.write(",")
                message = message + "There are " + str(count+1) + " customers in Zip asked for: " + amt
                with open('zipc.txt') as f:
                    data = f.readlines()
                    data = data[0]
                    vac = 0
                    mac = 0
                    nyc = 0
                    cac = 0
                    pac = 0
                    for i in range(0,len(data)-1):
                        if data[i]+data[i+1] == 'VA':
                            vac = vac+1
                        elif data[i]+data[i+1] == 'MA':
                            mac = mac+1
                        elif data[i]+data[i+1] == 'CA':
                            cac = cac+1
                        elif data[i]+data[i+1] == 'NY':
                            nyc = nyc+1
                        elif data[i]+data[i+1] == 'PA':
                            pac = pac+1
                    finaldata = {  "cols": [        {"id":"","label":"City","pattern":"","type":"string"},
                                                    {"id":"","label":"Requests","pattern":"","type":"number"}
                                                    ],
                                   "rows": [        {"c":[{"v":'VA',"f":"VA"},{"v":vac,"f":vac}]},
                                                    {"c":[{"v":'MA',"f":"MA"},{"v":mac,"f":mac}]},
                                                    {"c":[{"v":'NY',"f":"NY"},{"v":nyc,"f":nyc}]},
                                                    {"c":[{"v":'CA',"f":"CA"},{"v":cac,"f":cac}]},
                                                    {"c":[{"v":'PA',"f":"PA"},{"v":pac,"f":pac}]}
                                                    ]
                                   }
                    with open('final.json','w') as fp:
                        json.dump(finaldata,fp)
                        
                            
                            
                

        resp = twilio.twiml.Response()
    else:
        message = "Monkey, thanks for the message!"
     
    resp = twilio.twiml.Response()
    resp.message(message)

    
                
    
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)
