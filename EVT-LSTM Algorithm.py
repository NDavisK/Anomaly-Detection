import numpy
import pandas
import math
import tensorflow
import matplotlib.pyplot as plt
from numpy.random import seed
seed(1)
from math import sqrt
from numpy import concatenate
from matplotlib import pyplot
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from matplotlib.backends.backend_pdf import PdfPages
from tensorflow.python.keras.layers import *
from tensorflow.python.keras.models import *
from tensorflow.python.keras.optimizers import *
from tensorflow.python.keras import regularizers
from tensorflow.python.keras.callbacks import EarlyStopping
from tensorflow.python.keras import backend as K
stop = EarlyStopping(monitor='val_loss',min_delta = 0.00000001,patience=30,verbose = 0)
from spot import SPOT, biSPOT


tf_th = K.variable(0)

def evtloss(y_true,y_pred):

    wsum = (K.mean(K.square(K.abs(y_pred - y_true)-tf_th), axis=-1))
    
    return wsum
 
''' 
 Data is loaded and reshaped to match the LSTM's input shape and forms input2LSTM.
 n_train_hours is the number of training samples
'''

train_X_3d, train_y_3d = input2LSTM[:n_train_hours,:, :-1], input2LSTM[:n_train_hours,:, -1]

test_X_3d, test_y_3d = input2LSTM[n_train_hours:,:, :-1], input2LSTM[n_train_hours:,:, -1]

#suitable hyper-parameters obtained through Hyperopt for each data set

hcounter = 0

b_s = 64

L1 = [20]

L2 = [10]

q = 10e-4

reg = 10e-3

no_epochs = 100

dim = 1

model = Sequential()

model.add(LSTM(L1[hcounter],return_sequences=True,input_shape=(None,dim), use_bias = False, kernel_regularizer=regularizers.l2(reg), recurrent_regularizer= regularizers.l2(reg) ))

model.add(Dropout(0.17))

model.add(LSTM(L2[hcounter],return_sequences=True, use_bias = False, kernel_regularizer=regularizers.l2(reg), recurrent_regularizer= regularizers.l2(reg) ))

model.add(Dropout(0.45641472349028517))

model.add(Dense(1,activation = 'relu', use_bias = False, kernel_regularizer=regularizers.l2(reg)))

adam = Adam(lr= 10**-4)

update_epoch_set = range(20,no_epochs,20)

for epoch in range(no_epochs):

    model.compile(loss=evtloss, optimizer=adam)
    
    model.fit(train_X_3d,train_y_3d,batch_size =b_s, validation_split = 0.1,epochs=1,callbacks = [stop],verbose=1,shuffle = False)
    
    if epoch in update_epoch_set:
        
        intermediate_output = model.predict(train_X_3d)
        
        intermediate_errors = np.abs(intermediate_output.flatten() - train_y_3d.flatten())
        
        s = SPOT(q)
        
        s.fit(intermediate_errors.flatten()) 
        
        threshold = s.initialize()
        
        K.set_value(tf_th,(threshold))
        
        #Some verbose
        
        intermediate_output_test = model.predict(test_X_3d)
        
        intermediate_errors_test = np.abs(intermediate_output_test.flatten() - test_y_3d.flatten())
        
        results = s.run(intermediate_errors_test.flatten())
        
        print("Results at epoch:", epoch)
        
        print(results['alarms'])
        
        s.plot(results)
        
final_output = model.predict(test_X_3d)

final_errors = np.abs(final_output-test_y_3d)

anomalies = np.where(final_errors>threshold)

print("Detected Anomalies: ", anomalies)
