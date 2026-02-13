from fastapi import APIRouter, Depends
from datetime import datetime
from app.European_option_price_calculator.schemas import OptionInput, OptionOutput
from app.European_option_price_calculator.services import OptionPriceService
from app.European_option_price_calculator.depends import get_option_price_service

router = APIRouter(prefix="", tags=["european_option_price_calculator"])


@router.post("/calculate", summary="计算期权价格")
async def calculate(
        option_input: OptionInput,
        option_price_service: OptionPriceService = Depends(get_option_price_service)
):
    """计算期权价格"""
    option_price = await option_price_service.calculate_option_price(option_input)
    return OptionOutput(
        option_price=option_price,
        calculation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status="success",
        parameters=option_input
    )