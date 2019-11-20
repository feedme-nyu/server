import pandas as pd
import sklearn
import pickle

'''
Final Return
Json:{
	name
	address
	distance
	photoURL
	Need to edit CSV
}
'''

def vodoo(new_csv):
	fd = open('Logistic.sav','rb') #cannot find file. maybe need to do ..
	model = pickle.load(fd,encoding='utf-8')
	raw_data = pd.read_csv(new_csv, header = 0)
	#print(raw_data.head())
	x_val = raw_data[raw_data.columns[2:9]]
	#print(x_val.head(2))
	prediction = model.predict(x_val)
	#print(prediction[27])
	raw_data.insert(0,"Chosen",prediction,True)
	raw_data.sort_values(by='Chosen' , inplace=True)
	raw_data.loc[raw_data["Chosen"]==1.0]
	#print(raw_data.head(30))
	raw_data.drop_duplicates(subset = "place_id",keep='last',inplace=True)
	print(raw_data.head(30))
	print(raw_data.shape)
	jayson = raw_data.to_json(orient="index")
	#print(raw_data.to_json(orient="index"))
	return jayson
	

	


'''
if __name__=="__main__":
	new_csv = "Alpha20191120-070314 (copy).csv"
	vodoo(new_csv)
	
'''
