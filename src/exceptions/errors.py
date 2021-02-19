from http import HTTPStatus

NO_R2CONTEXT_FOUND = 'No R2Context found. Please login'
NO_USERINFO_PROVIDED = "No User ID provided. Please login"
NO_TENANTINFO_PROVIDED = "No Tenant ID provided. Please login"
NO_USERROLES_PROVIDED = "No User Roles provided as header x-r2-user-roles. Please login"
EXPLICIT_DENIAL_FOR_ROLE = "Access to perform this action is explicitly denied for this role {role_name}"
NO_AUTHORIZATION_FOR_ROLE = "Access to perform this action is not provided. You are required to a member of one of these roles {allowed_roles}"
ORDER_UPLOAD_FILE_PART_MISSION = "No file part provided in request. Use 'file'."
ORDER_UPLOAD_NO_FILE_PROVIDED = "No file provided in request."
FILE_TYPE_NOT_PERMITTED = "Unrecognized file format. Allowed file types are csv"
DEV_ERROR_TARGET_IO_OPERATION  = 'DEV: Your environment is missing the target folder.'
NOT_IMPLEMENTED = "This feature is not implemented. It is possible, that this feature is in development"
MULTIPLE_ROWS_FOUND = "Mulitple rows found for critiera: {criteria}. This is mostly a business rule failure and a development issue."
FILE_COMPLIANCE_MISSING_COLUMNS = 'Upload is missing columns {column_list}. Please add these columns to the compliance template or add these columns to the upload file.'
INVALID_DATA_PROVIDED = "Invalid data provided"
NO_RECORDS_FOUND = "No Records Found"
INVALID_FILE_PROVIDED = "Invalid file - {message}"
NO_DATA_PROVIDED = "Input data not provided"
INCOMPLIANT_DATA = "Incomplaint Data"
NOT_CONFIGURED = "{message} not yet configured"
NO_ACTIVE_CALENDAR_PERIOD="No active accounting calendar period"
SERVER_ERROR = "Internal Server Error. Please contact IT support."
DATA_MISMATCH = "Mismatch between policy and transaction type."
NO_ACCOUNTING_PERIOD = "Triggered period is not provided to calculate RC Metrics"
NO_PERIOD_IN_ACC_CALENDAR = "Given current open period is not valid in the accounting calendar setup"

class RCMetricsError(Exception):
    def __init__(self, error_message="", response_code=None,
                 response_body=None):

        Exception.__init__(self, error_message)

        self.response_code = response_code
        self.response_body = response_body
        self.error_message = error_message

    def __str__(self):
        if self.response_code is not None:
            return "{0}: {1}".format(self.response_code, self.error_message)
        else:
            return "{0}".format(self.error_message)

class ExplicitDenialForRole(Exception):
    def __init__(self, role_name):
        params_path = {"role_name": role_name}
        error_message = EXPLICIT_DENIAL_FOR_ROLE.format(**params_path)
        self.error_message = error_message
        Exception.__init__(self, error_message)
        self.response_code = HTTPStatus.UNAUTHORIZED
        self.role_name = role_name
    def __str__(self):
        return "{0}: {1}".format(self.response_code, self.error_message)

class UserMissingAuthorization(Exception):
    def __init__(self, roles):
        params_path = {"allowed_roles": roles}
        error_message = NO_AUTHORIZATION_FOR_ROLE.format(**params_path)
        self.error_message = error_message
        Exception.__init__(self, error_message)
        self.response_code = HTTPStatus.UNAUTHORIZED
        self.roles = roles
    def __str__(self):
        return "{0}: {1}".format(self.response_code, self.error_message)

class NoTriggeredPeriodinRequest(RCMetricsError):
    pass

class NoCurrentPeriodRequest(RCMetricsError):
    pass

class UserRolesNotProvided(RCMetricsError):
    pass

class NoFilePartInRequest(RCMetricsError):
    pass

class NoFileProvidedInRequest(RCMetricsError):
    pass

class FileTypeNoPermitted(RCMetricsError):
    pass

class UserInfoNotProvided(RCMetricsError):
    pass

class TenantInfoNotProvided(RCMetricsError):
    pass

class UploadFileSaveError(RCMetricsError):
    pass

class DBRegisterFileUploadedError(RCMetricsError):
    pass

class UnableToRegisterFileUploadMessage(RCMetricsError):
    pass

class DevEnvTargetFileAccessError(RCMetricsError):
    pass

class NotImplemented(RCMetricsError):
    pass

class MultipleResultsFound(RCMetricsError):
    pass

class InvalidDataProvided(RCMetricsError):
    def __init__(self, error_message=INVALID_DATA_PROVIDED,
                 response_code=HTTPStatus.BAD_REQUEST,
                 response_body=None):
        super().__init__(error_message, response_code, response_body)

class NoDataProvided(RCMetricsError):
    pass

class NoRecordsFound(RCMetricsError):
    pass

class IncompliantData(RCMetricsError):
    pass

class EmptyOrInvalidFileProvided(RCMetricsError):
    pass

