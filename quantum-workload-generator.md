## 1. Overview

The AMPEL360 Workload Generator Framework creates realistic quantum computing workloads that simulate actual aircraft operational scenarios. These generators produce workloads with varying characteristics, priorities, and resource requirements to thoroughly test the Quantum Resource Allocator system under realistic conditions.

## 2. Workload Generator Architecture

```plaintext
┌─────────────────────────────────────────────────────┐
│                Workload Generator                    │
├─────────────────┬───────────────────┬───────────────┤
│ Flight Scenario │  Workload Profile │ Distribution  │
│    Generator    │     Generator     │   Controller  │
├─────────────────┼───────────────────┼───────────────┤
│ Flight Phase    │  Quantum Circuit  │ Timing        │
│ Simulator       │  Generator        │ Controller    │
└─────────────────┴───────────────────┴───────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────┐
│                Workload Repository                   │
├─────────────────────────────────────────────────────┤
│ - Critical Workloads (QW1)                          │
│ - Essential Workloads (QW2)                         │
│ - Standard Workloads (QW3)                          │
│ - Background Workloads (QW4)                        │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│            Quantum Resource Allocator                │
└─────────────────────────────────────────────────────┘
```

## 3. Core Components

### 3.1 Flight Scenario Generator

```python
# flight_scenario_generator.py
import numpy as np
import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

class FlightPhase(Enum):
    PREFLIGHT = 1
    TAXI = 2
    TAKEOFF = 3
    CLIMB = 4
    CRUISE = 5
    DESCENT = 6
    APPROACH = 7
    LANDING = 8
    POSTFLIGHT = 9
    EMERGENCY = 10

class WeatherCondition(Enum):
    CLEAR = 1
    LIGHT_CLOUDS = 2
    OVERCAST = 3
    RAIN = 4
    THUNDERSTORM = 5
    SNOW = 6
    FOG = 7
    TURBULENCE = 8

class FlightScenario:
    def __init__(self, 
                 flight_id: str,
                 departure: str,
                 destination: str,
                 aircraft_type: str = "AMPEL360-BWB-Q100",
                 duration_minutes: int = 120,
                 passenger_count: int = 85,
                 cargo_weight_kg: int = 2000,
                 seed: Optional[int] = None):
        """Initialize a flight scenario"""
        self.flight_id = flight_id
        self.departure = departure
        self.destination = destination
        self.aircraft_type = aircraft_type
        self.duration_minutes = duration_minutes
        self.passenger_count = passenger_count
        self.cargo_weight_kg = cargo_weight_kg
        
        # Initialize random generator with seed for reproducibility
        self.rng = np.random.RandomState(seed if seed is not None else np.random.randint(0, 2**32))
        
        # Initialize scenario parameters
        self.current_time = datetime.datetime.now()
        self.current_phase = FlightPhase.PREFLIGHT
        self.phase_start_time = self.current_time
        self.weather_conditions = WeatherCondition.CLEAR
        self.altitude_m = 0
        self.speed_kph = 0
        self.fuel_remaining_kg = self._calculate_initial_fuel()
        self.system_status = self._initialize_system_status()
        
        # Phase duration probabilities (in minutes)
        self.phase_durations = {
            FlightPhase.PREFLIGHT: (15, 5),    # mean, std
            FlightPhase.TAXI: (10, 3),
            FlightPhase.TAKEOFF: (2, 0.5),
            FlightPhase.CLIMB: (15, 3),
            FlightPhase.CRUISE: (duration_minutes - 50, 10),
            FlightPhase.DESCENT: (15, 3),
            FlightPhase.APPROACH: (5, 1),
            FlightPhase.LANDING: (3, 0.5),
            FlightPhase.POSTFLIGHT: (15, 5),
            FlightPhase.EMERGENCY: (10, 5)
        }
        
        # Weather change probabilities
        self.weather_change_prob = 0.05  # 5% chance per time step
        
        # Emergency probability
        self.emergency_prob = 0.001  # 0.1% chance per time step
        
        # Initialize phase schedule
        self.phase_schedule = self._generate_phase_schedule()
    
    def _calculate_initial_fuel(self) -> float:
        """Calculate initial fuel based on flight parameters"""
        base_fuel = 5000  # Base fuel in kg
        distance_factor = self.duration_minutes / 60 * 2000  # 2000 kg per hour
        weight_factor = (self.passenger_count * 75 + self.cargo_weight_kg) * 0.01
        return base_fuel + distance_factor + weight_factor
    
    def _initialize_system_status(self) -> Dict[str, Dict]:
        """Initialize status of aircraft systems"""
        systems = ["flight_control", "navigation", "propulsion", 
                   "environmental", "communications", "power", "quantum"]
        
        status = {}
        for system in systems:
            status[system] = {
                "health": 1.0,  # 100% health
                "degradation_rate": self.rng.uniform(0.0001, 0.001),
                "last_maintenance": self.current_time - datetime.timedelta(
                    hours=self.rng.randint(1, 500))
            }
        return status
    
    def _generate_phase_schedule(self) -> List[Tuple[FlightPhase, datetime.datetime]]:
        """Generate a schedule of flight phases"""
        schedule = []
        current_time = self.current_time
        
        # Normal flight phases
        for phase in [FlightPhase.PREFLIGHT, FlightPhase.TAXI, FlightPhase.TAKEOFF,
                     FlightPhase.CLIMB, FlightPhase.CRUISE, FlightPhase.DESCENT,
                     FlightPhase.APPROACH, FlightPhase.LANDING, FlightPhase.POSTFLIGHT]:
            
            mean_duration, std_duration = self.phase_durations[phase]
            duration_minutes = max(1, int(self.rng.normal(mean_duration, std_duration)))
            
            schedule.append((phase, current_time))
            current_time += datetime.timedelta(minutes=duration_minutes)
        
        return schedule
    
    def advance_time(self, minutes: float) -> Dict:
        """Advance the simulation by specified minutes and return current state"""
        self.current_time += datetime.timedelta(minutes=minutes)
        
        # Check if we should transition to next phase
        self._check_phase_transition()
        
        # Update aircraft parameters based on phase
        self._update_aircraft_parameters(minutes)
        
        # Random events
        self._handle_random_events()
        
        # Return current state
        return self.get_current_state()
    
    def _check_phase_transition(self) -> None:
        """Check and perform phase transitions if needed"""
        # Find the next scheduled phase
        next_phase = None
        next_time = None
        
        for phase, time in self.phase_schedule:
            if time > self.current_time:
                break
            next_phase = phase
            next_time = time
        
        if next_phase and next_phase != self.current_phase:
            self.current_phase = next_phase
            self.phase_start_time = next_time
    
    def _update_aircraft_parameters(self, minutes: float) -> None:
        """Update aircraft parameters based on current phase"""
        # Update fuel
        if self.current_phase not in [FlightPhase.PREFLIGHT, FlightPhase.POSTFLIGHT]:
            fuel_consumption_rates = {
                FlightPhase.TAXI: 10,      # kg per minute
                FlightPhase.TAKEOFF: 50,
                FlightPhase.CLIMB: 40,
                FlightPhase.CRUISE: 30,
                FlightPhase.DESCENT: 20,
                FlightPhase.APPROACH: 15,
                FlightPhase.LANDING: 10,
                FlightPhase.EMERGENCY: 35
            }
            rate = fuel_consumption_rates.get(self.current_phase, 0)
            self.fuel_remaining_kg -= rate * minutes
        
        # Update altitude and speed
        if self.current_phase == FlightPhase.CLIMB:
            self.altitude_m += 300 * minutes  # 300m per minute
            self.speed_kph = min(850, self.speed_kph + 20 * minutes)
        elif self.current_phase == FlightPhase.CRUISE:
            self.altitude_m = 10000  # Cruise altitude
            self.speed_kph = 850     # Cruise speed
        elif self.current_phase == FlightPhase.DESCENT:
            self.altitude_m -= 200 * minutes
            self.speed_kph = max(300, self.speed_kph - 10 * minutes)
        elif self.current_phase == FlightPhase.APPROACH:
            self.altitude_m -= 100 * minutes
            self.speed_kph = max(200, self.speed_kph - 20 * minutes)
        elif self.current_phase == FlightPhase.LANDING:
            self.altitude_m = max(0, self.altitude_m - 100 * minutes)
            self.speed_kph = max(0, self.speed_kph - 50 * minutes)
        elif self.current_phase == FlightPhase.TAKEOFF:
            self.altitude_m += 50 * minutes
            self.speed_kph += 40 * minutes
        
        # Update system health
        for system in self.system_status:
            degradation = self.system_status[system]["degradation_rate"] * minutes
            self.system_status[system]["health"] = max(0.7, 
                                                      self.system_status[system]["health"] - degradation)
    
    def _handle_random_events(self) -> None:
        """Handle random events like weather changes or emergencies"""
        # Weather changes
        if self.rng.random() < self.weather_change_prob:
            weather_options = list(WeatherCondition)
            self.weather_conditions = self.rng.choice(weather_options)
        
        # Emergency situations
        if (self.current_phase not in [FlightPhase.PREFLIGHT, FlightPhase.POSTFLIGHT] and 
            self.current_phase != FlightPhase.EMERGENCY and
            self.rng.random() < self.emergency_prob):
            
            # Create emergency event
            self.current_phase = FlightPhase.EMERGENCY
            
            # Simulate system failure
            failing_system = self.rng.choice(list(self.system_status.keys()))
            self.system_status[failing_system]["health"] *= 0.5
    
    def get_current_state(self) -> Dict:
        """Get the current state of the flight scenario"""
        return {
            "flight_id": self.flight_id,
            "current_time": self.current_time.isoformat(),
            "flight_phase": self.current_phase.name,
            "phase_duration": (self.current_time - self.phase_start_time).total_seconds() / 60,
            "weather": self.weather_conditions.name,
            "altitude_m": self.altitude_m,
            "speed_kph": self.speed_kph,
            "fuel_remaining_kg": self.fuel_remaining_kg,
            "fuel_percentage": self.fuel_remaining_kg / self._calculate_initial_fuel() * 100,
            "system_status": {k: v["health"] for k, v in self.system_status.items()},
            "passenger_count": self.passenger_count,
            "cargo_weight_kg": self.cargo_weight_kg
        }

class FlightScenarioGenerator:
    """Generator for flight scenarios"""
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.RandomState(seed if seed is not None else np.random.randint(0, 2**32))
        
        # Airport database (IATA code, name)
        self.airports = [
            ("LHR", "London Heathrow"),
            ("CDG", "Paris Charles de Gaulle"),
            ("FRA", "Frankfurt"),
            ("AMS", "Amsterdam Schiphol"),
            ("MAD", "Madrid Barajas"),
            ("FCO", "Rome Fiumicino"),
            ("IST", "Istanbul"),
            ("MUC", "Munich"),
            ("BCN", "Barcelona"),
            ("LGW", "London Gatwick"),
            ("ORY", "Paris Orly"),
            ("MXP", "Milan Malpensa"),
            ("CPH", "Copenhagen"),
            ("ZRH", "Zurich"),
            ("OSL", "Oslo"),
            ("ARN", "Stockholm Arlanda"),
            ("VIE", "Vienna"),
            ("BRU", "Brussels"),
            ("DUB", "Dublin"),
            ("HEL", "Helsinki")
        ]
    
    def generate_scenario(self) -> FlightScenario:
        """Generate a random flight scenario"""
        # Select random departure and destination
        departure, destination = self.rng.choice(self.airports, size=2, replace=False)
        
        # Generate flight ID
        flight_id = f"AMP{self.rng.randint(100, 999)}"
        
        # Generate random flight parameters
        duration_minutes = self.rng.randint(60, 240)  # 1-4 hours
        passenger_count = self.rng.randint(50, 100)   # Up to 100 passengers
        cargo_weight_kg = self.rng.randint(1000, 5000)  # 1-5 tons
        
        return FlightScenario(
            flight_id=flight_id,
            departure=departure[0],
            destination=destination[0],
            duration_minutes=duration_minutes,
            passenger_count=passenger_count,
            cargo_weight_kg=cargo_weight_kg,
            seed=self.rng.randint(0, 2**32)
        )
```

