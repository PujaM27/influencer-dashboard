import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

# Influencer categories, platforms, genders
categories = ['fitness', 'lifestyle', 'wellness', 'food', 'fashion', 'tech']
platforms = ['Instagram', 'YouTube', 'Twitter']
genders = ['female', 'male', 'other']

# 1. influencers.csv
def generate_influencers(n=15):
    influencers = []
    for i in range(1, n+1):
        influencer = {
            'ID': f'inf_{i:03d}',
            'name': fake.name(),
            'category': random.choice(categories),
            'gender': random.choice(genders),
            'follower_count': random.randint(10000, 500000),
            'platform': random.choice(platforms)
        }
        influencers.append(influencer)
    return pd.DataFrame(influencers)

# 2. posts.csv
def generate_posts(influencers, min_posts=3, max_posts=5):
    posts = []
    for _, row in influencers.iterrows():
        n_posts = random.randint(min_posts, max_posts)
        for _ in range(n_posts):
            reach = random.randint(int(row['follower_count']*0.5), row['follower_count'])
            likes = int(reach * random.uniform(0.05, 0.15))
            comments = int(likes * random.uniform(0.05, 0.2))
            post = {
                'influencer_id': row['ID'],
                'platform': row['platform'],
                'date': (datetime(2024,6,1) + timedelta(days=random.randint(0,29))).strftime('%Y-%m-%d'),
                'URL': fake.url(),
                'caption': fake.sentence(nb_words=8),
                'reach': reach,
                'likes': likes,
                'comments': comments
            }
            posts.append(post)
    return pd.DataFrame(posts)

# 3. tracking_data.csv
def generate_tracking_data(influencers, products, min_users=10, max_users=20):
    tracking = []
    for _, row in influencers.iterrows():
        n_users = random.randint(min_users, max_users)
        for u in range(n_users):
            user_id = f'u_{row["ID"]}_{u+1:03d}'
            n_purchases = random.randint(1, 3)
            for _ in range(n_purchases):
                product = random.choice(products)
                orders = random.randint(1, 2)
                revenue = orders * random.choice([799, 999, 1299, 1499, 1999])
                tracking.append({
                    'source': row['platform'],
                    'campaign': random.choice(['MB-Summer23', 'MB-Winter23', 'MB-Spring24']),
                    'influencer_id': row['ID'],
                    'user_id': user_id,
                    'product': product,
                    'date': (datetime(2024,6,1) + timedelta(days=random.randint(0,29))).strftime('%Y-%m-%d'),
                    'orders': orders,
                    'revenue': revenue
                })
    return pd.DataFrame(tracking)

# 4. payouts.csv
def generate_payouts(influencers, posts):
    payouts = []
    for _, row in influencers.iterrows():
        payout_type = random.choice(['post', 'order'])
        if payout_type == 'post':
            n_posts = posts[posts['influencer_id'] == row['ID']].shape[0]
            rate = random.choice([3000, 4000, 5000, 6000])
            total_payout = n_posts * rate
            payouts.append({
                'influencer_id': row['ID'],
                'basis': 'post',
                'rate': rate,
                'orders': 0,
                'total_payout': total_payout
            })
        else:
            n_orders = random.randint(10, 40)
            rate = random.choice([100, 150, 200, 250])
            total_payout = n_orders * rate
            payouts.append({
                'influencer_id': row['ID'],
                'basis': 'order',
                'rate': rate,
                'orders': n_orders,
                'total_payout': total_payout
            })
    return pd.DataFrame(payouts)

if __name__ == '__main__':
    # Products for tracking data
    products = ['MB-WheyProtein', 'MB-Gainer', 'MB-VitaminC', 'MB-Preworkout', 'MB-BCAA']

    influencers = generate_influencers(15)
    posts = generate_posts(influencers)
    tracking = generate_tracking_data(influencers, products)
    payouts = generate_payouts(influencers, posts)

    influencers.to_csv('influencers.csv', index=False)
    posts.to_csv('posts.csv', index=False)
    tracking.to_csv('tracking_data.csv', index=False)
    payouts.to_csv('payouts.csv', index=False)

    print('Mock data CSVs generated: influencers.csv, posts.csv, tracking_data.csv, payouts.csv') 