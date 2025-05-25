#!/usr/bin/env python3
"""
AMPEL360-BWB-Q100 Quantum Resource Allocation Module
====================================================

This module implements the quantum resource allocation algorithm for the
AMPEL360-BWB-Q100 aircraft's Quantum Aerospace Operating System (QAOS).
It prioritizes and allocates quantum computing resources based on workload
classification, criticality, and available resources.

Author: AMPEL360 Quantum Systems Team
Version: 0.9.5
Status: Pre-certification prototype
"""

import logging
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("quantum_resource_allocator")

# Workload classification
class WorkloadClass(Enum):
    """Classification of quantum workloads by criticality"""
    QW1 = 1  # Critical: Real-time safety-critical functions
    QW2 = 2  # Essential: Core aircraft operations
    QW3 = 3  # Standard: Regular operational functions
    QW4 = 4  # Background: Non-time-critical functions


class QuantumResource:
    """Representation of a quantum computing resource"""
    
    def __init__(self, resource_id: str, qubits: int, coherence_time_us: int, 
                 error_rate: float, availability: float = 1.0):
        """
        Initialize a quantum resource
        
        Args:
            resource_id: Unique identifier for the resource
            qubits: Number of logical qubits available
            coherence_time_us: Coherence time in microseconds
            error_rate: Error rate of the quantum processor
            availability: Resource availability (0.0-1.0)
        """
        self.resource_id = resource_id
        self.qubits = qubits
        self.coherence_time_us = coherence_time_us
        self.error_rate = error_rate
        self.availability = availability
        self.allocated = 0  # Percentage of resource allocated (0-100)
        
    def available_qubits(self) -> int:
        """Calculate number of available qubits"""
        return int(self.qubits * (1 - self.allocated / 100))
    
    def __repr__(self) -> str:
        return (f"QuantumResource(id={self.resource_id}, qubits={self.qubits}, "
                f"allocated={self.allocated}%, available={self.available_qubits()})")


class QuantumWorkload:
    """Representation of a quantum computing workload"""
    
    def __init__(self, workload_id: str, class_type: WorkloadClass, 
                 required_qubits: int, max_error_rate: float,
                 min_coherence_time_us: int, deadline_ms: Optional[int] = None,
                 preemptable: bool = False):
        """
        Initialize a quantum workload
        
        Args:
            workload_id: Unique identifier for the workload
            class_type: Workload classification (QW1-QW4)
            required_qubits: Minimum number of qubits required
            max_error_rate: Maximum acceptable error rate
            min_coherence_time_us: Minimum required coherence time in microseconds
            deadline_ms: Deadline for completion in milliseconds (None for no deadline)
            preemptable: Whether the workload can be preempted
        """
        self.workload_id = workload_id
        self.class_type = class_type
        self.required_qubits = required_qubits
        self.max_error_rate = max_error_rate
        self.min_coherence_time_us = min_coherence_time_us
        self.deadline_ms = deadline_ms
        self.preemptable = preemptable
        self.allocated_resource = None
        self.priority_score = self._calculate_priority()
        
    def _calculate_priority(self) -> float:
        """Calculate priority score based on class and deadline"""
        # Base priority from workload class
        base_priority = {
            WorkloadClass.QW1: 1000,
            WorkloadClass.QW2: 100,
            WorkloadClass.QW3: 10,
            WorkloadClass.QW4: 1
        }[self.class_type]
        
        # Adjust for deadline if present
        if self.deadline_ms is not None:
            # Higher priority for closer deadlines
            deadline_factor = 1000 / max(self.deadline_ms, 1)
            return base_priority * (1 + deadline_factor)
        
        return base_priority
    
    def __repr__(self) -> str:
        return (f"QuantumWorkload(id={self.workload_id}, class={self.class_type.name}, "
                f"qubits={self.required_qubits}, priority={self.priority_score:.2f})")


class ResourceAllocationError(Exception):
    """Exception raised for resource allocation failures"""
    pass


