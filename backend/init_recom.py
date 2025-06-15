import os
import json
import math
from pymongo import MongoClient
import faiss
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
from sklearn.preprocessing import MultiLabelBinarizer
from time import time
from math import log, e
from datetime import datetime

class VectorDBBookRecommender:
    def __init__(self,
                 mongo_uri='mongodb://localhost:27017',
                 db_name='book',
                 books_col='books',
                 authors_col='authors',
                 users_col='users',
                 feature_col='book_features',
                 embed_model_dir='../all-MiniLM-L6-v2',
                 batch_size=64,
                 initialize=True):
        # Mongo setup
        self.client = MongoClient(mongo_uri)

        self.db = self.client[db_name]
        self.books_col = self.db[books_col]
        self.authors_col = self.db[authors_col]
        self.users = users_col
        self.users_col = self.db[users_col]
        self.feature_col = self.db[feature_col]
        
        self.initialize = initialize

        # Load data from Mongo
        self.books = list(self.books_col.find({}))
        self.authors = list(self.authors_col.find({}))

        # Encoder init
        self.tokenizer = AutoTokenizer.from_pretrained(embed_model_dir)
        self.model = AutoModel.from_pretrained(embed_model_dir)
        self.batch_size = batch_size
        
        if self.initialize:

            # Tag/profession encoders
            self._prepare_tag_encoder()
            # Build author embeddings once
            self._build_author_embeddings()
        # Build or load index
        self._build_index()

    def _prepare_tag_encoder(self):
        tag_lists = [b.get('tag','').split(',') for b in self.books]
        self.tag_encoder = MultiLabelBinarizer()
        self.tag_features = self.tag_encoder.fit_transform(tag_lists).astype('float32')

        prof_lists = [a.get('profession',[]) for a in self.authors]
        self.prof_encoder = MultiLabelBinarizer()
        self.prof_features = self.prof_encoder.fit_transform(prof_lists).astype('float32')

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        mask = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)

    def encode_sentences_batch(self, texts):
        encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_out = self.model(**encoded)
        embeddings = self.mean_pooling(model_out, encoded['attention_mask'])
        embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings.cpu().numpy()

    def _build_author_embeddings(self):
        author_texts = []
        for a in self.authors:
            titles = [item['subject']['title'] for item in json.loads(a.get('recent_works',{})).get('data',{}).get('items',[])]
            text = f"{a.get('name','')} {a.get('intro','')} {' '.join(titles)}"
            author_texts.append(text)
        total = len(author_texts)
        auth_embs = []
        for i in range(0, total, self.batch_size):
            batch = author_texts[i:i+self.batch_size]
            auth_embs.append(self.encode_sentences_batch(batch))
        auth_embs = np.vstack(auth_embs).astype('float32')
        faiss.normalize_L2(auth_embs)

        prof_embs = self.prof_features * 0.1
        self.author_embeddings = np.hstack([auth_embs, prof_embs])
        self.author_id_map = {a['author_douban_id']: idx for idx,a in enumerate(self.authors)}

    def get_author_embedding(self, author_id):
        idx = self.author_id_map.get(author_id)
        return self.author_embeddings[idx] if idx is not None else np.zeros(self.author_embeddings.shape[1], dtype='float32')

    def _build_index(self):
        # Check existing feature docs
        count_books = len(self.books)
        count_feats = self.feature_col.count_documents({})
        # Prepare text data
        texts = [f"{b.get('title','')} {b.get('related_intro','')}" for b in self.books]
        # Compute text embeddings if needed
        text_embs = np.zeros((count_books, self.model.config.hidden_size), dtype='float32')
        
        print(count_feats, count_books)
        
        if self.initialize:
            for i in range(0, count_books, self.batch_size):
                embs = self.encode_sentences_batch(texts[i:i+self.batch_size])
                text_embs[i:i+embs.shape[0]] = embs
            faiss.normalize_L2(text_embs)
            # Build other parts
            tag_embs = (self.tag_features * 0.2).astype('float32')
            auth_list = []
            for b in self.books:
                vecs = [self.get_author_embedding(a.get('douban_id')) for a in b.get('authors',[])]
                auth_list.append(np.mean(vecs, axis=0) if vecs else np.zeros(self.author_embeddings.shape[1], dtype='float32'))
            auth_embs = np.vstack(auth_list)
            faiss.normalize_L2(auth_embs)
            auth_embs *= 0.3
            # Combine and store features
            for idx,(b, te, ta, ae) in enumerate(zip(self.books, text_embs, tag_embs, auth_embs)):
                feat = np.hstack([te, ta, ae]).astype('float32')
                self.feature_col.update_one(
                    {'douban_id': b['douban_id']},
                    {'$set': {'feature_vector': feat.tolist()}},
                    upsert=True
                )
        # Load features from DB
        features = []
        for b in self.books:
            doc = self.feature_col.find_one({'douban_id': b['douban_id']})
            features.append(np.array(doc['feature_vector'], dtype='float32'))
        features = np.vstack(features)
        # Build FAISS index
        dim = features.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(features)
        self.index.add(features)

    def recommend(self, user_book_ids, weight, top_k=5):
        """
        user_book_ids: list of douban_id strings
        returns: list of dicts with keys 'douban_id' and 'title'
        """
        # Map douban_ids to indices, ignore missing

        history_vecs = []
        weight_list = []
        
        for idx, bid in enumerate(user_book_ids):
            book_feature = self.feature_col.find_one({'douban_id': bid})
            if book_feature:
                history_vecs.append(np.array(book_feature['feature_vector'], dtype='float32'))
                weight_list.append(weight[idx])
        
        weight_list = np.array(weight_list, dtype='float32')
        history_vecs = np.array(history_vecs, dtype='float32')
        
        weight_list = weight_list / sum(weight_list)
        history_vecs = history_vecs * weight_list.reshape(-1,1)

        # Build user profile
        profile = sum(history_vecs)
        faiss.normalize_L2(profile.reshape(1,-1))
        # Search
        _, result = self.index.search(profile.reshape(1,-1), top_k + len(history_vecs))
        recs = []
        for idx in result[0]:
            b = self.books[idx]
            book_douban_id = b['douban_id']
            if book_douban_id not in user_book_ids:
                # recs.append({'douban_id': b['douban_id'], 'title': b['title']})
                recs.append(b['douban_id'])
            if len(recs) >= top_k:
                break
        return recs
    
    def recommend_by_user(self, user_id, top_k=5):
        self.users_col = self.db[self.users]
        
        if user_id is None:
            import random
            all_books = [b['douban_id'] for b in self.books if 'douban_id' in b]
            if len(all_books) <= top_k:
                return all_books
            return random.sample(all_books, top_k)
        
        user = self.users_col.find_one({'user_id': user_id})
        user_history_list = user.get('history_list', [])
        user_star_list = user.get('star_list', [])
        
        user_history_ids = {}
        for idx, it in enumerate(user_history_list):
            # it[1] 是 "2025-05-22 15:02:44.357" 这样的字符串，需要转为时间戳
            # dt = datetime.strptime(it[1], "%Y-%m-%d %H:%M:%S.%f")
            # timestamp = dt.timestamp()
            # user_history_ids[it] = 0.95 ** ((time() - timestamp) / 86400) * log(it[0] + e-1) ** 2
            user_history_ids[it] = log(int(it[0]) + e-1) ** 2
        
        for it in user_star_list:
            if it not in user_history_ids:
                user_history_ids[it] = 5
            else:
                user_history_ids[it] += 5

        recs = self.recommend(list(user_history_ids.keys()), list(user_history_ids.values()), top_k)
        return recs


if __name__ == "__main__":
    # Usage:
    recommender = VectorDBBookRecommender(initialize=False)
    recs = recommender.recommend(["26685240","26787940","36998357"], [1, 1, 1], top_k=5)
    print(recs)
    recs = recommender.recommend(["27593462","26776239","26916149"], [1, 1, 1], top_k=5)
    print(recs)
    recs = recommender.recommend(["27593462","26776239","26916149", "26685240","26787940","36998357"], [1, 1, 1, 1, 1, 1], top_k=5)
    print(recs)
    recs = recommender.recommend(["27593462","26776239","26916149", "26685240","26787940","36998357"], [1, 0, 0, 0, 0, 0], top_k=5)
    print(recs)
    recs = recommender.recommend_by_user(None, top_k=5)
    print(recs)

    # 应该调用recommend_by_user(user_id, top_k)，返回一个list，里面是豆瓣id
