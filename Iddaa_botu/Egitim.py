import tensorflow as tsf
from sklearn.model_selection import train_test_split
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation,Dense,Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.metrics import categorical_crossentropy
import numpy as np
import mysql.connector
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler
from keras.optimizer_v2.gradient_descent import SGD
from sklearn.metrics import confusion_matrix
import itertools
import matplotlib.pyplot as plt
"""
def plot_confusion_matrix(cm,classes,normalize=False,title = "Confusion matrix",cmap = plt.cm.Blues):
    plt.imshow(cm,interpolation = 'nearest',cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks,classes,rotation = 45)
    plt.yticks(tick_marks,classes)

    if normalize:
        cm = cm.astype('float')/cm.sum(axis=1)[:,np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('confusion matrix,without normalization')
    print(cm)

    thresh = cm.max()/2
    for i,j in itertools.product(range(cm.shape[0]),range(cm.shape[1])):
        plt.text(j,i,cm[i,j],
                 horizontalaligments="center",
                 color = "white"if cm[i,j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
"""

def mysql_veri_cek():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Emireren1",
        database="ysa_proje"
    )
    cur = mydb.cursor()
    cur.execute("select * from tbl_maclar")
    records = cur.fetchall()
    records = list(records)
    array = []
    for record in records:
        record = record[6:]
        array.append(record)
    train_samples = np.array(array)
    cur.close()

    cur = mydb.cursor()
    cur.execute("select * from tbl_labellar ")
    records = cur.fetchall()
    records = list(records)

    array = []
    print("*" * 10)
    for record in records:
        record = record[1:4]
        array.append(record)
    train_labels = np.array(array)
    print(train_labels.shape)
    cur.close()
    mydb.close()
    return train_samples,train_labels



samples,labels=mysql_veri_cek()
train_samples,train_labels = shuffle(samples,labels)
train_samples,test_samples,train_labels, test_labels = train_test_split(samples,labels, test_size=0.15)


scaler = MinMaxScaler(feature_range=(0,1))
scaled_train_samples = scaler.fit_transform(train_samples)
scaled_test_samples = scaler.fit_transform(test_samples)

"""
model = Sequential([
    Dense(units=64,input_shape=(59,),activation="relu"),
    Dropout(0.3),
    Dense(units=128,activation="relu"),
    Dropout(0.3),
    Dense(units=128, activation="relu"),
    Dropout(0.3),
    Dense(units=64,activation="relu"),
    Dropout(0.3),
    Dense(units=3,activation="softmax")
])"""

model = Sequential([
    Dense(units=64,input_shape=(59,),activation="relu"),
    Dropout(0.3),
    Dense(units=128,activation="relu"),
    Dropout(0.3),
    Dense(units=128,activation="relu"),
    Dropout(0.3),
    Dense(units=64,activation="relu"),
    Dropout(0.3),
    Dense(units=3,activation="softmax")
])
#64,128,128,3 dropout 4847 acc
#64,128,128,64,3 dropout  4889 acc bu iyi

model.summary()
#62 128 100 85 62
#13 45 30 15
opt =SGD(learning_rate=0.001)
model.compile(optimizer=Adam(0.001),loss='categorical_crossentropy',metrics=['accuracy'])
model.fit(x=scaled_train_samples,y=train_labels,validation_split=0.1,batch_size=128,epochs=120,verbose=2)
predictions = model.predict(x = scaled_test_samples, batch_size=64,verbose=0)
for i in predictions:
    #if i[0]> 0.60 or i[1] > 0.60 :
    print(i)
model.save('models/iddaa_botu_modeli.h5')

