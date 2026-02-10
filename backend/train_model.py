"""
Train ML model for expense categorization using TF-IDF + Naive Bayes
"""
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Training dataset - labeled expense descriptions
TRAINING_DATA = [
    # Food
    ("swiggy dinner order", "Food"),
    ("zomato lunch", "Food"),
    ("pizza hut delivery", "Food"),
    ("restaurant bill", "Food"),
    ("cafe coffee", "Food"),
    ("breakfast at hotel", "Food"),
    ("burger king meal", "Food"),
    ("grocery shopping", "Food"),
    ("food delivery", "Food"),
    ("dinner with friends", "Food"),
    ("lunch meeting", "Food"),
    ("snacks purchase", "Food"),
    ("dominos pizza", "Food"),
    ("starbucks coffee", "Food"),
    ("restaurant dinner", "Food"),
    ("food court meal", "Food"),
    ("takeout food", "Food"),
    ("breakfast cereal", "Food"),
    ("vegetables market", "Food"),
    ("fruits shopping", "Food"),
    
    # Gym
    ("gym membership", "Gym"),
    ("fitness center", "Gym"),
    ("yoga classes", "Gym"),
    ("personal trainer", "Gym"),
    ("workout equipment", "Gym"),
    ("sports club", "Gym"),
    ("swimming pool", "Gym"),
    ("exercise class", "Gym"),
    ("gym subscription", "Gym"),
    ("fitness training", "Gym"),
    ("zumba class", "Gym"),
    ("pilates session", "Gym"),
    ("crossfit membership", "Gym"),
    ("sports gear", "Gym"),
    ("running shoes", "Gym"),
    
    # Travel
    ("uber ride", "Travel"),
    ("ola cab", "Travel"),
    ("metro card", "Travel"),
    ("bus ticket", "Travel"),
    ("flight booking", "Travel"),
    ("train ticket", "Travel"),
    ("taxi fare", "Travel"),
    ("petrol fuel", "Travel"),
    ("parking fee", "Travel"),
    ("hotel booking", "Travel"),
    ("car rental", "Travel"),
    ("airport transfer", "Travel"),
    ("toll charges", "Travel"),
    ("gas station", "Travel"),
    ("auto rickshaw", "Travel"),
    ("vacation trip", "Travel"),
    ("travel insurance", "Travel"),
    ("bus pass", "Travel"),
    ("metro recharge", "Travel"),
    ("cab service", "Travel"),
    
    # Shopping
    ("amazon order", "Shopping"),
    ("flipkart purchase", "Shopping"),
    ("clothes shopping", "Shopping"),
    ("shoes purchase", "Shopping"),
    ("mall shopping", "Shopping"),
    ("online shopping", "Shopping"),
    ("electronics store", "Shopping"),
    ("mobile phone", "Shopping"),
    ("laptop purchase", "Shopping"),
    ("clothing store", "Shopping"),
    ("fashion accessories", "Shopping"),
    ("jewelry shopping", "Shopping"),
    ("cosmetics purchase", "Shopping"),
    ("home decor", "Shopping"),
    ("furniture shopping", "Shopping"),
    ("book purchase", "Shopping"),
    ("gift shopping", "Shopping"),
    ("toy store", "Shopping"),
    ("stationery items", "Shopping"),
    ("gadget purchase", "Shopping"),
    
    # Misc
    ("electricity bill", "Misc"),
    ("water bill", "Misc"),
    ("internet bill", "Misc"),
    ("phone bill", "Misc"),
    ("rent payment", "Misc"),
    ("insurance premium", "Misc"),
    ("medical expenses", "Misc"),
    ("doctor consultation", "Misc"),
    ("pharmacy medicine", "Misc"),
    ("hospital bill", "Misc"),
    ("movie tickets", "Misc"),
    ("netflix subscription", "Misc"),
    ("spotify premium", "Misc"),
    ("concert tickets", "Misc"),
    ("game purchase", "Misc"),
    ("entertainment", "Misc"),
    ("haircut salon", "Misc"),
    ("laundry service", "Misc"),
    ("repair service", "Misc"),
    ("miscellaneous", "Misc"),
]

def train_model():
    """Train the ML model and save it."""
    print("🤖 Training ML model for expense categorization...")
    
    # Prepare data
    texts = [text for text, _ in TRAINING_DATA]
    labels = [label for _, label in TRAINING_DATA]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    
    # Create pipeline with TF-IDF + Naive Bayes
    model = Pipeline([
        ('tfidf', TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),  # Use unigrams and bigrams
            max_features=500
        )),
        ('classifier', MultinomialNB(alpha=0.1))
    ])
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model trained successfully!")
    print(f"📊 Accuracy: {accuracy:.2%}")
    print(f"📈 Training samples: {len(X_train)}")
    print(f"🧪 Test samples: {len(X_test)}")
    
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, 'expense_model.pkl')
    print("\n💾 Model saved as 'expense_model.pkl'")
    
    # Test predictions
    print("\n🔮 Sample Predictions:")
    test_cases = [
        "swiggy food order",
        "uber ride to office",
        "gym membership renewal",
        "amazon shopping",
        "electricity bill payment"
    ]
    
    for text in test_cases:
        prediction = model.predict([text])[0]
        print(f"  '{text}' → {prediction}")
    
    return model

if __name__ == "__main__":
    train_model()
