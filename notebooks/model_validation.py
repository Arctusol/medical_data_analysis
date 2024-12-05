import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def plot_learning_curves(model, X, y, cv=5):
    """
    Trace les courbes d'apprentissage pour évaluer le surapprentissage.
    
    Args:
        model: Le modèle à évaluer
        X: Features d'entraînement
        y: Variable cible
        cv: Nombre de folds pour la validation croisée
    """
    train_sizes, train_scores, val_scores = learning_curve(
        model, X, y, cv=cv, n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='r2'
    )
    
    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    val_mean = np.mean(val_scores, axis=1)
    val_std = np.std(val_scores, axis=1)
    
    plt.figure(figsize=(10, 6))
    plt.plot(train_sizes, train_mean, label='Score d\'entraînement')
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1)
    plt.plot(train_sizes, val_mean, label='Score de validation')
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1)
    
    plt.xlabel('Taille de l\'échantillon d\'entraînement')
    plt.ylabel('Score R²')
    plt.title('Courbes d\'apprentissage')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()

def evaluate_cross_validation(model, X, y, cv=5):
    """
    Effectue une validation croisée et affiche les résultats détaillés.
    
    Args:
        model: Le modèle à évaluer
        X: Features d'entraînement
        y: Variable cible
        cv: Nombre de folds pour la validation croisée
    """
    scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
    mae_scores = -cross_val_score(model, X, y, cv=cv, scoring='neg_mean_absolute_error')
    rmse_scores = np.sqrt(-cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error'))
    
    print(f"Résultats de la validation croisée ({cv} folds):")
    print(f"R² moyen: {scores.mean():.3f} (±{scores.std() * 2:.3f})")
    print(f"MAE moyenne: {mae_scores.mean():.3f} (±{mae_scores.std() * 2:.3f})")
    print(f"RMSE moyenne: {rmse_scores.mean():.3f} (±{rmse_scores.std() * 2:.3f})")
    
    return scores, mae_scores, rmse_scores

def plot_prediction_errors(y_true, y_pred):
    """
    Visualise les erreurs de prédiction.
    
    Args:
        y_true: Valeurs réelles
        y_pred: Valeurs prédites
    """
    errors = y_pred - y_true
    
    plt.figure(figsize=(12, 5))
    
    # Distribution des erreurs
    plt.subplot(1, 2, 1)
    plt.hist(errors, bins=30)
    plt.title('Distribution des erreurs de prédiction')
    plt.xlabel('Erreur')
    plt.ylabel('Fréquence')
    
    # Scatter plot des prédictions vs réalité
    plt.subplot(1, 2, 2)
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.title('Prédictions vs Valeurs réelles')
    plt.xlabel('Valeurs réelles')
    plt.ylabel('Prédictions')
    
    plt.tight_layout()
    plt.show()

def calculate_error_statistics(y_true, y_pred):
    """
    Calcule et affiche des statistiques détaillées sur les erreurs.
    
    Args:
        y_true: Valeurs réelles
        y_pred: Valeurs prédites
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    # Calcul du pourcentage d'erreur moyen
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    print("Statistiques détaillées des erreurs:")
    print(f"R² Score: {r2:.3f}")
    print(f"MAE: {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")
    print(f"MAPE: {mape:.2f}%")
    
    return mae, rmse, r2, mape