class QuantumResourceAllocator:
    """Allocates quantum resources to workloads based on priority and requirements"""
    
    def __init__(self):
        """Initialize the quantum resource allocator"""
        self.resources: List[QuantumResource] = []
        self.workloads: List[QuantumWorkload] = []
        self.allocation_map: Dict[str, str] = {}  # workload_id -> resource_id
        
    def register_resource(self, resource: QuantumResource) -> None:
        """Register a quantum resource with the allocator"""
        self.resources.append(resource)
        logger.info(f"Registered quantum resource: {resource}")
        
    def register_workload(self, workload: QuantumWorkload) -> None:
        """Register a quantum workload with the allocator"""
        self.workloads.append(workload)
        logger.info(f"Registered quantum workload: {workload}")
        
    def can_allocate(self, workload: QuantumWorkload, resource: QuantumResource) -> bool:
        """Check if a resource can satisfy a workload's requirements"""
        # Check if resource has enough available qubits
        if resource.available_qubits() < workload.required_qubits:
            return False
        
        # Check if resource meets error rate requirements
        if resource.error_rate > workload.max_error_rate:
            return False
        
        # Check if resource meets coherence time requirements
        if resource.coherence_time_us < workload.min_coherence_time_us:
            return False
        
        return True
    
    def find_best_resource(self, workload: QuantumWorkload) -> Optional[QuantumResource]:
        """Find the best resource for a workload based on fit and availability"""
        suitable_resources = [r for r in self.resources if self.can_allocate(workload, r)]
        
        if not suitable_resources:
            return None
        
        # Sort by best fit (minimize excess qubits) and then by error rate
        return min(suitable_resources, 
                  key=lambda r: (r.available_qubits() - workload.required_qubits, 
                                r.error_rate))
    
    def allocate_resources(self) -> Dict[str, str]:
        """
        Allocate quantum resources to workloads based on priority
        
        Returns:
            Dictionary mapping workload IDs to resource IDs
        
        Raises:
            ResourceAllocationError: If critical workloads cannot be allocated
        """
        # Reset current allocations
        self.allocation_map = {}
        for resource in self.resources:
            resource.allocated = 0
        
        # Sort workloads by priority (highest first)
        sorted_workloads = sorted(self.workloads, 
                                 key=lambda w: w.priority_score, 
                                 reverse=True)
        
        # First pass: Allocate resources to QW1 (Critical) workloads
        critical_workloads = [w for w in sorted_workloads 
                             if w.class_type == WorkloadClass.QW1]
        
        for workload in critical_workloads:
            resource = self.find_best_resource(workload)
            if resource:
                # Calculate allocation percentage
                allocation_percent = (workload.required_qubits / resource.qubits) * 100
                resource.allocated += allocation_percent
                self.allocation_map[workload.workload_id] = resource.resource_id
                logger.info(f"Allocated {workload} to {resource}")
            else:
                error_msg = f"CRITICAL RESOURCE SHORTAGE: Cannot allocate {workload}"
                logger.error(error_msg)
                raise ResourceAllocationError(error_msg)
        
        # Second pass: Allocate resources to QW2 (Essential) workloads
        essential_workloads = [w for w in sorted_workloads 
                              if w.class_type == WorkloadClass.QW2]
        
        for workload in essential_workloads:
            resource = self.find_best_resource(workload)
            if resource:
                allocation_percent = (workload.required_qubits / resource.qubits) * 100
                resource.allocated += allocation_percent
                self.allocation_map[workload.workload_id] = resource.resource_id
                logger.info(f"Allocated {workload} to {resource}")
            else:
                logger.warning(f"Cannot allocate essential workload: {workload}")
        
        # Third pass: Allocate resources to QW3 (Standard) workloads
        standard_workloads = [w for w in sorted_workloads 
                             if w.class_type == WorkloadClass.QW3]
        
        for workload in standard_workloads:
            resource = self.find_best_resource(workload)
            if resource:
                allocation_percent = (workload.required_qubits / resource.qubits) * 100
                resource.allocated += allocation_percent
                self.allocation_map[workload.workload_id] = resource.resource_id
                logger.info(f"Allocated {workload} to {resource}")
            else:
                logger.info(f"Cannot allocate standard workload: {workload}")
        
        # Fourth pass: Allocate resources to QW4 (Background) workloads
        background_workloads = [w for w in sorted_workloads 
                               if w.class_type == WorkloadClass.QW4]
        
        for workload in background_workloads:
            resource = self.find_best_resource(workload)
            if resource:
                allocation_percent = (workload.required_qubits / resource.qubits) * 100
                resource.allocated += allocation_percent
                self.allocation_map[workload.workload_id] = resource.resource_id
                logger.debug(f"Allocated {workload} to {resource}")
            else:
                logger.debug(f"Cannot allocate background workload: {workload}")
        
        # Optimization pass: Redistribute unused resources to improve performance
        self._optimize_allocation()
        
        return self.allocation_map
    
    def _optimize_allocation(self) -> None:
        """Optimize resource allocation by redistributing unused resources"""
        # Implementation of optimization strategies
        # This would include load balancing, consolidation, etc.
        logger.info("Optimizing quantum resource allocation")
        
        # Calculate total allocation percentage for each resource
        for resource in self.resources:
            logger.info(f"Resource {resource.resource_id} allocation: {resource.allocated:.2f}%")
    
    def get_allocation_status(self) -> Dict:
        """Get the current allocation status"""
        status = {
            "total_resources": len(self.resources),
            "total_workloads": len(self.workloads),
            "allocated_workloads": len(self.allocation_map),
            "resource_utilization": {
                r.resource_id: r.allocated for r in self.resources
            }
        }
        return status