### 3.2 Quantum Workload Profile Generator

```python
# quantum_workload_generator.py
import numpy as np
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any

class WorkloadClass(Enum):
    QW1 = 1  # Critical: Real-time safety-critical functions
    QW2 = 2  # Essential: Core aircraft operations
    QW3 = 3  # Standard: Regular operational functions
    QW4 = 4  # Background: Non-time-critical functions

class WorkloadType(Enum):
    OPTIMIZATION = 1
    SIMULATION = 2
    MACHINE_LEARNING = 3
    CRYPTOGRAPHY = 4
    SENSING = 5
    ERROR_CORRECTION = 6

class QuantumWorkloadProfile:
    """Profile for a quantum workload"""
    
    def __init__(self,
                 workload_id: str,
                 class_type: WorkloadClass,
                 workload_type: WorkloadType,
                 required_qubits: int,
                 max_error_rate: float,
                 min_coherence_time_us: int,
                 deadline_ms: Optional[int] = None,
                 preemptable: bool = False,
                 circuit_depth: int = 100,
                 entanglement_pattern: str = "linear",
                 measurement_count: int = 1000,
                 classical_preprocessing_ms: int = 10,
                 classical_postprocessing_ms: int = 20,
                 priority_boost: float = 1.0):
        """Initialize a quantum workload profile"""
        self.workload_id = workload_id
        self.class_type = class_type
        self.workload_type = workload_type
        self.required_qubits = required_qubits
        self.max_error_rate = max_error_rate
        self.min_coherence_time_us = min_coherence_time_us
        self.deadline_ms = deadline_ms
        self.preemptable = preemptable
        self.circuit_depth = circuit_depth
        self.entanglement_pattern = entanglement_pattern
        self.measurement_count = measurement_count
        self.classical_preprocessing_ms = classical_preprocessing_ms
        self.classical_postprocessing_ms = classical_postprocessing_ms
        self.priority_boost = priority_boost
        
        # Calculate estimated execution time
        self.estimated_execution_time_ms = self._calculate_execution_time()
        
        # Calculate priority score
        self.priority_score = self._calculate_priority()
    
    def _calculate_execution_time(self) -> int:
        """Estimate execution time based on workload characteristics"""
        # Base time for quantum execution (simplified model)
        gate_time_ns = 50  # Average gate time in nanoseconds
        quantum_time_ms = (self.circuit_depth * gate_time_ns * 
                          self.required_qubits / 1_000_000)
        
        # Add classical pre/post processing time
        total_time_ms = (quantum_time_ms + 
                        self.classical_preprocessing_ms + 
                        self.classical_postprocessing_ms)
        
        # Add time for measurements
        measurement_time_ms = self.measurement_count * 0.01
        
        return int(total_time_ms + measurement_time_ms)
    
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
            return base_priority * (1 + deadline_factor) * self.priority_boost
        
        return base_priority * self.priority_boost
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "workload_id": self.workload_id,
            "class_type": self.class_type.name,
            "workload_type": self.workload_type.name,
            "required_qubits": self.required_qubits,
            "max_error_rate": self.max_error_rate,
            "min_coherence_time_us": self.min_coherence_time_us,
            "deadline_ms": self.deadline_ms,
            "preemptable": self.preemptable,
            "circuit_depth": self.circuit_depth,
            "entanglement_pattern": self.entanglement_pattern,
            "measurement_count": self.measurement_count,
            "classical_preprocessing_ms": self.classical_preprocessing_ms,
            "classical_postprocessing_ms": self.classical_postprocessing_ms,
            "estimated_execution_time_ms": self.estimated_execution_time_ms,
            "priority_score": self.priority_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantumWorkloadProfile':
        """Create from dictionary representation"""
        return cls(
            workload_id=data["workload_id"],
            class_type=WorkloadClass[data["class_type"]],
            workload_type=WorkloadType[data["workload_type"]],
            required_qubits=data["required_qubits"],
            max_error_rate=data["max_error_rate"],
            min_coherence_time_us=data["min_coherence_time_us"],
            deadline_ms=data.get("deadline_ms"),
            preemptable=data["preemptable"],
            circuit_depth=data["circuit_depth"],
            entanglement_pattern=data["entanglement_pattern"],
            measurement_count=data["measurement_count"],
            classical_preprocessing_ms=data["classical_preprocessing_ms"],
            classical_postprocessing_ms=data["classical_postprocessing_ms"],
            priority_boost=data.get("priority_boost", 1.0)
        )

class QuantumWorkloadGenerator:
    """Generator for quantum workloads"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the quantum workload generator"""
        self.rng = np.random.RandomState(seed if seed is not None else np.random.randint(0, 2**32))
        
        # Workload templates by flight phase and system
        self.workload_templates = self._initialize_workload_templates()
    
    def _initialize_workload_templates(self) -> Dict:
        """Initialize workload templates for different flight phases and systems"""
        templates = {}
        
        # Flight control workloads
        templates["flight_control"] = {
            "preflight": [
                {
                    "name": "control-surface-optimization",
                    "class_type": WorkloadClass.QW3,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (8, 12),
                    "circuit_depth_range": (50, 150),
                    "deadline_ms_range": (500, 1000),
                    "preemptable": True
                }
            ],
            "takeoff": [
                {
                    "name": "real-time-control-optimization",
                    "class_type": WorkloadClass.QW1,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (12, 16),
                    "circuit_depth_range": (80, 120),
                    "deadline_ms_range": (5, 10),
                    "preemptable": False
                },
                {
                    "name": "stability-analysis",
                    "class_type": WorkloadClass.QW2,
                    "workload_type": WorkloadType.SIMULATION,
                    "required_qubits_range": (10, 14),
                    "circuit_depth_range": (100, 200),
                    "deadline_ms_range": (50, 100),
                    "preemptable": False
                }
            ],
            "cruise": [
                {
                    "name": "efficiency-optimization",
                    "class_type": WorkloadClass.QW2,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (8, 12),
                    "circuit_depth_range": (100, 300),
                    "deadline_ms_range": (200, 500),
                    "preemptable": True
                },
                {
                    "name": "turbulence-response",
                    "class_type": WorkloadClass.QW1,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (10, 14),
                    "circuit_depth_range": (50, 100),
                    "deadline_ms_range": (5, 20),
                    "preemptable": False
                }
            ],
            "landing": [
                {
                    "name": "approach-optimization",
                    "class_type": WorkloadClass.QW1,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (12, 16),
                    "circuit_depth_range": (80, 120),
                    "deadline_ms_range": (5, 10),
                    "preemptable": False
                }
            ],
            "emergency": [
                {
                    "name": "emergency-trajectory",
                    "class_type": WorkloadClass.QW1,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (14, 20),
                    "circuit_depth_range": (50, 100),
                    "deadline_ms_range": (2, 5),
                    "preemptable": False
                }
            ]
        }
        
        # Navigation workloads
        templates["navigation"] = {
            "preflight": [
                {
                    "name": "route-optimization",
                    "class_type": WorkloadClass.QW3,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (10, 16),
                    "circuit_depth_range": (200, 500),
                    "deadline_ms_range": (1000, 5000),
                    "preemptable": True
                }
            ],
            "cruise": [
                {
                    "name": "weather-rerouting",
                    "class_type": WorkloadClass.QW2,
                    "workload_type": WorkloadType.OPTIMIZATION,
                    "required_qubits_range": (12, 18),
                    "circuit_depth_range": (150, 300),
                    "deadline_ms_range": (100, 500),
                    "preemptable": True
                },
                {
                    "name": "position-optimization",
                    "class_type": WorkloadClass.QW2,
                    "workload_type": WorkloadType.SENSING,
                    "required_qubits_range": (8, 12),
                    "circuit_depth_range": (50, 150),
                    "deadline_ms_range": (50, 200),
                    "preemptable": False
                }
            ]
        }
        
        # Add more systems and templates...
        
        return templates
    
    def generate_workload(self, 
                          flight_state: Dict, 
                          system: str) -> Optional[QuantumWorkloadProfile]:
        """Generate a workload based on flight state and system"""
        flight_phase = flight_state["flight_phase"].lower()
        
        # Check if we have templates for this system and phase
        if system not in self.workload_templates:
            return None
        
        if flight_phase not in self.workload_templates[system]:
            # Try to use a default phase
            if "cruise" in self.workload_templates[system]:
                flight_phase = "cruise"
            else:
                return None
        
        # Get templates for this system and phase
        templates = self.workload_templates[system][flight_phase]
        
        if not templates:
            return None
        
        # Select a random template
        template = self.rng.choice(templates)
        
        # Generate workload ID
        workload_id = f"{system}-{template['name']}-{uuid.uuid4().hex[:8]}"
        
        # Generate parameters from ranges
        required_qubits = self.rng.randint(
            template["required_qubits_range"][0],
            template["required_qubits_range"][1] + 1
        )
        
        circuit_depth = self.rng.randint(
            template["circuit_depth_range"][0],
            template["circuit_depth_range"][1] + 1
        )
        
        if "deadline_ms_range" in template:
            deadline_ms = self.rng.randint(
                template["deadline_ms_range"][0],
                template["deadline_ms_range"][1] + 1
            )
        else:
            deadline_ms = None
        
        # Set error rate and coherence time based on workload class
        if template["class_type"] == WorkloadClass.QW1:
            max_error_rate = 0.001
            min_coherence_time_us = 100
        elif template["class_type"] == WorkloadClass.QW2:
            max_error_rate = 0.002
            min_coherence_time_us = 80
        elif template["class_type"] == WorkloadClass.QW3:
            max_error_rate = 0.005
            min_coherence_time_us = 50
        else:  # QW4
            max_error_rate = 0.01
            min_coherence_time_us = 30
        
        # Adjust parameters based on flight state
        priority_boost = 1.0
        
        # Boost priority in emergency
        if flight_state["flight_phase"] == "EMERGENCY":
            priority_boost = 2.0
        
        # Adjust based on system health
        if system in flight_state["system_status"]:
            system_health = flight_state["system_status"][system]
            if system_health < 0.8:
                priority_boost *= (2.0 - system_health)
        
        # Create the workload profile
        return QuantumWorkloadProfile(
            workload_id=workload_id,
            class_type=template["class_type"],
            workload_type=template["workload_type"],
            required_qubits=required_qubits,
            max_error_rate=max_error_rate,
            min_coherence_time_us=min_coherence_time_us,
            deadline_ms=deadline_ms,
            preemptable=template.get("preemptable", False),
            circuit_depth=circuit_depth,
            entanglement_pattern="linear",  # Default pattern
            measurement_count=self.rng.randint(100, 2000),
            classical_preprocessing_ms=self.rng.randint(5, 50),
            classical_postprocessing_ms=self.rng.randint(5, 100),
            priority_boost=priority_boost
        )
    
    def generate_workloads_for_state(self, 
                                     flight_state: Dict, 
                                     count_range: Tuple[int, int] = (5, 15)) -> List[QuantumWorkloadProfile]:
        """Generate multiple workloads for a given flight state"""
        # Determine how many workloads to generate
        count = self.rng.randint(count_range[0], count_range[1] + 1)
        
        workloads = []
        systems = list(flight_state["system_status"].keys())
        
        for _ in range(count):
            # Select a random system
            system = self.rng.choice(systems)
            
            # Generate a workload for this system
            workload = self.generate_workload(flight_state, system)
            
            if workload:
                workloads.append(workload)
        
        return workloads
```

