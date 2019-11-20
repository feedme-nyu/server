import fasttext

# Skipgram model :
skipgram = fasttext.train_unsupervised('chinese.txt', model='skipgram')

skipgram.save_model("skipgram_chinese_food.bin")

# or, cbow model :
cbow = fasttext.train_unsupervised('chinese.txt', model='cbow')

cbow.save_model("cbow_chinese_food.bin")