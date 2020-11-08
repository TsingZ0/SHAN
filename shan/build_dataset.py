import random
import pickle
import numpy as np
import copy

max_length = 90
random.seed(1234)

with open('../Data/Electronics.pkl', 'rb') as f:
    reviews_df, meta_df = pickle.load(f)
    item_cate_list = pickle.load(f)
    user_count, item_count, cate_count, example_count = pickle.load(f)
    

train_set = []
test_set = []
for reviewerID, hist in reviews_df.groupby('reviewerID'):
    pos_list = hist['asin'].tolist()
    tim_list = hist['unixReviewTime'].tolist()
    def gen_neg():
        neg = pos_list[0]
        while neg in pos_list:
            neg = random.randint(0, item_count-1)
        return neg
    neg_list = [gen_neg() for i in range(len(pos_list))]

    length = len(pos_list)
    valid_length = min(length, max_length)
    i = 0
    tim_list_session = list(set(tim_list))
    tim_list_session.sort()
    pre_session = []
    for t in tim_list_session:
        count = tim_list.count(t)
        new_session = pos_list[i:i+count]

        if t == tim_list_session[0]:
            pre_session.extend(new_session)
        else:
            if i+count < valid_length-1:
                pre_session_copy = copy.deepcopy(pre_session)
                pos_neg = (pos_list[i+count], neg_list[i+count])
                train_set.append((reviewerID, pre_session_copy, new_session, pos_neg))
                pre_session.extend(new_session)
            else:
                pos_item = pos_list[i]
                if count > 1:
                    pos_item = random.choice(new_session)
                    new_session.remove(pos_item)
                neg_index = pos_list.index(pos_item)
                pos_neg = (pos_item, neg_list[neg_index])
                test_set.append((reviewerID, pre_session, new_session, pos_neg))
                break
        i += count

random.shuffle(train_set)
random.shuffle(test_set)

assert len(test_set) == user_count

with open('dataset.pkl', 'wb') as f:
    pickle.dump(train_set, f, pickle.HIGHEST_PROTOCOL)
    pickle.dump(test_set, f, pickle.HIGHEST_PROTOCOL)
    pickle.dump((user_count, item_count), f, pickle.HIGHEST_PROTOCOL)