### 3.3 Quantum Circuit Generator

```python
# quantum_circuit_generator.py
import numpy as np
from typing import Dict, List, Optional, Tuple, Any

class QuantumCircuitGenerator:
    """Generator for quantum circuits based on workload profiles"""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the quantum circuit generator"""
        self.rng = np.random.RandomState(seed if seed is not None else np.random.randint(0, 2**32))
        
        # Gate set by workload type
        self.gate_sets = {
            "OPTIMIZATION": ["h", "x", "y", "z", "cx", "cz", "rx", "ry", "rz"],
            "SIMULATION": ["h", "x", "y", "z", "cx", "cy", "cz", "rx", "ry", "rz", "p", "t"],
            "MACHINE_LEARNING": ["h", "rx", "ry", "rz", "cx", "cz"],
            "CRYPTOGRAPHY": ["h", "x", "y", "z", "cx"],
            "SENSING": ["h", "x", "y", "rx", "ry", "rz", "cx", "cz"],
            "ERROR_CORRECTION": ["h", "x", "z", "cx", "cz", "measure", "reset"]
        }
        
        # Entanglement patterns
        self.entanglement_patterns = {
            "linear": self._linear_entanglement,
            "full": self._full_entanglement,
            "star": self._star_entanglement,
            "grid": self._grid_entanglement,
            "random": self._random_entanglement
        }
    
    def _linear_entanglement(self, num_qubits: int) -> List[Tuple[int, int]]:
        """Generate linear entanglement pattern (each qubit connected to neighbors)"""
        return [(i, i+1) for i in range(num_qubits-1)]
    
    def _full_entanglement(self, num_qubits: int) -> List[Tuple[int, int]]:
        """Generate full entanglement pattern (all-to-all connections)"""
        return [(i, j) for i in range(num_qubits) for j in range(i+1, num_qubits)]
    
    def _star_entanglement(self, num_qubits: int) -> List[Tuple[int, int]]:
        """Generate star entanglement pattern (central qubit connected to all others)"""
        return [(0, i) for i in range(1, num_qubits)]
    
    def _grid_entanglement(self, num_qubits: int) -> List[Tuple[int, int]]:
        """Generate grid entanglement pattern (2D grid-like connections)"""
        # Calculate grid dimensions
        side = int(np.ceil(np.sqrt(num_qubits)))
        
        connections = []
        for i in range(num_qubits):
            row, col = i // side, i % side
            
            # Connect to right neighbor if exists
            if col < side - 1 and i + 1 < num_qubits:
                connections.append((i, i + 1))
            
            # Connect to bottom neighbor if exists
            if row < side - 1 and i + side < num_qubits:
                connections.append((i, i + side))
        
        return connections
    
    def _random_entanglement(self, num_qubits: int) -> List[Tuple[int, int]]:
        """Generate random entanglement pattern"""
        # Determine number of connections (between n-1 and n(n-1)/2)
        min_connections = num_qubits - 1
        max_connections = num_qubits * (num_qubits - 1) // 2
        
        num_connections = self.rng.randint(min_connections, max_connections + 1)
        
        # Generate random unique connections
        all_possible = [(i, j) for i in range(num_qubits) for j in range(i+1, num_qubits)]
        
        if num_connections >= len(all_possible):
            return all_possible
        
        return self.rng.choice(all_possible, size=num_connections, replace=False).tolist()
    
    def generate_circuit(self, workload: Dict) -> Dict:
        """Generate a quantum circuit based on workload profile"""
        # Extract parameters
        num_qubits = workload["required_qubits"]
        circuit_depth = workload["circuit_depth"]
        workload_type = workload["workload_type"]
        entanglement_pattern = workload.get("entanglement_pattern", "linear")
        
        # Get appropriate gate set
        gate_set = self.gate_sets.get(workload_type, self.gate_sets["OPTIMIZATION"])
        
        # Generate entanglement connections
        if entanglement_pattern in self.entanglement_patterns:
            connections = self.entanglement_patterns[entanglement_pattern](num_qubits)
        else:
            connections = self._linear_entanglement(num_qubits)
        
        # Generate circuit
        circuit = []
        
        # Initial layer - typically Hadamards for superposition
        for q in range(num_qubits):
            circuit.append({"gate": "h", "qubits": [q]})
        
        # Main circuit body
        for d in range(circuit_depth - 2):  # -2 for initial and final layers
            # Determine if this is an entanglement layer or single-qubit layer
            if d % 2 == 0:  # Even depths: entanglement layer
                # Select random subset of connections
                selected_connections = self.rng.choice(
                    connections, 
                    size=min(len(connections), num_qubits//2),
                    replace=False
                )
                
                for c in selected_connections:
                    # Choose a random 2-qubit gate
                    two_qubit_gates = [g for g in gate_set if g.startswith("c")]
                    if two_qubit_gates:
                        gate = self.rng.choice(two_qubit_gates)
                        circuit.append({"gate": gate, "qubits": list(c)})
            else:  # Odd depths: single-qubit layer
                for q in range(num_qubits):
                    # Choose a random 1-qubit gate
                    one_qubit_gates = [g for g in gate_set if not g.startswith("c")]
                    if one_qubit_gates:
                        gate = self.rng.choice(one_qubit_gates)
                        
                        # Add parameters for rotation gates
                        if gate in ["rx", "ry", "rz", "p"]:
                            angle = self.rng.uniform(0, 2 * np.pi)
                            circuit.append({"gate": gate, "qubits": [q], "params": [angle]})
                        else:
                            circuit.append({"gate": gate, "qubits": [q]})
        
        # Final layer - measurements
        for q in range(num_qubits):
            circuit.append({"gate": "measure", "qubits": [q]})
        
        return {
            "workload_id": workload["workload_id"],
            "num_qubits": num_qubits,
            "circuit_depth": circuit_depth,
            "gates": circuit,
            "connections": connections,
            "shots": workload.get("measurement_count", 1000)
        }
```

