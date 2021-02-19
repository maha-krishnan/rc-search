SPEC_MISSING_FIELD = "{field} in missing in {block}"
NO_GROUPING_FOUND = "No Grouping found when processing message"
CANNOT_FOLD_INVALID_FIELD_IN_GROUPING = "Folding Error when grouping gield: '{field}' in rule '{title}'. Field does not exist in upload specification. Please remove this field in grouping specification or add this field to the order upload template"
NOT_IMPLEMENTED = "No Implementation Found"
CANNOT_LOCATE_EXISTING_CONTRACT = "Cannot locate existing contract from Financial ID: {Financial_ID} or Grouping ID: {Grouping_ID}"
FINANCIAL_ID_NOT_FOUND = "No entry for financial id: {FINANCIAL_ID}"
GROUPING_ID_NOT_FOUND = "No entry for grouping id: {GROUPING_ID}"
EXPLICIT_DENIAL_FOR_ROLE = "Access to perform this action is explicitly denied for this role {role_name}"
NO_AUTHORIZATION_FOR_ROLE = "Access to perform this action is not provided. You are required to a member of one of these roles {allowed_roles}"
NO_R2CONTEXT_FOUND = 'No R2Context found. Please login'
NO_USERINFO_PROVIDED = "No User ID provided. Please login"
NO_TENANTINFO_PROVIDED = "No Tenant ID provided. Please login"
NO_USERROLES_PROVIDED = "No User Roles provided as header x-r2-user-roles. Please login"
EXPLICIT_DENIAL_FOR_ROLE = "Access to perform this action is explicitly denied for this role {role_name}"
NO_AUTHORIZATION_FOR_ROLE = "Access to perform this action is not provided. You are required to a member of one of these roles {allowed_roles}"


class stamperError(Exception):
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

class NotImplemented(Exception):
    def __init__(self, error_message=NOT_IMPLEMENTED,
                 debug=None):

        Exception.__init__(self, error_message)

        self.debug = debug
        self.error_message = error_message

    def __str__(self):
        return "{0}".format(self.error_message)

class NoGroupingFound(stamperError):
    pass

class CannotLocateRevenueContract(stamperError):
    pass

class FinancialIdNotFound(Exception):
  def __init__(self, error_message=FINANCIAL_ID_NOT_FOUND,
    debug=None):

    Exception.__init__(self, error_message)
    self.debug = debug
    self.error_message = error_message
    self.response_code = 204

  def __str__(self):
    return "{0}".format(self.error_message)

class GroupingIdNotFound(Exception):
  def __init__(self, error_message=GROUPING_ID_NOT_FOUND,
    debug=None):

    Exception.__init__(self, error_message)
    self.debug = debug
    self.error_message = error_message
    self.response_code = 204

  def __str__(self):
    return "{0}".format(self.error_message)


class TenantInfoNotProvided(stamperError):
    pass

class UserInfoNotProvided(stamperError):
    pass


class UserRolesNotProvided(stamperError):
    pass


class ExplicitDenialForRole(Exception):
    def __init__(self, role_name):
        params_path = {"role_name": role_name}
        error_message = EXPLICIT_DENIAL_FOR_ROLE.format(**params_path)
        self.error_message = error_message
        Exception.__init__(self, error_message)
        self.response_code = 401
        self.role_name = role_name
    def __str__(self):
        return "{0}: {1}".format(self.response_code, self.error_message)


class UserMissingAuthorization(Exception):
    def __init__(self, roles):
        params_path = {"allowed_roles": roles}
        error_message = NO_AUTHORIZATION_FOR_ROLE.format(**params_path)
        self.error_message = error_message
        Exception.__init__(self, error_message)
        self.response_code = 401
        self.roles = roles
    def __str__(self):
        return "{0}: {1}".format(self.response_code, self.error_message)
