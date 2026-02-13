from app.European_option_price_calculator.services import OptionPriceService
def get_option_price_service() -> OptionPriceService:
    """获取期权价格服务"""
    return OptionPriceService()