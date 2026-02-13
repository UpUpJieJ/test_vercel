import pytest
import math
from app.European_option_price_calculator.services import OptionPriceService
from app.European_option_price_calculator.schemas import OptionInput, OptionType


class TestOptionPriceService:
    """期权价格服务测试类"""

    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return OptionPriceService()

    @pytest.fixture
    def sample_call_input(self):
        """示例看涨期权输入参数"""
        return OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=100.0,
            strike_price=95.0,
            days_to_expiry=30
        )

    @pytest.fixture
    def sample_put_input(self):
        """示例看跌期权输入参数"""
        return OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.PUT,
            spot_rate=100.0,
            strike_price=105.0,
            days_to_expiry=30
        )

    @pytest.mark.asyncio
    async def test_calculate_call_option_price(self, service, sample_call_input):
        """测试看涨期权价格计算"""
        price = await service.calculate_option_price(sample_call_input)
        
        assert isinstance(price, float), "价格应为浮点数"
        assert price > 0, "看涨期权价格应为正数"
        assert price < sample_call_input.spot_rate, "期权价格不应超过标的资产价格"
        print(f"看涨期权价格: {price}")

    @pytest.mark.asyncio
    async def test_calculate_put_option_price(self, service, sample_put_input):
        """测试看跌期权价格计算"""
        price = await service.calculate_option_price(sample_put_input)
        
        assert isinstance(price, float), "价格应为浮点数"
        assert price > 0, "看跌期权价格应为正数"
        print(f"看跌期权价格: {price}")

    @pytest.mark.asyncio
    async def test_call_price_less_than_put_when_spot_below_strike(self, service):
        """测试当即期价格低于行权价时，看跌期权价格应高于看涨期权"""
        input_data = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=95.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        
        call_price = await service.calculate_option_price(input_data)
        
        put_input = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.PUT,
            spot_rate=95.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        put_price = await service.calculate_option_price(put_input)
        
        assert put_price > call_price, "当即期价低于行权价时，看跌期权价格应高于看涨期权"
        print(f"看涨期权价格: {call_price}, 看跌期权价格: {put_price}")

    @pytest.mark.asyncio
    async def test_call_price_greater_than_put_when_spot_above_strike(self, service):
        """测试当即期价格高于行权价时，看涨期权价格应高于看跌期权"""
        input_data = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=110.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        
        call_price = await service.calculate_option_price(input_data)
        
        put_input = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.PUT,
            spot_rate=110.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        put_price = await service.calculate_option_price(put_input)
        
        assert call_price > put_price, "当即期价高于行权价时，看涨期权价格应高于看跌期权"
        print(f"看涨期权价格: {call_price}, 看跌期权价格: {put_price}")

    @pytest.mark.asyncio
    async def test_price_rounding(self, service, sample_call_input):
        """测试价格保留8位小数"""
        price = await service.calculate_option_price(sample_call_input)
        
        decimal_places = len(str(price).split('.')[-1]) if '.' in str(price) else 0
        assert decimal_places <= 8, f"价格应保留最多8位小数，实际为{decimal_places}位"

    @pytest.mark.asyncio
    async def test_at_the_money_option(self, service):
        """测试平价期权（ATM）"""
        input_data = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=100.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        
        call_price = await service.calculate_option_price(input_data)
        
        put_input = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.PUT,
            spot_rate=100.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        put_price = await service.calculate_option_price(put_input)
        
        assert call_price > 0, "平价看涨期权应有正的时间价值"
        assert put_price > 0, "平价看跌期权应有正的时间价值"
        print(f"平价看涨期权价格: {call_price}, 平价看跌期权价格: {put_price}")

    @pytest.mark.asyncio
    async def test_deep_in_the_money_call(self, service):
        """测试深度实值看涨期权"""
        input_data = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=150.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        
        price = await service.calculate_option_price(input_data)
        
        intrinsic_value = input_data.spot_rate - input_data.strike_price
        assert price > intrinsic_value * 0.99, "深度实值期权价格应接近内在价值"

    @pytest.mark.asyncio
    async def test_deep_out_of_the_money_call(self, service):
        """测试深度虚值看涨期权"""
        input_data = OptionInput(
            ccy_pair="USDCNY",
            option_type=OptionType.CALL,
            spot_rate=50.0,
            strike_price=100.0,
            days_to_expiry=30
        )
        
        price = await service.calculate_option_price(input_data)
        
        assert price < 1.0, "深度虚值期权价格应较低"
        print(f"深度虚值看涨期权价格: {price}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
