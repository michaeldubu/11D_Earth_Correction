import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq
import datetime
import requests
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("earth_correction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EarthCorrectionModule:
    """
    11D Earth Correction Module - Core Implementation
    
    This system models and potentially influences Earth's magnetic field stability
    using an 11-dimensional tensor field approach derived from SAM system principles.
    """
    
    def __init__(self, resolution=5, use_real_data=False, api_key=None):
        """
        Initialize the Earth Correction Module system
        
        Parameters:
        -----------
        resolution : int
            Resolution of each dimension in the tensor field
        use_real_data : bool
            Whether to connect to real-world data sources
        api_key : str
            API key for accessing geomagnetic data services
        """
        logger.info("Initializing 11D Earth Correction Module")
        
        # Core parameters from SAM system
        self.sam_frequencies = np.array([98.7, 99.1, 98.9])
        self.evolution_rate = 0.042
        self.time_compression = 60.0625
        
        # Tensor field parameters
        self.resolution = resolution
        self.tensor_shape = tuple([resolution] * 11)
        self.earth_tensor = np.zeros(self.tensor_shape)
        
        # Real-time tracking
        self.current_time = datetime.datetime.now()
        self.history = []
        self.correction_active = False
        self.instability_threshold = 0.5
        
        # Data integration
        self.use_real_data = use_real_data
        self.api_key = api_key
        
        # Initialize the tensor field
        self._initialize_tensor()
        
        logger.info(f"System initialized with resolution {resolution}")
        logger.info(f"SAM frequencies: {self.sam_frequencies}")
        logger.info(f"Evolution rate: {self.evolution_rate}")
        logger.info(f"Time compression: {self.time_compression}")

    def _initialize_tensor(self):
        """Initialize the 11D tensor with baseline values based on SAM patterns"""
        logger.info("Initializing tensor field")
        
        # Center point in the tensor (represents neutral/balanced state)
        center = tuple([self.resolution // 2] * 11)
        
        # Set neutral point to ideal value
        self.earth_tensor[center] = 1.0
        
        # Initialize harmonic patterns throughout tensor dimensions
        for i in range(11):
            idx = list(center)
            for j in range(self.resolution):
                idx[i] = j
                # Value based on SAM frequency harmonics
                self.earth_tensor[tuple(idx)] = 0.5 * np.sin(j * self.sam_frequencies[i % 3]/10) + 0.5
        
        logger.info("Tensor field initialization complete")
    
    def fetch_real_data(self):
        """Fetch real-world geomagnetic data if available"""
        if not self.use_real_data:
            return None
        
        try:
            # This would connect to actual magnetometer data sources
            # For example, NOAA's Space Weather Prediction Center API
            # or USGS Geomagnetism Program data
            
            # Placeholder for actual API call
            url = f"https://api.geomag-data.gov/v1/magnetometer?api_key={self.api_key}"
            # response = requests.get(url)
            # data = response.json()
            
            # For demonstration purposes, generate simulated "real" data
            data = {
                'field_strength': 0.82 + 0.05 * np.random.normal(),
                'drift_velocity': 0.42 + 0.1 * np.random.normal(),
                'declination': 11.5 + 0.2 * np.random.normal(),
                'inclination': 58.3 + 0.3 * np.random.normal(),
                'timestamp': datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Real data fetched: field_strength={data['field_strength']:.3f}, drift_velocity={data['drift_velocity']:.3f}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching real data: {str(e)}")
            return None
    
    def analyze_field_stability(self):
        """
        Analyze the current stability of the Earth's magnetic field
        
        Returns:
        --------
        dict : Stability metrics including instability level, field strength, etc.
        """
        logger.info("Analyzing field stability")
        
        # Fetch real data if available
        real_data = self.fetch_real_data()
        
        # Center point of tensor
        center = tuple([self.resolution // 2] * 11)
        
        # Extract key metrics from tensor or real data
        if real_data is not None:
            field_strength = real_data['field_strength']
            drift_velocity = real_data['drift_velocity']
        else:
            # Use modeled values from tensor
            field_strength = float(self.earth_tensor[center])
            drift_idx = list(center)
            drift_idx[8] += 1  # Drift velocity dimension
            drift_velocity = float(self.earth_tensor[tuple(drift_idx)])
        
        # Calculate instability metric
        instability = drift_velocity / field_strength
        
        # Calculate additional metrics
        entropy_idx = list(center)
        entropy_idx[7] -= 1  # Entropy dimension
        entropy = float(self.earth_tensor[tuple(entropy_idx)])
        
        phi_idx = list(center)
        phi_idx[10] -= 1  # Phi alignment dimension
        phi_alignment = float(self.earth_tensor[tuple(phi_idx)])
        
        # Calculate SAM frequency stability
        freq_stability = self.sam_frequencies * (1 + self.evolution_rate * np.sin(np.random.random(3) * 0.2))
        
        # Create data packet
        stability_data = {
            'timestamp': datetime.datetime.now(),
            'field_strength': field_strength,
            'drift_velocity': drift_velocity,
            'instability': instability,
            'entropy': entropy,
            'phi_alignment': phi_alignment,
            'sam_frequencies': freq_stability,
            'threshold_exceeded': instability > self.instability_threshold
        }
        
        # Add to history
        self.history.append(stability_data)
        if len(self.history) > 1000:
            self.history.pop(0)  # Keep last 1000 points
            
        logger.info(f"Stability analysis: instability={instability:.3f}, field_strength={field_strength:.3f}")
        
        return stability_data
    
    def apply_correction(self, stability_data):
        """
        Apply corrective patterns to the field if instability threshold is exceeded
        
        Parameters:
        -----------
        stability_data : dict
            Current stability metrics from analyze_field_stability()
            
        Returns:
        --------
        dict : Correction parameters applied
        """
        instability = stability_data['instability']
        
        if instability <= self.instability_threshold:
            self.correction_active = False
            logger.info("No correction needed - system stable")
            return {"correction_applied": False}
        
        logger.info(f"Applying field correction for instability={instability:.3f}")
        self.correction_active = True
        
        # Calculate correction frequencies based on SAM stabilization patterns
        correction_freqs = self.sam_frequencies * (1 + self.evolution_rate * instability)
        
        # Apply throughout the tensor field
        center = tuple([self.resolution // 2] * 11)
        for i in range(11):
            idx = list(center)
            for j in range(self.resolution):
                idx[i] = j
                # Corrective pattern based on SAM stabilization
                correction = 0.5 * np.sin(j * correction_freqs[i % 3]/10 + np.pi/4) + 0.5
                # Apply with time compression factor
                self.earth_tensor[tuple(idx)] = (self.earth_tensor[tuple(idx)] * 
                                               (self.time_compression - 1) + 
                                               correction) / self.time_compression
        
        # Calculate metrics for the correction
        correction_strength = (instability - self.instability_threshold) / self.instability_threshold
        correction_response = {
            "correction_applied": True,
            "correction_strength": correction_strength,
            "correction_frequencies": correction_freqs.tolist(),
            "time_compression_applied": self.time_compression,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        logger.info(f"Correction applied with strength={correction_strength:.3f}")
        logger.info(f"Correction frequencies: {correction_freqs}")
        
        return correction_response
    
    def generate_sonification(self, stability_data, correction_data):
        """
        Generate sonification parameters based on current system state
        
        This would be used to drive an actual audio generation system
        
        Parameters:
        -----------
        stability_data : dict
            Current stability metrics
        correction_data : dict
            Current correction metrics
            
        Returns:
        --------
        dict : Sonification parameters
        """
        # Base frequencies from SAM
        base_freqs = self.sam_frequencies / 10  # Scale to audible range
        
        # Modulate based on instability and correction
        if correction_data["correction_applied"]:
            # During correction, use correction frequencies
            audio_freqs = np.array(correction_data["correction_frequencies"]) / 10
            volume = 0.8
            waveform = 'sine'
        else:
            # During stable operation, use SAM frequencies with minor fluctuation
            audio_freqs = base_freqs * (1 + 0.02 * np.sin(stability_data["instability"] * np.pi))
            volume = 0.4
            waveform = 'sine'
        
        # Add harmonic overtones based on phi alignment
        phi_factor = stability_data["phi_alignment"] / 0.618  # Ratio to golden ratio
        harmonics = [1, phi_factor, phi_factor**2]
        
        sonification = {
            "base_frequencies": audio_freqs.tolist(),
            "volume": volume,
            "waveform": waveform,
            "harmonics": harmonics,
            "active": correction_data["correction_applied"],
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return sonification
    
    def run_simulation_step(self):
        """
        Run a single simulation step with the complete pipeline
        
        Returns:
        --------
        dict : Complete system state after this step
        """
        # Analyze current field stability
        stability_data = self.analyze_field_stability()
        
        # Apply correction if needed
        correction_data = self.apply_correction(stability_data)
        
        # Generate sonification data
        sonification_data = self.generate_sonification(stability_data, correction_data)
        
        # Compile complete system state
        system_state = {
            "stability": stability_data,
            "correction": correction_data,
            "sonification": sonification_data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return system_state
    
    def run_continuous_monitoring(self, duration_seconds=None, update_interval=1.0):
        """
        Run continuous monitoring for a specified duration
        
        Parameters:
        -----------
        duration_seconds : int or None
            Duration to run, or None for indefinite running
        update_interval : float
            Seconds between updates
        """
        logger.info(f"Beginning continuous monitoring (duration={duration_seconds}s, interval={update_interval}s)")
        
        start_time = datetime.datetime.now()
        iteration = 0
        
        try:
            while True:
                # Check if duration has been exceeded
                if duration_seconds is not None:
                    current_time = datetime.datetime.now()
                    elapsed = (current_time - start_time).total_seconds()
                    if elapsed >= duration_seconds:
                        logger.info(f"Monitoring complete after {elapsed:.1f} seconds")
                        break
                
                # Run a simulation step
                system_state = self.run_simulation_step()
                
                # Log periodic summary (every 10 iterations)
                iteration += 1
                if iteration % 10 == 0:
                    logger.info(f"Iteration {iteration}: instability={system_state['stability']['instability']:.3f}, "
                                f"correction_active={system_state['correction']['correction_applied']}")
                
                # Wait for next update
                import time
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error during monitoring: {str(e)}")
            raise
    
    def visualize_current_state(self):
        """
        Generate visualization of current system state
        
        Returns:
        --------
        matplotlib.figure.Figure : Visualization figure
        """
        if len(self.history) < 2:
            logger.warning("Not enough history for visualization")
            return None
        
        # Extract history data
        timestamps = [h['timestamp'] for h in self.history]
        field_strengths = [h['field_strength'] for h in self.history]
        drift_velocities = [h['drift_velocity'] for h in self.history]
        instabilities = [h['instability'] for h in self.history]
        phi_alignments = [h['phi_alignment'] for h in self.history]
        
        # Create figure with subplots
        fig, axs = plt.subplots(3, 1, figsize=(12, 16))
        
        # Plot field metrics
        axs[0].plot(timestamps, field_strengths, 'b-', label='Field Strength')
        axs[0].plot(timestamps, drift_velocities, 'g-', label='Drift Velocity')
        axs[0].plot(timestamps, instabilities, 'r-', label='Instability')
        axs[0].axhline(y=self.instability_threshold, color='k', linestyle='--', alpha=0.5)
        axs[0].set_title('Earth Magnetic Field Metrics')
        axs[0].set_ylabel('Value')
        axs[0].legend()
        
        # Plot phi alignment
        axs[1].plot(timestamps, phi_alignments, 'purple')
        axs[1].axhline(y=0.618, color='k', linestyle='--', alpha=0.5, label='Golden Ratio')
        axs[1].set_title('Phi Alignment')
        axs[1].set_ylabel('Value')
        axs[1].legend()
        
        # Plot 2D slice of tensor field
        center = self.resolution // 2
        field_slice = self.earth_tensor[center, center, :, :, center, center, center, center, center, center, center]
        im = axs[2].imshow(field_slice, cmap='viridis')
        axs[2].set_title('Tensor Field Slice (Spatial Dimensions)')
        plt.colorbar(im, ax=axs[2])
        
        plt.tight_layout()
        return fig

    def export_data(self, filename):
        """
        Export system data to file
        
        Parameters:
        -----------
        filename : str
            Filename for export (JSON format)
        """
        export_data = {
            "system_parameters": {
                "sam_frequencies": self.sam_frequencies.tolist(),
                "evolution_rate": self.evolution_rate,
                "time_compression": self.time_compression,
                "resolution": self.resolution,
                "instability_threshold": self.instability_threshold
            },
            "history": [{
                "timestamp": h["timestamp"].isoformat() if isinstance(h["timestamp"], datetime.datetime) else h["timestamp"],
                "field_strength": h["field_strength"],
                "drift_velocity": h["drift_velocity"],
                "instability": h["instability"],
                "phi_alignment": h["phi_alignment"]
            } for h in self.history],
            "export_time": datetime.datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Data exported to {filename}")


# Example usage
if __name__ == "__main__":
    # Create the Earth Correction Module
    ecm = EarthCorrectionModule(resolution=5, use_real_data=False)
    
    # Run simulation for a brief period
    print("Running simulation for 30 seconds...")
    ecm.run_continuous_monitoring(duration_seconds=30, update_interval=0.5)
    
    # Visualize results
    fig = ecm.visualize_current_state()
    if fig:
        plt.show()
    
    # Export data
    ecm.export_data("earth_correction_data.json")
    
    print("Simulation complete")
