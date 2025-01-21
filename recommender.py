from surprise import SVD, Dataset, Reader
from surprise.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


# Collaborative Filtering using Surprise SVD
def collaborative_filtering(user_id, interaction_data, n=5):
    """
    Perform collaborative filtering to recommend products for a given user.

    Parameters:
    - user_id (int): The ID of the user to generate recommendations for.
    - interaction_data (DataFrame): DataFrame containing user-product interactions.
    - n (int): Number of recommendations to return.

    Returns:
    - List of recommended products with predicted scores.
    """
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(interaction_data[['user_id', 'product_id', 'rating']], reader)
    trainset, testset = train_test_split(data, test_size=0.2)

    algo = SVD()
    algo.fit(trainset)

    # Get all unique products
    unique_products = interaction_data['product_id'].unique()
    recommendations = []

    # Predict rating for each product the user hasn't interacted with
    for product_id in unique_products:
        if interaction_data[(interaction_data['user_id'] == user_id) & (interaction_data['product_id'] == product_id)].empty:
            predicted_rating = algo.predict(user_id, product_id).est
            recommendations.append((product_id, predicted_rating))

    # Sort recommendations by predicted rating
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:n]
    return [{"ProductID": prod, "Score": score} for prod, score in recommendations]


# Content-Based Filtering using TF-IDF and Cosine Similarity
def content_based_recommendation(product_id, product_data, n=5):
    """
    Perform content-based recommendation to suggest similar products.

    Parameters:
    - product_id (int): The ID of the product to find similar items for.
    - product_data (DataFrame): DataFrame containing product information (id, description).
    - n (int): Number of similar products to return.

    Returns:
    - List of similar products with similarity scores.
    """
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(product_data['product_description'])

    # Compute cosine similarity matrix
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    # Find the index of the product
    product_index = product_data[product_data['product_id'] == product_id].index[0]

    # Get similarity scores for all products with the given product
    similarity_scores = list(enumerate(cosine_sim[product_index]))

    # Sort by similarity scores
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:n+1]

    recommendations = [{"ProductID": product_data.iloc[i[0]]['product_id'], "Score": i[1]} for i in similarity_scores]
    return recommendations


# Hybrid Recommendation System
def hybrid_recommendation(user_id, product_id, interaction_data, product_data, n=5):
    """
    Combine collaborative filtering and content-based filtering for recommendations.

    Parameters:
    - user_id (int): The ID of the user to generate recommendations for.
    - product_id (int): The ID of the product to find similar items for.
    - interaction_data (DataFrame): DataFrame containing user-product interactions.
    - product_data (DataFrame): DataFrame containing product information (id, description).
    - n (int): Number of recommendations to return.

    Returns:
    - List of recommended products with combined scores.
    """
    # Get collaborative filtering recommendations
    cf_recs = collaborative_filtering(user_id, interaction_data, n=n)

    # Get content-based recommendations
    cb_recs = content_based_recommendation(product_id, product_data, n=n)

    # Combine recommendations by merging scores
    cf_dict = {rec['ProductID']: rec['Score'] for rec in cf_recs}
    cb_dict = {rec['ProductID']: rec['Score'] for rec in cb_recs}

    combined_scores = {}
    for product in set(cf_dict.keys()).union(cb_dict.keys()):
        combined_scores[product] = cf_dict.get(product, 0) + cb_dict.get(product, 0)

    # Sort combined scores
    combined_recommendations = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:n]
    return [{"ProductID": prod, "Score": score} for prod, score in combined_recommendations]

# Example interaction data
interaction_data = pd.DataFrame({
    'user_id': [1, 2, 1, 3, 2],
    'product_id': [101, 101, 102, 103, 102],
    'rating': [5, 4, 3, 4, 5]
})

# Example product data
product_data = pd.DataFrame({
    'product_id': [101, 102, 103, 104],
    'product_description': [
        "This is a great product for outdoor activities.",
        "High-quality product for indoor use.",
        "A reliable product with excellent performance.",
        "Affordable and durable product for everyday use."
    ]
})

# Collaborative Filtering Recommendations
cf_recs = collaborative_filtering(user_id=1, interaction_data=interaction_data)
print("Collaborative Filtering Recommendations:", cf_recs)

# Content-Based Recommendations
cb_recs = content_based_recommendation(product_id=101, product_data=product_data)
print("Content-Based Recommendations:", cb_recs)

# Hybrid Recommendations
hybrid_recs = hybrid_recommendation(user_id=1, product_id=101, interaction_data=interaction_data, product_data=product_data)
print("Hybrid Recommendations:", hybrid_recs)

if __name__ == "__main__":
    print("Collaborative Filtering Recommendations:", collaborative_filtering(1))
    print("Content-Based Recommendations:", content_based(1))
    print("Hybrid Recommendations:", hybrid_recommendation(1, 101))
