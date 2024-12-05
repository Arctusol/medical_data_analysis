import mlflow
from mlflow.tracking import MlflowClient
import pandas as pd
import numpy as np
from typing import Dict, List
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

class HospitalRecommender:
    """
    Système de recommandation d'hôpitaux qui combine les prédictions
    de plusieurs modèles pour fournir des recommandations personnalisées.
    """
    
    def __init__(self):
        self.service_classifier = None
        self.duration_predictor = None
        self.mlflow_client = MlflowClient()
        self.hospital_data = None
        self.geolocator = Nominatim(user_agent="hospital_recommender")
        
    def load_models(self, service_run_id: str, duration_run_id: str):
        """
        Charge les modèles entraînés depuis MLflow
        
        Args:
            service_run_id: ID MLflow du modèle de classification de service
            duration_run_id: ID MLflow du modèle de prédiction de durée
        """
        self.service_classifier = mlflow.pycaret.load_model(
            f"runs:/{service_run_id}/service_classifier"
        )
        self.duration_predictor = mlflow.pycaret.load_model(
            f"runs:/{duration_run_id}/duration_predictor"
        )
    
    def load_hospital_data(self, data: pd.DataFrame):
        """
        Charge les données des hôpitaux
        
        Args:
            data: DataFrame contenant les informations des hôpitaux
        """
        self.hospital_data = data
    
    def predict(self, patient_data: Dict) -> List[Dict]:
        """
        Génère des recommandations d'hôpitaux pour un patient
        
        Args:
            patient_data: Dictionnaire contenant les informations du patient
                (âge, sexe, pathologie, localisation, etc.)
                
        Returns:
            Liste de dictionnaires contenant les recommandations d'hôpitaux,
            triées par pertinence
        """
        if self.hospital_data is None:
            raise ValueError("Les données des hôpitaux n'ont pas été chargées")
            
        # Convertir les données patient en DataFrame
        patient_df = pd.DataFrame([patient_data])
        
        # 1. Prédire le service nécessaire
        service = self.service_classifier.predict(patient_df)[0]
        
        # 2. Prédire la durée estimée du séjour
        estimated_duration = self.duration_predictor.predict(patient_df)[0]
        
        # 3. Calculer les scores pour chaque hôpital
        recommendations = self._get_hospital_recommendations(
            service,
            estimated_duration,
            patient_data
        )
        
        return recommendations
    
    def _calculate_distance_score(self, hospital_location: str, patient_location: str) -> float:
        """
        Calcule un score basé sur la distance entre l'hôpital et le patient
        """
        try:
            patient_loc = self.geolocator.geocode(patient_location)
            hospital_loc = self.geolocator.geocode(hospital_location)
            
            if patient_loc and hospital_loc:
                distance = geodesic(
                    (patient_loc.latitude, patient_loc.longitude),
                    (hospital_loc.latitude, hospital_loc.longitude)
                ).kilometers
                
                # Convertir la distance en score (0-1, plus proche = meilleur score)
                return 1 / (1 + distance/100)
        except:
            return 0
        return 0
    
    def _calculate_capacity_score(self, hospital_data: pd.Series, estimated_duration: float) -> float:
        """
        Calcule un score basé sur la capacité d'accueil de l'hôpital
        """
        # Utiliser le nombre de lits disponibles et le taux d'occupation
        lit_hospi = hospital_data.get('lit_hospi_complete', 0)
        occupation = hospital_data.get('hospi_total_24h', 0) / lit_hospi if lit_hospi > 0 else 1
        
        # Score basé sur la capacité (0-1, plus de capacité = meilleur score)
        capacity_score = 1 - occupation
        
        return max(0, capacity_score)
    
    def _calculate_service_score(self, hospital_data: pd.Series, service: str) -> float:
        """
        Calcule un score basé sur la correspondance du service
        """
        hospital_service = hospital_data.get('classification', '')
        
        # Score parfait si le service correspond exactement
        if hospital_service == service:
            return 1.0
            
        # Score partiel pour les services compatibles
        service_compatibility = {
            'M': {'C': 0.5, 'SSR': 0.3},
            'C': {'M': 0.5, 'SSR': 0.3},
            'SSR': {'M': 0.3, 'C': 0.3},
            'O': {'M': 0.4},
            'PSY': {'M': 0.2},
            'ESND': {'SSR': 0.4, 'M': 0.3}
        }
        
        return service_compatibility.get(service, {}).get(hospital_service, 0.0)
    
    def _get_hospital_recommendations(
        self,
        service: str,
        estimated_duration: float,
        patient_data: Dict,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Calcule les scores et retourne les meilleurs hôpitaux
        
        Args:
            service: Service médical prédit
            estimated_duration: Durée estimée du séjour
            patient_data: Données du patient
            top_n: Nombre de recommandations à retourner
            
        Returns:
            Liste des meilleurs hôpitaux avec leurs scores
        """
        recommendations = []
        
        for _, hospital in self.hospital_data.iterrows():
            # Calculer les différents scores
            distance_score = self._calculate_distance_score(
                f"{hospital['nom_region']}, France",
                f"{patient_data.get('region', '')}, France"
            )
            
            capacity_score = self._calculate_capacity_score(hospital, estimated_duration)
            service_score = self._calculate_service_score(hospital, service)
            
            # Calculer le score composite (avec pondération)
            composite_score = (
                0.4 * service_score +
                0.3 * distance_score +
                0.3 * capacity_score
            )
            
            if composite_score > 0:  # Ne garder que les hôpitaux pertinents
                recommendations.append({
                    'hospital_name': hospital.get('nom_region', ''),
                    'service': hospital.get('classification', ''),
                    'score': composite_score,
                    'distance_score': distance_score,
                    'capacity_score': capacity_score,
                    'service_score': service_score,
                    'estimated_duration': estimated_duration
                })
        
        # Trier par score et prendre les top_n
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_n]
