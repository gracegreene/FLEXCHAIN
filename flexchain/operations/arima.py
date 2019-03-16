# 1. Store whole sales history in pandas df
# 2. Divide data to test and train
# 3. Generate pdq combinations
# 4. Loop to build models around pdq. Store pdq and MSE
# 5. Find the minimum MSE and use the pdq as final model for that week

import pandas as pd
from pandas import datetime
import matplotlib.pyplot as plt


def parser(x):
    return datetime.strptime(x, '%m/%d/%Y')


# store sales to pandas and use date as the index
sales = pd.read_csv('penholder_sales.csv', parse_dates=[0], index_col=[0], date_parser=parser)
# print(sales.head)

# split data for training and testing
x = sales.values
train_size = int(len(x) * 0.70)
train, test = x[0:train_size], x[train_size:len(x)]
# train = x[0:27] #27 as test data
# test = x[27:]
predictions = []

# Convert series to stationary because data has a trend

# sales_diff=sales.diff(periods=1)

# take the NAN out

# sales_diff=sales_diff[1:]
# sales_diff.head()

# print(sales_diff.head)

# checking autocorrelation
# from statsmodels.graphics.tsaplots import plot_acf
# plot_acf(sales)

# check autocorrelation of integral with order 1
# plot_acf(sales_diff)

# x=sales.values
# train = x[0:27] #27 as test data
# test = x[27:]
# predictions=[]
#
# # AR model
# from statsmodels.tsa.ar_model import AR
# from sklearn.metrics import mean_squared_error
# #model_ar=AR(train)
# #model_ar_fit = model_ar.fit()
#
# #ARIMA model
from statsmodels.tsa.arima_model import ARIMA
from sklearn.metrics import mean_squared_error


#
# # p=periods taken for autoregressive model
# # d= integrated order,difference
# # q periods in moving average model,shift
# # model_arima = ARIMA(train,order=(3,1,1))
# # model_arima_fit=model_arima.fit()
# # print(model_arima_fit.aic)  #AIC is like MSE
# # predictions=model_arima_fit.forecast(steps=9)
# # print(predictions)
#


class ARIMAModelResult:
    def __init__(self, autoregressive_periods, integrated_order, moving_average_model_periods, training_data, test):
        self.autoregressive_periods = autoregressive_periods
        self.integrated_order = integrated_order
        self.moving_average_model_periods = moving_average_model_periods
        self.model = ARIMA(training_data, order=(
            self.autoregressive_periods,
            self.integrated_order,
            self.moving_average_model_periods
        )
                           )
        self.fit = self.model.fit()
        self.aic = self.fit.aic
        self.predictions = self.fit.forecast(steps=len(test))[0]
        self.model_fitness = mean_squared_error(test, self.predictions)

    def __eq__(self, other):
        return self.model_fitness == other.model_fitness

    def __lt__(self, other):
        return self.model_fitness < other.model_fitness

    def __gt__(self, other):
        return self.model_fitness > other.model_fitness

    def __str__(self):
        return "Autoregressive periods: {}\nIntegraded Order: {}\nMoving Average Model Periods: {}\n Predictions: {}\nMSE: {}".format(
            self.autoregressive_periods,
            self.integrated_order,
            self.moving_average_model_periods,
            self.predictions,
            self.model_fitness
        )


# generating combinations of pdq
import itertools
import warnings

warnings.filterwarnings('ignore')
p = [12]
d = q = range(0, 3)
pdq = list(itertools.product(p, d, q))
arima_model_results = []
for p, d, q in pdq:
    try:
        arima_model_results.append(ARIMAModelResult(p, d, q, train, test))
    except:
        continue

minimum_mse_model = min(arima_model_results)
print(minimum_mse_model)
# predictions=minimum_aic_model.fit.forecast(steps=len(test))[0]
# mse = mean_squared_error(test, predictions)
# print(predictions)
# print(mse)

# resultset={}
# import warnings
# warnings.filterwarnings('ignore')
# for param in pdq:
#     try:
#         model_arima = ARIMA(train, order=param)
#         model_arima_fit = model_arima.fit()
#         key = ''.join([str(e) for e in param])
#         resultset[key]=model_arima_fit.aic  #WHAT TO USE FOR KEY IF NOT ALLOWED
#     except:
#         continue
#
# minimum = 9999999999999999999
# minimum_key = None
# for key, value in resultset.items():
#     if value < minimum:
#         minimum = value
#         minimum_key = key
#
# print("Key: {}\tMinimum: {}".format(minimum_key, minimum))
#
# #MSE
# mean_squared_error(test,predictions)
