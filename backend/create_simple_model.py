"""
Create a simple pre-trained model without requiring scikit-learn installation.
This creates a lightweight pickle file that can be used immediately.
"""
import pickle
import os

# Simple model structure that mimics sklearn pipeline
class SimpleModel:
    def __init__(self):
        # Category keywords for simple matching
        self.categories = {
            "Food": ["swiggy", "zomato", "food", "restaurant", "cafe", "pizza", "burger", "lunch", "dinner", "breakfast", "meal"],
            "Gym": ["gym", "fitness", "workout", "yoga", "sports", "exercise", "trainer", "membership"],
            "Travel": ["uber", "ola", "taxi", "metro", "bus", "petrol", "fuel", "parking", "flight", "train", "hotel"],
            "Shopping": ["amazon", "flipkart", "shopping", "clothes", "shoes", "mall", "store", "purchase"],
            "Misc": []
        }
    
    def predict(self, texts):
        """Predict categories for list of texts."""
        predictions = []
        for text in texts:
            predictions.append(self._predict_single(text))
        return predictions
    
    def _predict_single(self, text):
        """Predict category for single text."""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            if category == "Misc":
                continue
            score = sum(2 if keyword in text_lower else 0 for keyword in keywords)
            if score > 0:
                scores[category] = score
        
        return max(scores, key=scores.get) if scores else "Misc"

def create_model():
    """Create and save the simple model."""
    print("Creating simple categorization model...")
    
    model = SimpleModel()
    
    # Test it
    test_cases = [
        "swiggy food order",
        "uber ride to office",
        "gym membership",
        "amazon shopping",
        "electricity bill"
    ]
    
    print("\nTesting model:")
    for text in test_cases:
        pred = model.predict([text])[0]
        print(f"  '{text}' → {pred}")
    
    # Save model
    with open('expense_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    print("\n✅ Model saved as 'expense_model.pkl'")
    print("📝 This is a simple keyword-based model.")
    print("💡 For better accuracy, install scikit-learn and run train_model.py")

if __name__ == "__main__":
    create_model()
