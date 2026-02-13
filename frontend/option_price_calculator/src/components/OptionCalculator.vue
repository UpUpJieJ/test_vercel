<template>
  <div class="calculator-container">
    <el-card class="box-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <h2>欧式期权价格计算器</h2>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧输入框 -->
        <el-col :xs="24" :md="12">
          <div class="input-section">
            <h3>参数输入</h3>
            <el-form :model="form" :rules="rules" ref="formRef" label-position="top" size="large" >
              
              <el-form-item label="标的资产币种对" prop="ccyPair">
                <el-input @input="onInputChange" v-model="form.ccyPair" placeholder="如 USDCNY" />
              </el-form-item>

              <el-form-item label="即期汇率" prop="spotRate">
                <el-input-number @input="onInputChange" v-model="form.spotRate" :min="0" :precision="6" :step="0.0001" style="width: 100%" placeholder="请输入即期汇率" />
              </el-form-item>

              <el-form-item label="行权价格 (K)" prop="strikePrice">
                <el-input-number @input="onInputChange" v-model="form.strikePrice" :min="0" :precision="6" :step="0.0001" style="width: 100%" placeholder="请输入行权价格" />
              </el-form-item>

              <el-form-item label="到期时间 (T)" prop="daysToExpiry">
                <el-input-number @input="onInputChange" v-model="form.daysToExpiry" :min="0" :step="1" :precision="0" style="width: 100%" placeholder="天" >
                    <template #suffix>天</template>
                </el-input-number>
              </el-form-item>

              <el-form-item label="期权类型" prop="optionType">
                <el-radio-group @input="onInputChange" v-model="form.optionType" style="width: 100%">
                  <el-radio-button label="call" value="call">看涨期权 (Call)</el-radio-button>
                  <el-radio-button label="put" value="put">看跌期权 (Put)</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="calculate" :loading="loading" style="width: 100%">计算</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-col>

        <!-- 展示数据框 -->
        <el-col :xs="24" :md="12">
          <div class="result-section">
              <h3>计算结果(基于 Black-Scholes 模型)</h3>
            <!-- 加载动画 -->
              <div v-if="loading" class="loading-container">
                <el-skeleton class="loading-skeleton" animated>
                  <template #template>
                    <el-skeleton-item variant="rect" style="width: 100%; height: 120px; border-radius: 8px;" />
                  </template>
                </el-skeleton>
                <div class="loading-text">计算中...</div>
              </div>
              <!-- 结果展示 -->
              <div v-else-if="result" class="result-content">
                <el-card class="price-card" :class="form.optionType">
                  <div class="price-label">期权理论价格</div>
                  <div class="price-value">{{ formatCurrency(result.price) }}</div>
                  <div class="price-label">计算时间：{{ resultTime.time }}</div>
                </el-card>
              </div>
            <el-empty style="padding-bottom: 10px;" v-else description="请输入参数并点击计算" />
            <el-alert
              v-if="error"
              :title="error"
              type="error"
              show-icon
              style="margin-top: 20px"
            />
          </div>
          <!-- 历史记录部分 -->
          <div class="history-section">
            <div class="history-header">
              <h4>历史记录</h4>
              <el-button 
                v-if="localResult.length > 0" 
                type="danger" 
                size="small" 
                @click="clearHistory"
              >
                清空记录
              </el-button>
            </div>
            
            <div class="history-list">
              <div 
                v-for="record in localResult" 
                :key="record.id" 
                class="history-item"
              >
                <div class="history-info">
                  <div class="history-price">
                    <span class="price">{{ formatCurrency(record.result.price) }}</span>
                    <span 
                      class="type-tag" 
                      :class="record.params.option_type === 'call' ? 'call' : 'put'"
                    >
                      {{ record.params.option_type === 'call' ? '看涨' : '看跌' }}
                    </span>
                  </div>
                  <div class="history-details">
                    <div class="detail-item">
                      <label>币种对:</label>
                      <span>{{ record.params.ccy_pair }}</span>
                    </div>
                    <div class="detail-item">
                      <label>即期:</label>
                      <span>{{ record.params.spot_rate }}</span>
                    </div>
                    <div class="detail-item">
                      <label>行权价:</label>
                      <span>{{ record.params.strike_price }}</span>
                    </div>
                    <div class="detail-item">
                      <label>天数:</label>
                      <span>{{ record.params.days_to_expiry }}天</span>
                    </div>
                  </div>
                  <div class="history-time">
                    {{ formatDate(record.calculationTime) }}
                  </div>
                </div>
                <div class="history-actions">
                  <el-button 
                    type="primary" 
                    link 
                    size="small"
                    @click="useHistory(record)"
                  >
                    重用
                  </el-button>
                </div>
              </div>
              
              <el-empty 
                v-if="localResult.length === 0" 
                description="暂无历史记录" 
                :image-size="80" 
              />
            </div>
          </div>
        </el-col>
        
        
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const formRef = ref(null)
const loading = ref(false)
const result = ref(null)
const resultTime = ref(null)
const error = ref(null)
const localResult = ref([])

// 加载历史记录
onMounted(() => {
  const savedHistory = localStorage.getItem('optionCalculatorHistory')
  if (savedHistory) {
    localResult.value = JSON.parse(savedHistory)
  }
})

const form = reactive({
  ccyPair: 'USDCNY',
  spotRate: 8.8,
  strikePrice: 8.8,
  daysToExpiry: 30,
  optionType: 'call'
})