### 3.4 Distribution Controller

```python
# distribution_controller.py
import time
import threading
import queue
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable

class WorkloadDistributionController:
    """Controls the distribution of workloads to the Quantum Resource Allocator"""
    
    def __init__(self, 
                 qra_client,  # Client for the Quantum Resource Allocator
                 seed: Optional[int] = None):
        """Initialize the workload distribution controller"""
        self.qra_client = qra_client
        self.rng = np.random.RandomState(seed if seed is not None else np.random.randint(0, 2**32))
        
        # Workload queue
        self.workload_queue = queue.PriorityQueue()
        
        # Distribution parameters
        self.distribution_rate = 10  # workloads per second
        self.burst_probability = 0.1  # probability of a burst
        self.burst_size_range = (10, 30)  # min/max workloads in a burst
        
        # Statistics
        self.stats = {
            "submitted": 0,
            "accepted": 0,
            "rejected": 0,
            "by_class": {
                "QW1": 0,
                "QW2": 0,
                "QW3": 0,
                "QW4": 0
            }
        }
        
        # Control flags
        self.running = False
        self.distribution_thread = None
    
    def enqueue_workload(self, workload: Dict, priority: Optional[float] = None) -> None:
        """Add a workload to the distribution queue"""
        # Use provided priority or extract from workload
        if priority is None:
            priority = -workload.get("priority_score", 0)  # Negative for priority queue
        
        self.workload_queue.put((priority, workload))
    
    def enqueue_workloads(self, workloads: List[Dict]) -> None:
        """Add multiple workloads to the distribution queue"""
        for workload in workloads:
            self.enqueue_workload(workload)
    
    def start_distribution(self, callback: Optional[Callable] = None) -> None:
        """Start the workload distribution process"""
        if self.running:
            return
        
        self.running = True
        self.distribution_thread = threading.Thread(
            target=self._distribution_loop,
            args=(callback,),
            daemon=True
        )
        self.distribution_thread.start()
    
    def stop_distribution(self) -> None:
        """Stop the workload distribution process"""
        self.running = False
        if self.distribution_thread:
            self.distribution_thread.join(timeout=2.0)
            self.distribution_thread = None
    
    def _distribution_loop(self, callback: Optional[Callable]) -> None:
        """Main distribution loop"""
        last_time = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - last_time
            
            # Determine how many workloads to distribute in this cycle
            base_count = int(self.distribution_rate * elapsed)
            
            # Check for burst
            if self.rng.random() < self.burst_probability * elapsed:
                burst_size = self.rng.randint(
                    self.burst_size_range[0],
                    self.burst_size_range[1] + 1
                )
                base_count += burst_size
            
            # Distribute workloads
            for _ in range(base_count):
                if self.workload_queue.empty():
                    break
                
                _, workload = self.workload_queue.get()
                self._submit_workload(workload)
                
                # Call the callback if provided
                if callback:
                    callback(workload)
            
            # Update last time
            last_time = current_time
            
            # Sleep to prevent CPU hogging
            time.sleep(0.1)
    
    def _submit_workload(self, workload: Dict) -> bool:
        """Submit a workload to the Quantum Resource Allocator"""
        try:
            # Submit to QRA
            result = self.qra_client.register_workload(workload)
            
            # Update statistics
            self.stats["submitted"] += 1
            
            if result.get("accepted", False):
                self.stats["accepted"] += 1
                class_type = workload.get("class_type", "QW4")
                self.stats["by_class"][class_type] += 1
                return True
            else:
                self.stats["rejected"] += 1
                return False
                
        except Exception as e:
            print(f"Error submitting workload: {e}")
            self.stats["rejected"] += 1
            return False
    
    def get_statistics(self) -> Dict:
        """Get distribution statistics"""
        return self.stats
```

## 4. Workload Generator Framework

