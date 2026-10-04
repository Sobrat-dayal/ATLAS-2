from atlas.core.exceptions import AtlasError

class CompanyError(AtlasError):
    def __init__(self, message: str, code: str = "COMPANY_ERROR", status_code: int = 400):
        super().__init__(message, code=code, status_code=status_code)

class CompanyNotFoundError(CompanyError):
    def __init__(self, entity_id: str):
        super().__init__(f"Company not found: {entity_id}", code="COMPANY_NOT_FOUND", status_code=404)

class CompanyDataInconsistentError(CompanyError):
    def __init__(self, entity_id: str):
        super().__init__(f"Company data inconsistent for entity: {entity_id}", code="COMPANY_DATA_INCONSISTENT", status_code=500)

class InvalidOrganizationTypeError(CompanyError):
    def __init__(self, org_type: str):
        super().__init__(f"Invalid organization type: {org_type}", code="INVALID_ORGANIZATION_TYPE", status_code=400)

class InvalidCompanyStatusError(CompanyError):
    def __init__(self, status: str):
        super().__init__(f"Invalid company status: {status}", code="INVALID_COMPANY_STATUS", status_code=400)

class InvalidCompanyCountryError(CompanyError):
    def __init__(self, entity_id: str):
        super().__init__(f"Invalid primary country entity ID: {entity_id}. Must be a country entity.", code="INVALID_COMPANY_COUNTRY", status_code=400)

class InvalidCompanyURLError(CompanyError):
    def __init__(self, url: str):
        super().__init__(f"Invalid company website URL: {url}", code="INVALID_COMPANY_URL", status_code=400)
