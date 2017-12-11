import gc
import time
import warnings

import numpy as np
import pandas as pd


def process_train_user_log(train, istest):
    ###############Feature engineering####################
    # 划分近一个月的数据为数据集28天
    if istest == 0:
        train = train[(train['date'] < 20170301) & (train['date'] > 20170131)]
    else:
        train = train[(train['date'] < 20170329) & (train['date'] > 20170228)]

    # 用户一个月的活跃角度
    # 一个月的登陆天数
    train_log_day = train.groupby(['msno']).date.agg({'log_day': 'count'}).reset_index()
    if 'log_day' in train.columns:
        train = pd.merge(train.drop(['log_day'], axis=1), train_log_day, on=['msno'], how='left')
    else:
        train = pd.merge(train, train_log_day, on=['msno'], how='left')

    del train_log_day
    gc.collect()

    # 一个月的听歌汇总
    train_total_25_sum = train.groupby(['msno']).num_25.agg({'total_25_sum_monthly': np.sum}).reset_index()
    train_total_50_sum = train.groupby(['msno']).num_50.agg({'total_50_sum_monthly': np.sum}).reset_index()
    train_total_75_sum = train.groupby(['msno']).num_75.agg({'total_75_sum_monthly': np.sum}).reset_index()
    train_total_985_sum = train.groupby(['msno']).num_985.agg({'total_985_sum_monthly': np.sum}).reset_index()
    train_total_100_sum = train.groupby(['msno']).num_100.agg({'total_100_sum_monthly': np.sum}).reset_index()
    train_total_unq_sum = train.groupby(['msno']).num_unq.agg({'total_unq_sum_monthly': np.sum}).reset_index()
    train_total_secs_sum = train.groupby(['msno']).total_secs.agg({'total_secs_sum_monthly': np.sum}).reset_index()

    if 'total_25_sum_monthly' in train.columns:
        train = pd.merge(train.drop('total_25_sum_monthly', axis=1), train_total_25_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_50_sum_monthly', axis=1), train_total_50_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_75_sum_monthly', axis=1), train_total_75_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_985_sum_monthly', axis=1), train_total_985_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_100_sum_monthly', axis=1), train_total_100_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_unq_sum_monthly', axis=1), train_total_unq_sum, on=['msno'], how='left')
        train = pd.merge(train.drop('total_secs_sum_monthly', axis=1), train_total_secs_sum, on=['msno'], how='left')
    else:
        train = pd.merge(train, train_total_25_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_50_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_75_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_985_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_100_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_unq_sum, on=['msno'], how='left')
        train = pd.merge(train, train_total_secs_sum, on=['msno'], how='left')

    del train_total_25_sum, train_total_50_sum, train_total_75_sum, train_total_985_sum, train_total_100_sum, train_total_unq_sum, train_total_secs_sum
    gc.collect()

    train['total_sum_monthly'] = train['total_25_sum_monthly'] + train['total_50_sum_monthly'] + train[
        'total_75_sum_monthly'] + train[
                                     'total_985_sum_monthly'] + \
                                 train['total_100_sum_monthly']
    # 一个月的听歌习惯
    train['total_25ratio'] = train['total_25_sum_monthly'] / train['total_sum_monthly']
    train['total_100ratio'] = train['total_100_sum_monthly'] / train['total_sum_monthly']
    # 听歌是循环播放还是试听,每首歌播放次数
    train['persong_play'] = train['total_sum_monthly'] / train['total_unq_sum_monthly']
    # 听歌每首歌平均播放时间
    train['persong_time'] = train['total_secs_sum_monthly'] / train['total_sum_monthly']
    # 平均每天听歌数量
    train['daily_play'] = train['total_sum_monthly'] / train['log_day']
    # 平均每天听歌时间
    train['daily_listentime'] = train['total_secs_sum_monthly'] / train['log_day']

    # train数据两个礼拜的变化
    if istest == 0:
        train_one_week = train[(train['date'] < 20170220) & (train['date'] > 20170212)]
        train_two_week = train[(train['date'] < 20170227) & (train['date'] > 20170219)]
    else:
        train_one_week = train[(train['date'] < 20170320) & (train['date'] > 20170312)]
        train_two_week = train[(train['date'] < 20170327) & (train['date'] > 20170319)]

    train_one_week_total_25_sum = train_one_week.groupby(['msno']).num_25.agg({'total_25_sum': np.sum}).reset_index()
    train_one_week_total_50_sum = train_one_week.groupby(['msno']).num_50.agg({'total_50_sum': np.sum}).reset_index()
    train_one_week_total_75_sum = train_one_week.groupby(['msno']).num_75.agg({'total_75_sum': np.sum}).reset_index()
    train_one_week_total_985_sum = train_one_week.groupby(['msno']).num_985.agg({'total_985_sum': np.sum}).reset_index()
    train_one_week_total_100_sum = train_one_week.groupby(['msno']).num_100.agg({'total_100_sum': np.sum}).reset_index()
    train_one_week_total_secs_sum = train_one_week.groupby(['msno']).total_secs.agg(
        {'one_week_secs_sum': np.sum}).reset_index()

    train_one_week = pd.merge(train_one_week, train_one_week_total_25_sum, on=['msno'], how='left')
    train_one_week = pd.merge(train_one_week, train_one_week_total_50_sum, on=['msno'], how='left')
    train_one_week = pd.merge(train_one_week, train_one_week_total_75_sum, on=['msno'], how='left')
    train_one_week = pd.merge(train_one_week, train_one_week_total_985_sum, on=['msno'], how='left')
    train_one_week = pd.merge(train_one_week, train_one_week_total_100_sum, on=['msno'], how='left')
    train_one_week = pd.merge(train_one_week, train_one_week_total_secs_sum, on=['msno'], how='left')
    train_one_week['one_week_sum'] = train_one_week['total_25_sum'] + train_one_week['total_50_sum'] + train_one_week[
        'total_75_sum'] + train_one_week['total_985_sum'] + train_one_week['total_100_sum']
    if 'one_week_secs_sum_y' in train_one_week.columns:
        train_one_week['one_week_secs_sum'] = train_one_week['one_week_secs_sum_y']
        train_one_week = train_one_week.drop('one_week_secs_sum_y', axis=1)

    del train_one_week_total_25_sum, train_one_week_total_50_sum, train_one_week_total_75_sum, train_one_week_total_985_sum, train_one_week_total_100_sum, train_one_week_total_secs_sum
    gc.collect()

    train_two_week_total_25_sum = train_two_week.groupby(['msno']).num_25.agg({'total_25_sum': np.sum}).reset_index()
    train_two_week_total_50_sum = train_two_week.groupby(['msno']).num_50.agg({'total_50_sum': np.sum}).reset_index()
    train_two_week_total_75_sum = train_two_week.groupby(['msno']).num_75.agg({'total_75_sum': np.sum}).reset_index()
    train_two_week_total_985_sum = train_two_week.groupby(['msno']).num_985.agg({'total_985_sum': np.sum}).reset_index()
    train_two_week_total_100_sum = train_two_week.groupby(['msno']).num_100.agg({'total_100_sum': np.sum}).reset_index()
    train_two_week_total_secs_sum = train_two_week.groupby(['msno']).total_secs.agg(
        {'two_week_secs_sum': np.sum}).reset_index()

    train_two_week = pd.merge(train_two_week, train_two_week_total_25_sum, on=['msno'], how='left')
    train_two_week = pd.merge(train_two_week, train_two_week_total_50_sum, on=['msno'], how='left')
    train_two_week = pd.merge(train_two_week, train_two_week_total_75_sum, on=['msno'], how='left')
    train_two_week = pd.merge(train_two_week, train_two_week_total_985_sum, on=['msno'], how='left')
    train_two_week = pd.merge(train_two_week, train_two_week_total_100_sum, on=['msno'], how='left')
    train_two_week = pd.merge(train_two_week, train_two_week_total_secs_sum, on=['msno'], how='left')
    train_two_week['two_week_sum'] = train_two_week['total_25_sum'] + train_two_week['total_50_sum'] + train_two_week[
        'total_75_sum'] + train_two_week['total_985_sum'] + train_two_week['total_100_sum']
    if 'two_week_secs_sum_y' in train_two_week.columns:
        train_two_week['two_week_secs_sum'] = train_two_week['two_week_secs_sum_y']
        train_two_week = train_two_week.drop('two_week_secs_sum_y', axis=1)

    del train_two_week_total_25_sum, train_two_week_total_50_sum, train_two_week_total_75_sum, train_two_week_total_985_sum, train_two_week_total_100_sum, train_two_week_total_secs_sum
    gc.collect()

    if 'one_week_secs_sum' in train.columns:
        train = pd.merge(train.drop(['one_week_secs_sum', 'one_week_sum'], axis=1),
                         train_one_week[['msno', 'one_week_secs_sum', 'one_week_sum']], on=['msno'], how='left')
        train = pd.merge(train.drop(['two_week_secs_sum', 'two_week_sum'], axis=1),
                         train_two_week[['msno', 'two_week_secs_sum', 'two_week_sum']], on=['msno'], how='left')
    else:
        train = pd.merge(train, train_one_week[['msno', 'one_week_secs_sum', 'one_week_sum']], on=['msno'], how='left')
        train = pd.merge(train, train_two_week[['msno', 'two_week_secs_sum', 'two_week_sum']], on=['msno'], how='left')

    # 第四周听歌时间与第三周比较
    train['week_secs_sum_ratio'] = train['two_week_secs_sum'] / train['one_week_secs_sum']
    # 第四周听歌数与第三周比较
    train['week_sum_ratio'] = train['two_week_sum'] / train['one_week_sum']

    # train数据两个半月的变化
    if istest == 0:
        train_one_semimonth = train[(train['date'] < 20170215) & (train['date'] > 20170131)]
        train_two_semimonth = train[(train['date'] < 20170301) & (train['date'] > 20170214)]
    else:
        train_one_semimonth = train[(train['date'] < 20170315) & (train['date'] > 20170228)]
        train_two_semimonth = train[(train['date'] < 20170329) & (train['date'] > 20170314)]

    train_one_semimonth_total_25_sum = train_one_semimonth.groupby(['msno']).num_25.agg(
        {'total_25_sum': np.sum}).reset_index()
    train_one_semimonth_total_50_sum = train_one_semimonth.groupby(['msno']).num_50.agg(
        {'total_50_sum': np.sum}).reset_index()
    train_one_semimonth_total_75_sum = train_one_semimonth.groupby(['msno']).num_75.agg(
        {'total_75_sum': np.sum}).reset_index()
    train_one_semimonth_total_985_sum = train_one_semimonth.groupby(['msno']).num_985.agg(
        {'total_985_sum': np.sum}).reset_index()
    train_one_semimonth_total_100_sum = train_one_semimonth.groupby(['msno']).num_100.agg(
        {'total_100_sum': np.sum}).reset_index()
    train_one_semimonth_total_secs_sum = train_one_semimonth.groupby(['msno']).total_secs.agg(
        {'one_semimonth_secs_sum': np.sum}).reset_index()

    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_25_sum, on=['msno'], how='left')
    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_50_sum, on=['msno'], how='left')
    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_75_sum, on=['msno'], how='left')
    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_985_sum, on=['msno'], how='left')
    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_100_sum, on=['msno'], how='left')
    train_one_semimonth = pd.merge(train_one_semimonth, train_one_semimonth_total_secs_sum, on=['msno'], how='left')
    train_one_semimonth['one_semimonth_sum'] = train_one_semimonth['total_25_sum'] + train_one_semimonth['total_50_sum'] \
                                               + train_one_semimonth['total_75_sum'] + train_one_semimonth[
                                                   'total_985_sum'] + train_one_semimonth['total_100_sum']
    if 'one_semimonth_secs_sum_y' in train_one_semimonth.columns:
        train_one_semimonth['one_semimonth_secs_sum'] = train_one_semimonth['one_semimonth_secs_sum_y']
        train_one_semimonth = train_one_semimonth.drop('one_semimonth_secs_sum_y', axis=1)

    del train_one_semimonth_total_25_sum, train_one_semimonth_total_50_sum, train_one_semimonth_total_75_sum, train_one_semimonth_total_985_sum, train_one_semimonth_total_100_sum, train_one_semimonth_total_secs_sum
    gc.collect()

    train_two_semimonth_total_25_sum = train_two_semimonth.groupby(['msno']).num_25.agg(
        {'total_25_sum': np.sum}).reset_index()
    train_two_semimonth_total_50_sum = train_two_semimonth.groupby(['msno']).num_50.agg(
        {'total_50_sum': np.sum}).reset_index()
    train_two_semimonth_total_75_sum = train_two_semimonth.groupby(['msno']).num_75.agg(
        {'total_75_sum': np.sum}).reset_index()
    train_two_semimonth_total_985_sum = train_two_semimonth.groupby(['msno']).num_985.agg(
        {'total_985_sum': np.sum}).reset_index()
    train_two_semimonth_total_100_sum = train_two_semimonth.groupby(['msno']).num_100.agg(
        {'total_100_sum': np.sum}).reset_index()
    train_two_semimonth_total_secs_sum = train_two_semimonth.groupby(['msno']).total_secs.agg(
        {'two_semimonth_secs_sum': np.sum}).reset_index()
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_25_sum, on=['msno'], how='left')
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_50_sum, on=['msno'], how='left')
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_75_sum, on=['msno'], how='left')
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_985_sum, on=['msno'], how='left')
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_100_sum, on=['msno'], how='left')
    train_two_semimonth = pd.merge(train_two_semimonth, train_two_semimonth_total_secs_sum, on=['msno'], how='left')
    train_two_semimonth['two_semimonth_sum'] = train_two_semimonth['total_25_sum'] + train_two_semimonth['total_50_sum'] \
                                               + train_two_semimonth['total_75_sum'] + train_two_semimonth[
                                                   'total_985_sum'] + train_two_semimonth['total_100_sum']

    if 'two_semimonth_secs_sum_y' in train_two_semimonth.columns:
        train_two_semimonth['two_semimonth_secs_sum'] = train_two_semimonth['two_semimonth_secs_sum_y']
        train_two_semimonth = train_two_semimonth.drop('two_semimonth_secs_sum_y', axis=1)

    train = pd.merge(train, train_one_semimonth[['msno', 'one_semimonth_secs_sum', 'one_semimonth_sum']], on=['msno'],
                     how='left')
    train = pd.merge(train, train_two_semimonth[['msno', 'two_semimonth_secs_sum', 'two_semimonth_sum']], on=['msno'],
                     how='left')

    if 'one_semimonth_secs_sum' in train.columns:
        train = pd.merge(train.drop(['one_semimonth_secs_sum', 'one_semimonth_sum'], axis=1),
                         train_one_semimonth[['msno', 'one_semimonth_secs_sum', 'one_semimonth_sum']],
                         on=['msno'],
                         how='left')
        train = pd.merge(train.drop(['two_semimonth_secs_sum', 'two_semimonth_sum'], axis=1),
                         train_two_semimonth[['msno', 'two_semimonth_secs_sum', 'two_semimonth_sum']],
                         on=['msno'],
                         how='left')
    else:
        train = pd.merge(train, train_one_semimonth[['msno', 'one_semimonth_secs_sum', 'one_semimonth_sum']],
                         on=['msno'],
                         how='left')
        train = pd.merge(train, train_two_semimonth[['msno', 'two_semimonth_secs_sum', 'two_semimonth_sum']],
                         on=['msno'],
                         how='left')

    del train_two_semimonth_total_25_sum, train_two_semimonth_total_50_sum, train_two_semimonth_total_75_sum, train_two_semimonth_total_985_sum, train_two_semimonth_total_100_sum, train_two_semimonth_total_secs_sum
    gc.collect()

    # 第二个半月听歌时间与第一个半月比较
    train['semimonth_secs_sum_ratio'] = train['two_semimonth_secs_sum'] / train['one_semimonth_secs_sum']
    # 第二个半月听歌数与第一个半月比较
    train['semimonth_sum_ratio'] = train['two_semimonth_sum'] / train['one_semimonth_sum']

    return train