```python
# workload_generator_framework.py
import time
import threading
import json
import os
from typing import Dict, List, Optional, Tuple, Any

from flight_scenario_generator import FlightScenarioGenerator, FlightScenario
from quantum_workload_generator import QuantumWorkloadGenerator
from quantum_circuit_generator import QuantumCircuitGenerator
from distribution_controller import WorkloadDistributionController

class WorkloadGeneratorFramework:
    """Framework for generating and distributing realistic quantum workloads"""
    
    def __init__(self, 
                 qra_client,  # Client for the Quantum Resource Allocator
                 config_file: Optional[str] = None,
                 seed: Optional[int] = None):
        """Initialize the workload generator framework"""
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Initialize components with consistent seeds for reproducibility
        base_seed = seed if seed is not None else int(time.time())
        
        self.flight_scenario_gen = FlightScenarioGenerator(seed=base_seed)
        self.workload_gen = QuantumWorkloadGenerator(seed=base_seed + 1)
        self.circuit_gen = QuantumCircuitGenerator(seed=base_seed + 2)
        self.distribution_ctrl = WorkloadDistributionController(
            qra_client=qra_client,
            seed=base_seed + 3
        )
        
        # Active flight scenario
        self.flight_scenario = None
        
        # Control flags
        self.running = False
        self.simulation_thread = None
        
        # Statistics
        self.stats = {
            "simulation_time": 0,
            "flight_phase_changes": 0,
            "workloads_generated": 0,
            "workloads_by_class": {
                "QW1": 0,
                "QW2": 0,
                "QW3": 0,
                "QW4": 0
            }
        }
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "simulation": {
                "time_step_minutes": 1.0,
                "acceleration_factor": 60.0,  # 60x real-time
                "workload_generation_rate": {
                    "min": 5,
                    "max": 15
                }
            },
            "distribution": {
                "rate": 10,  # workloads per second
                "burst_probability": 0.1,
                "burst_size": {
                    "min": 10,
                    "max": 30
                }
            },
            "scenarios": {
                "default_duration_minutes": 120,
                "emergency_probability": 0.001
            }
        }
        
        if not config_file or not os.path.exists(config_file):
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            # Merge with defaults for any missing values
            for section in default_config:
                if section not in config:
                    config[section] = default_config[section]
                elif isinstance(default_config[section], dict):
                    for key in default_config[section]:
                        if key not in config[section]:
                            config[section][key] = default_config[section][key]
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return default_config
    
    def start_simulation(self, scenario: Optional[FlightScenario] = None) -> None:
        """Start the workload generation simulation"""
        if self.running:
            return
        
        # Create a new scenario if none provided
        if not scenario:
            scenario = self.flight_scenario_gen.generate_scenario()
        
        self.flight_scenario = scenario
        
        # Configure distribution controller
        dist_config = self.config["distribution"]
        self.distribution_ctrl.distribution_rate = dist_config["rate"]
        self.distribution_ctrl.burst_probability = dist_config["burst_probability"]
        self.distribution_ctrl.burst_size_range = (
            dist_config["burst_size"]["min"],
            dist_config["burst_size"]["max"]
        )
        
        # Start distribution
        self.distribution_ctrl.start_distribution(
            callback=self._workload_submitted_callback
        )
        
        # Start simulation
        self.running = True
        self.simulation_thread = threading.Thread(
            target=self._simulation_loop,
            daemon=True
        )
        self.simulation_thread.start()
        
        print(f"Started simulation for flight {scenario.flight_id} "
              f"from {scenario.departure} to {scenario.destination}")
    
    def stop_simulation(self) -> None:
        """Stop the workload generation simulation"""
        self.running = False
        
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2.0)
            self.simulation_thread = None
        
        self.distribution_ctrl.stop_distribution()
        
        print("Simulation stopped")
    
    def _simulation_loop(self) -> None:
        """Main simulation loop"""
        sim_config = self.config["simulation"]
        time_step_minutes = sim_config["time_step_minutes"]
        acceleration_factor = sim_config["acceleration_factor"]
        
        last_phase = self.flight_scenario.current_phase
        
        while self.running:
            # Advance flight scenario
            flight_state = self.flight_scenario.advance_time(time_step_minutes)
            
            # Check for phase change
            if self.flight_scenario.current_phase != last_phase:
                self.stats["flight_phase_changes"] += 1
                last_phase = self.flight_scenario.current_phase
                print(f"Flight phase changed to: {last_phase.name}")
            
            # Generate workloads for current state
            workloads = self.workload_gen.generate_workloads_for_state(
                flight_state,
                count_range=(
                    sim_config["workload_generation_rate"]["min"],
                    sim_config["workload_generation_rate"]["max"]
                )
            )
            
            # Generate circuits for workloads
            for workload in workloads:
                workload_dict = workload.to_dict()
                circuit = self.circuit_gen.generate_circuit(workload_dict)
                
                # Add circuit to workload
                workload_dict["circuit"] = circuit
                
                # Update statistics
                self.stats["workloads_generated"] += 1
                self.stats["workloads_by_class"][workload_dict["class_type"]] += 1
                
                # Queue for distribution
                self.distribution_ctrl.enqueue_workload(workload_dict)
            
            # Update simulation time
            self.stats["simulation_time"] += time_step_minutes
            
            # Sleep based on acceleration factor
            real_time_sleep = (time_step_minutes * 60) / acceleration_factor
            time.sleep(real_time_sleep)
    
    def _workload_submitted_callback(self, workload: Dict) -> None:
        """Callback when a workload is submitted"""
        # This could be used for logging, monitoring, etc.
        pass
    
    def get_statistics(self) -> Dict:
        """Get combined statistics"""
        stats = {
            "simulation": self.stats,
            "distribution": self.distribution_ctrl.get_statistics()
        }
        
        if self.flight_scenario:
            stats["flight"] = self.flight_scenario.get_current_state()
        
        return stats
    
    def generate_test_suite(self, 
                           name: str, 
                           num_scenarios: int = 5,
                           output_dir: str = "./test_suites") -> str:
        """Generate a test suite with multiple scenarios and save to disk"""
        os.makedirs(output_dir, exist_ok=True)
        
        suite_dir = os.path.join(output_dir, name)
        os.makedirs(suite_dir, exist_ok=True)
        
        suite_info = {
            "name": name,
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scenarios": []
        }
        
        # Generate scenarios
        for i in range(num_scenarios):
            scenario = self.flight_scenario_gen.generate_scenario()
            
            # Generate workloads for key flight phases
            scenario_workloads = []
            
            for phase in ["PREFLIGHT", "TAKEOFF", "CRUISE", "LANDING"]:
                # Create a state for this phase
                state = scenario.get_current_state()
                state["flight_phase"] = phase
                
                # Generate workloads
                workloads = self.workload_gen.generate_workloads_for_state(
                    state, count_range=(10, 20)
                )
                
                for workload in workloads:
                    workload_dict = workload.to_dict()
                    circuit = self.circuit_gen.generate_circuit(workload_dict)
                    workload_dict["circuit"] = circuit
                    scenario_workloads.append(workload_dict)
            
            # Save scenario and workloads
            scenario_info = {
                "id": f"scenario_{i+1}",
                "flight_id": scenario.flight_id,
                "departure": scenario.departure,
                "destination": scenario.destination,
                "duration_minutes": scenario.duration_minutes,
                "passenger_count": scenario.passenger_count,
                "cargo_weight_kg": scenario.cargo_weight_kg
            }
            
            suite_info["scenarios"].append(scenario_info)
            
            # Save workloads
            workloads_file = os.path.join(suite_dir, f"scenario_{i+1}_workloads.json")
            with open(workloads_file, 'w') as f:
                json.dump(scenario_workloads, f, indent=2)
        
        # Save suite info
        suite_file = os.path.join(suite_dir, "suite_info.json")
        with open(suite_file, 'w') as f:
            json.dump(suite_info, f, indent=2)
        
        return suite_dir
```

## 5. Predefined Test Workload Suites

### 5.1 Normal Operation Suite

```python
# generate_normal_operation_suite.py
import os
import json
from workload_generator_framework import WorkloadGeneratorFramework

def generate_normal_operation_suite(output_dir: str = "./test_suites"):
    """Generate a test suite for normal aircraft operation"""
    # Create a mock QRA client for standalone generation
    class MockQRAClient:
        def register_workload(self, workload):
            return {"accepted": True}
    
    # Initialize the framework
    framework = WorkloadGeneratorFramework(
        qra_client=MockQRAClient(),
        seed=12345  # Fixed seed for reproducibility
    )
    
    # Generate the test suite
    suite_dir = framework.generate_test_suite(
        name="normal_operation",
        num_scenarios=5,
        output_dir=output_dir
    )
    
    # Add suite metadata
    metadata = {
        "name": "Normal Operation Test Suite",
        "description": "Realistic workloads for normal aircraft operation",
        "version": "1.0.0",
        "workload_count": {
            "total": 0,
            "by_class": {
                "QW1": 0,
                "QW2": 0,
                "QW3": 0,
                "QW4": 0
            }
        }
    }
    
    # Count workloads by class
    for scenario_id in range(1, 6):
        workloads_file = os.path.join(suite_dir, f"scenario_{scenario_id}_workloads.json")
        with open(workloads_file, 'r') as f:
            workloads = json.load(f)
            
        metadata["workload_count"]["total"] += len(workloads)
        
        for workload in workloads:
            metadata["workload_count"]["by_class"][workload["class_type"]] += 1
    
    # Save metadata
    metadata_file = os.path.join(suite_dir, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Generated normal operation test suite at {suite_dir}")
    print(f"Total workloads: {metadata['workload_count']['total']}")
    
    return suite_dir

if __name__ == "__main__":
    generate_normal_operation_suite()
```

