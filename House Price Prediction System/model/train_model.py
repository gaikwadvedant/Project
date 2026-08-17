import os
import sys
import pickle
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score
# Add root folder to sys.path to import transit_engine correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.transit_engine import calculate_transit_score

def train():
    data_path = 'data/indian_houses_transit.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError("Run 'python data/generate_dataset.py' first.")

    df = pd.read_csv(data_path)

    # Feature Engineering: Generate Transit Score
    df['Transit_Score'] = df.apply(
        lambda row: calculate_transit_score(
            row['Distance_Metro_KM'], 
            row['Distance_Railway_KM'], 
            row['Distance_Highway_KM']
        ), axis=1
    )

    categorical_cols = ['City', 'Property_Type', 'Furnishing', 'Possession_Status']
    numerical_cols = ['BHK', 'Size_SqFt', 'Distance_Metro_KM', 'Distance_Railway_KM', 'Distance_Highway_KM', 'Transit_Score']

    X = df[categorical_cols + numerical_cols]
    y = df['Price_Lakhs']

    # Preprocessor to encode string columns automatically
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ]
    )

    # Scikit-learn Pipeline incorporating XGBoost Regressor
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', XGBRegressor(
            n_estimators=200, 
            learning_rate=0.08, 
            max_depth=6, 
            random_state=42
        ))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training XGBoost Pipeline...")
    model_pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = model_pipeline.predict(X_test)
    print(f"Model Performance:")
    print(f"  R2 Score: {r2_score(y_test, y_pred):.4f}")
    print(f"  MAE: ₹{mean_absolute_error(y_test, y_pred):.2f} Lakhs")

    # Save artifact
    os.makedirs('model', exist_ok=True)
    with open('model/house_price_model.pkl', 'wb') as f:
        pickle.dump(model_pipeline, f)
        
    print("Trained model saved to 'model/house_price_model.pkl'")

if __name__ == '__main__':
    train()