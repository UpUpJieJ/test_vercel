



from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(status_code=status_code, detail=message)



class OptionPriceCalculationError(AppException):
    """
    期权价格计算错误
    """

    def __init__(self, message:str , status_code: int = 400):
        super().__init__(message=message, status_code=status_code)
