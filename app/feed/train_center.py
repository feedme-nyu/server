import os
import pandas as pd
import glob

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import pickle


def find_csv_filenames():
    all_files = glob.glob("*.csv")
    print(all_files)
      
    combined_csv = pd.concat([pd.read_csv(f) for f in all_files ])
    print(combined_csv.head(5))
    print(combined_csv.shape)
    for f in all_files:
        print(f)
        os.remove(f)
    return combined_csv
    

	#filenames = os.listdir(path)
	#return [filename for filename in filenames if filename.endswitch( suffix )]
		
def test_cron():
    print("Hello World, ths is test_cron()")
    return None

def retrain_model():
    print("train_center.py -> retrain_model()")
    merge_dataset()
    raw_data = pd.read_csv("Alpha.csv", delimiter=",")
    X_val = raw_data[raw_data.columns[2:-3]]
    Y_val = raw_data[raw_data.columns[-3]]
    
    print(X_val.shape, Y_val.shape)
    
    x_train, x_test, y_train, y_test = train_test_split(X_val, Y_val, random_state=10)
    l1 = LogisticRegression(random_state=0, solver='lbfgs',max_iter= 70000,penalty='l2',multi_class = 'multinomial')
    l1.fit(x_train, y_train)
    pickle.dump(l1, open('Logistic.sav', 'wb'))   
    
def merge_dataset():
    print("train_center.py -> merge_dataset()")   
    #  main .csv file
    new_dataset = find_csv_filenames()
    new_dataset.to_csv("Alpha.csv", index=False)
    
    
    
    
    
    





