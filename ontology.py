"""
ontology.py

Knowledge Graph Ontology for Machine Learning / Data Mining PDFs

Used by:
- Entity Extraction
- Relationship Extraction
- Entity Resolution
- Neo4j Loader
"""

from dataclasses import dataclass
from typing import Dict, List, Set


# ============================================================
# ENTITY TYPES
# ============================================================

ENTITY_TYPES: Set[str] = {

    # Algorithms
    "Algorithm",

    # ML Models
    "Model",

    # General Concepts
    "Concept",

    # Techniques
    "Technique",

    # Layers / Components
    "Layer",

    # Data structures
    "DataStructure",

    # Mathematical formulas
    "Formula",

    # Metrics
    "Metric",

    # Evaluation metrics
    "EvaluationMetric",

    # Optimization
    "OptimizationMethod",

    # Distance Measures
    "DistanceMeasure",

    # Parameters
    "Parameter",

    # Datasets
    "Dataset",

    # Applications
    "Application",

    # Cluster Types
    "ClusterType",

    # Point Types
    "PointType",

    # Activation Functions
    "ActivationFunction",

    # Loss Functions
    "LossFunction",

    # Optimizers
    "Optimizer",

    # Hardware
    "Hardware",

    # Software Library
    "Library",

    # Framework
    "Framework",

}


# ============================================================
# RELATIONSHIP TYPES
# ============================================================

RELATIONSHIP_TYPES: Set[str] = {

    "USES",

    "HAS_PARAMETER",

    "HAS_LAYER",

    "HAS_PROPERTY",

    "HAS_TYPE",

    "PRODUCES",

    "GENERATES",

    "COMPUTES",

    "CALCULATES",

    "MEASURES",

    "MINIMIZES",

    "MAXIMIZES",

    "OPTIMIZES",

    "BASED_ON",

    "PART_OF",

    "CONNECTED_TO",

    "EVALUATED_BY",

    "COMPARES_WITH",

    "INITIALIZES",

    "TRAINS",

    "PREDICTS",

    "CLASSIFIES",

    "CLUSTERS",

    "REQUIRES",

    "OUTPUTS",

}


# ============================================================
# ENTITY ALIASES
# ============================================================

ENTITY_ALIASES: Dict[str, str] = {

    # KMeans

    "KMeans": "K-Means",

    "K Means": "K-Means",

    "kmeans": "K-Means",

    "k-means": "K-Means",

    # ANN

    "ANN": "Artificial Neural Network",

    "Artificial Neural Networks": "Artificial Neural Network",

    # DBSCAN

    "DB Scan": "DBSCAN",

    "DB-Scan": "DBSCAN",

    # Hierarchical

    "Agglomerative": "Agglomerative Clustering",

    "Divisive": "Divisive Clustering",

    # Metrics

    "SSE": "Sum of Squared Error",

    "MSE": "Mean Squared Error",

    "Cross Entropy Loss": "Cross Entropy",

    "Silhouette": "Silhouette Coefficient",

    # Distance

    "L2 Distance": "Euclidean Distance",

    "L1 Distance": "Manhattan Distance",

    # Activation

    "Rectified Linear Unit": "ReLU",

    # Gradient

    "GD": "Gradient Descent",

}


# ============================================================
# VALID ENTITY TYPES
# ============================================================

VALID_ENTITIES = {

    # Clustering

    "K-Means": "Algorithm",

    "DBSCAN": "Algorithm",

    "Hierarchical Clustering": "Algorithm",

    "Agglomerative Clustering": "Algorithm",

    "Divisive Clustering": "Algorithm",

    # Concepts

    "Cluster": "Concept",

    "Centroid": "Concept",

    "Prototype": "Concept",

    "Noise Point": "PointType",

    "Border Point": "PointType",

    "Core Point": "PointType",

    # Structures

    "Dendrogram": "DataStructure",

    "Proximity Matrix": "DataStructure",

    # Distance

    "Euclidean Distance": "DistanceMeasure",

    "Manhattan Distance": "DistanceMeasure",

    # Metrics

    "Silhouette Coefficient": "EvaluationMetric",

    "Entropy": "EvaluationMetric",

    "Sum of Squared Error": "EvaluationMetric",

    "Cluster Cohesion": "Metric",

    "Cluster Separation": "Metric",

    # Parameters

    "K": "Parameter",

    "Eps": "Parameter",

    "MinPts": "Parameter",

    # Neural Networks

    "Artificial Neural Network": "Model",

    "Perceptron": "Model",

    "Gradient Descent": "Optimizer",

    "Backpropagation": "Algorithm",

    "Sigmoid": "ActivationFunction",

    "ReLU": "ActivationFunction",

    "Hidden Layer": "Layer",

    "Output Layer": "Layer",

}


# ============================================================
# NODE SCHEMA
# ============================================================

@dataclass
class EntityNode:

    name: str

    entity_type: str

    page: int

    chunk_id: str

    description: str = ""

    aliases: List[str] = None


# ============================================================
# EDGE SCHEMA
# ============================================================

@dataclass
class Relationship:

    source: str

    relation: str

    target: str

    page: int

    chunk_id: str

    confidence: float = 1.0


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_entity(entity_name: str) -> str:
    """
    Convert aliases into canonical names.
    """

    entity_name = entity_name.strip()

    return ENTITY_ALIASES.get(entity_name, entity_name)


# ============================================================
# VALIDATION
# ============================================================

def is_valid_entity_type(entity_type: str) -> bool:

    return entity_type in ENTITY_TYPES


def is_valid_relation(relation: str) -> bool:

    return relation in RELATIONSHIP_TYPES


# ============================================================
# LOOKUP
# ============================================================

def get_entity_type(entity_name: str):

    entity_name = normalize_entity(entity_name)

    return VALID_ENTITIES.get(entity_name)


# ============================================================
# GRAPH PROMPT HELPERS
# ============================================================

ENTITY_TYPE_PROMPT = "\n".join(sorted(ENTITY_TYPES))

RELATIONSHIP_PROMPT = "\n".join(sorted(RELATIONSHIP_TYPES))