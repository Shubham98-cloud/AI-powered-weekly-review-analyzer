import umap
import hdbscan
import numpy as np
from typing import List, Tuple

def cluster_embeddings(
    embeddings: List[List[float]], 
    umap_params: dict, 
    hdbscan_params: dict
) -> np.ndarray:
    """
    Perform UMAP dimensionality reduction followed by HDBSCAN clustering.
    Returns an array of cluster labels.
    """
    if not embeddings:
        return np.array([])
        
    data = np.array(embeddings)
    
    # 1. UMAP reduction
    print(f"Reducing dimensions with UMAP (n_neighbors={umap_params['n_neighbors']})...")
    reducer = umap.UMAP(
        n_neighbors=umap_params['n_neighbors'],
        min_dist=umap_params['min_dist'],
        metric=umap_params['metric'],
        n_components=2, # Reduce to 2D for clustering
        random_state=42
    )
    u_embeddings = reducer.fit_transform(data)
    
    # 2. HDBSCAN clustering
    print(f"Clustering with HDBSCAN (min_cluster_size={hdbscan_params['min_cluster_size']})...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=hdbscan_params['min_cluster_size'],
        min_samples=hdbscan_params['min_samples'],
        prediction_data=True
    )
    labels = clusterer.fit_predict(u_embeddings)
    
    return labels
