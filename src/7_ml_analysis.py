"""
Machine Learning Analysis - ML ашиглан урьдчилан таамаглах

Энэ модуль нь Machine Learning алгоритмуудыг ашиглан
сарны муу өдөр ба гамшигт үйл явдлын хамаарлыг судална.

Models:
- Logistic Regression
- Random Forest
- Gradient Boosting
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple
import json
import sys

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_fscore_support, accuracy_score
)
import warnings
warnings.filterwarnings('ignore')

sys.path.append(str(Path(__file__).parent))
from utils.checkpoint_manager import CheckpointManager


class MLAnalyzer:
    """
    Machine Learning шинжилгээний класс

    Сарны өдрийн төрлөөс үйл явдлын хүндрэлийг
    урьдчилан таамаглах загвар бүтээнэ.
    """

    def __init__(
        self,
        matched_file: str = 'data/processed/matched_events.csv',
        lunar_file: str = 'data/processed/lunar_bad_days_gregorian.csv',
        output_file: str = 'results/reports/ml_results.json'
    ):
        """
        MLAnalyzer эхлүүлэх

        Args:
            matched_file: Таарсан өгөгдлийн файл
            lunar_file: Сарны өдрүүдийн файл
            output_file: Үр дүн хадгалах файл
        """
        self.matched_file = Path(matched_file)
        self.lunar_file = Path(lunar_file)
        self.output_file = Path(output_file)

        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.results = {}
        self.models = {}

    def load_data(self) -> pd.DataFrame:
        """
        Өгөгдөл унших ба feature engineering хийх

        Returns:
            Боловсруулсан DataFrame
        """
        print("📖 ML өгөгдөл уншиж байна...")

        matched_df = pd.read_csv(self.matched_file)
        lunar_df = pd.read_csv(self.lunar_file)

        print(f"  ✓ Таарсан үйл явдал: {len(matched_df)}")
        print(f"  ✓ Сарны өдрүүд: {len(lunar_df)}")

        return matched_df

    def prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        ML-д зориулсан features бэлдэх

        Args:
            df: Input DataFrame

        Returns:
            Tuple (X, y)
        """
        print("\n🔧 Features бэлдэж байна...")

        # Features үүсгэх
        features = pd.DataFrame()

        # 1. Сарны өдрийн features
        features['is_bad_day'] = df['start_is_bad_day'].astype(int)
        features['is_good_day'] = df['start_is_good_day'].astype(int)

        # 2. Цаг хугацааны features
        features['month'] = df['month']
        features['year'] = df['year']

        # 3. Category encoding
        le = LabelEncoder()
        features['category_encoded'] = le.fit_transform(df['category'])

        # 4. Нэмэлт features
        features['is_normal_day'] = ((df['start_is_bad_day'] == False) &
                                     (df['start_is_good_day'] == False)).astype(int)

        # Target variable - High severity эсэх
        severity_threshold = df['severity_score'].median()
        y = (df['severity_score'] >= severity_threshold).astype(int)

        X = features.values

        print(f"  ✓ Features: {features.columns.tolist()}")
        print(f"  ✓ X shape: {X.shape}")
        print(f"  ✓ y distribution: {np.bincount(y)}")

        return X, y, features.columns.tolist()

    def train_models(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Олон загвар сургах

        Args:
            X: Features
            y: Target

        Returns:
            Загваруудын үр дүн
        """
        print("\n🤖 ML загваруудыг сургаж байна...")

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Models to train
        models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
        }

        results = {}

        for name, model in models.items():
            print(f"\n  📊 {name}...")

            # Train
            if 'Logistic' in name:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]

            # Metrics
            accuracy = accuracy_score(y_test, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_test, y_pred, average='binary'
            )

            # ROC-AUC (handle small sample)
            try:
                roc_auc = roc_auc_score(y_test, y_pred_proba)
            except:
                roc_auc = None

            # Cross-validation
            if 'Logistic' in name:
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3)
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=3)

            results[name] = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(roc_auc) if roc_auc else None,
                'cv_mean': float(cv_scores.mean()),
                'cv_std': float(cv_scores.std()),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
            }

            # Feature importance (for tree-based models)
            if hasattr(model, 'feature_importances_'):
                results[name]['feature_importance'] = model.feature_importances_.tolist()

            print(f"     Accuracy: {accuracy:.3f}")
            print(f"     F1 Score: {f1:.3f}")
            print(f"     CV Mean: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

            # Save model
            self.models[name] = model

        return results

    def analyze_feature_importance(
        self,
        model_results: Dict,
        feature_names: list
    ) -> Dict[str, Any]:
        """
        Feature importance шинжилгээ

        Args:
            model_results: Model үр дүнгүүд
            feature_names: Feature нэрс

        Returns:
            Feature importance analysis
        """
        print("\n📊 Feature Importance шинжилж байна...")

        importance_analysis = {}

        # Random Forest feature importance
        if 'Random Forest' in model_results:
            rf_importance = model_results['Random Forest'].get('feature_importance', [])

            if rf_importance:
                importance_df = pd.DataFrame({
                    'feature': feature_names,
                    'importance': rf_importance
                }).sort_values('importance', ascending=False)

                importance_analysis['random_forest'] = {
                    'ranking': importance_df.to_dict('records'),
                    'top_feature': importance_df.iloc[0]['feature'],
                    'bad_day_importance': float(importance_df[
                        importance_df['feature'] == 'is_bad_day'
                    ]['importance'].values[0]) if 'is_bad_day' in importance_df['feature'].values else 0
                }

                print("\n  Feature Importance (Random Forest):")
                for idx, row in importance_df.head().iterrows():
                    print(f"    {row['feature']}: {row['importance']:.4f}")

        return importance_analysis

    def run_analysis(self) -> Dict[str, Any]:
        """
        Бүх ML шинжилгээг ажиллуулах

        Returns:
            Бүх үр дүн
        """
        print("="*60)
        print("🤖 MACHINE LEARNING ШИНЖИЛГЭЭ")
        print("="*60)

        # Load and prepare data
        df = self.load_data()

        # Check if enough data
        if len(df) < 20:
            print("\n⚠ Өгөгдөл хангалтгүй байна (< 20 rows)")
            print("  ML шинжилгээ хийхэд илүү их өгөгдөл хэрэгтэй.")
            self.results = {
                'error': 'Insufficient data for ML analysis',
                'required': 20,
                'actual': len(df)
            }
            return self.results

        # Prepare features
        X, y, feature_names = self.prepare_features(df)

        # Train models
        model_results = self.train_models(X, y)

        # Feature importance
        importance = self.analyze_feature_importance(model_results, feature_names)

        # Compile results
        self.results = {
            'models': model_results,
            'feature_importance': importance,
            'data_info': {
                'total_samples': int(len(df)),
                'features_used': feature_names,
                'target_description': 'High severity (>= median)'
            },
            'best_model': max(model_results.items(), key=lambda x: x[1]['accuracy'])[0],
            'interpretation': self._generate_interpretation(model_results, importance)
        }

        return self.results

    def _generate_interpretation(
        self,
        model_results: Dict,
        importance: Dict
    ) -> str:
        """
        Үр дүнгийн тайлбар үүсгэх

        Args:
            model_results: Model үр дүнгүүд
            importance: Feature importance

        Returns:
            Тайлбар текст
        """
        interpretations = []

        # Best model
        best_model = max(model_results.items(), key=lambda x: x[1]['accuracy'])
        interpretations.append(
            f"Хамгийн сайн загвар: {best_model[0]} "
            f"(Accuracy: {best_model[1]['accuracy']:.2%})"
        )

        # Feature importance
        if 'random_forest' in importance:
            bad_day_imp = importance['random_forest']['bad_day_importance']
            if bad_day_imp > 0.2:
                interpretations.append(
                    f"✓ 'is_bad_day' feature чухал нөлөөтэй (importance: {bad_day_imp:.4f})"
                )
            else:
                interpretations.append(
                    f"✗ 'is_bad_day' feature бага нөлөөтэй (importance: {bad_day_imp:.4f})"
                )

        # Model performance
        avg_accuracy = np.mean([r['accuracy'] for r in model_results.values()])
        if avg_accuracy > 0.7:
            interpretations.append(
                "✓ Загваруудын дундаж accuracy сайн (>70%)"
            )
        elif avg_accuracy > 0.5:
            interpretations.append(
                "○ Загваруудын дундаж accuracy дунд зэрэг (50-70%)"
            )
        else:
            interpretations.append(
                "✗ Загваруудын accuracy бага (<50%) - Random baseline-тай ойролцоо"
            )

        return "\n".join(interpretations)

    def save_results(self) -> None:
        """Үр дүнг хадгалах"""
        print(f"\n💾 ML үр дүн хадгалж байна: {self.output_file}")

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print("✓ Амжилттай хадгалагдлаа!")

    def print_summary(self) -> None:
        """Хураангуй харуулах"""
        print("\n" + "="*60)
        print("📊 ML ШИНЖИЛГЭЭНИЙ ҮР ДҮН")
        print("="*60)

        if 'error' in self.results:
            print(f"\n⚠ {self.results['error']}")
            return

        if 'interpretation' in self.results:
            print("\n" + self.results['interpretation'])

        if 'best_model' in self.results:
            best = self.results['best_model']
            metrics = self.results['models'][best]
            print(f"\n🏆 Хамгийн сайн загвар: {best}")
            print(f"   Accuracy: {metrics['accuracy']:.2%}")
            print(f"   F1 Score: {metrics['f1_score']:.2%}")
            if metrics['roc_auc']:
                print(f"   ROC-AUC: {metrics['roc_auc']:.2%}")

        print("\n" + "="*60)


def main():
    """Main функц"""
    print("="*60)
    print("🤖 MACHINE LEARNING ANALYSIS")
    print("="*60)

    try:
        analyzer = MLAnalyzer()
        results = analyzer.run_analysis()
        analyzer.save_results()
        analyzer.print_summary()

        print("\n✅ ML шинжилгээ амжилттай дууслаа!")
        return results

    except FileNotFoundError as e:
        print(f"\n❌ Файл олдсонгүй: {e}")
        return None

    except Exception as e:
        print(f"\n❌ Алдаа: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    results = main()
