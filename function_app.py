import datetime
import smtplib
import json
import azure.functions as func
import dns.resolver

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="verifyemail",methods=["POST"])
def verifyemail(req: func.HttpRequest) -> func.HttpResponse:

    name = None

    try:
        req_body = req.get_json()
        name = req_body.get('email')
    except ValueError:
        return func.HttpResponse(ApiResponse("Provide Email Address",False).to_json(),status_code=400)

    if check_email_exists(name):
        return func.HttpResponse(ApiResponse("Email Exist",True).to_json(),status_code=200)
    else:
        return func.HttpResponse(
             ApiResponse("Provided Email Not Exist",False).to_json(),
             status_code=200
        )
    


def get_mx_records(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        mx_records = [str(record.exchange) for record in records]
        return mx_records
    except Exception as e:
        print(f"Error retrieving MX records for domain {domain}: {e}")
        return []

def check_email_exists(email):
    domain = email.split('@')[-1]
    mx_records = get_mx_records(domain)

    if not mx_records:
        print(f"No MX records found for domain {domain}")
        return False

    for mx in mx_records:
        try:
            server = smtplib.SMTP(mx)
            server.set_debuglevel(0)
            server.helo()
            server.mail('test@example.com')
            code, message = server.rcpt(email)
            server.quit()

            if code == 250:
                return True
            else:
                continue
        except Exception as e:
            print(f"Error connecting to mail server {mx}: {e}")
            continue

    return False


class ApiResponse:
    def __init__(self, message, isExist):
        self.message = message
        self.isExist = isExist
        self.timestamp = datetime.datetime.now()

    def to_json(self):
        return json.dumps({
            "message": self.message,
            "isExist": self.isExist,
            "timestamp": self.timestamp.isoformat()
        })

    def __str__(self):
        return f"{self.message} at {self.timestamp}"

@app.route(route="checkhealth", auth_level=func.AuthLevel.ANONYMOUS,methods=["GET"])
def checkhealth(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse("Health is Up",status_code=200)