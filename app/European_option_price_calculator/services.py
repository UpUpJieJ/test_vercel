import math
import time
from scipy.stats import norm
from app.European_option_price_calculator.exceptions import OptionPriceCalculationError
from app.European_option_price_calculator.schemas import OptionInput
from app.utils.logger import log

class OptionPriceService:
    async def calculate_option_price(self, option_input: OptionInput) -> float:
        """计算期权价格"""
        try:
            S = option_input.spot_rate  # 即期汇率
            K = option_input.strike_price  # 行权价
            T = option_input.days_to_expiry / 365.0  # 年期
            r = 0.02  # 无风险利率，假设为2%
            sigma = 0.03  # 历史波动率，假设为3%

            # 计算公共变量d1 d2
            d1 = (math.log(S / K) + (r + 1/2 * sigma ** 2) * T) / (sigma * math.sqrt(T))
            d2 = d1 - sigma * math.sqrt(T)

            # 计算标准正态分布的累计分布函数
            N_d1 = norm.cdf(d1)
            N_d2 = norm.cdf(d2)
            N_neg_d1 = norm.cdf(-d1)
            N_neg_d2 = norm.cdf(-d2)

            # 根据期权类型计算期权价格
            if option_input.option_type == "call":
                price = S * N_d1 - K * math.exp(-r * T) * N_d2
            else:  
                price = K * math.exp(-r * T) * N_neg_d2 - S * N_neg_d1
        except Exception as e:
            log.error(f"Error calculating option price: {e}")
            raise OptionPriceCalculationError(message=str(e))
            
        return round(price, 8)