### 5.2 Emergency Scenarios Suite

```python
# generate_emergency_suite.py
import os
import json
import random
from workload_generator_framework import WorkloadGeneratorFramework
from flight_scenario_generator import FlightScenario, FlightPhase, WeatherCondition

def generate_emergency_suite(output_dir: str = "./test_suites"):
    """Generate a test suite for emergency scenarios"""
    # Create a mock QRA client for standalone generation
    class MockQRAClient:
        def register_workload(self, workload):
            return {"accepted": True}
    
    # Initialize the framework
    framework = WorkloadGeneratorFramework(
        qra_client=MockQRAClient(),
        seed=54321  # Fixed seed for reproducibility
    )
    
    # Create directory
    suite_name = "emergency_scenarios"
    suite_dir = os.path.join(output_dir, suite_name)
    os.makedirs(suite_dir, exist_ok=True)
    
    suite_info = {
        "name": suite_name,
        "created": "2025-05-26 14:30:00",
        "scenarios": []
    }
    
    # Define emergency scenarios
    emergency_scenarios = [
        {
            "name": "engine_failure",
            "description": "Simulates engine failure during cruise",
            "phase": FlightPhase.CRUISE,
            "failing_system": "propulsion",
            "health_reduction": 0.7
        },
        {
            "name": "navigation_failure",
            "description": "Simulates navigation system failure during cruise",
            "phase": FlightPhase.CRUISE,
            "failing_system": "navigation",
            "health_reduction": 0.6
        },
        {
            "name": "severe_turbulence",
            "description": "Simulates severe turbulence during cruise",
            "phase": FlightPhase.CRUISE,
            "weather": WeatherCondition.TURBULENCE,
            "failing_system": None,
            "health_reduction": 0.0
        },
        {
            "name": "hydraulic_failure",
            "description": "Simulates hydraulic system failure during descent",
            "phase": FlightPhase.DESCENT,
            "failing_system": "flight_control",
            "health_reduction": 0.5
        },
        {
            "name": "communications_failure",
            "description": "Simulates communications failure during approach",
            "phase": FlightPhase.APPROACH,
            "failing_system": "communications",
            "health_reduction": 0.8
        }
    ]
    
    # Generate scenarios
    for i, emergency in enumerate(emergency_scenarios):
        # Create base scenario
        scenario = framework.flight_scenario_gen.generate_scenario()
        
        # Set to emergency phase
        scenario.current_phase = emergency["phase"]
        
        # Apply emergency conditions
        if emergency["failing_system"]:
            scenario.system_status[emergency["failing_system"]]["health"] *= emergency["health_reduction"]
        
        if "weather" in emergency:
            scenario.weather_conditions = emergency["weather"]
        
        # Get current state
        state = scenario.get_current_state()
        state["flight_phase"] = "EMERGENCY"
        
        # Generate emergency workloads
        workloads = framework.workload_gen.generate_workloads_for_state(
            state, count_range=(20, 30)  # More workloads for emergency
        )
        
        # Process workloads
        scenario_workloads = []
        for workload in workloads:
            workload_dict = workload.to_dict()
            circuit = framework.circuit_gen.generate_circuit(workload_dict)
            workload_dict["circuit"] = circuit
            scenario_workloads.append(workload_dict)
        
        # Save scenario info
        scenario_info = {
            "id": f"emergency_{i+1}",
            "name": emergency["name"],
            "description": emergency["description"],
            "flight_id": scenario.flight_id,
            "flight_phase": "EMERGENCY",
            "failing_system": emergency["failing_system"],
            "workload_count": len(scenario_workloads)
        }
        
        suite_info["scenarios"].append(scenario_info)
        
        # Save workloads
        workloads_file = os.path.join(suite_dir, f"emergency_{i+1}_workloads.json")
        with open(workloads_file, 'w') as f:
            json.dump(scenario_workloads, f, indent=2)
    
    # Save suite info
    suite_file = os.path.join(suite_dir, "suite_info.json")
    with open(suite_file, 'w') as f:
        json.dump(suite_info, f, indent=2)
    
    # Add metadata
    metadata = {
        "name": "Emergency Scenarios Test Suite",
        "description": "Realistic workloads for aircraft emergency situations",
        "version": "1.0.0",
        "emergency_types": [e["name"] for e in emergency_scenarios],
        "priority_distribution": {
            "critical": "60-70%",
            "essential": "20-30%",
            "standard": "5-10%",
            "background": "0-5%"
        }
    }
    
    metadata_file = os.path.join(suite_dir, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Generated emergency scenarios test suite at {suite_dir}")
    
    return suite_dir
```

### 5.3 Performance Stress Test Suite

```python
# generate_stress_test_suite.py
import os
import json
import random
import numpy as np
from workload_generator_framework import WorkloadGeneratorFramework

def generate_stress_test_suite(output_dir: str = "./test_suites"):
    """Generate a test suite for performance stress testing"""
    # Create a mock QRA client for standalone generation
    class MockQRAClient:
        def register_workload(self, workload):
            return {"accepted": True}
    
    # Initialize the framework
    framework = WorkloadGeneratorFramework(
        qra_client=MockQRAClient(),
        seed=98765  # Fixed seed for reproducibility
    )
    
    # Create directory
    suite_name = "performance_stress_test"
    suite_dir = os.path.join(output_dir, suite_name)
    os.makedirs(suite_dir, exist_ok=True)
    
    # Define stress test patterns
    stress_patterns = [
        {
            "name": "high_volume",
            _patterns = [
        {
            "name": "high_volume",
            "description": "High volume of workloads across all classes",
            "workload_count": 500,
            "class_distribution": {
                "QW1": 0.15,  # 15% critical
                "QW2": 0.25,  # 25% essential
                "QW3": 0.35,  # 35% standard
                "QW4": 0.25   # 25% background
            },
            "submission_pattern": "burst",  # All at once
            "qubit_range": (8, 24)  # Range of qubits per workload
        },
        {
            "name": "critical_heavy",
            "description": "Heavy load of critical workloads",
            "workload_count": 300,
            "class_distribution": {
                "QW1": 0.60,  # 60% critical
                "QW2": 0.30,  # 30% essential
                "QW3": 0.08,  # 8% standard
                "QW4": 0.02   # 2% background
            },
            "submission_pattern": "rapid",  # Fast sequential
            "qubit_range": (12, 20)  # Range of qubits per workload
        },
        {
            "name": "resource_intensive",
            "description": "Fewer but resource-intensive workloads",
            "workload_count": 100,
            "class_distribution": {
                "QW1": 0.20,  # 20% critical
                "QW2": 0.30,  # 30% essential
                "QW3": 0.30,  # 30% standard
                "QW4": 0.20   # 20% background
            },
            "submission_pattern": "steady",  # Steady stream
            "qubit_range": (20, 32)  # Range of qubits per workload
        },
        {
            "name": "mixed_priority",
            "description": "Rapidly changing priority workloads",
            "workload_count": 400,
            "class_distribution": {
                "QW1": 0.25,  # 25% critical
                "QW2": 0.25,  # 25% essential
                "QW3": 0.25,  # 25% standard
                "QW4": 0.25   # 25% background
            },
            "submission_pattern": "oscillating",  # Alternating bursts
            "qubit_range": (8, 16)  # Range of qubits per workload
        },
        {
            "name": "deadline_pressure",
            "description": "Workloads with tight deadlines",
            "workload_count": 250,
            "class_distribution": {
                "QW1": 0.40,  # 40% critical
                "QW2": 0.40,  # 40% essential
                "QW3": 0.15,  # 15% standard
                "QW4": 0.05   # 5% background
            },
            "submission_pattern": "steady",  # Steady stream
            "qubit_range": (10, 18),  # Range of qubits per workload
            "deadline_factor": 0.5  # Tighter deadlines (multiplier)
        }
    ]
    
    suite_info = {
        "name": suite_name,
        "created": "2025-05-26 15:45:00",
        "patterns": [p["name"] for p in stress_patterns],
        "description": "Performance stress test suite for the Quantum Resource Allocator"
    }
    
    # Generate workloads for each pattern
    rng = np.random.RandomState(98765)  # Fixed seed for reproducibility
    
    for i, pattern in enumerate(stress_patterns):
        pattern_workloads = []
        
        # Generate workloads
        for _ in range(pattern["workload_count"]):
            # Determine workload class
            r = rng.random()
            cumulative = 0
            workload_class = "QW4"  # Default
            
            for cls, prob in pattern["class_distribution"].items():
                cumulative += prob
                if r <= cumulative:
                    workload_class = cls
                    break
            
            # Create base state for workload generation
            state = {
                "flight_phase": "CRUISE",
                "system_status": {
                    "flight_control": 1.0,
                    "navigation": 1.0,
                    "propulsion": 1.0,
                    "environmental": 1.0,
                    "communications": 1.0,
                    "power": 1.0,
                    "quantum": 1.0
                }
            }
            
            # Generate a workload
            workload = None
            while not workload:
                # Try different systems until we get a workload of the desired class
                system = rng.choice(list(state["system_status"].keys()))
                temp_workload = framework.workload_gen.generate_workload(state, system)
                
                if temp_workload and temp_workload.class_type.name == workload_class:
                    workload = temp_workload
            
            # Adjust qubit requirements to match pattern
            min_qubits, max_qubits = pattern["qubit_range"]
            workload.required_qubits = rng.randint(min_qubits, max_qubits + 1)
            
            # Adjust deadline if specified
            if "deadline_factor" in pattern and workload.deadline_ms:
                workload.deadline_ms = int(workload.deadline_ms * pattern["deadline_factor"])
            
            # Generate circuit
            workload_dict = workload.to_dict()
            circuit = framework.circuit_gen.generate_circuit(workload_dict)
            workload_dict["circuit"] = circuit
            
            pattern_workloads.append(workload_dict)
        
        # Save workloads
        workloads_file = os.path.join(suite_dir, f"{pattern['name']}_workloads.json")
        with open(workloads_file, 'w') as f:
            json.dump(pattern_workloads, f, indent=2)
        
        # Add pattern info
        pattern_info = {
            "id": f"pattern_{i+1}",
            "name": pattern["name"],
            "description": pattern["description"],
            "workload_count": len(pattern_workloads),
            "submission_pattern": pattern["submission_pattern"]
        }
        
        if "suite_patterns" not in suite_info:
            suite_info["suite_patterns"] = []
        
        suite_info["suite_patterns"].append(pattern_info)
    
    # Save suite info
    suite_file = os.path.join(suite_dir, "suite_info.json")
    with open(suite_file, 'w') as f:
        json.dump(suite_info, f, indent=2)
    
    # Add metadata
    metadata = {
        "name": "Performance Stress Test Suite",
        "description": "Stress test patterns for the Quantum Resource Allocator",
        "version": "1.0.0",
        "total_workloads": sum(p["workload_count"] for p in stress_patterns),
        "usage_instructions": "Use with qaos-test-runner --stress-test --pattern=[pattern_name]"
    }
    
    metadata_file = os.path.join(suite_dir, "metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Generated performance stress test suite at {suite_dir}")
    
    return suite_dir

if __name__ == "__main__":
    generate_stress_test_suite()
```

