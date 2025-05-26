
```python
# qaos_master_ui.py
#!/usr/bin/env python3
"""
AMPEL360-BWB-Q100 Quantum Aerospace Operating System (QAOS) Master UI
=====================================================================

This module implements the master UI for the QAOS system, providing a comprehensive
interface for monitoring and controlling quantum resources, workloads, and system status.

Author: AMPEL360 Quantum Systems Team
Version: 0.9.0
Status: Pre-certification prototype
"""

import sys
import os
import time
import json
import logging
import threading
import datetime
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.animation as animation
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox, QTableWidget, 
                            QTableWidgetItem, QProgressBar, QFrame, QSplitter, QTextEdit, 
                            QGroupBox, QFormLayout, QLineEdit, QCheckBox, QSpinBox, 
                            QDoubleSpinBox, QFileDialog, QMessageBox, QStatusBar, QToolBar, 
                            QAction, QMenu, QSizePolicy, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QDateTime, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QDesktopServices

# Import QAOS modules
try:
    from qaos_client import QAOSClient, ResourceAllocationError
    from qaos_models import WorkloadClass, QuantumResource, QuantumWorkload
    from qaos_monitoring import SystemMonitor, ResourceMonitor, WorkloadMonitor
    from qaos_config import QAOSConfig
    from qaos_auth import QAOSAuth
    from qaos_diagnostics import QAOSDiagnostics
    from qaos_simulator import QAOSSimulator
except ImportError:
    # For development/demo purposes, create mock classes
    logging.warning("QAOS modules not found, using mock implementations")
    
    class WorkloadClass:
        QW1 = "QW1"  # Critical: Real-time safety-critical functions
        QW2 = "QW2"  # Essential: Core aircraft operations
        QW3 = "QW3"  # Standard: Regular operational functions
        QW4 = "QW4"  # Background: Non-time-critical functions
    
    class QuantumResource:
        def __init__(self, resource_id, qubits, coherence_time_us, error_rate, availability=1.0):
            self.resource_id = resource_id
            self.qubits = qubits
            self.coherence_time_us = coherence_time_us
            self.error_rate = error_rate
            self.availability = availability
            self.allocated = 0  # Percentage of resource allocated (0-100)
        
        def available_qubits(self):
            return int(self.qubits * (1 - self.allocated / 100))
    
    class QuantumWorkload:
        def __init__(self, workload_id, class_type, required_qubits, max_error_rate,
                    min_coherence_time_us, deadline_ms=None, preemptable=False):
            self.workload_id = workload_id
            self.class_type = class_type
            self.required_qubits = required_qubits
            self.max_error_rate = max_error_rate
            self.min_coherence_time_us = min_coherence_time_us
            self.deadline_ms = deadline_ms
            self.preemptable = preemptable
            self.allocated_resource = None
            self.priority_score = self._calculate_priority()
            self.status = "Pending"
            self.submission_time = datetime.datetime.now()
            self.completion_time = None
        
        def _calculate_priority(self):
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
    
    class QAOSClient:
        def __init__(self, endpoint="http://localhost:8080"):
            self.endpoint = endpoint
            self.resources = [
                QuantumResource("QPU-1", qubits=32, coherence_time_us=100, error_rate=0.001),
                QuantumResource("QPU-2", qubits=24, coherence_time_us=150, error_rate=0.0008),
                QuantumResource("QPU-3", qubits=16, coherence_time_us=200, error_rate=0.0005)
            ]
            self.workloads = []
            self.allocation_map = {}
            self.connected = True
        
        def get_resources(self):
            return self.resources
        
        def get_workloads(self):
            return self.workloads
        
        def get_allocation_map(self):
            return self.allocation_map
        
        def register_workload(self, workload):
            self.workloads.append(workload)
            return {"success": True, "message": "Workload registered"}
        
        def allocate_resources(self):
            # Mock allocation logic
            for workload in self.workloads:
                if workload.status == "Pending":
                    # Find a resource
                    for resource in self.resources:
                        if resource.available_qubits() >= workload.required_qubits:
                            # Allocate
                            allocation_percent = (workload.required_qubits / resource.qubits) * 100
                            resource.allocated += allocation_percent
                            self.allocation_map[workload.workload_id] = resource.resource_id
                            workload.status = "Running"
                            workload.allocated_resource = resource.resource_id
                            break
            
            return self.allocation_map
        
        def get_system_status(self):
            return {
                "status": "Operational",
                "uptime": "3d 12h 45m",
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "temperature": 36.5,
                "error_rate": 0.0012,
                "flight_phase": "CRUISE",
                "altitude": 10000,
                "speed": 850,
                "coordinates": "N48°51'12.28\", E2°20'55.68\"",
                "next_waypoint": "EGLL",
                "eta": "2h 15m"
            }
        
        def get_resource_metrics(self, resource_id):
            # Generate mock metrics
            return {
                "utilization": np.random.uniform(20, 80),
                "error_rate": np.random.uniform(0.0001, 0.002),
                "temperature": np.random.uniform(30, 40),
                "coherence_stability": np.random.uniform(90, 99),
                "gate_fidelity": np.random.uniform(95, 99.5),
                "readout_fidelity": np.random.uniform(94, 99),
                "historical_utilization": [np.random.uniform(20, 80) for _ in range(20)],
                "historical_error_rate": [np.random.uniform(0.0001, 0.002) for _ in range(20)]
            }
        
        def get_workload_metrics(self, workload_id=None):
            # Generate mock metrics
            if workload_id:
                return {
                    "execution_time": np.random.uniform(10, 1000),
                    "qubits_used": np.random.randint(4, 24),
                    "circuit_depth": np.random.randint(50, 500),
                    "gate_count": np.random.randint(100, 2000),
                    "error_probability": np.random.uniform(0.001, 0.1),
                    "success_probability": np.random.uniform(0.7, 0.99)
                }
            else:
                return {
                    "total_workloads": len(self.workloads),
                    "running_workloads": sum(1 for w in self.workloads if w.status == "Running"),
                    "completed_workloads": sum(1 for w in self.workloads if w.status == "Completed"),
                    "failed_workloads": sum(1 for w in self.workloads if w.status == "Failed"),
                    "average_execution_time": np.random.uniform(100, 500),
                    "workloads_by_class": {
                        "QW1": sum(1 for w in self.workloads if w.class_type == WorkloadClass.QW1),
                        "QW2": sum(1 for w in self.workloads if w.class_type == WorkloadClass.QW2),
                        "QW3": sum(1 for w in self.workloads if w.class_type == WorkloadClass.QW3),
                        "QW4": sum(1 for w in self.workloads if w.class_type == WorkloadClass.QW4)
                    }
                }
    
    class SystemMonitor:
        def __init__(self, client):
            self.client = client
        
        def get_system_status(self):
            return self.client.get_system_status()
    
    class ResourceMonitor:
        def __init__(self, client):
            self.client = client
        
        def get_resources(self):
            return self.client.get_resources()
        
        def get_resource_metrics(self, resource_id):
            return self.client.get_resource_metrics(resource_id)
    
    class WorkloadMonitor:
        def __init__(self, client):
            self.client = client
        
        def get_workloads(self):
            return self.client.get_workloads()
        
        def get_workload_metrics(self, workload_id=None):
            return self.client.get_workload_metrics(workload_id)
    
    class QAOSConfig:
        def __init__(self):
            self.config = {
                "endpoint": "http://localhost:8080",
                "refresh_interval": 5,
                "log_level": "INFO",
                "theme": "dark",
                "auto_allocate": True,
                "allocation_interval": 10,
                "show_advanced_metrics": True,
                "alert_thresholds": {
                    "cpu_usage": 90,
                    "memory_usage": 85,
                    "temperature": 45,
                    "error_rate": 0.01
                }
            }
        
        def get(self, key, default=None):
            return self.config.get(key, default)
        
        def set(self, key, value):
            self.config[key] = value
            return True
        
        def save(self, filename=None):
            return True
        
        def load(self, filename=None):
            return True
    
    class QAOSAuth:
        def __init__(self):
            self.authenticated = False
            self.username = None
            self.role = None
        
        def login(self, username, password):
            self.authenticated = True
            self.username = username
            self.role = "admin" if username == "admin" else "operator"
            return True
        
        def logout(self):
            self.authenticated = False
            self.username = None
            self.role = None
            return True
        
        def is_authenticated(self):
            return self.authenticated
        
        def get_username(self):
            return self.username
        
        def get_role(self):
            return self.role
    
    class QAOSDiagnostics:
        def __init__(self, client):
            self.client = client
        
        def run_diagnostics(self, resource_id=None):
            return {
                "status": "passed",
                "tests_run": 12,
                "tests_passed": 12,
                "tests_failed": 0,
                "details": [
                    {"name": "Connectivity Test", "status": "passed", "message": "All systems connected"},
                    {"name": "Resource Health Check", "status": "passed", "message": "All resources operational"},
                    {"name": "Calibration Test", "status": "passed", "message": "Calibration within parameters"},
                    {"name": "Error Correction Test", "status": "passed", "message": "Error correction functioning normally"}
                ]
            }
        
        def get_logs(self, count=100):
            return [
                {"timestamp": "2025-05-26T10:15:23", "level": "INFO", "message": "System startup complete"},
                {"timestamp": "2025-05-26T10:15:25", "level": "INFO", "message": "Resource QPU-1 initialized"},
                {"timestamp": "2025-05-26T10:15:26", "level": "INFO", "message": "Resource QPU-2 initialized"},
                {"timestamp": "2025-05-26T10:15:27", "level": "INFO", "message": "Resource QPU-3 initialized"},
                {"timestamp": "2025-05-26T10:15:30", "level": "INFO", "message": "Workload scheduler started"},
                {"timestamp": "2025-05-26T10:16:05", "level": "INFO", "message": "Allocated workload flight-control-optimization to QPU-1"},
                {"timestamp": "2025-05-26T10:16:10", "level": "INFO", "message": "Allocated workload collision-avoidance to QPU-2"},
                {"timestamp": "2025-05-26T10:16:15", "level": "WARNING", "message": "High error rate detected on QPU-3, initiating recalibration"},
                {"timestamp": "2025-05-26T10:16:45", "level": "INFO", "message": "QPU-3 recalibration complete, error rate normalized"},
                {"timestamp": "2025-05-26T10:17:00", "level": "INFO", "message": "Allocated workload energy-distribution to QPU-3"}
            ]
    
    class QAOSSimulator:
        def __init__(self):
            self.running = False
            self.scenario = None
        
        def load_scenario(self, scenario_file):
            self.scenario = "Standard Flight Scenario"
            return True
        
        def start_simulation(self):
            self.running = True
            return True
        
        def stop_simulation(self):
            self.running = False
            return True
        
        def is_running(self):
            return self.running
        
        def get_available_scenarios(self):
            return [
                "Standard Flight Scenario",
                "Emergency Landing Scenario",
                "Turbulence Response Scenario",
                "System Failure Scenario",
                "High Workload Scenario"
            ]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("qaos_master_ui")

class MatplotlibCanvas(FigureCanvas):
    """Matplotlib canvas for embedding plots in Qt"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(self.fig)
        self.setParent(parent)
        
        FigureCanvas.setSizePolicy(self,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class ResourceUtilizationChart(MatplotlibCanvas):
    """Chart showing resource utilization over time"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(ResourceUtilizationChart, self).__init__(parent, width, height, dpi)
        self.resource_data = {}
        self.time_points = list(range(20))  # Last 20 time points
        
        # Set up the plot
        self.axes.set_title('Quantum Resource Utilization')
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Utilization (%)')
        self.axes.set_ylim(0, 100)
        self.axes.grid(True)
        
        # Create empty lines for each resource
        self.lines = {}
        
        # Add legend
        self.axes.legend(loc='upper right')
        
        self.fig.tight_layout()
    
    def update_data(self, resources):
        """Update chart with new resource data"""
        # Add new resources if needed
        for resource in resources:
            resource_id = resource.resource_id
            if resource_id not in self.resource_data:
                self.resource_data[resource_id] = [0] * len(self.time_points)
                self.lines[resource_id], = self.axes.plot(
                    self.time_points, 
                    self.resource_data[resource_id],
                    label=resource_id
                )
        
        # Update data for each resource
        for resource in resources:
            resource_id = resource.resource_id
            # Shift data and add new point
            self.resource_data[resource_id] = self.resource_data[resource_id][1:] + [resource.allocated]
            self.lines[resource_id].set_ydata(self.resource_data[resource_id])
        
        # Update legend
        self.axes.legend(loc='upper right')
        
        self.draw()

class WorkloadClassDistributionChart(MatplotlibCanvas):
    """Pie chart showing distribution of workloads by class"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(WorkloadClassDistributionChart, self).__init__(parent, width, height, dpi)
        
        # Set up the plot
        self.axes.set_title('Workload Class Distribution')
        
        # Initial empty plot
        self.update_data({
            WorkloadClass.QW1: 0,
            WorkloadClass.QW2: 0,
            WorkloadClass.QW3: 0,
            WorkloadClass.QW4: 0
        })
    
    def update_data(self, class_counts):
        """Update chart with new workload class distribution"""
        self.axes.clear()
        self.axes.set_title('Workload Class Distribution')
        
        labels = list(class_counts.keys())
        sizes = list(class_counts.values())
        
        if sum(sizes) > 0:
            # Colors for each class
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
            
            # Create pie chart
            self.axes.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                         shadow=True, startangle=90)
            self.axes.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        else:
            self.axes.text(0.5, 0.5, 'No workloads', horizontalalignment='center',
                          verticalalignment='center', transform=self.axes.transAxes)
        
        self.draw()

class ErrorRateChart(MatplotlibCanvas):
    """Line chart showing error rates over time"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(ErrorRateChart, self).__init__(parent, width, height, dpi)
        self.resource_data = {}
        self.time_points = list(range(20))  # Last 20 time points
        
        # Set up the plot
        self.axes.set_title('Quantum Error Rates')
        self.axes.set_xlabel('Time')
        self.axes.set_ylabel('Error Rate')
        self.axes.set_ylim(0, 0.01)
        self.axes.grid(True)
        
        # Create empty lines for each resource
        self.lines = {}
        
        # Add legend
        self.axes.legend(loc='upper right')
        
        self.fig.tight_layout()
    
    def update_data(self, resource_metrics):
        """Update chart with new error rate data"""
        # Add new resources if needed
        for resource_id, metrics in resource_metrics.items():
            if resource_id not in self.resource_data:
                self.resource_data[resource_id] = [0] * len(self.time_points)
                self.lines[resource_id], = self.axes.plot(
                    self.time_points, 
                    self.resource_data[resource_id],
                    label=resource_id
                )
        
        # Update data for each resource
        for resource_id, metrics in resource_metrics.items():
            # Shift data and add new point
            self.resource_data[resource_id] = self.resource_data[resource_id][1:] + [metrics['error_rate']]
            self.lines[resource_id].set_ydata(self.resource_data[resource_id])
        
        # Update legend
        self.axes.legend(loc='upper right')
        
        self.draw()

class WorkloadStatusChart(MatplotlibCanvas):
    """Stacked bar chart showing workload status counts"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        super(WorkloadStatusChart, self).__init__(parent, width, height, dpi)
        
        # Set up the plot
        self.axes.set_title('Workload Status')
        self.axes.set_xlabel('Status')
        self.axes.set_ylabel('Count')
        self.axes.grid(True, axis='y')
        
        # Initial empty plot
        self.update_data({
            'Pending': 0,
            'Running': 0,
            'Completed': 0,
            'Failed': 0
        })
    
    def update_data(self, status_counts):
        """Update chart with new workload status counts"""
        self.axes.clear()
        self.axes.set_title('Workload Status')
        self.axes.set_xlabel('Status')
        self.axes.set_ylabel('Count')
        self.axes.grid(True, axis='y')
        
        statuses = list(status_counts.keys())
        counts = list(status_counts.values())
        
        # Colors for each status
        colors = {
            'Pending': '#66b3ff',
            'Running': '#99ff99',
            'Completed': '#c2c2f0',
            'Failed': '#ff9999'
        }
        
        # Create bar chart
        bars = self.axes.bar(statuses, counts, color=[colors.get(s, '#cccccc') for s in statuses])
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                          f'{int(height)}', ha='center', va='bottom')
        
        self.draw()

class DataRefreshThread(QThread):
    """Thread for refreshing data from the QAOS system"""
    
    update_signal = pyqtSignal(dict)
    
    def __init__(self, client, config):
        super(DataRefreshThread, self).__init__()
        self.client = client
        self.config = config
        self.running = False
    
    def run(self):
        self.running = True
        
        while self.running:
            try:
                # Collect all data
                data = {}
                
                # System status
                data['system_status'] = self.client.get_system_status()
                
                # Resources
                data['resources'] = self.client.get_resources()
                
                # Resource metrics
                data['resource_metrics'] = {}
                for resource in data['resources']:
                    data['resource_metrics'][resource.resource_id] = self.client.get_resource_metrics(resource.resource_id)
                
                # Workloads
                data['workloads'] = self.client.get_workloads()
                
                # Workload metrics
                data['workload_metrics'] = self.client.get_workload_metrics()
                
                # Allocation map
                data['allocation_map'] = self.client.get_allocation_map()
                
                # Emit signal with all data
                self.update_signal.emit(data)
                
            except Exception as e:
                logger.error(f"Error refreshing data: {e}")
            
            # Sleep for refresh interval
            time.sleep(self.config.get('refresh_interval', 5))
    
    def stop(self):
        self.running = False

class QAOSMasterUI(QMainWindow):
    """Master UI for the QAOS system"""
    
    def __init__(self):
        super(QAOSMasterUI, self).__init__()
        
        # Initialize components
        self.config = QAOSConfig()
        self.auth = QAOSAuth()
        self.client = QAOSClient(self.config.get('endpoint', 'http://localhost:8080'))
        self.system_monitor = SystemMonitor(self.client)
        self.resource_monitor = ResourceMonitor(self.client)
        self.workload_monitor = WorkloadMonitor(self.client)
        self.diagnostics = QAOSDiagnostics(self.client)
        self.simulator = QAOSSimulator()
        
        # Set up UI
        self.setup_ui()
        
        # Start data refresh thread
        self.refresh_thread = DataRefreshThread(self.client, self.config)
        self.refresh_thread.update_signal.connect(self.update_data)
        self.refresh_thread.start()
        
        # Auto allocation timer
        self.allocation_timer = QTimer(self)
        self.allocation_timer.timeout.connect(self.auto_allocate_resources)
        if self.config.get('auto_allocate', True):
            self.allocation_timer.start(self.config.get('allocation_interval', 10) * 1000)
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("AMPEL360-BWB-Q100 QAOS Master UI")
        self.setGeometry(100, 100, 1280, 800)
        
        # Set up central widget with tab layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create tabs
        self.dashboard_tab = self.create_dashboard_tab()
        self.resources_tab = self.create_resources_tab()
        self.workloads_tab = self.create_workloads_tab()
        self.allocation_tab = self.create_allocation_tab()
        self.diagnostics_tab = self.create_diagnostics_tab()
        self.simulator_tab = self.create_simulator_tab()
        self.settings_tab = self.create_settings_tab()
        
        # Add tabs to central widget
        self.central_widget.addTab(self.dashboard_tab, "Dashboard")
        self.central_widget.addTab(self.resources_tab, "Resources")
        self.central_widget.addTab(self.workloads_tab, "Workloads")
        self.central_widget.addTab(self.allocation_tab, "Allocation")
        self.central_widget.addTab(self.diagnostics_tab, "Diagnostics")
        self.central_widget.addTab(self.simulator_tab, "Simulator")
        self.central_widget.addTab(self.settings_tab, "Settings")
        
        # Set up status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status bar elements
        self.connection_status_label = QLabel("Connected")
        self.connection_status_label.setStyleSheet("color: green;")
        self.status_bar.addPermanentWidget(self.connection_status_label)
        
        self.system_status_label = QLabel("System: Operational")
        self.status_bar.addPermanentWidget(self.system_status_label)
        
        self.flight_phase_label = QLabel("Flight Phase: CRUISE")
        self.status_bar.addPermanentWidget(self.flight_phase_label)
        
        self.user_label = QLabel("User: Admin")
        self.status_bar.addPermanentWidget(self.user_label)
        
        # Set up toolbar
        self.toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.toolbar)
        
        # Toolbar actions
        self.refresh_action = QAction(QIcon.fromTheme("view-refresh"), "Refresh", self)
        self.refresh_action.triggered.connect(self.manual_refresh)
        self.toolbar.addAction(self.refresh_action)
        
        self.allocate_action = QAction(QIcon.fromTheme("system-run"), "Allocate Resources", self)
        self.allocate_action.triggered.connect(self.manual_allocate_resources)
        self.toolbar.addAction(self.allocate_action)
        
        self.toolbar.addSeparator()
        
        self.help_action = QAction(QIcon.fromTheme("help-browser"), "Help", self)
        self.help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(self.help_action)
        
        # Apply theme
        self.apply_theme(self.config.get('theme', 'light'))
    
    def create_dashboard_tab(self):
        """Create the dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # System status section
        system_group = QGroupBox("System Status")
        system_layout = QGridLayout()
        
        # Status indicators
        self.system_status_indicator = QLabel("Operational")
        self.system_status_indicator.setStyleSheet("color: green; font-weight: bold;")
        system_layout.addWidget(QLabel("Status:"), 0, 0)
        system_layout.addWidget(self.system_status_indicator, 0, 1)
        
        self.uptime_label = QLabel("3d 12h 45m")
        system_layout.addWidget(QLabel("Uptime:"), 0, 2)
        system_layout.addWidget(self.uptime_label, 0, 3)
        
        self.cpu_usage_bar = QProgressBar()
        self.cpu_usage_bar.setRange(0, 100)
        self.cpu_usage_bar.setValue(45)
        system_layout.addWidget(QLabel("CPU Usage:"), 1, 0)
        system_layout.addWidget(self.cpu_usage_bar, 1, 1)
        
        self.memory_usage_bar = QProgressBar()
        self.memory_usage_bar.setRange(0, 100)
        self.memory_usage_bar.setValue(63)
        system_layout.addWidget(QLabel("Memory Usage:"), 1, 2)
        system_layout.addWidget(self.memory_usage_bar, 1, 3)
        
        self.temperature_label = QLabel("36.5°C")
        system_layout.addWidget(QLabel("Temperature:"), 2, 0)
        system_layout.addWidget(self.temperature_label, 2, 1)
        
        self.error_rate_label = QLabel("0.0012")
        system_layout.addWidget(QLabel("Error Rate:"), 2, 2)
        system_layout.addWidget(self.error_rate_label, 2, 3)
        
        # Flight info
        self.flight_phase_indicator = QLabel("CRUISE")
        self.flight_phase_indicator.setStyleSheet("font-weight: bold;")
        system_layout.addWidget(QLabel("Flight Phase:"), 3, 0)
        system_layout.addWidget(self.flight_phase_indicator, 3, 1)
        
        self.altitude_label = QLabel("10,000 m")
        system_layout.addWidget(QLabel("Altitude:"), 3, 2)
        system_layout.addWidget(self.altitude_label, 3, 3)
        
        self.speed_label = QLabel("850 km/h")
        system_layout.addWidget(QLabel("Speed:"), 4, 0)
        system_layout.addWidget(self.speed_label, 4, 1)
        
        self.coordinates_label = QLabel("N48°51'12.28\", E2°20'55.68\"")
        system_layout.addWidget(QLabel("Coordinates:"), 4, 2)
        system_layout.addWidget(self.coordinates_label, 4, 3)
        
        self.next_waypoint_label = QLabel("EGLL")
        system_layout.addWidget(QLabel("Next Waypoint:"), 5, 0)
        system_layout.addWidget(self.next_waypoint_label, 5, 1)
        
        self.eta_label = QLabel("2h 15m")
        system_layout.addWidget(QLabel("ETA:"), 5, 2)
        system_layout.addWidget(self.eta_label, 5, 3)
        
        system_group.setLayout(system_layout)
        layout.addWidget(system_group)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Resource utilization chart
        self.resource_chart = ResourceUtilizationChart(width=5, height=3)
        charts_layout.addWidget(self.resource_chart)
        
        # Workload class distribution chart
        self.workload_class_chart = WorkloadClassDistributionChart(width=5, height=3)
        charts_layout.addWidget(self.workload_class_chart)
        
        layout.addLayout(charts_layout)
        
        # More charts
        charts_layout2 = QHBoxLayout()
        
        # Error rate chart
        self.error_rate_chart = ErrorRateChart(width=5, height=3)
        charts_layout2.addWidget(self.error_rate_chart)
        
        # Workload status chart
        self.workload_status_chart = WorkloadStatusChart(width=5, height=3)
        charts_layout2.addWidget(self.workload_status_chart)
        
        layout.addLayout(charts_layout2)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        self.allocate_button = QPushButton("Allocate Resources")
        self.allocate_button.clicked.connect(self.manual_allocate_resources)
        actions_layout.addWidget(self.allocate_button)
        
        self.diagnostics_button = QPushButton("Run Diagnostics")
        self.diagnostics_button.clicked.connect(self.run_quick_diagnostics)
        actions_layout.addWidget(self.diagnostics_button)
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.clicked.connect(self.manual_refresh)
        actions_layout.addWidget(self.refresh_button)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_resources_tab(self):
        """Create the resources tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Resources table
        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(7)
        self.resources_table.setHorizontalHeaderLabels([
            "Resource ID", "Qubits", "Coherence Time (μs)", "Error Rate", 
            "Availability", "Allocated (%)", "Available Qubits"
        ])
        self.resources_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.resources_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.resources_table.cellClicked.connect(self.resource_selected)
        
        layout.addWidget(self.resources_table)
        
        # Resource details section
        details_group = QGroupBox("Resource Details")
        details_layout = QGridLayout()
        
        self.resource_id_label = QLabel("Select a resource")
        details_layout.addWidget(QLabel("Resource ID:"), 0, 0)
        details_layout.addWidget(self.resource_id_label, 0, 1)
        
        self.resource_utilization_bar = QProgressBar()
        self.resource_utilization_bar.setRange(0, 100)
        details_layout.addWidget(QLabel("Utilization:"), 1, 0)
        details_layout.addWidget(self.resource_utilization_bar, 1, 1)
        
        self.resource_error_rate_label = QLabel("-")
        details_layout.addWidget(QLabel("Error Rate:"), 2, 0)
        details_layout.addWidget(self.resource_error_rate_label, 2, 1)
        
        self.resource_temperature_label = QLabel("-")
        details_layout.addWidget(QLabel("Temperature:"), 3, 0)
        details_layout.addWidget(self.resource_temperature_label, 3, 1)
        
        self.resource_coherence_label = QLabel("-")
        details_layout.addWidget(QLabel("Coherence Stability:"), 4, 0)
        details_layout.addWidget(self.resource_coherence_label, 4, 1)
        
        self.resource_gate_fidelity_label = QLabel("-")
        details_layout.addWidget(QLabel("Gate Fidelity:"), 5, 0)
        details_layout.addWidget(self.resource_gate_fidelity_label, 5, 1)
        
        self.resource_readout_fidelity_label = QLabel("-")
        details_layout.addWidget(QLabel("Readout Fidelity:"), 6, 0)
        details_layout.addWidget(self.resource_readout_fidelity_label, 6, 1)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Resource actions
        actions_layout = QHBoxLayout()
        
        self.calibrate_button = QPushButton("Calibrate Resource")
        self.calibrate_button.clicked.connect(self.calibrate_resource)
        self.calibrate_button.setEnabled(False)
        actions_layout.addWidget(self.calibrate_button)
        
        self.reset_button = QPushButton("Reset Resource")
        self.reset_button.clicked.connect(self.reset_resource)
        self.reset_button.setEnabled(False)
        actions_layout.addWidget(self.reset_button)
        
        self.diagnose_resource_button = QPushButton("Diagnose Resource")
        self.diagnose_resource_button.clicked.connect(self.diagnose_resource)
        self.diagnose_resource_button.setEnabled(False)
        actions_layout.addWidget(self.diagnose_resource_button)
        
        layout.addLayout(actions_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_workloads_tab(self):
        """Create the workloads tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Workload filters
        filters_layout = QHBoxLayout()
        
        filters_layout.addWidget(QLabel("Filter by Class:"))
        self.class_filter_combo = QComboBox()
        self.class_filter_combo.addItem("All Classes")
        self.class_filter_combo.addItem("QW1 - Critical")
        self.class_filter_combo.addItem("QW2 - Essential")
        self.class_filter_combo.addItem("QW3 - Standard")
        self.class_filter_combo.addItem("QW4 - Background")
        self.class_filter_combo.currentIndexChanged.connect(self.filter_workloads)
        filters_layout.addWidget(self.class_filter_combo)
        
        filters_layout.addWidget(QLabel("Filter by Status:"))
        self.status_filter_combo = QComboBox()
        self.status_filter_combo.addItem("All Statuses")
        self.status_filter_combo.addItem("Pending")
        self.status_filter_combo.addItem("Running")
        self.status_filter_combo.addItem("Completed")
        self.status_filter_combo.addItem("Failed")
        self.status_filter_combo.currentIndexChanged.connect(self.filter_workloads)
        filters_layout.addWidget(self.status_filter_combo)
        
        filters_layout.addStretch()
        
        self.add_workload_button = QPushButton("Add Workload")
        self.add_workload_button.clicked.connect(self.show_add_workload_dialog)
        filters_layout.addWidget(self.add_workload_button)
        
        layout.addLayout(filters_layout)
        
        # Workloads table
        self.workloads_table = QTableWidget()
        self.workloads_table.setColumnCount(8)
        self.workloads_table.setHorizontalHeaderLabels([
            "Workload ID", "Class", "Required Qubits", "Max Error Rate", 
            "Min Coherence Time", "Deadline (ms)", "Status", "Allocated Resource"
        ])
        self.workloads_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.workloads_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.workloads_table.cellClicked.connect(self.workload_selected)
        
        layout.addWidget(self.workloads_table)
        
        # Workload details section
        details_group = QGroupBox("Workload Details")
        details_layout = QGridLayout()
        
        self.workload_id_label = QLabel("Select a workload")
        details_layout.addWidget(QLabel("Workload ID:"), 0, 0)
        details_layout.addWidget(self.workload_id_label, 0, 1)
        
        self.workload_class_label = QLabel("-")
        details_layout.addWidget(QLabel("Class:"), 0, 2)
        details_layout.addWidget(self.workload_class_label, 0, 3)
        
        self.workload_status_label = QLabel("-")
        details_layout.addWidget(QLabel("Status:"), 1, 0)
        details_layout.addWidget(self.workload_status_label, 1, 1)
        
        self.workload_priority_label = QLabel("-")
        details_layout.addWidget(QLabel("Priority Score:"), 1, 2)
        details_layout.addWidget(self.workload_priority_label, 1, 3)
        
        self.workload_resource_label = QLabel("-")
        details_layout.addWidget(QLabel("Allocated Resource:"), 2, 0)
        details_layout.addWidget(self.workload_resource_label, 2, 1)
        
        self.workload_execution_time_label = QLabel("-")
        details_layout.addWidget(QLabel("Execution Time (ms):"), 2, 2)
        details_layout.addWidget(self.workload_execution_time_label, 2, 3)
        
        self.workload_qubits_label = QLabel("-")
        details_layout.addWidget(QLabel("Qubits Used:"), 3, 0)
        details_layout.addWidget(self.workload_qubits_label, 3, 1)
        
        self.workload_circuit_depth_label = QLabel("-")
        details_layout.addWidget(QLabel("Circuit Depth:"), 3, 2)
        details_layout.addWidget(self.workload_circuit_depth_label, 3, 3)
        
        self.workload_gate_count_label = QLabel("-")
        details_layout.addWidget(QLabel("Gate Count:"), 4, 0)
        details_layout.addWidget(self.workload_gate_count_label, 4, 1)
        
        self.workload_error_prob_label = QLabel("-")
        details_layout.addWidget(QLabel("Error Probability:"), 4, 2)
        details_layout.addWidget(self.workload_error_prob_label, 4, 3)
        
        self.workload_success_prob_label = QLabel("-")
        details_layout.addWidget(QLabel("Success Probability:"), 5, 0)
        details_layout.addWidget(self.workload_success_prob_label, 5, 1)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Workload actions
        actions_layout = QHBoxLayout()
        
        self.cancel_workload_button = QPushButton("Cancel Workload")
        self.cancel_workload_button.clicked.connect(self.cancel_workload)
        self.cancel_workload_button.setEnabled(False)
        actions_layout.addWidget(self.cancel_workload_button)
        
        self.prioritize_workload_button = QPushButton("Prioritize Workload")
        self.prioritize_workload_button.clicked.connect(self.prioritize_workload)
        self.prioritize_workload_button.setEnabled(False)
        actions_layout.addWidget(self.prioritize_workload_button)
        
        self.view_results_button = QPushButton("View Results")
        self.view_results_button.clicked.connect(self.view_workload_results)
        self.view_results_button.setEnabled(False)
        actions_layout.addWidget(self.view_results_button)
        
        layout.addLayout(actions_layout)
        
        tab.setLayout(layout)
        return tab
    
    def create_allocation_tab(self):
        """Create the allocation tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Allocation settings
        settings_group = QGroupBox("Allocation Settings")
        settings_layout = QGridLayout()
        
        self.auto_allocate_checkbox = QCheckBox("Auto-allocate resources")
        self.auto_allocate_checkbox.setChecked(self.config.get('auto_allocate', True))
        self.auto_allocate_checkbox.stateChanged.connect(self.toggle_auto_allocation)
        settings_layout.addWidget(self.auto_allocate_checkbox, 0, 0, 1, 2)
        
        settings_layout.addWidget(QLabel("Allocation interval (seconds):"), 1, 0)
        self.allocation_interval_spin = QSpinBox()
        self.allocation_interval_spin.setRange(1, 60)
        self.allocation_interval_spin.setValue(self.config.get('allocation_interval', 10))
        self.allocation_interval_spin.valueChanged.connect(self.update_allocation_interval)
        settings_layout.addWidget(self.allocation_interval_spin, 1, 1)
        
        settings_layout.addWidget(QLabel("Prioritize class:"), 2, 0)
        self.priority_class_combo = QComboBox()
        self.priority_class_combo.addItem("Default (QW1 > QW2 > QW3 > QW4)")
        self.priority_class_combo.addItem("Custom Priority")
        settings_layout.addWidget(self.priority_class_combo, 2, 1)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Current allocation map
        allocation_group = QGroupBox("Current Allocation Map")
        allocation_layout = QVBoxLayout()
        
        self.allocation_table = QTableWidget()
        self.allocation_table.setColumnCount(3)
        self.allocation_table.setHorizontalHeaderLabels([
            "Workload ID", "Resource ID", "Allocation Time"
        ])
        self.allocation_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.allocation_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        allocation_layout.addWidget(self.allocation_table)
        
        allocation_group.setLayout(allocation_layout)
        layout.addWidget(allocation_group)
        
        # Allocation actions
        actions_layout = QHBoxLayout()
        
        self.manual_allocate_button = QPushButton("Allocate Resources Now")
        self.manual_allocate_button.clicked.connect(self.manual_allocate_resources)
        actions_layout.addWidget(self.manual_allocate_button)
        
        self.clear_allocations_button = QPushButton("Clear All Allocations")
        self.clear_allocations_button.clicked.connect(self.clear_allocations)
        actions_layout.addWidget(self.clear_allocations_button)
        
        self.optimize_allocations_button = QPushButton("Optimize Allocations")
        self.optimize_allocations_button.clicked.connect(self.optimize_allocations)
        actions_layout.addWidget(self.optimize_allocations_button)
        
        layout.addLayout(actions_layout)
        
        # Allocation history
        history_group = QGroupBox("Allocation History")
        history_layout = QVBoxLayout()
        
        self.allocation_history_text = QTextEdit()
        self.allocation_history_text.setReadOnly(True)
        
        history_layout.addWidget(self.allocation_history_text)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_diagnostics_tab(self):
        """Create the diagnostics tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Diagnostics controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Select Resource:"))
        self.diagnostic_resource_combo = QComboBox()
        self.diagnostic_resource_combo.addItem("All Resources")
        controls_layout.addWidget(self.diagnostic_resource_combo)
        
        controls_layout.addWidget(QLabel("Test Level:"))
        self.diagnostic_level_combo = QComboBox()
        self.diagnostic_level_combo.addItem("Basic")
        self.diagnostic_level_combo.addItem("Comprehensive")
        self.diagnostic_level_combo.addItem("Deep")
        controls_layout.addWidget(self.diagnostic_level_combo)
        
        self.run_diagnostics_button = QPushButton("Run Diagnostics")
        self.run_diagnostics_button.clicked.connect(self.run_diagnostics)
        controls_layout.addWidget(self.run_diagnostics_button)
        
        layout.addLayout(controls_layout)
        
        # Diagnostics results
        results_group = QGroupBox("Diagnostics Results")
        results_layout = QVBoxLayout()
        
        self.diagnostics_results_text = QTextEdit()
        self.diagnostics_results_text.setReadOnly(True)
        
        results_layout.addWidget(self.diagnostics_results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # System logs
        logs_group = QGroupBox("System Logs")
        logs_layout = QVBoxLayout()
        
        logs_controls = QHBoxLayout()
        
        logs_controls.addWidget(QLabel("Log Level:"))
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItem("All")
        self.log_level_combo.addItem("INFO")
        self.log_level_combo.addItem("WARNING")
        self.log_level_combo.addItem("ERROR")
        self.log_level_combo.currentIndexChanged.connect(self.filter_logs)
        logs_controls.addWidget(self.log_level_combo)
        
        self.refresh_logs_button = QPushButton("Refresh Logs")
        self.refresh_logs_button.clicked.connect(self.refresh_logs)
        logs_controls.addWidget(self.refresh_logs_button)
        
        logs_layout.addLayout(logs_controls)
        
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Level", "Message"
        ])
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        logs_layout.addWidget(self.logs_table)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_simulator_tab(self):
        """Create the simulator tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Simulator controls
        controls_group = QGroupBox("Simulator Controls")
        controls_layout = QGridLayout()
        
        controls_layout.addWidget(QLabel("Scenario:"), 0, 0)
        self.scenario_combo = QComboBox()
        for scenario in self.simulator.get_available_scenarios():
            self.scenario_combo.addItem(scenario)
        controls_layout.addWidget(self.scenario_combo, 0, 1)
        
        self.load_scenario_button = QPushButton("Load Scenario")
        self.load_scenario_button.clicked.connect(self.load_scenario)
        controls_layout.addWidget(self.load_scenario_button, 0, 2)
        
        controls_layout.addWidget(QLabel("Simulation Speed:"), 1, 0)
        self.simulation_speed_slider = QSlider(Qt.Horizontal)
        self.simulation_speed_slider.setRange(1, 10)
        self.simulation_speed_slider.setValue(5)
        controls_layout.addWidget(self.simulation_speed_slider, 1, 1)
        
        self.simulation_speed_label = QLabel("5x")
        controls_layout.addWidget(self.simulation_speed_label, 1, 2)
        self.simulation_speed_slider.valueChanged.connect(
            lambda v: self.simulation_speed_label.setText(f"{v}x")
        )
        
        controls_layout.addWidget(QLabel("Inject Fault:"), 2, 0)
        self.fault_combo = QComboBox()
        self.fault_combo.addItem("None")
        self.fault_combo.addItem("Resource Failure")
        self.fault_combo.addItem("Communication Error")
        self.fault_combo.addItem("High Error Rate")
        self.fault_combo.addItem("Workload Spike")
        controls_layout.addWidget(self.fault_combo, 2, 1)
        
        self.inject_fault_button = QPushButton("Inject")
        self.inject_fault_button.clicked.connect(self.inject_fault)
        controls_layout.addWidget(self.inject_fault_button, 2, 2)
        
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)
        
        # Simulation controls
        sim_controls_layout = QHBoxLayout()
        
        self.start_sim_button = QPushButton("Start Simulation")
        self.start_sim_button.clicked.connect(self.start_simulation)
        sim_controls_layout.addWidget(self.start_sim_button)
        
        self.pause_sim_button = QPushButton("Pause Simulation")
        self.pause_sim_button.clicked.connect(self.pause_simulation)
        self.pause_sim_button.setEnabled(False)
        sim_controls_layout.addWidget(self.pause_sim_button)
        
        self.stop_sim_button = QPushButton("Stop Simulation")
        self.stop_sim_button.clicked.connect(self.stop_simulation)
        self.stop_sim_button.setEnabled(False)
        sim_controls_layout.addWidget(self.stop_sim_button)
        
        layout.addLayout(sim_controls_layout)
        
        # Simulation status
        status_group = QGroupBox("Simulation Status")
        status_layout = QGridLayout()
        
        self.sim_status_label = QLabel("Not Running")
        status_layout.addWidget(QLabel("Status:"), 0, 0)
        status_layout.addWidget(self.sim_status_label, 0, 1)
        
        self.sim_scenario_label = QLabel("No scenario loaded")
        status_layout.addWidget(QLabel("Scenario:"), 0, 2)
        status_layout.addWidget(self.sim_scenario_label, 0, 3)
        
        self.sim_time_label = QLabel("00:00:00")
        status_layout.addWidget(QLabel("Simulation Time:"), 1, 0)
        status_layout.addWidget(self.sim_time_label, 1, 1)
        
        self.sim_workloads_label = QLabel("0")
        status_layout.addWidget(QLabel("Active Workloads:"), 1, 2)
        status_layout.addWidget(self.sim_workloads_label, 1, 3)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Simulation output
        output_group = QGroupBox("Simulation Output")
        output_layout = QVBoxLayout()
        
        self.simulation_output_text = QTextEdit()
        self.simulation_output_text.setReadOnly(True)
        
        output_layout.addWidget(self.simulation_output_text)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        tab.setLayout(layout)
        return tab
    
    def create_settings_tab(self):
        """Create the settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QGridLayout()
        
        connection_layout.addWidget(QLabel("QAOS Endpoint:"), 0, 0)
        self.endpoint_edit = QLineEdit(self.config.get('endpoint', 'http://localhost:8080'))
        connection_layout.addWidget(self.endpoint_edit, 0, 1)
        
        self.test_connection_button = QPushButton("Test Connection")
        self.test_connection_button.clicked.connect(self.test_connection)
        connection_layout.addWidget(self.test_connection_button, 0, 2)
        
        connection_layout.addWidget(QLabel("Authentication:"), 1, 0)
        self.auth_combo = QComboBox()
        self.auth_combo.addItem("None")
        self.auth_combo.addItem("Basic")
        self.auth_combo.addItem("Token")
        connection_layout.addWidget(self.auth_combo, 1, 1)
        
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)
        
        # UI settings
        ui_group = QGroupBox("UI Settings")
        ui_layout = QGridLayout()
        
        ui_layout.addWidget(QLabel("Refresh Interval (seconds):"), 0, 0)
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setValue(self.config.get('refresh_interval', 5))
        ui_layout.addWidget(self.refresh_interval_spin, 0, 1)
        
        ui_layout.addWidget(QLabel("Theme:"), 1, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Light")
        self.theme_combo.addItem("Dark")
        self.theme_combo.setCurrentText(self.config.get('theme', 'Light').capitalize())
        self.theme_combo.currentTextChanged.connect(
            lambda t: self.apply_theme(t.lower())
        )
        ui_layout.addWidget(self.theme_combo, 1, 1)
        
        ui_layout.addWidget(QLabel("Show Advanced Metrics:"), 2, 0)
        self.advanced_metrics_checkbox = QCheckBox()
        self.advanced_metrics_checkbox.setChecked(self.config.get('show_advanced_metrics', True))
        ui_layout.addWidget(self.advanced_metrics_checkbox, 2, 1)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Alert settings
        alert_group = QGroupBox("Alert Settings")
        alert_layout = QGridLayout()
        
        alert_layout.addWidget(QLabel("CPU Usage Threshold (%):"), 0, 0)
        self.cpu_threshold_spin = QSpinBox()
        self.cpu_threshold_spin.setRange(50, 100)
        self.cpu_threshold_spin.setValue(self.config.get('alert_thresholds', {}).get('cpu_usage', 90))
        alert_layout.addWidget(self.cpu_threshold_spin, 0, 1)
        
        alert_layout.addWidget(QLabel("Memory Usage Threshold (%):"), 1, 0)
        self.memory_threshold_spin = QSpinBox()
        self.memory_threshold_spin.setRange(50, 100)
        self.memory_threshold_spin.setValue(self.config.get('alert_thresholds', {}).get('memory_usage', 85))
        alert_layout.addWidget(self.memory_threshold_spin, 1, 1)
        
        alert_  85))
        alert_layout.addWidget(self.memory_threshold_spin, 1, 1)
        
        alert_layout.addWidget(QLabel("Temperature Threshold (°C):"), 2, 0)
        self.temperature_threshold_spin = QSpinBox()
        self.temperature_threshold_spin.setRange(30, 60)
        self.temperature_threshold_spin.setValue(self.config.get('alert_thresholds', {}).get('temperature', 45))
        alert_layout.addWidget(self.temperature_threshold_spin, 2, 1)
        
        alert_layout.addWidget(QLabel("Error Rate Threshold:"), 3, 0)
        self.error_threshold_spin = QDoubleSpinBox()
        self.error_threshold_spin.setRange(0.001, 0.1)
        self.error_threshold_spin.setSingleStep(0.001)
        self.error_threshold_spin.setDecimals(4)
        self.error_threshold_spin.setValue(self.config.get('alert_thresholds', {}).get('error_rate', 0.01))
        alert_layout.addWidget(self.error_threshold_spin, 3, 1)
        
        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)
        
        # Settings actions
        actions_layout = QHBoxLayout()
        
        self.save_settings_button = QPushButton("Save Settings")
        self.save_settings_button.clicked.connect(self.save_settings)
        actions_layout.addWidget(self.save_settings_button)
        
        self.reset_settings_button = QPushButton("Reset to Defaults")
        self.reset_settings_button.clicked.connect(self.reset_settings)
        actions_layout.addWidget(self.reset_settings_button)
        
        layout.addLayout(actions_layout)
        
        tab.setLayout(layout)
        return tab
    
    def update_data(self, data):
        """Update UI with new data"""
        # Update system status
        system_status = data.get('system_status', {})
        self.update_system_status(system_status)
        
        # Update resources
        resources = data.get('resources', [])
        self.update_resources(resources)
        
        # Update resource metrics
        resource_metrics = data.get('resource_metrics', {})
        self.update_resource_metrics(resource_metrics)
        
        # Update workloads
        workloads = data.get('workloads', [])
        self.update_workloads(workloads)
        
        # Update workload metrics
        workload_metrics = data.get('workload_metrics', {})
        self.update_workload_metrics(workload_metrics)
        
        # Update allocation map
        allocation_map = data.get('allocation_map', {})
        self.update_allocation_map(allocation_map)
        
        # Update charts
        self.update_charts(resources, workloads, resource_metrics)
    
    def update_system_status(self, status):
        """Update system status indicators"""
        # Update status indicator
        self.system_status_indicator.setText(status.get('status', 'Unknown'))
        if status.get('status') == 'Operational':
            self.system_status_indicator.setStyleSheet("color: green; font-weight: bold;")
        elif status.get('status') == 'Degraded':
            self.system_status_indicator.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.system_status_indicator.setStyleSheet("color: red; font-weight: bold;")
        
        # Update other status fields
        self.uptime_label.setText(status.get('uptime', '-'))
        
        cpu_usage = status.get('cpu_usage', 0)
        self.cpu_usage_bar.setValue(int(cpu_usage))
        if cpu_usage > self.config.get('alert_thresholds', {}).get('cpu_usage', 90):
            self.cpu_usage_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        else:
            self.cpu_usage_bar.setStyleSheet("")
        
        memory_usage = status.get('memory_usage', 0)
        self.memory_usage_bar.setValue(int(memory_usage))
        if memory_usage > self.config.get('alert_thresholds', {}).get('memory_usage', 85):
            self.memory_usage_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        else:
            self.memory_usage_bar.setStyleSheet("")
        
        self.temperature_label.setText(f"{status.get('temperature', 0)}°C")
        self.error_rate_label.setText(str(status.get('error_rate', 0)))
        
        # Update flight info
        self.flight_phase_indicator.setText(status.get('flight_phase', '-'))
        self.altitude_label.setText(f"{status.get('altitude', 0)} m")
        self.speed_label.setText(f"{status.get('speed', 0)} km/h")
        self.coordinates_label.setText(status.get('coordinates', '-'))
        self.next_waypoint_label.setText(status.get('next_waypoint', '-'))
        self.eta_label.setText(status.get('eta', '-'))
        
        # Update status bar
        self.system_status_label.setText(f"System: {status.get('status', 'Unknown')}")
        self.flight_phase_label.setText(f"Flight Phase: {status.get('flight_phase', '-')}")
    
    def update_resources(self, resources):
        """Update resources table"""
        self.resources_table.setRowCount(len(resources))
        
        # Update resource combo boxes
        current_resource = self.diagnostic_resource_combo.currentText()
        self.diagnostic_resource_combo.clear()
        self.diagnostic_resource_combo.addItem("All Resources")
        
        for i, resource in enumerate(resources):
            # Add to resources table
            self.resources_table.setItem(i, 0, QTableWidgetItem(resource.resource_id))
            self.resources_table.setItem(i, 1, QTableWidgetItem(str(resource.qubits)))
            self.resources_table.setItem(i, 2, QTableWidgetItem(str(resource.coherence_time_us)))
            self.resources_table.setItem(i, 3, QTableWidgetItem(str(resource.error_rate)))
            self.resources_table.setItem(i, 4, QTableWidgetItem(f"{resource.availability:.2f}"))
            self.resources_table.setItem(i, 5, QTableWidgetItem(f"{resource.allocated:.2f}"))
            self.resources_table.setItem(i, 6, QTableWidgetItem(str(resource.available_qubits())))
            
            # Add to resource combo box
            self.diagnostic_resource_combo.addItem(resource.resource_id)
        
        # Restore selected resource if possible
        index = self.diagnostic_resource_combo.findText(current_resource)
        if index >= 0:
            self.diagnostic_resource_combo.setCurrentIndex(index)
    
    def update_resource_metrics(self, resource_metrics):
        """Update resource metrics"""
        # If a resource is selected, update its details
        selected_rows = self.resources_table.selectedItems()
        if selected_rows:
            resource_id = self.resources_table.item(selected_rows[0].row(), 0).text()
            if resource_id in resource_metrics:
                metrics = resource_metrics[resource_id]
                self.resource_utilization_bar.setValue(int(metrics.get('utilization', 0)))
                self.resource_error_rate_label.setText(f"{metrics.get('error_rate', 0):.6f}")
                self.resource_temperature_label.setText(f"{metrics.get('temperature', 0):.1f}°C")
                self.resource_coherence_label.setText(f"{metrics.get('coherence_stability', 0):.2f}%")
                self.resource_gate_fidelity_label.setText(f"{metrics.get('gate_fidelity', 0):.2f}%")
                self.resource_readout_fidelity_label.setText(f"{metrics.get('readout_fidelity', 0):.2f}%")
    
    def update_workloads(self, workloads):
        """Update workloads table"""
        # Apply filters
        filtered_workloads = self.apply_workload_filters(workloads)
        
        self.workloads_table.setRowCount(len(filtered_workloads))
        
        for i, workload in enumerate(filtered_workloads):
            self.workloads_table.setItem(i, 0, QTableWidgetItem(workload.workload_id))
            self.workloads_table.setItem(i, 1, QTableWidgetItem(workload.class_type))
            self.workloads_table.setItem(i, 2, QTableWidgetItem(str(workload.required_qubits)))
            self.workloads_table.setItem(i, 3, QTableWidgetItem(str(workload.max_error_rate)))
            self.workloads_table.setItem(i, 4, QTableWidgetItem(str(workload.min_coherence_time_us)))
            
            deadline = "-" if workload.deadline_ms is None else str(workload.deadline_ms)
            self.workloads_table.setItem(i, 5, QTableWidgetItem(deadline))
            
            self.workloads_table.setItem(i, 6, QTableWidgetItem(workload.status))
            
            resource = "-" if workload.allocated_resource is None else workload.allocated_resource
            self.workloads_table.setItem(i, 7, QTableWidgetItem(resource))
            
            # Color rows based on status
            if workload.status == "Running":
                for j in range(8):
                    self.workloads_table.item(i, j).setBackground(QColor(230, 255, 230))
            elif workload.status == "Completed":
                for j in range(8):
                    self.workloads_table.item(i, j).setBackground(QColor(230, 230, 255))
            elif workload.status == "Failed":
                for j in range(8):
                    self.workloads_table.item(i, j).setBackground(QColor(255, 230, 230))
    
    def apply_workload_filters(self, workloads):
        """Apply filters to workloads"""
        filtered_workloads = workloads
        
        # Apply class filter
        class_filter = self.class_filter_combo.currentText()
        if class_filter != "All Classes":
            class_type = class_filter.split(" - ")[0]
            filtered_workloads = [w for w in filtered_workloads if w.class_type == class_type]
        
        # Apply status filter
        status_filter = self.status_filter_combo.currentText()
        if status_filter != "All Statuses":
            filtered_workloads = [w for w in filtered_workloads if w.status == status_filter]
        
        return filtered_workloads
    
    def update_workload_metrics(self, metrics):
        """Update workload metrics"""
        # If a workload is selected, update its details
        selected_rows = self.workloads_table.selectedItems()
        if selected_rows:
            workload_id = self.workloads_table.item(selected_rows[0].row(), 0).text()
            workload_metrics = self.client.get_workload_metrics(workload_id)
            
            if workload_metrics:
                self.workload_execution_time_label.setText(f"{workload_metrics.get('execution_time', 0):.2f}")
                self.workload_qubits_label.setText(str(workload_metrics.get('qubits_used', 0)))
                self.workload_circuit_depth_label.setText(str(workload_metrics.get('circuit_depth', 0)))
                self.workload_gate_count_label.setText(str(workload_metrics.get('gate_count', 0)))
                self.workload_error_prob_label.setText(f"{workload_metrics.get('error_probability', 0):.4f}")
                self.workload_success_prob_label.setText(f"{workload_metrics.get('success_probability', 0):.4f}")
        
        # Update workload status chart data
        status_counts = {
            'Pending': sum(1 for w in self.client.get_workloads() if w.status == 'Pending'),
            'Running': sum(1 for w in self.client.get_workloads() if w.status == 'Running'),
            'Completed': sum(1 for w in self.client.get_workloads() if w.status == 'Completed'),
            'Failed': sum(1 for w in self.client.get_workloads() if w.status == 'Failed')
        }
        self.workload_status_chart.update_data(status_counts)
    
    def update_allocation_map(self, allocation_map):
        """Update allocation map table"""
        self.allocation_table.setRowCount(len(allocation_map))
        
        row = 0
        for workload_id, resource_id in allocation_map.items():
            self.allocation_table.setItem(row, 0, QTableWidgetItem(workload_id))
            self.allocation_table.setItem(row, 1, QTableWidgetItem(resource_id))
            
            # Use current time as allocation time (in a real system, this would come from the server)
            allocation_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            self.allocation_table.setItem(row, 2, QTableWidgetItem(allocation_time))
            
            row += 1
        
        # Update allocation history
        if hasattr(self, 'last_allocation_map'):
            # Find new allocations
            for workload_id, resource_id in allocation_map.items():
                if workload_id not in self.last_allocation_map:
                    time_str = QDateTime.currentDateTime().toString("hh:mm:ss")
                    self.allocation_history_text.append(
                        f"[{time_str}] Allocated workload {workload_id} to resource {resource_id}"
                    )
            
            # Find deallocations
            for workload_id, resource_id in self.last_allocation_map.items():
                if workload_id not in allocation_map:
                    time_str = QDateTime.currentDateTime().toString("hh:mm:ss")
                    self.allocation_history_text.append(
                        f"[{time_str}] Deallocated workload {workload_id} from resource {resource_id}"
                    )
        
        # Save current allocation map for next comparison
        self.last_allocation_map = allocation_map.copy()
    
    def update_charts(self, resources, workloads, resource_metrics):
        """Update all charts"""
        # Update resource utilization chart
        self.resource_chart.update_data(resources)
        
        # Update workload class distribution chart
        class_counts = {
            WorkloadClass.QW1: sum(1 for w in workloads if w.class_type == WorkloadClass.QW1),
            WorkloadClass.QW2: sum(1 for w in workloads if w.class_type == WorkloadClass.QW2),
            WorkloadClass.QW3: sum(1 for w in workloads if w.class_type == WorkloadClass.QW3),
            WorkloadClass.QW4: sum(1 for w in workloads if w.class_type == WorkloadClass.QW4)
        }
        self.workload_class_chart.update_data(class_counts)
        
        # Update error rate chart
        self.error_rate_chart.update_data(resource_metrics)
    
    def resource_selected(self, row, column):
        """Handle resource selection"""
        resource_id = self.resources_table.item(row, 0).text()
        self.resource_id_label.setText(resource_id)
        
        # Enable resource action buttons
        self.calibrate_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.diagnose_resource_button.setEnabled(True)
        
        # Update resource metrics
        metrics = self.client.get_resource_metrics(resource_id)
        if metrics:
            self.resource_utilization_bar.setValue(int(metrics.get('utilization', 0)))
            self.resource_error_rate_label.setText(f"{metrics.get('error_rate', 0):.6f}")
            self.resource_temperature_label.setText(f"{metrics.get('temperature', 0):.1f}°C")
            self.resource_coherence_label.setText(f"{metrics.get('coherence_stability', 0):.2f}%")
            self.resource_gate_fidelity_label.setText(f"{metrics.get('gate_fidelity', 0):.2f}%")
            self.resource_readout_fidelity_label.setText(f"{metrics.get('readout_fidelity', 0):.2f}%")
    
    def workload_selected(self, row, column):
        """Handle workload selection"""
        workload_id = self.workloads_table.item(row, 0).text()
        workload_class = self.workloads_table.item(row, 1).text()
        workload_status = self.workloads_table.item(row, 6).text()
        workload_resource = self.workloads_table.item(row, 7).text()
        
        self.workload_id_label.setText(workload_id)
        self.workload_class_label.setText(workload_class)
        self.workload_status_label.setText(workload_status)
        self.workload_resource_label.setText(workload_resource)
        
        # Find the workload object
        workload = next((w for w in self.client.get_workloads() if w.workload_id == workload_id), None)
        if workload:
            self.workload_priority_label.setText(f"{workload.priority_score:.2f}")
        
        # Enable/disable action buttons based on status
        self.cancel_workload_button.setEnabled(workload_status in ["Pending", "Running"])
        self.prioritize_workload_button.setEnabled(workload_status == "Pending")
        self.view_results_button.setEnabled(workload_status in ["Completed", "Failed"])
        
        # Update workload metrics
        metrics = self.client.get_workload_metrics(workload_id)
        if metrics:
            self.workload_execution_time_label.setText(f"{metrics.get('execution_time', 0):.2f}")
            self.workload_qubits_label.setText(str(metrics.get('qubits_used', 0)))
            self.workload_circuit_depth_label.setText(str(metrics.get('circuit_depth', 0)))
            self.workload_gate_count_label.setText(str(metrics.get('gate_count', 0)))
            self.workload_error_prob_label.setText(f"{metrics.get('error_probability', 0):.4f}")
            self.workload_success_prob_label.setText(f"{metrics.get('success_probability', 0):.4f}")
    
    def filter_workloads(self):
        """Filter workloads based on selected filters"""
        self.update_workloads(self.client.get_workloads())
    
    def manual_refresh(self):
        """Manually refresh data"""
        try:
            # Collect all data
            data = {}
            
            # System status
            data['system_status'] = self.client.get_system_status()
            
            # Resources
            data['resources'] = self.client.get_resources()
            
            # Resource metrics
            data['resource_metrics'] = {}
            for resource in data['resources']:
                data['resource_metrics'][resource.resource_id] = self.client.get_resource_metrics(resource.resource_id)
            
            # Workloads
            data['workloads'] = self.client.get_workloads()
            
            # Workload metrics
            data['workload_metrics'] = self.client.get_workload_metrics()
            
            # Allocation map
            data['allocation_map'] = self.client.get_allocation_map()
            
            # Update UI
            self.update_data(data)
            
            self.status_bar.showMessage("Data refreshed successfully", 3000)
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            self.status_bar.showMessage(f"Error refreshing data: {str(e)}", 5000)
    
    def manual_allocate_resources(self):
        """Manually allocate resources"""
        try:
            allocation_map = self.client.allocate_resources()
            self.update_allocation_map(allocation_map)
            self.status_bar.showMessage("Resources allocated successfully", 3000)
        except ResourceAllocationError as e:
            logger.error(f"Resource allocation error: {e}")
            QMessageBox.critical(self, "Allocation Error", str(e))
        except Exception as e:
            logger.error(f"Error allocating resources: {e}")
            self.status_bar.showMessage(f"Error allocating resources: {str(e)}", 5000)
    
    def auto_allocate_resources(self):
        """Automatically allocate resources"""
        if self.config.get('auto_allocate', True):
            try:
                allocation_map = self.client.allocate_resources()
                self.update_allocation_map(allocation_map)
            except Exception as e:
                logger.error(f"Error in auto allocation: {e}")
    
    def toggle_auto_allocation(self, state):
        """Toggle automatic resource allocation"""
        auto_allocate = state == Qt.Checked
        self.config.set('auto_allocate', auto_allocate)
        
        if auto_allocate:
            interval = self.config.get('allocation_interval', 10)
            self.allocation_timer.start(interval * 1000)
        else:
            self.allocation_timer.stop()
    
    def update_allocation_interval(self, value):
        """Update allocation interval"""
        self.config.set('allocation_interval', value)
        
        if self.config.get('auto_allocate', True):
            self.allocation_timer.start(value * 1000)
    
    def clear_allocations(self):
        """Clear all allocations"""
        # In a real system, this would call an API to clear allocations
        # For the mock implementation, we'll just reset the allocated percentage
        for resource in self.client.resources:
            resource.allocated = 0
        
        self.client.allocation_map = {}
        self.update_allocation_map({})
        
        self.status_bar.showMessage("All allocations cleared", 3000)
    
    def optimize_allocations(self):
        """Optimize resource allocations"""
        # In a real system, this would call an API to optimize allocations
        # For the mock implementation, we'll just show a message
        QMessageBox.information(self, "Optimize Allocations", 
                               "Allocation optimization would be performed here.")
        
        self.status_bar.showMessage("Allocations optimized", 3000)
    
    def show_add_workload_dialog(self):
        """Show dialog to add a new workload"""
        # In a real system, this would show a dialog to add a workload
        # For the mock implementation, we'll create a simple workload
        workload_id = f"workload-{len(self.client.workloads) + 1}"
        
        # Create a random workload
        workload_classes = [WorkloadClass.QW1, WorkloadClass.QW2, WorkloadClass.QW3, WorkloadClass.QW4]
        workload_class = np.random.choice(workload_classes)
        
        required_qubits = np.random.randint(4, 20)
        max_error_rate = np.random.uniform(0.0005, 0.005)
        min_coherence_time_us = np.random.randint(50, 200)
        
        # 50% chance of having a deadline
        deadline_ms = np.random.randint(10, 1000) if np.random.random() > 0.5 else None
        
        # 30% chance of being preemptable
        preemptable = np.random.random() > 0.7
        
        workload = QuantumWorkload(
            workload_id=workload_id,
            class_type=workload_class,
            required_qubits=required_qubits,
            max_error_rate=max_error_rate,
            min_coherence_time_us=min_coherence_time_us,
            deadline_ms=deadline_ms,
            preemptable=preemptable
        )
        
        # Register the workload
        self.client.register_workload(workload)
        
        # Update UI
        self.update_workloads(self.client.get_workloads())
        
        self.status_bar.showMessage(f"Workload {workload_id} added", 3000)
    
    def cancel_workload(self):
        """Cancel the selected workload"""
        selected_rows = self.workloads_table.selectedItems()
        if not selected_rows:
            return
        
        workload_id = self.workloads_table.item(selected_rows[0].row(), 0).text()
        
        # Find the workload
        workload = next((w for w in self.client.workloads if w.workload_id == workload_id), None)
        if workload:
            workload.status = "Cancelled"
            
            # If allocated, deallocate
            if workload.allocated_resource and workload.workload_id in self.client.allocation_map:
                resource_id = self.client.allocation_map[workload.workload_id]
                resource = next((r for r in self.client.resources if r.resource_id == resource_id), None)
                
                if resource:
                    # Calculate allocation percentage
                    allocation_percent = (workload.required_qubits / resource.qubits) * 100
                    resource.allocated -= allocation_percent
                
                # Remove from allocation map
                del self.client.allocation_map[workload.workload_id]
            
            # Update UI
            self.update_workloads(self.client.get_workloads())
            self.update_allocation_map(self.client.get_allocation_map())
            
            self.status_bar.showMessage(f"Workload {workload_id} cancelled", 3000)
    
    def prioritize_workload(self):
        """Increase priority of the selected workload"""
        selected_rows = self.workloads_table.selectedItems()
        if not selected_rows:
            return
        
        workload_id = self.workloads_table.item(selected_rows[0].row(), 0).text()
        
        # Find the workload
        workload = next((w for w in self.client.workloads if w.workload_id == workload_id), None)
        if workload:
            # Increase priority by 50%
            workload.priority_score *= 1.5
            
            # Update UI
            self.workload_priority_label.setText(f"{workload.priority_score:.2f}")
            
            self.status_bar.showMessage(f"Workload {workload_id} prioritized", 3000)
    
    def view_workload_results(self):
        """View results of the selected workload"""
        selected_rows = self.workloads_table.selectedItems()
        if not selected_rows:
            return
        
        workload_id = self.workloads_table.item(selected_rows[0].row(), 0).text()
        
        # In a real system, this would show detailed results
        # For the mock implementation, we'll just show a message
        QMessageBox.information(self, "Workload Results", 
                               f"Detailed results for workload {workload_id} would be shown here.")
    
    def run_quick_diagnostics(self):
        """Run quick diagnostics on all resources"""
        try:
            results = self.diagnostics.run_diagnostics()
            
            if results['status'] == 'passed':
                QMessageBox.information(self, "Diagnostics Results", 
                                      f"All diagnostics passed ({results['tests_passed']}/{results['tests_run']} tests)")
            else:
                QMessageBox.warning(self, "Diagnostics Results", 
                                   f"Some diagnostics failed ({results['tests_failed']}/{results['tests_run']} tests)")
            
            self.status_bar.showMessage("Diagnostics completed", 3000)
        except Exception as e:
            logger.error(f"Error running diagnostics: {e}")
            QMessageBox.critical(self, "Diagnostics Error", str(e))
    
    def run_diagnostics(self):
        """Run diagnostics on selected resource"""
        resource_id = None
        if self.diagnostic_resource_combo.currentText() != "All Resources":
            resource_id = self.diagnostic_resource_combo.currentText()
        
        try:
            results = self.diagnostics.run_diagnostics(resource_id)
            
            # Display results
            self.diagnostics_results_text.clear()
            self.diagnostics_results_text.append(f"Diagnostics Status: {results['status']}")
            self.diagnostics_results_text.append(f"Tests Run: {results['tests_run']}")
            self.diagnostics_results_text.append(f"Tests Passed: {results['tests_passed']}")
            self.diagnostics_results_text.append(f"Tests Failed: {results['tests_failed']}")
            self.diagnostics_results_text.append("\nDetails:")
            
            for test in results['details']:
                status_color = "green" if test['status'] == 'passed' else "red"
                self.diagnostics_results_text.append(
                    f"<span style='color: {status_color};'>{test['name']}: {test['status']}</span> - {test['message']}"
                )
            
            self.status_bar.showMessage("Diagnostics completed", 3000)
        except Exception as e:
            logger.error(f"Error running diagnostics: {e}")
            QMessageBox.critical(self, "Diagnostics Error", str(e))
    
    def refresh_logs(self):
        """Refresh system logs"""
        try:
            logs = self.diagnostics.get_logs()
            
            # Apply filter
            log_level = self.log_level_combo.currentText()
            if log_level != "All":
                logs = [log for log in logs if log['level'] == log_level]
            
            # Update logs table
            self.logs_table.setRowCount(len(logs))
            
            for i, log in enumerate(logs):
                self.logs_table.setItem(i, 0, QTableWidgetItem(log['timestamp']))
                self.logs_table.setItem(i, 1, QTableWidgetItem(log['level']))
                self.logs_table.setItem(i, 2, QTableWidgetItem(log['message']))
                
                # Color rows based on level
                if log['level'] == 'ERROR':
                    for j in range(3):
                        self.logs_table.item(i, j).setBackground(QColor(255, 200, 200))
                elif log['level'] == 'WARNING':
                    for j in range(3):
                        self.logs_table.item(i, j).setBackground(QColor(255, 255, 200))
            
            self.status_bar.showMessage("Logs refreshed", 3000)
        except Exception as e:
            logger.error(f"Error refreshing logs: {e}")
            QMessageBox.critical(self, "Log Error", str(e))
    
    def filter_logs(self):
        """Filter logs based on selected level"""
        self.refresh_logs()
    
    def calibrate_resource(self):
        """Calibrate the selected resource"""
        selected_rows = self.resources_table.selectedItems()
        if not selected_rows:
            return
        
        resource_id = self.resources_table.item(selected_rows[0].row(), 0).text()
        
        # In a real system, this would call an API to calibrate the resource
        # For the mock implementation, we'll just show a message
        QMessageBox.information(self, "Calibrate Resource", 
                               f"Resource {resource_id} would be calibrated here.")
        
        self.status_bar.showMessage(f"Resource {resource_id} calibrated", 3000)
    
    def reset_resource(self):
        """Reset the selected resource"""
        selected_rows = self.resources_table.selectedItems()
        if not selected_rows:
            return
        
        resource_id = self.resources_table.item(selected_rows[0].row(), 0).text()
        
        # In a real system, this would call an API to reset the resource
        # For the mock implementation, we'll just show a message
        QMessageBox.information(self, "Reset Resource", 
                               f"Resource {resource_id} would be reset here.")
        
        self.status_bar.showMessage(f"Resource {resource_id} reset", 3000)
    
    def diagnose_resource(self):
        """Diagnose the selected resource"""
        selected_rows = self.resources_table.selectedItems()
        if not selected_rows:
            return
        
        resource_id = self.resources_table.item(selected_rows[0].row(), 0).text()
        
        # Set the resource in the diagnostics tab
        index = self.diagnostic_resource_combo.findText(resource_id)
        if index >= 0:
            self.diagnostic_resource_combo.setCurrentIndex(index)
        
        # Switch to diagnostics tab
        self.central_widget.setCurrentIndex(4)  # Diagnostics tab
        
        # Run diagnostics
        self.run_diagnostics()
    
    def load_scenario(self):
        """Load the selected scenario"""
        scenario = self.scenario_combo.currentText()
        
        if self.simulator.load_scenario(scenario):
            self.sim_scenario_label.setText(scenario)
            self.sim_status_label.setText("Loaded")
            self.start_sim_button.setEnabled(True)
            
            # Add to simulation output
            self.simulation_output_text.append(f"Loaded scenario: {scenario}")
            
            self.status_bar.showMessage(f"Scenario {scenario} loaded", 3000)
    
    def start_simulation(self):
        """Start the simulation"""
        if self.simulator.start_simulation():
            self.sim_status_label.setText("Running")
            self.start_sim_button.setEnabled(False)
            self.pause_sim_button.setEnabled(True)
            self.stop_sim_button.setEnabled(True)
            
            # Add to simulation output
            self.simulation_output_text.append("Simulation started")
            
            # Start a timer to update simulation time
            self.sim_time = 0
            self.sim_timer = QTimer(self)
            self.sim_timer.timeout.connect(self.update_simulation_time)
            self.sim_timer.start(1000)  # Update every second
            
            self.status_bar.showMessage("Simulation started", 3000)
    
    def pause_simulation(self):
        """Pause the simulation"""
        # In a real system, this would pause the simulation
        # For the mock implementation, we'll just update the UI
        self.sim_status_label.setText("Paused")
        self.start_sim_button.setEnabled(True)
        self.pause_sim_button.setEnabled(False)
        
        # Add to simulation output
        self.simulation_output_text.append("Simulation paused")
        
        # Pause the timer
        self.sim_timer.stop()
        
        self.status_bar.showMessage("Simulation paused", 3000)
    
    def stop_simulation(self):
        """Stop the simulation"""
        if self.simulator.stop_simulation():
            self.sim_status_label.setText("Stopped")
            self.start_sim_button.setEnabled(True)
            self.pause_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(False)
            
            # Add to simulation output
            self.simulation_output_text.append("Simulation stopped")
            
            # Stop the timer
            self.sim_timer.stop()
            
            self.status_bar.showMessage("Simulation stopped", 3000)
    
    def update_simulation_time(self):
        """Update simulation time"""
        self.sim_time += 1
        
        # Format time as HH:MM:SS
        hours = self.sim_time // 3600
        minutes = (self.sim_time % 3600) // 60
        seconds = self.sim_time % 60
        
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.sim_time_label.setText(time_str)
        
        # Update active workloads (random for demo)
        active_workloads = np.random.randint(5, 20)
        self.sim_workloads_label.setText(str(active_workloads))
        
        # Periodically add simulation events
        if self.sim_time % 10 == 0:
            event = np.random.choice([
                "New workload added: navigation-optimization",
                "Workload completed: flight-control-optimization",
                "Resource QPU-2 utilization at 85%",
                "Adjusting quantum error correction parameters",
                "Optimizing resource allocation"
            ])
            self.simulation_output_text.append(f"[{time_str}] {event}")
    
    def inject_fault(self):
        """Inject a fault into the simulation"""
        fault_type = self.fault_combo.currentText()
        
        if fault_type == "None":
            return
        
        # Add to simulation output
        self.simulation_output_text.append(f"Injecting fault: {fault_type}")
        
        # In a real system, this would actually inject the fault
        # For the mock implementation, we'll just show different messages
        if fault_type == "Resource Failure":
            self.simulation_output_text.append("ALERT: QPU-2 has failed!")
            self.simulation_output_text.append("Initiating failover to backup QPU")
            self.simulation_output_text.append("Redistributing workloads...")
        elif fault_type == "Communication Error":
            self.simulation_output_text.append("ALERT: Communication error detected!")
            self.simulation_output_text.append("Packet loss rate: 15%")
            self.simulation_output_text.append("Retrying critical communications...")
        elif fault_type == "High Error Rate":
            self.simulation_output_text.append("ALERT: High error rate detected on QPU-1!")
            self.simulation_output_text.append("Error rate: 0.0089 (threshold: 0.005)")
            self.simulation_output_text.append("Initiating error mitigation protocols...")
        elif fault_type == "Workload Spike":
            self.simulation_output_text.append("ALERT: Sudden spike in workload submissions!")
            self.simulation_output_text.append("25 new workloads received in last 2 seconds")
            self.simulation_output_text.append("Prioritizing critical workloads...")
        
        self.status_bar.showMessage(f"Fault injected: {fault_type}", 3000)
    
    def test_connection(self):
        """Test connection to QAOS endpoint"""
        endpoint = self.endpoint_edit.text()
        
        # In a real system, this would actually test the connection
        # For the mock implementation, we'll just show a success message
        QMessageBox.information(self, "Connection Test", 
                               f"Successfully connected to {endpoint}")
        
        self.status_bar.showMessage("Connection test successful", 3000)
    
    def save_settings(self):
        """Save settings"""
        # Update config from UI
        self.config.set('endpoint', self.endpoint_edit.text())
        self.config.set('refresh_interval', self.refresh_interval_spin.value())
        self.config.set('theme', self.theme_combo.currentText().lower())
        self.config.set('auto_allocate', self.auto_allocate_checkbox.isChecked())
        self.config.set('allocation_interval', self.allocation_interval_spin.value())
        self.config.set('show_advanced_metrics', self.advanced_metrics_checkbox.isChecked())
        
        # Update alert thresholds
        alert_thresholds = {
            'cpu_usage': self.cpu_threshold_spin.value(),
            'memory_usage': self.memory_threshold_spin.value(),
            'temperature': self.temperature_threshold_spin.value(),
            'error_rate': self.error_threshold_spin.value()
        }
        self.config.set('alert_thresholds', alert_thresholds)
        
        # Save to file (in a real system)
        if self.config.save():
            QMessageBox.information(self, "Settings", "Settings saved successfully")
            self.status_bar.showMessage("Settings saved", 3000)
        else:
            QMessageBox.warning(self, "Settings", "Error saving settings")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        # Confirm reset
        reply = QMessageBox.question(self, "Reset Settings", 
                                    "Are you sure you want to reset all settings to defaults?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Create new config with defaults
            self.config = QAOSConfig()
            
            # Update UI
            self.endpoint_edit.setText(self.config.get('endpoint', 'http://localhost:8080'))
            self.refresh_interval_spin.setValue(self.config.get('refresh_interval', 5))
            self.theme_combo.setCurrentText(self.config.get('theme', 'light').capitalize())
            self.auto_allocate_checkbox.setChecked(self.config.get('auto_allocate', True))
            self.allocation_interval_spin.setValue(self.config.get('allocation_interval', 10))
            self.advanced_metrics_checkbox.setChecked(self.config.get('show_advanced_metrics', True))
            
            # Update alert thresholds
            alert_thresholds = self.config.get('alert_thresholds', {})
            self.cpu_threshold_spin.setValue(alert_thresholds.get('cpu_usage', 90))
            self.memory_threshold_spin.setValue(alert_thresholds.get('memory_usage', 85))
            self.temperature_threshold_spin.setValue(alert_thresholds.get('temperature', 45))
            self.error_threshold_spin.setValue(alert_thresholds.get('error_rate', 0.01))
            
            # Apply theme
            self.apply_theme(self.config.get('theme', 'light'))
            
            self.status_bar.showMessage("Settings reset to defaults", 3000)
    
    def apply_theme(self, theme):
        """Apply the selected theme"""
        if theme.lower() == 'dark':
            # Set dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2D2D30;
                    color: #E1E1E1;
                }
                QTabWidget::pane {
                    border: 1px solid #3F3F46;
                    background-color: #2D2D30;
                }
                QTabBar::tab {
                    background-color: #252526;
                    color: #E1E1E1;
                    padding: 8px 12px;
                    border: 1px solid #3F3F46;
                    border-bottom: none;
                }
                QTabBar::tab:selected {
                    background-color: #3F3F46;
                }
                QGroupBox {
                    border: 1px solid #3F3F46;
                    margin-top: 1.5ex;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 3px;
                }
                QPushButton {
                    background-color: #0E639C;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #1177BB;
                }
                QPushButton:disabled {
                    background-color: #3F3F46;
                    color: #A0A0A0;
                }
                QTableWidget {
                    background-color: #252526;
                    color: #E1E1E1;
                    gridline-color: #3F3F46;
                }
                QHeaderView::section {
                    background-color: #3F3F46;
                    color: #E1E1E1;
                    padding: 5px;
                    border: 1px solid #252526;
                }
                QTextEdit {
                    background-color: #252526;
                    color: #E1E1E1;
                    border: 1px solid #3F3F46;
                }
                QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                    background-color: #252526;
                    color: #E1E1E1;
                    border: 1px solid #3F3F46;
                    padding: 3px;
                }
                QProgressBar {
                    border: 1px solid #3F3F46;
                    background-color: #252526;
                    text-align: center;
                    color: white;
                }
                QProgressBar::chunk {
                    background-color: #0E639C;
                }
                QCheckBox {
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 15px;
                    height: 15px;
                }
                QCheckBox::indicator:unchecked {
                    border: 1px solid #3F3F46;
                    background-color: #252526;
                }
                QCheckBox::indicator:checked {
                    border: 1px solid #3F3F46;
                    background-color: #0E639C;
                }
            """)
        else:
            # Set light theme
            self.setStyleSheet("")
    
    def show_help(self):
        """Show help documentation"""
        # In a real system, this would open help documentation
        # For the mock implementation, we'll just show a message
        QMessageBox.information(self, "Help", 
                               "QAOS Master UI Help\n\n"
                               "This is the master UI for the QAOS system, providing a comprehensive "
                               "interface for monitoring and controlling quantum resources, workloads, "
                               "and system status.\n\n"
                               "For more information, please refer to the QAOS documentation.")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop threads
        self.refresh_thread.stop()
        self.refresh_thread.wait()
        
        # Stop timers
        self.allocation_timer.stop()
        
        # Stop simulation if running
        if hasattr(self, 'sim_timer') and self.sim_timer.isActive():
            self.sim_timer.stop()
        
        if self.simulator.is_running():
            self.simulator.stop_simulation()
        
        event.accept()

def main():
    """Main function"""
    app = QApplication(sys.argv)
    window = QAOSMasterUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
```

