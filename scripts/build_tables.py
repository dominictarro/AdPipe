"""
Script for generating user data for the Kaggle dataset arashnic/ctrtest.
"""
from datetime import datetime, timedelta
import logging
import os
import random
import sys

import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

DATA_PATH = os.path.abspath("data")
generator_input_path = os.path.join(DATA_PATH, 'generator_input')
kaggle_raw_path = os.path.join(DATA_PATH, "kaggle_raw")
table_path = os.path.join(DATA_PATH, "tables")

if __name__ == '__main__':

    if not os.path.isdir(table_path):
        os.mkdir(table_path)

    # load kaggle data
    logging.info("Reading Kaggle impression data")
    test_df = pd.read_csv(os.path.join(kaggle_raw_path, "test_ctr/test.csv"))
    train_df = pd.read_csv(os.path.join(kaggle_raw_path, "train_adc/train.csv"))

    logging.info("Reading Kaggle item data")
    item_df = pd.read_csv(os.path.join(kaggle_raw_path, "train_adc", "item_data.csv"))
    # drop null item
    item_df = item_df.drop(index=item_df[item_df['item_id'].isna()].index)

    logging.info("Reading Kaggle view log data")
    views_df = pd.read_csv(os.path.join(kaggle_raw_path, "train_adc", "view_log.csv"))

    logging.info("Reading country data")
    country_df = pd.read_csv(os.path.join(generator_input_path, 'country-codes.csv'))


    logging.info("Merging impressions")
    # join train/test impression data
    impression_df = pd.concat((train_df, test_df))
    # drop null impression
    impression_df = impression_df.drop(index=impression_df[impression_df['impression_id'].isna()].index)

    ###################################################################################################
    # USER TABLE
    # 
    # - Country
    # - Date user registers
    # - User birth date
    ###################################################################################################
    logging.info("Generating user data")
    # create user table
    user_df = pd.DataFrame({'user_id': impression_df['user_id'].unique()})

    # drop null user
    user_df = user_df.drop(index=user_df[user_df['user_id'].isna()].index)

    # generate user country
    user_df['country'] = random.choices(country_df['ISO3166-1-Alpha-2'].to_list(), k=len(user_df))

    # generate user registration timestamp
    def generate_registration_timestamp(server_time):
        days_between_registration_first_use = random.uniform(0, 365)
        ts: datetime = server_time - timedelta(days=days_between_registration_first_use)
        return datetime(ts.year, ts.month, ts.day, ts.hour, ts.minute, int(ts.second))

    user_log_pivot = views_df.groupby('user_id', as_index=False).min()
    user_log_pivot['server_time'] = user_log_pivot['server_time'].apply(lambda ts: datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
    # interpolate missing log ts
    # user_log_pivot['server_time'] = user_log_pivot['server_time'].interpolate(method='linear')
    # generate registration ts
    user_log_pivot['created_at'] = user_log_pivot['server_time'].apply(generate_registration_timestamp)

    user_df = user_df.merge(user_log_pivot, how='left', left_on='user_id', right_on='user_id')[['user_id', 'country', 'created_at']]
    # free memory
    del user_log_pivot

    # generate birth date
    MAX_AGE = 45
    def generate_birth_date(created_at: datetime):
        _13_years_before_registration = created_at - timedelta(days=13*365)
        age_span = (MAX_AGE - 13) * 365
        return (_13_years_before_registration - timedelta(days=random.randint(0, age_span))).date()

    user_df['date_of_birth'] = user_df['created_at'].apply(generate_birth_date)

    logging.info("Writing users")
    user_df = user_df.drop_duplicates('user_id')
    user_df = user_df.rename(columns={'user_id': 'id'})
    user_df.to_csv(os.path.join(table_path, 'user_accounts.csv'), index=False)

    logging.info("Writing items")
    item_df = item_df.drop_duplicates('item_id')
    item_df = item_df.rename(columns={
        'item_id': 'id',
        'item_price': 'price'
    })
    item_df.to_csv(os.path.join(table_path, 'items.csv'), index=False)

    logging.info("Writing impressions")
    impression_df = impression_df.drop_duplicates('impression_id')
    impression_df = impression_df.rename(columns={
        'impression_id': 'id',
        'impression_time': 'shown_at'
    })
    impression_df.to_csv(os.path.join(table_path, 'impressions.csv'), index=False)

    logging.info("Writing views")
    views_df.insert(loc=0, column='id', value=range(1, len(views_df)+1))
    views_df.to_csv(os.path.join(table_path, 'view_logs.csv'), index=False)
    logging.info(table_path)
