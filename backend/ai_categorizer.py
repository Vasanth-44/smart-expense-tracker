import re
import os
import pickle

# Try to import joblib, but don't fail if not available
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    print("⚠️  joblib not available, using pickle for model loading")

class AICategorizer:
    """AI-powered expense categorization using ML model with keyword fallback.
    Uses TF-IDF + Naive Bayes for intelligent categorization."""
    
    # Keyword-based fallback
    CATEGORY_KEYWORDS = {
        "Food": ["swiggy", "zomato", "food", "restaurant", "cafe", "pizza", "burger", "lunch", "dinner", "breakfast", "meal", "snack", "coffee", "tea"],
        "Gym": ["gym", "fitness", "workout", "yoga", "sports", "exercise", "trainer", "membership"],
        "Travel": ["uber", "ola", "taxi", "metro", "bus", "petrol", "fuel", "parking", "flight", "train", "hotel", "trip", "vacation"],
        "Shopping": ["amazon", "flipkart", "shopping", "clothes", "shoes", "mall", "store", "purchase", "buy"],
        "Misc": []
    }
    
    # ML model (loaded lazily)
    _model = None
    _model_loaded = False
    
    @classmethod
    def _load_model(cls):
        """Load the ML model if available."""
        if cls._model_loaded:
            return cls._model
        
        model_path = os.path.join(os.path.dirname(__file__), 'expense_model.pkl')
        try:
            if os.path.exists(model_path):
                # Try joblib first, then pickle
                if JOBLIB_AVAILABLE:
                    cls._model = joblib.load(model_path)
                else:
                    with open(model_path, 'rb') as f:
                        cls._model = pickle.load(f)
                print("✅ ML model loaded successfully")
            else:
                print("⚠️  ML model not found, using keyword fallback")
        except Exception as e:
            print(f"⚠️  Error loading ML model: {e}, using keyword fallback")
        
        cls._model_loaded = True
        return cls._model
    
    @classmethod
    def predict_category(cls, note: str) -> str:
        """Predict category using ML model with keyword fallback."""
        if not note:
            return "Misc"
        
        # Try ML model first
        model = cls._load_model()
        if model is not None:
            try:
                prediction = model.predict([note])[0]
                return prediction
            except Exception as e:
                print(f"⚠️  ML prediction failed: {e}, falling back to keywords")
        
        # Fallback to keyword matching
        return cls._predict_with_keywords(note)
    
    @classmethod
    def _predict_with_keywords(cls, note: str) -> str:
        """Fallback keyword-based prediction."""
        note_lower = note.lower()
        
        # Score each category
        scores = {}
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            if category == "Misc":
                continue
            score = sum(1 for keyword in keywords if keyword in note_lower)
            if score > 0:
                scores[category] = score
        
        # Return category with highest score
        if scores:
            return max(scores, key=scores.get)
        
        return "Misc"
    
    @classmethod
    def get_categories(cls):
        """Return list of all available categories."""
        return list(cls.CATEGORY_KEYWORDS.keys())
