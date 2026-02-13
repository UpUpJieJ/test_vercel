import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

class OptionInput(BaseModel):
    ccy_pair: str = Field(..., description="标的资产币种对 (如：USDCNY)")
    option_type: OptionType = Field(..., description="期权类型: call (看涨期权) 或 put (看跌期权)")
    spot_rate: float = Field(..., gt=0, description="即期汇率/现汇汇率")
    strike_price: float = Field(..., gt=0, description="期权行权价 (K)")
    days_to_expiry: int = Field(..., gt=0, description="期权到期时间 (T), 单位：天")
    @field_validator("option_type", mode="before")
    @classmethod
    def validate_option_type(cls, value):
        if isinstance(value, OptionType):
            return value
        if str(value).lower() not in {"call", "put"}:
            raise ValueError("option_type 只能是 'call' 或 'put', 请检查输入")
        return str(value).lower()

    @field_validator("spot_rate", "strike_price", "days_to_expiry", mode="before")
    @classmethod
    def validate_positive(cls, value, info):
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{info.field_name} 必须是正数")
        if numeric_value <= 0:
            raise ValueError(f"{info.field_name} 必须是正数")
        if info.field_name == "days_to_expiry" and int(numeric_value) != numeric_value:
            raise ValueError("days_to_expiry 必须是正整数")
        return value

    @field_validator("ccy_pair", mode="before")
    @classmethod
    def validate_ccy_pair(cls, value):
        if not isinstance(value, str):
            raise ValueError("ccy_pair 必须为字符串")
        ccy = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{6}", ccy):
            raise ValueError("必须为 6 位大写字母，如 USDCNY")
        return ccy


class OptionOutput(BaseModel):
    option_price: float = Field(..., description="期权理论价格")
    calculation_time: str = Field(..., description="计算时间")
    status: str = Field(..., description="计算状态")
    parameters: Optional[OptionInput] = Field(None, description="回显输入参数")

