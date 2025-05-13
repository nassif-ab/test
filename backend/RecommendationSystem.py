from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

# Import models (assuming they're in a file called models.py)
from models import User, Post, Like, Visit

# Create engine and session
engine = create_engine("sqlite:///blog.db")  # Replace with your actual database URL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RecommendationSystem:
    def __init__(self):
        self.db = SessionLocal()
        # Cache for recommendation results
        self.user_based_recommendations_cache = {}
        self.content_based_recommendations_cache = {}
        # When the cache was last updated
        self.last_cache_update = None

    def close(self):
        """Close the database session"""
        self.db.close()

    def _build_user_item_matrix(self) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Build a user-item interaction matrix based on likes and visits
        Returns:
            - matrix: The user-item matrix where rows are users and columns are posts
            - user_indices: List of user IDs corresponding to matrix rows
            - post_indices: List of post IDs corresponding to matrix columns
        """
        # Get all likes and visits
        likes = self.db.query(Like.user_id, Like.post_id).all()
        visits = self.db.query(Visit.user_id, Visit.post_id).filter(Visit.user_id != None).all()
        
        # Map user and post IDs to matrix indices
        unique_users = set(like[0] for like in likes).union(set(visit[0] for visit in visits if visit[0] is not None))
        unique_posts = set(like[1] for like in likes).union(set(visit[1] for visit in visits))
        
        user_indices = sorted(list(unique_users))
        post_indices = sorted(list(unique_posts))
        
        user_id_to_idx = {user_id: idx for idx, user_id in enumerate(user_indices)}
        post_id_to_idx = {post_id: idx for idx, post_id in enumerate(post_indices)}
        
        # Create interaction matrix
        matrix = np.zeros((len(user_indices), len(post_indices)))
        
        # Weight likes more than visits (like = 1.0, visit = 0.5)
        for user_id, post_id in likes:
            if user_id in user_id_to_idx and post_id in post_id_to_idx:
                matrix[user_id_to_idx[user_id], post_id_to_idx[post_id]] += 1.0
                
        for user_id, post_id in visits:
            if user_id is not None and user_id in user_id_to_idx and post_id in post_id_to_idx:
                matrix[user_id_to_idx[user_id], post_id_to_idx[post_id]] += 0.5
        
        return matrix, user_indices, post_indices

    def get_user_based_recommendations(self, user_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Get content recommendations for a user based on collaborative filtering using SVD
        Args:
            user_id: The user ID to get recommendations for
            n_recommendations: Number of recommendations to return
        Returns:
            List of recommended post dictionaries
        """
        # Check cache first
        if user_id in self.user_based_recommendations_cache:
            return self.user_based_recommendations_cache[user_id][:n_recommendations]
        
        # Build user-item matrix
        matrix, user_indices, post_indices = self._build_user_item_matrix()
        
        if not matrix.any():  # Empty matrix
            return []
        
        # Apply SVD
        n_components = min(min(matrix.shape) - 1, 10)  # Use at most 10 components
        svd = TruncatedSVD(n_components=max(1, n_components))
        svd.fit(matrix)
        
        # Transform the matrix to latent space
        latent_matrix = svd.transform(matrix)
        
        # Find the user index
        try:
            user_idx = user_indices.index(user_id)
        except ValueError:
            # User not found in matrix
            return self.get_popular_posts(n_recommendations)
        
        # Calculate similarities between users
        user_similarities = cosine_similarity([latent_matrix[user_idx]], latent_matrix)[0]
        
        # Get posts that user has not interacted with
        user_interactions = matrix[user_idx]
        non_interacted_posts = [post_indices[i] for i, val in enumerate(user_interactions) if val == 0]
        
        # Calculate recommendation scores
        post_scores = {}
        for post_idx, post_id in enumerate(post_indices):
            if post_id in non_interacted_posts:
                score = 0
                for other_user_idx, sim in enumerate(user_similarities):
                    if other_user_idx != user_idx:
                        score += sim * matrix[other_user_idx, post_idx]
                if score > 0:
                    post_scores[post_id] = score
        
        # Get top N recommendations
        recommended_post_ids = sorted(post_scores.items(), key=lambda x: x[1], reverse=True)[:n_recommendations]
        recommended_post_ids = [post_id for post_id, score in recommended_post_ids]
        
        # Get post details
        recommendations = []
        for post_id in recommended_post_ids:
            post = self.db.query(Post).filter(Post.id == post_id).first()
            if post:
                recommendations.append({
                    "id": post.id,
                    "title": post.title,
                    "category": post.categorie,
                    "score": post_scores[post_id]
                })
        
        # Cache results
        self.user_based_recommendations_cache[user_id] = recommendations
        
        return recommendations

    def get_content_based_recommendations(self, post_id: int, n_recommendations: int = 5) -> List[Dict]:
        """
        Get similar posts to a given post using content-based approach
        Args:
            post_id: The post ID to find similar posts for
            n_recommendations: Number of recommendations to return
        Returns:
            List of recommended post dictionaries
        """
        # Check cache first
        if post_id in self.content_based_recommendations_cache:
            return self.content_based_recommendations_cache[post_id][:n_recommendations]
        
        # Get all posts with categories
        posts = self.db.query(Post).filter(Post.categorie != None).all()
        
        # Create post features based on category and user interactions
        post_features = {}
        categories = set()
        
        # Get unique categories
        for post in posts:
            if post.categorie:
                categories.add(post.categorie)
        
        # Create one-hot encoding for categories
        categories = sorted(list(categories))
        category_to_idx = {cat: idx for idx, cat in enumerate(categories)}
        
        # Create feature vectors for posts
        for post in posts:
            # Start with category one-hot encoding
            feature_vector = np.zeros(len(categories))
            if post.categorie and post.categorie in category_to_idx:
                feature_vector[category_to_idx[post.categorie]] = 1.0
            post_features[post.id] = feature_vector
        
        # Apply SVD on post features
        post_ids = list(post_features.keys())
        feature_matrix = np.array([post_features[pid] for pid in post_ids])
        
        if feature_matrix.shape[0] <= 1 or feature_matrix.shape[1] == 0:
            return []
        
        # Apply SVD if we have enough data
        n_components = min(feature_matrix.shape[1], 5)
        if n_components > 0:
            svd = TruncatedSVD(n_components=n_components)
            latent_matrix = svd.fit_transform(feature_matrix)
        else:
            latent_matrix = feature_matrix
        
        # Find the post index
        try:
            post_idx = post_ids.index(post_id)
        except ValueError:
            # Post not found
            return []
        
        # Calculate similarities between posts
        post_similarities = cosine_similarity([latent_matrix[post_idx]], latent_matrix)[0]
        
        # Get similar posts
        similar_posts = [(post_ids[i], sim) for i, sim in enumerate(post_similarities) if post_ids[i] != post_id]
        similar_posts.sort(key=lambda x: x[1], reverse=True)
        similar_post_ids = [pid for pid, _ in similar_posts[:n_recommendations]]
        
        # Get post details
        recommendations = []
        for idx, sp_id in enumerate(similar_post_ids):
            post = self.db.query(Post).filter(Post.id == sp_id).first()
            if post:
                recommendations.append({
                    "id": post.id,
                    "title": post.title,
                    "category": post.categorie,
                    "similarity_score": similar_posts[idx][1]
                })
        
        # Cache results
        self.content_based_recommendations_cache[post_id] = recommendations
        
        return recommendations
    
    def get_popular_posts(self, n_recommendations: int = 5) -> List[Dict]:
        """
        Get popular posts based on likes and visits
        Args:
            n_recommendations: Number of recommendations to return
        Returns:
            List of post dictionaries
        """
        # Calculate post popularity scores based on likes and visits
        likes_count = self.db.query(Like.post_id, func.count(Like.id).label('likes'))\
            .group_by(Like.post_id).subquery()
        
        visits_count = self.db.query(Visit.post_id, func.count(Visit.id).label('visits'))\
            .group_by(Visit.post_id).subquery()
        
        popular_posts = self.db.query(
            Post,
            func.coalesce(likes_count.c.likes, 0).label('likes_count'),
            func.coalesce(visits_count.c.visits, 0).label('visits_count')
        ).outerjoin(
            likes_count, Post.id == likes_count.c.post_id
        ).outerjoin(
            visits_count, Post.id == visits_count.c.post_id
        ).order_by(
            # Weight likes more than visits
            (func.coalesce(likes_count.c.likes, 0) * 2 + func.coalesce(visits_count.c.visits, 0)).desc()
        ).limit(n_recommendations).all()
        
        return [
            {
                "id": post.id,
                "title": post.title,
                "category": post.categorie,
                "likes": likes_count,
                "visits": visits_count,
                "popularity_score": likes_count * 2 + visits_count
            }
            for post, likes_count, visits_count in popular_posts
        ]
    
    def get_recommendations_for_anonymous_visitor(self, ip_address: str, n_recommendations: int = 5) -> List[Dict]:
        """
        Get recommendations for anonymous visitors based on their IP address and visit history
        Args:
            ip_address: Visitor's IP address
            n_recommendations: Number of recommendations to return
        Returns:
            List of post dictionaries
        """
        # Get posts visited by this IP
        visits = self.db.query(Visit.post_id).filter(Visit.ip_address == ip_address).all()
        visited_post_ids = [v[0] for v in visits]
        
        if not visited_post_ids:
            # No visit history, return popular posts
            return self.get_popular_posts(n_recommendations)
        
        # Get categories of visited posts
        visited_posts = self.db.query(Post).filter(Post.id.in_(visited_post_ids)).all()
        visited_categories = [p.categorie for p in visited_posts if p.categorie]
        
        # Count category occurrences to determine interests
        category_counts = defaultdict(int)
        for cat in visited_categories:
            category_counts[cat] += 1
        
        # Get most visited categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        top_categories = [cat for cat, _ in top_categories]
        
        # Get posts from these categories that haven't been visited
        recommendations = []
        for category in top_categories:
            if len(recommendations) >= n_recommendations:
                break
                
            # Get posts from this category that haven't been visited
            category_posts = self.db.query(Post).filter(
                Post.categorie == category,
                ~Post.id.in_(visited_post_ids)
            ).order_by(Post.created_at.desc()).limit(n_recommendations - len(recommendations)).all()
            
            for post in category_posts:
                recommendations.append({
                    "id": post.id,
                    "title": post.title,
                    "category": post.categorie,
                    "recommendation_reason": f"Because you viewed other posts in {category}"
                })
        
        # If we still need more recommendations, add popular posts
        if len(recommendations) < n_recommendations:
            additional_posts = self.get_popular_posts(n_recommendations - len(recommendations))
            # Filter out any posts that are already in the recommendations
            recommended_ids = {rec["id"] for rec in recommendations}
            additional_posts = [p for p in additional_posts if p["id"] not in recommended_ids]
            recommendations.extend(additional_posts)
        
        return recommendations[:n_recommendations]


# Example usage
def get_recommendations_for_user(user_id: int, n_recommendations: int = 5):
    """Get personalized recommendations for a user"""
    recommender = RecommendationSystem()
    try:
        return recommender.get_user_based_recommendations(user_id, n_recommendations)
    finally:
        recommender.close()

def get_similar_posts(post_id: int, n_recommendations: int = 5):
    """Get similar posts to the given post"""
    recommender = RecommendationSystem()
    try:
        return recommender.get_content_based_recommendations(post_id, n_recommendations)
    finally:
        recommender.close()

def get_recommendations_for_visitor(ip_address: str, n_recommendations: int = 5):
    """Get recommendations for anonymous visitors"""
    recommender = RecommendationSystem()
    try:
        return recommender.get_recommendations_for_anonymous_visitor(ip_address, n_recommendations)
    finally:
        recommender.close()