def demo_allocation():
    """Demonstrate the quantum resource allocation algorithm"""
    allocator = QuantumResourceAllocator()
    
    # Register quantum resources
    allocator.register_resource(QuantumResource("QPU-1", qubits=32, 
                                              coherence_time_us=100, 
                                              error_rate=0.001))
    allocator.register_resource(QuantumResource("QPU-2", qubits=24, 
                                              coherence_time_us=150, 
                                              error_rate=0.0008))
    allocator.register_resource(QuantumResource("QPU-3", qubits=16, 
                                              coherence_time_us=200, 
                                              error_rate=0.0005))
    
    # Register quantum workloads
    allocator.register_workload(QuantumWorkload(
        "flight-control-optimization", 
        WorkloadClass.QW1, 
        required_qubits=8,
        max_error_rate=0.001,
        min_coherence_time_us=100,
        deadline_ms=10
    ))
    
    allocator.register_workload(QuantumWorkload(
        "collision-avoidance", 
        WorkloadClass.QW1, 
        required_qubits=12,
        max_error_rate=0.001,
        min_coherence_time_us=100,
        deadline_ms=5
    ))
    
    allocator.register_workload(QuantumWorkload(
        "energy-distribution", 
        WorkloadClass.QW2, 
        required_qubits=10,
        max_error_rate=0.002,
        min_coherence_time_us=80,
        deadline_ms=50
    ))
    
    allocator.register_workload(QuantumWorkload(
        "navigation-optimization", 
        WorkloadClass.QW2, 
        required_qubits=14,
        max_error_rate=0.001,
        min_coherence_time_us=120,
        deadline_ms=100
    ))
    
    allocator.register_workload(QuantumWorkload(
        "environmental-control", 
        WorkloadClass.QW3, 
        required_qubits=6,
        max_error_rate=0.002,
        min_coherence_time_us=50,
        deadline_ms=500
    ))
    
    allocator.register_workload(QuantumWorkload(
        "predictive-maintenance", 
        WorkloadClass.QW4, 
        required_qubits=16,
        max_error_rate=0.005,
        min_coherence_time_us=50,
        deadline_ms=None,
        preemptable=True
    ))
    
    # Perform allocation
    try:
        allocation = allocator.allocate_resources()
        print("\nAllocation Results:")
        for workload_id, resource_id in allocation.items():
            print(f"  {workload_id} -> {resource_id}")
        
        print("\nAllocation Status:")
        status = allocator.get_allocation_status()
        print(f"  Total Resources: {status['total_resources']}")
        print(f"  Total Workloads: {status['total_workloads']}")
        print(f"  Allocated Workloads: {status['allocated_workloads']}")
        print("\nResource Utilization:")
        for resource_id, utilization in status['resource_utilization'].items():
            print(f"  {resource_id}: {utilization:.2f}%")
            
    except ResourceAllocationError as e:
        print(f"Allocation failed: {e}")


if __name__ == "__main__":
    print("AMPEL360-BWB-Q100 Quantum Resource Allocator")
    print("============================================")
    demo_allocation()