## 6. Usage Examples

### 6.1 Basic Usage

```python
# basic_usage.py
from workload_generator_framework import WorkloadGeneratorFramework

# Create a client for your Quantum Resource Allocator
class QRAClient:
    def register_workload(self, workload):
        # In a real implementation, this would send the workload to the QRA
        print(f"Registering workload {workload['workload_id']} (Class: {workload['class_type']})")
        return {"accepted": True}

# Initialize the framework
framework = WorkloadGeneratorFramework(
    qra_client=QRAClient(),
    config_file="config.json"  # Optional
)

# Start the simulation
framework.start_simulation()

# Let it run for a while
import time
time.sleep(60)  # Run for 60 seconds

# Stop the simulation
framework.stop_simulation()

# Get statistics
stats = framework.get_statistics()
print(f"Simulation time: {stats['simulation']['simulation_time']} minutes")
print(f"Workloads generated: {stats['simulation']['workloads_generated']}")
print(f"Workloads by class: {stats['simulation']['workloads_by_class']}")
```

### 6.2 Test Suite Generation

```python
# generate_test_suites.py
import os
from generate_normal_operation_suite import generate_normal_operation_suite
from generate_emergency_suite import generate_emergency_suite
from generate_stress_test_suite import generate_stress_test_suite

def generate_all_test_suites(output_dir: str = "./test_suites"):
    """Generate all test suites"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate suites
    normal_suite = generate_normal_operation_suite(output_dir)
    emergency_suite = generate_emergency_suite(output_dir)
    stress_suite = generate_stress_test_suite(output_dir)
    
    # Create index file
    index = {
        "test_suites": [
            {
                "name": "Normal Operation",
                "path": os.path.relpath(normal_suite, output_dir),
                "description": "Realistic workloads for normal aircraft operation"
            },
            {
                "name": "Emergency Scenarios",
                "path": os.path.relpath(emergency_suite, output_dir),
                "description": "Realistic workloads for aircraft emergency situations"
            },
            {
                "name": "Performance Stress Test",
                "path": os.path.relpath(stress_suite, output_dir),
                "description": "Stress test patterns for the Quantum Resource Allocator"
            }
        ],
        "usage": {
            "qaos-test-runner": "Use qaos-test-runner --suite=[suite_name] to run a test suite",
            "qaos-workload-player": "Use qaos-workload-player --file=[workload_file] to replay workloads"
        }
    }
    
    import json
    with open(os.path.join(output_dir, "index.json"), 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"Generated all test suites in {output_dir}")
    print("Available test suites:")
    for suite in index["test_suites"]:
        print(f"- {suite['name']}: {suite['description']}")

if __name__ == "__main__":
    generate_all_test_suites()
```

### 6.3 Running Tests with the Test Runner

```shellscript
#!/bin/bash
# run_tests.sh

# Set environment variables
export TEST_SUITES_DIR="/etc/ampel360/test-suites"
export RESULTS_DIR="/var/log/ampel360/test-results/$(date +%Y%m%d%H%M%S)"
export QRA_ENDPOINT="http://localhost:8080/api/v1"

# Create results directory
mkdir -p $RESULTS_DIR

# Function to run a test suite
run_test_suite() {
    local suite_name=$1
    local pattern=$2
    local options=$3
    
    echo "Running test suite: $suite_name"
    echo "Pattern: $pattern"
    echo "Options: $options"
    
    # Run the test
    qaos-test-runner \
        --suite $suite_name \
        --pattern $pattern \
        --endpoint $QRA_ENDPOINT \
        --results-dir $RESULTS_DIR/$suite_name \
        --report-format html,json \
        $options
    
    # Check result
    if [ $? -eq 0 ]; then
        echo "Test suite $suite_name completed successfully"
    else
        echo "Test suite $suite_name failed"
    fi
}

# Run normal operation tests
run_test_suite "normal_operation" "all" "--real-time-factor 10"

# Run emergency scenario tests
run_test_suite "emergency_scenarios" "all" "--priority-boost 1.5"

# Run stress tests
for pattern in "high_volume" "critical_heavy" "resource_intensive" "mixed_priority" "deadline_pressure"; do
    run_test_suite "performance_stress_test" $pattern "--stress-mode"
done

# Generate combined report
qaos-test-report \
    --results-dir $RESULTS_DIR \
    --output-dir $RESULTS_DIR/combined \
    --title "AMPEL360-BWB-Q100 QRA Test Results" \
    --include-charts \
    --include-recommendations

echo "All tests completed. Results available at $RESULTS_DIR/combined"
```

## 7. Integration with Test Framework

