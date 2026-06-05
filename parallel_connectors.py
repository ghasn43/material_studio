#!/usr/bin/env python
"""
Optimized Dataset Connector with Parallel Batch Queries
Provides significant performance improvements through concurrent API calls

Features:
- Parallel dataset queries (ThreadPoolExecutor)
- Batch material verification
- Performance metrics tracking
- Configurable parallelism
- Backward compatible with existing API
"""

from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from typing import Dict, List, Any, Tuple
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
MAX_WORKERS = 4  # Number of parallel threads
QUERY_TIMEOUT = 12  # Timeout per query in seconds
BATCH_SIZE = 10  # Max materials to process in one batch

# ============================================================================
# PERFORMANCE TRACKING
# ============================================================================

class PerformanceMetrics:
    """Track query performance metrics"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.queries_executed = 0
        self.queries_succeeded = 0
        self.queries_failed = 0
        self.datasets_queried = set()
        self.components_checked = 0
    
    def start(self):
        self.start_time = time.time()
    
    def end(self):
        self.end_time = time.time()
    
    @property
    def elapsed_seconds(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    @property
    def success_rate(self) -> float:
        if self.queries_executed == 0:
            return 0.0
        return (self.queries_succeeded / self.queries_executed) * 100
    
    def record_query(self, dataset: str, success: bool):
        self.queries_executed += 1
        self.datasets_queried.add(dataset)
        if success:
            self.queries_succeeded += 1
        else:
            self.queries_failed += 1
    
    def summary(self) -> Dict[str, Any]:
        return {
            'elapsed_seconds': round(self.elapsed_seconds, 3),
            'queries_executed': self.queries_executed,
            'queries_succeeded': self.queries_succeeded,
            'queries_failed': self.queries_failed,
            'success_rate': round(self.success_rate, 1),
            'unique_datasets': len(self.datasets_queried),
            'components_checked': self.components_checked,
            'avg_query_time_ms': round((self.elapsed_seconds / max(self.queries_executed, 1)) * 1000, 2)
        }


# ============================================================================
# PARALLEL QUERY EXECUTION
# ============================================================================

def _query_dataset_parallel(dataset_info: Tuple[str, Any, str]) -> Dict[str, Any]:
    """
    Query a single dataset (used in thread pool)
    
    Args:
        dataset_info: (dataset_name, lookup_function, component_name)
    
    Returns:
        Result with query metadata
    """
    dataset_name, lookup_func, component_name = dataset_info
    try:
        result = lookup_func(component_name)
        return {
            'dataset': dataset_name,
            'component': component_name,
            'found': result.get('found', False),
            'result': result,
            'success': True,
            'error': None
        }
    except Exception as e:
        return {
            'dataset': dataset_name,
            'component': component_name,
            'found': False,
            'result': None,
            'success': False,
            'error': str(e)
        }


def verify_component_parallel(
    component_name: str,
    datasets: List[Tuple[str, Any]],
    max_workers: int = MAX_WORKERS,
    timeout: int = QUERY_TIMEOUT
) -> Dict[str, Any]:
    """
    Verify a single component against all datasets in parallel
    
    Args:
        component_name: Name of component to verify
        datasets: List of (dataset_name, lookup_function) tuples
        max_workers: Number of parallel threads
        timeout: Timeout per query in seconds
    
    Returns:
        Verification result with metrics
    """
    metrics = PerformanceMetrics()
    metrics.start()
    metrics.components_checked = 1
    
    # Prepare parallel queries
    query_tasks = [
        (dataset_name, lookup_func, component_name)
        for dataset_name, lookup_func in datasets
    ]
    
    verification_results = []
    found_evidence = False
    
    # Execute queries in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_query_dataset_parallel, task): task[0]
            for task in query_tasks
        }
        
        for future in as_completed(futures, timeout=timeout):
            dataset_name = futures[future]
            try:
                result = future.result(timeout=timeout)
                verification_results.append(result)
                metrics.record_query(dataset_name, result['success'])
                
                if result['found'] and not found_evidence:
                    found_evidence = True
                    # Log first successful verification
                    logger.debug(f"Component '{component_name}' found in {dataset_name}")
                    
            except TimeoutError:
                logger.warning(f"Query timeout for {component_name} on {dataset_name}")
                metrics.record_query(dataset_name, False)
            except Exception as e:
                logger.error(f"Query error for {component_name} on {dataset_name}: {e}")
                metrics.record_query(dataset_name, False)
    
    metrics.end()
    
    return {
        'component': component_name,
        'found': found_evidence,
        'verification_results': verification_results,
        'metrics': metrics.summary()
    }


def verify_batch_parallel(
    materials: List[Dict[str, Any]],
    category: str,
    datasets: List[Tuple[str, Any]],
    max_workers: int = MAX_WORKERS,
    timeout: int = QUERY_TIMEOUT
) -> Dict[str, Any]:
    """
    Verify multiple materials in parallel batch
    
    Args:
        materials: List of material dicts with components
        category: Material category
        datasets: List of (dataset_name, lookup_function) tuples
        max_workers: Number of parallel threads
        timeout: Timeout per query in seconds
    
    Returns:
        Batch verification results with performance metrics
    """
    metrics = PerformanceMetrics()
    metrics.start()
    
    all_components = []
    for material in materials:
        components = material.get("components", [])
        for comp in components:
            comp_name = comp if isinstance(comp, str) else comp.get("name", "")
            all_components.append((comp_name, material))
    
    metrics.components_checked = len(all_components)
    
    # Process all components in parallel
    component_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(verify_component_parallel, comp_name, datasets, 1, timeout): comp_name
            for comp_name, _ in all_components
        }
        
        for future in as_completed(futures, timeout=timeout * 3):
            comp_name = futures[future]
            try:
                result = future.result()
                component_results.append(result)
                metrics.queries_executed += result['metrics']['queries_executed']
                metrics.queries_succeeded += result['metrics']['queries_succeeded']
                metrics.queries_failed += result['metrics']['queries_failed']
                
            except Exception as e:
                logger.error(f"Batch query error for {comp_name}: {e}")
    
    metrics.end()
    
    # Aggregate results
    verified_count = sum(1 for r in component_results if r['found'])
    not_found_count = len(component_results) - verified_count
    
    return {
        'category': category,
        'materials_checked': len(materials),
        'components_checked': len(all_components),
        'components_verified': verified_count,
        'components_not_found': not_found_count,
        'success_rate': round((verified_count / len(all_components) * 100) if all_components else 0, 1),
        'component_results': component_results,
        'metrics': metrics.summary()
    }


# ============================================================================
# INTEGRATED OPTIMIZATION (for existing function)
# ============================================================================

def verify_with_datasets_optimized(
    material_data: Dict[str, Any],
    category: str,
    datasets: List[Tuple[str, Any]],
    use_parallel: bool = True,
    max_workers: int = MAX_WORKERS
) -> Dict[str, Any]:
    """
    Optimized verification with optional parallel execution
    
    Args:
        material_data: Material data with components
        category: Material category
        datasets: List of (dataset_name, lookup_function) tuples
        use_parallel: Use parallel queries (default: True)
        max_workers: Number of parallel threads
    
    Returns:
        Verification result with performance metrics
    """
    metrics = PerformanceMetrics()
    metrics.start()
    
    components = material_data.get("components", [])
    verified = []
    not_found = []
    all_datasets = set()
    total_papers = 0
    
    if not components:
        return {
            "verification_status": "pass",
            "components_checked": 0,
            "components_verified": [],
            "components_not_found": [],
            "materials_found": 0,
            "datasets_queried": [],
            "literature_hits": 0,
            "evidence_summary": "No components to verify",
            "dataset_urls": [],
            "performance_metrics": metrics.summary()
        }
    
    metrics.components_checked = len(components)
    
    if use_parallel:
        # Parallel verification for each component
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(verify_component_parallel, comp_name, datasets, 1, QUERY_TIMEOUT): comp_name
                for comp_name in [c if isinstance(c, str) else c.get("name", "") for c in components]
            }
            
            for future in as_completed(futures, timeout=QUERY_TIMEOUT * 3):
                comp_name = futures[future]
                try:
                    result = future.result()
                    
                    # Extract metadata
                    for v_result in result['verification_results']:
                        all_datasets.add(v_result['dataset'])
                        metrics.record_query(v_result['dataset'], v_result['success'])
                        
                        if v_result['result'] and "papers_found" in v_result['result']:
                            total_papers += v_result['result'].get("papers_found", 0)
                    
                    if result['found']:
                        verified.append(comp_name)
                    else:
                        not_found.append(comp_name)
                
                except Exception as e:
                    logger.error(f"Error in parallel verification for {comp_name}: {e}")
                    not_found.append(comp_name)
    
    else:
        # Sequential verification (original behavior)
        for component in components:
            comp_name = component if isinstance(component, str) else component.get("name", "")
            found_evidence = False
            
            for dataset_name, lookup_func in datasets:
                try:
                    result = lookup_func(comp_name)
                    all_datasets.add(dataset_name)
                    metrics.record_query(dataset_name, result.get('found', False))
                    
                    if result.get("found"):
                        found_evidence = True
                        if "papers_found" in result:
                            total_papers += result.get("papers_found", 0)
                        break
                
                except Exception as e:
                    logger.debug(f"Error verifying {comp_name} with {dataset_name}: {e}")
            
            if found_evidence:
                verified.append(comp_name)
            else:
                not_found.append(comp_name)
    
    metrics.end()
    
    status = "pass" if len(verified) >= len(components) * 0.5 else "warning"
    evidence_text = f"{len(verified)}/{len(components)} components verified in external databases. "
    if total_papers > 0:
        evidence_text += f"{total_papers} supporting papers found. "
    evidence_text += "Dataset matches do NOT prove performance; experimental validation required."
    
    return {
        "verification_status": status,
        "components_checked": len(components),
        "components_verified": verified,
        "components_not_found": not_found,
        "materials_found": len(verified),
        "datasets_queried": list(all_datasets),
        "literature_hits": total_papers,
        "evidence_summary": evidence_text,
        "dataset_urls": [
            "https://pubchem.ncbi.nlm.nih.gov/",
            "https://www.crossref.org/",
            "https://openalex.org/",
            "https://www.materialsproject.org/"
        ],
        "performance_metrics": metrics.summary()
    }


# ============================================================================
# BENCHMARKING UTILITIES
# ============================================================================

def benchmark_verification(
    materials: List[Dict[str, Any]],
    category: str,
    datasets: List[Tuple[str, Any]],
    iterations: int = 1
) -> Dict[str, Any]:
    """
    Benchmark sequential vs parallel verification
    
    Args:
        materials: List of materials to verify
        category: Material category
        datasets: List of datasets to query
        iterations: Number of iterations to average
    
    Returns:
        Benchmark results comparing sequential and parallel
    """
    results = {
        'materials': len(materials),
        'components': sum(len(m.get("components", [])) for m in materials),
        'iterations': iterations,
        'sequential_times': [],
        'parallel_times': [],
        'sequential_metrics': [],
        'parallel_metrics': []
    }
    
    # Clear cache for fair comparison
    import os
    cache_dir = "data_cache"
    if os.path.exists(cache_dir):
        import shutil
        shutil.rmtree(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
    
    # Benchmark sequential
    for _ in range(iterations):
        for material in materials:
            result = verify_with_datasets_optimized(
                material, category, datasets, use_parallel=False
            )
            results['sequential_times'].append(result['performance_metrics']['elapsed_seconds'])
            results['sequential_metrics'].append(result['performance_metrics'])
    
    # Clear cache again
    if os.path.exists(cache_dir):
        import shutil
        shutil.rmtree(cache_dir)
        os.makedirs(cache_dir, exist_ok=True)
    
    # Benchmark parallel
    for _ in range(iterations):
        for material in materials:
            result = verify_with_datasets_optimized(
                material, category, datasets, use_parallel=True
            )
            results['parallel_times'].append(result['performance_metrics']['elapsed_seconds'])
            results['parallel_metrics'].append(result['performance_metrics'])
    
    # Calculate statistics
    import statistics
    results['sequential_avg'] = round(statistics.mean(results['sequential_times']), 3)
    results['parallel_avg'] = round(statistics.mean(results['parallel_times']), 3)
    results['speedup'] = round(results['sequential_avg'] / results['parallel_avg'], 2)
    results['time_saved'] = round(results['sequential_avg'] - results['parallel_avg'], 3)
    
    return results


if __name__ == '__main__':
    print("Parallel Dataset Connector Module Loaded")
    print(f"Configuration: MAX_WORKERS={MAX_WORKERS}, QUERY_TIMEOUT={QUERY_TIMEOUT}s")
