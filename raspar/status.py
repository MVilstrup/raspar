class Status:
    def __init__(self, *general, **specific):
        self.general = list(set(general))
        self.specific = specific

    def __add__(self, other):
        general = self.general + other.general
        specific = self.specific.copy()
        specific.update(other.specific)
        return Status(*general, **specific)

TIMEOUT_ERROR = "Timeout Error"
CONTENT_TOO_BIG_ERROR = "Content Too Big Error"
TOO_MANY_REDIRECTS = "Too Many Redirects"

REQUEST_ERROR = "Request Error"
CLIENT_ERROR = "Client Error"
SERVER_ERROR = "Server Error"
INFORMATION_RESPONSE = "Information Response"

COULD_NOT_PARSE_ERROR = "Could Not Parse Page"

NULL_ERROR = "NULL Error"
VALIDATION_ERROR = "Validation Error"
RUNTIME_ERROR = "Run Time Error"

ALL_OK = "All Okay"