# Deal with first part
def ignore_warn(*args, **kwargs):
    pass


warnings.warn = ignore_warn

gc.enable()

size = 4e6  # 1 million
reader = pd.read_csv('../input/user_logs.csv', chunksize=size, nrows=4e7)
start_time = time.time()
for i in range(10):
    user_log_chunk = next(reader)
    if i == 0:
        train_final = process_train_user_log(user_log_chunk, 0)
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    else:
        train_final = train_final.append(process_train_user_log(user_log_chunk, 0))
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    del user_log_chunk

train_final = process_train_user_log(train_final, 0)
train_final.columns = train_final.columns.get_level_values(0)

print(len(train_final))
print(train_final.columns)

# train_final.to_csv("../input/processed_features_train_final_v1.csv", index=False)

del train_final
gc.collect()

reader = pd.read_csv('../input/user_logs.csv', chunksize=size, nrows=4e7)
start_time = time.time()
for i in range(10):
    user_log_chunk = next(reader)
    if i == 0:
        test_final = process_train_user_log(user_log_chunk, 1)
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    else:
        test_final = test_final.append(process_train_user_log(user_log_chunk, 1))
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    del user_log_chunk

test_final = process_train_user_log(test_final, 1)
test_final.columns = test_final.columns.get_level_values(0)