const rules = {
  ccyPair: [
    { required: true, message: '请输入标的资产币种对', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!value || !/^[A-Za-z]{6}$/.test(value.trim())) {
          callback(new Error('币种对格式应为 6 位字母，如 USDCNY'))
        } 
        else if (value.slice(0,3)===value.slice(3)) {
          callback(new Error('币种对格式不正确, 两种币种不能相同'))
        }
        else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  spotRate: [{ required: true, message: '请输入即期汇率', trigger: 'blur' }],
  strikePrice: [{ required: true, message: '请输入行权价格', trigger: 'blur' }],
  daysToExpiry: [
    { required: true, message: '请输入到期时间', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (!Number.isInteger(value) || value <= 0) {
          callback(new Error('到期时间必须为正整数'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  optionType: [{ required: true, message: '请选择期权类型', trigger: 'change' }]
}
const onInputChange = (value) => {
  // 如果是币种对输入框,则转换为大写
  if (typeof value === 'string') {
    form.ccyPair = value.toUpperCase()
  }
  
  // 清空右侧的内容
  result.value = null
  resultTime.value = null
  error.value = null
}
const calculate = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate((valid) => {
    if (valid) {
      performCalculation()
    } else {
      ElMessage.error('请检查输入参数')
    }
  })
}

const performCalculation = () => {
  loading.value = true
  error.value = null
  const data = JSON.stringify({
      ccy_pair: form.ccyPair,
      option_type: form.optionType,
      spot_rate: form.spotRate,
      strike_price: form.strikePrice,
      days_to_expiry: form.daysToExpiry
    })
  fetch('api/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: data
  })
    .then(async (response) => {
      const data = await response.json()
      if (!response.ok) {
        let errorMessage = '服务器计算失败'
        if (data?.message && Array.isArray(data.message)) {
          // 处理后端返回的对象数组格式
          const errorDetails = data.message.map(item => {
            const field = Object.keys(item)[0]
            const message = item[field]
            return `${field}: ${message}`
          }).join('; ')
          errorMessage = errorDetails
        } else {
          errorMessage = data?.message || data?.status || '计算失败'
        }
        throw new Error(errorMessage)
      }
      // 成功请求
      result.value = {
        price: data.option_price
      }
      resultTime.value = {
        time: data.calculation_time
      }
      // 保存到历史记录
      const historyRecord = {
        id: Date.now(), 
        params: data.parameters,
        result: {
          price: data.option_price
        },
        calculationTime: data.calculation_time
      }

      localResult.value.unshift(historyRecord)
      
      if (localResult.value.length > 10) {
        localResult.value = localResult.value.slice(0, 10)
      }
      
      localStorage.setItem('optionCalculatorHistory', JSON.stringify(localResult.value))
      loading.value = false
    })
    .catch((err) => {
      error.value = '计算错误: ' + err.message
      result.value = null
      loading.value = false
    })
}
// 货币格式化 动态识别目标货币
const formatCurrency = (val) => {
  let targetCurrency = "CNY";
  const cleanPair = form.ccyPair.toUpperCase();
  if (cleanPair.length === 6) {
    targetCurrency = cleanPair.slice(3);
  }
  const currencyLocaleMap = {
    CNY: 'zh-CN', // 人民币-中文
    USD: 'en-US', // 美元-英文
    EUR: 'de-DE', // 欧元-德文
    GBP: 'en-GB', // 英镑-英文
    JPY: 'ja-JP'  // 日元-日文
  };

  return new Intl.NumberFormat(
    currencyLocaleMap[targetCurrency] || 'zh-CN', 
    { 
      style: 'currency', 
      currency: targetCurrency, 
      minimumFractionDigits: 5, 
      maximumFractionDigits: 8 
    }
  ).format(val);
};
// 添加格式化时间的方法
const formatDate = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
// 清空历史记录
const clearHistory = () => {
  localResult.value = []
  localStorage.removeItem('optionCalculatorHistory')
}
// 使用历史记录数据重新计算
const useHistory = (record) => {
  form.ccyPair = record.params.ccy_pair
  form.optionType = record.params.option_type
  form.spotRate = record.params.spot_rate
  form.strikePrice = record.params.strike_price
  form.daysToExpiry = record.params.days_to_expiry

  calculate()
}

</script>

<style scoped>
.calculator-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  color: #909399;
  font-size: 14px;
}

.input-section, .result-section {
  padding: 20px;
  padding-bottom: 5px;
}

.input-section, .result-history-section {
  padding: 5px;
}

h3 {
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #EBEEF5;
  color: #606266;
}

.price-card {
  text-align: center;
  margin-bottom: 20px;
  padding: 20px 0;
  background-color: #f5f7fa;
  border: none;
}

.price-card.call .price-value {
  color: #f56c6c;
}

.price-card.put .price-value {
  color: #67c23a;
}

.price-label {
  font-size: 16px;
  color: #909399;
  margin-bottom: 10px;
}

.price-value {
  font-size: 36px;
  font-weight: bold;
}

.loading-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  padding: 20px;
}

.loading-skeleton {
  width: 100%;
  margin-bottom: 15px;
}

.loading-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 30px;
  color: #909399;
  text-align: center;
  z-index: 1;
}
.history-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.history-header h4 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background-color: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.history-info {
  flex: 1;
}

.history-price {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.price {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
  margin-right: 10px;
}

.type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
}

.type-tag.call {
  background-color: #f56c6c;
}

.type-tag.put {
  background-color: #67c23a;
}

.history-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
}

.detail-item {
  display: flex;
  gap: 4px;
}

.detail-item label {
  font-weight: bold;
  color: #909399;
  min-width: 40px;
}

.detail-item span {
  color: #606266;
  flex: 1;
}

.history-time {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.history-actions {
  margin-left: 10px;
}
</style>
