import json, urllib, logging
from urllib.request import Request, urlopen
from urllib.parse import urlencode

API_SERVER = "https://www.google.com/recaptcha/api/siteverify"

logger = logging.getLogger(__name__)

def get_ip(request):
    get = request.headers.get
    ip = get('REMOTE_ADDRESS') or get("HTTP_X_FORWARDED_FOR") or '127.0.0.1'
    return ip

def html_field(site_key):
    """
    """
    field = """
    <div class="recaptcha">
    <script src="https://www.google.com/recaptcha/api.js" async="async" defer="defer"></script>
    <div class="g-recaptcha" data-sitekey={site_key}"></div>
    </div>
    """.format(
        site_key=site_key,
    )
    return field


def validate_captcha(request, secret, remoteip=''):

    response = request.POST.get('g-recaptcha-response')

    data = urlencode({
        'secret': secret,
        'response': response,
        'remoteip': remoteip
    })

    data = data.encode('utf-8')

    req = Request(
        url=API_SERVER,
        data=data,
        headers={
            "Content-type": "application/x-www-form-urlencoded",
            "User-agent": "reCAPTCHA Python"
        }
    )

    try:
        with urlopen(req) as resp:
            values = resp.read()
            values = values.decode("utf-8")
            values = json.loads(values)

            if values.get('success'):
                return True, "success"

            # Attempt to provide a reason
            errors = ", ".join(values.get('error-codes', ['?']))
            msg = "Captcha validation failed: {}".format(errors)
            return False, msg

    except Exception as exc:
        msg = "{}".format(exc)
        logger.error(exc)

    return False, msg