print(len(test_final))
print(test_final.columns)

# test_final.to_csv("../input/processed_features_test_final_v1.csv", index=False)

del test_final
gc.collect()

print('Done')

'''
train_size = len(train_final) / 10  # 1 million
test_size = len(test_final) / 10  # 1 million

train_final.to_csv("../input/processed_features_train_stage_1_v1.csv", index=False)
test_final.to_csv("../input/processed_features_test_stage_1_v1.csv", index=False)


reader = pd.read_csv('../input/processed_features_train_stage_1_v1.csv', chunksize=train_size, nrows=4e7)
start_time = time.time()
for i in range(10):
    user_log_chunk = next(reader)
    if i == 0:
        train_final = process_train_user_log(user_log_chunk, 0)
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    else:
        train_final = train_final.append(process_train_user_log(user_log_chunk, 0))
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    del user_log_chunk
'''

size = 1e6
reader = pd.read_csv('../input/user_logs_v2.csv', chunksize=size)
start_time = time.time()
for i in range(18):
    user_log_chunk = next(reader)
    if i == 0:
        train_final = process_train_user_log(user_log_chunk, 0)
        test_final = process_train_user_log(user_log_chunk, 1)
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    else:
        train_final = train_final.append(process_train_user_log(user_log_chunk, 0))
        test_final = test_final.append(process_train_user_log(user_log_chunk, 1))
        print("Loop ", i, "took %s seconds" % (time.time() - start_time))
    del user_log_chunk

