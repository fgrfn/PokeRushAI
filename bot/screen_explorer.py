"""Screen-based exploration using KNN for frame deduplication.

Uses hnswlib for efficient nearest-neighbor search to detect unique frames.
This prevents the bot from getting stuck in menus or repeated states.

Based on PokemonRedExperiments approach.
"""

import numpy as np
try:
    import hnswlib
    HNSWLIB_AVAILABLE = True
except ImportError:
    HNSWLIB_AVAILABLE = False
    print("⚠️  Warning: hnswlib not available. Screen exploration will be limited.")


class ScreenExplorer:
    """KNN-based screen frame deduplication for exploration tracking."""
    
    def __init__(
        self,
        frame_shape: tuple = (144, 160, 3),
        max_elements: int = 20000,
        similarity_threshold: float = 2000000.0
    ):
        """Initialize screen explorer.
        
        Args:
            frame_shape: Expected screen frame shape (H, W, C)
            max_elements: Maximum number of frames to store
            similarity_threshold: Distance threshold for considering frames similar
        """
        self.frame_shape = frame_shape
        self.max_elements = max_elements
        self.similarity_threshold = similarity_threshold
        
        # Calculate vector dimension (flattened frame)
        self.vec_dim = int(np.prod(frame_shape))
        
        # Initialize KNN index
        self.knn_index = None
        self.use_knn = HNSWLIB_AVAILABLE
        
        if self.use_knn:
            self._init_knn_index()
        
        # Fallback to simple frame hashing if hnswlib unavailable
        self.seen_frame_hashes = set()
        self.frame_count = 0
    
    def _init_knn_index(self):
        """Initialize hnswlib KNN index."""
        try:
            # L2 distance, dimension = flattened frame size
            self.knn_index = hnswlib.Index(space='l2', dim=self.vec_dim)
            
            # Initialize index with max elements
            # ef_construction=100 and M=16 are recommended values
            self.knn_index.init_index(
                max_elements=self.max_elements,
                ef_construction=100,
                M=16
            )
            
            self.frame_count = 0
            print(f"✅ KNN Screen Explorer initialized (dim={self.vec_dim}, max={self.max_elements})")
        except Exception as e:
            print(f"⚠️  Failed to initialize KNN index: {e}")
            self.use_knn = False
    
    def reset(self):
        """Reset the explorer for a new episode."""
        if self.use_knn:
            self._init_knn_index()
        else:
            self.seen_frame_hashes.clear()
            self.frame_count = 0
    
    def add_frame(self, frame: np.ndarray) -> bool:
        """Add a frame and check if it's novel.
        
        Args:
            frame: Screen frame array (H, W, C)
            
        Returns:
            True if frame is novel (different from seen frames), False otherwise
        """
        if self.use_knn:
            return self._add_frame_knn(frame)
        else:
            return self._add_frame_hash(frame)
    
    def _add_frame_knn(self, frame: np.ndarray) -> bool:
        """Add frame using KNN index (accurate deduplication)."""
        # Flatten frame to vector
        frame_vec = frame.flatten().astype(np.float32)
        
        # Ensure correct dimension
        if len(frame_vec) != self.vec_dim:
            print(f"⚠️  Frame dimension mismatch: {len(frame_vec)} != {self.vec_dim}")
            return False
        
        # Check if we've reached capacity
        if self.frame_count >= self.max_elements:
            # Index is full, just query without adding
            labels, distances = self.knn_index.knn_query(frame_vec, k=1)
            is_novel = distances[0][0] > self.similarity_threshold
            return is_novel
        
        # Query existing frames if we have any
        if self.frame_count > 0:
            try:
                labels, distances = self.knn_index.knn_query(frame_vec, k=1)
                
                # Check if frame is similar to any existing frame
                if distances[0][0] < self.similarity_threshold:
                    # Frame is too similar to an existing one
                    return False
            except Exception as e:
                print(f"⚠️  KNN query error: {e}")
                pass
        
        # Add new frame to index
        try:
            self.knn_index.add_items(frame_vec, self.frame_count)
            self.frame_count += 1
            return True
        except Exception as e:
            print(f"⚠️  Failed to add frame to KNN index: {e}")
            return False
    
    def _add_frame_hash(self, frame: np.ndarray) -> bool:
        """Add frame using simple hashing (fallback method)."""
        # Create hash from downsampled frame
        # Downsample to reduce hash collisions while keeping uniqueness
        downsampled = frame[::4, ::4, :].tobytes()
        frame_hash = hash(downsampled)
        
        if frame_hash not in self.seen_frame_hashes:
            self.seen_frame_hashes.add(frame_hash)
            self.frame_count += 1
            return True
        
        return False
    
    def get_unique_frame_count(self) -> int:
        """Get number of unique frames seen."""
        return self.frame_count
    
    def get_stats(self) -> dict:
        """Get exploration statistics."""
        return {
            'unique_frames': self.frame_count,
            'max_capacity': self.max_elements,
            'capacity_used': f"{(self.frame_count / self.max_elements) * 100:.1f}%",
            'using_knn': self.use_knn,
            'vec_dim': self.vec_dim
        }