```python
# qaos_test_integration.py
import os
import json
import argparse
import time
from typing import Dict, List, Optional

class QAOSTestRunner:
    """Test runner for the QAOS workload generators"""
    
    def __init__(self, 
                 suite_dir: str,
                 qra_endpoint: str,
                 results_dir: str,
                 real_time_factor: float = 1.0):
        """Initialize the test runner"""
        self.suite_dir = suite_dir
        self.qra_endpoint = qra_endpoint
        self.results_dir = results_dir
        self.real_time_factor = real_time_factor
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Load suite info
        suite_info_path = os.path.join(suite_dir, "suite_info.json")
        if not os.path.exists(suite_info_path):
            raise ValueError(f"Suite info not found at {suite_info_path}")
        
        with open(suite_info_path, 'r') as f:
            self.suite_info = json.load(f)
        
        # Initialize QRA client
        self.qra_client = self._create_qra_client()
    
    def _create_qra_client(self):
        """Create a client for the Quantum Resource Allocator"""
        # In a real implementation, this would create a proper client
        # For this example, we'll use a simple mock
        class QRAClient:
            def __init__(self, endpoint):
                self.endpoint = endpoint
                self.submitted_workloads = 0
                self.accepted_workloads = 0
                self.rejected_workloads = 0
            
            def register_workload(self, workload):
                self.submitted_workloads += 1
                
                # Simulate some rejections based on resource availability
                if workload["required_qubits"] > 24:
                    self.rejected_workloads += 1
                    return {"accepted": False, "reason": "Insufficient qubits"}
                
                self.accepted_workloads += 1
                return {"accepted": True, "resource_id": f"QPU-{workload['class_type'][2:]}"}
            
            def get_stats(self):
                return {
                    "submitted": self.submitted_workloads,
                    "accepted": self.accepted_workloads,
                    "rejected": self.rejected_workloads,
                    "acceptance_rate": self.accepted_workloads / max(1, self.submitted_workloads)
                }
        
        return QRAClient(self.qra_endpoint)
    
    def run_scenario(self, scenario_id: str, pattern: Optional[str] = None) -> Dict:
        """Run a specific scenario from the test suite"""
        # Find the scenario info
        scenario_info = None
        for scenario in self.suite_info.get("scenarios", []):
            if scenario["id"] == scenario_id:
                scenario_info = scenario
                break
        
        if not scenario_info:
            for pattern_info in self.suite_info.get("suite_patterns", []):
                if pattern_info["id"] == scenario_id or pattern_info["name"] == scenario_id:
                    scenario_info = pattern_info
                    break
        
        if not scenario_info:
            raise ValueError(f"Scenario {scenario_id} not found in suite")
        
        # Load workloads
        workloads_file = None
        if "name" in scenario_info:
            workloads_file = os.path.join(self.suite_dir, f"{scenario_info['name']}_workloads.json")
        else:
            workloads_file = os.path.join(self.suite_dir, f"{scenario_id}_workloads.json")
        
        if not os.path.exists(workloads_file):
            raise ValueError(f"Workloads file not found at {workloads_file}")
        
        with open(workloads_file, 'r') as f:
            workloads = json.load(f)
        
        # Determine submission pattern
        submission_pattern = pattern or scenario_info.get("submission_pattern", "steady")
        
        # Run the scenario
        start_time = time.time()
        results = self._submit_workloads(workloads, submission_pattern)
        end_time = time.time()
        
        # Compile results
        scenario_results = {
            "scenario_id": scenario_id,
            "workload_count": len(workloads),
            "execution_time_s": end_time - start_time,
            "submission_pattern": submission_pattern,
            "qra_stats": self.qra_client.get_stats(),
            "workload_results": results
        }
        
        # Save results
        results_file = os.path.join(self.results_dir, f"{scenario_id}_results.json")
        with open(results_file, 'w') as f:
            json.dump(scenario_results, f, indent=2)
        
        return scenario_results
    
    def _submit_workloads(self, workloads: List[Dict], pattern: str) -> Dict:
        """Submit workloads according to the specified pattern"""
        results = {
            "submitted": 0,
            "accepted": 0,
            "rejected": 0,
            "by_class": {
                "QW1": {"submitted": 0, "accepted": 0},
                "QW2": {"submitted": 0, "accepted": 0},
                "QW3": {"submitted": 0, "accepted": 0},
                "QW4": {"submitted": 0, "accepted": 0}
            }
        }
        
        # Sort workloads by priority if needed
        if pattern in ["priority", "reverse_priority"]:
            workloads = sorted(workloads, 
                              key=lambda w: w.get("priority_score", 0),
                              reverse=(pattern == "priority"))
        
        # Determine submission timing
        if pattern == "burst":
            # Submit all at once
            for workload in workloads:
                self._submit_and_track(workload, results)
        
        elif pattern == "steady":
            # Submit at a steady rate
            rate = len(workloads) / 60  # Workloads per second
            interval = 1.0 / rate
            
            for workload in workloads:
                self._submit_and_track(workload, results)
                time.sleep(interval / self.real_time_factor)
        
        elif pattern == "oscillating":
            # Submit in alternating bursts
            burst_size = min(20, len(workloads) // 10)
            
            for i in range(0, len(workloads), burst_size):
                # Submit a burst
                for j in range(i, min(i + burst_size, len(workloads))):
                    self._submit_and_track(workloads[j], results)
                
                # Wait between bursts
                time.sleep(2.0 / self.real_time_factor)
        
        elif pattern == "rapid":
            # Submit quickly but not all at once
            for workload in workloads:
                self._submit_and_track(workload, results)
                time.sleep(0.01 / self.real_time_factor)
        
        else:
            # Default: steady submission
            for workload in workloads:
                self._submit_and_track(workload, results)
                time.sleep(0.1 / self.real_time_factor)
        
        return results
    
    def _submit_and_track(self, workload: Dict, results: Dict) -> None:
        """Submit a workload and track results"""
        # Submit to QRA
        response = self.qra_client.register_workload(workload)
        
        # Update statistics
        results["submitted"] += 1
        class_type = workload.get("class_type", "QW4")
        results["by_class"][class_type]["submitted"] += 1
        
        if response.get("accepted", False):
            results["accepted"] += 1
            results["by_class"][class_type]["accepted"] += 1
        else:
            results["rejected"] += 1
    
    def run_all_scenarios(self, pattern: Optional[str] = None) -> Dict:
        """Run all scenarios in the test suite"""
        all_results = {
            "suite_name": self.suite_info.get("name", "Unknown"),
            "scenarios": [],
            "summary": {
                "total_workloads": 0,
                "accepted_workloads": 0,
                "rejected_workloads": 0,
                "total_execution_time_s": 0
            }
        }
        
        # Run each scenario
        if "scenarios" in self.suite_info:
            for scenario in self.suite_info["scenarios"]:
                print(f"Running scenario {scenario['id']}...")
                result = self.run_scenario(scenario["id"], pattern)
                all_results["scenarios"].append(result)
                
                # Update summary
                all_results["summary"]["total_workloads"] += result["workload_count"]
                all_results["summary"]["accepted_workloads"] += result["qra_stats"]["accepted"]
                all_results["summary"]["rejected_workloads"] += result["qra_stats"]["rejected"]
                all_results["summary"]["total_execution_time_s"] += result["execution_time_s"]
        
        elif "suite_patterns" in self.suite_info:
            for pattern_info in self.suite_info["suite_patterns"]:
                print(f"Running pattern {pattern_info['name']}...")
                result = self.run_scenario(pattern_info["name"], pattern or pattern_info.get("submission_pattern"))
                all_results["scenarios"].append(result)
                
                # Update summary
                all_results["summary"]["total_workloads"] += result["workload_count"]
                all_results["summary"]["accepted_workloads"] += result["qra_stats"]["accepted"]
                all_results["summary"]["rejected_workloads"] += result["qra_stats"]["rejected"]
                all_results["summary"]["total_execution_time_s"] += result["execution_time_s"]
        
        # Calculate acceptance rate
        total = all_results["summary"]["total_workloads"]
        accepted = all_results["summary"]["accepted_workloads"]
        all_results["summary"]["acceptance_rate"] = accepted / max(1, total)
        
        # Save overall results
        results_file = os.path.join(self.results_dir, "all_results.json")
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        return all_results

def main():
    """Main function for the test runner"""
    parser = argparse.ArgumentParser(description="QAOS Test Runner")
    parser.add_argument("--suite", required=True, help="Path to test suite directory")
    parser.add_argument("--endpoint", default="http://localhost:8080/api/v1", help="QRA API endpoint")
    parser.add_argument("--results-dir", required=True, help="Directory for test results")
    parser.add_argument("--scenario", help="Specific scenario to run")
    parser.add_argument("--pattern", help="Submission pattern override")
    parser.add_argument("--real-time-factor", type=float, default=1.0, help="Real-time acceleration factor")
    
    args = parser.parse_args()
    
    # Create and run the test runner
    runner = QAOSTestRunner(
        suite_dir=args.suite,
        qra_endpoint=args.endpoint,
        results_dir=args.results_dir,
        real_time_factor=args.real_time_factor
    )
    
    if args.scenario:
        print(f"Running scenario {args.scenario}...")
        result = runner.run_scenario(args.scenario, args.pattern)
        print(f"Scenario completed. Acceptance rate: {result['qra_stats']['acceptance_rate']:.2%}")
    else:
        print("Running all scenarios...")
        results = runner.run_all_scenarios(args.pattern)
        print(f"All scenarios completed. Overall acceptance rate: {results['summary']['acceptance_rate']:.2%}")
    
    print(f"Results saved to {args.results_dir}")

if __name__ == "__main__":
    main()
```

This comprehensive workload generator framework provides realistic test workloads for the AMPEL360-BWB-Q100 Quantum Resource Allocator system. It simulates various flight scenarios, generates appropriate quantum workloads, and distributes them to the resource allocator for testing and validation.