train_final = process_train_user_log(train_final, 0)
test_final = process_train_user_log(test_final, 1)

print(len(train_final))
print(len(test_final))
train_final.columns = train_final.columns.get_level_values(0)
test_final.columns = test_final.columns.get_level_values(0)

train_final.to_csv("../input/processed_features_train_final_v2.csv")
test_final.to_csv("../input/processed_features_test_final_v2.csv")

del train_final
del test_final

train_final_v1 = pd.read_csv('../input/processed_features_train_final_v1.csv')
train_final_v2 = pd.read_csv('../input/processed_features_train_final_v2.csv')

train_final = train_final_v1.append(train_final_v2, ignore_index=True)
del train_final_v1
del train_final_v2

train_final = process_train_user_log(train_final)
train_final.columns = train_final.columns.get_level_values(0)
train_final.to_csv("../input/processed_features_train_final.csv")

del train_final

'''
test_final_v1 = pd.read_csv('../input/processed_features_test_final_v1.csv')
test_final_v2 = pd.read_csv('../input/processed_features_test_final_v2.csv')

test_final = test_final_v1.append(test_final_v2, ignore_index=True)
del test_final_v1
del test_final_v2

test_final = process_test_user_log(test_final)
test_final.columns = test_final.columns.get_level_values(0)
test_final.to_csv("../input/processed_features_test_final.csv")

del test_final
'''
