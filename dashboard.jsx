import React, { useState, useEffect, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';

// Simulated data generator for the Earth correction module
const generateData = (time) => {
  // Sam reference frequencies
  const samFrequencies = [98.7, 99.1, 98.9];
  const evolutionRate = 0.042;
  const timeCompression = 60.0625;
  
  // Simulate magnetic field readings
  const fieldStrength = 0.82 + 0.05 * Math.sin(time / 10);
  
  // Simulate drift velocity with occasional instability
  const driftBase = 0.42;
  const driftSpike = time % 60 > 50 ? 0.3 * Math.sin((time % 60 - 50)) : 0;
  const driftVelocity = driftBase + driftSpike;
  
  // Calculate instability based on drift and field strength
  const instability = driftVelocity / fieldStrength;
  
  // Simulated resonance patterns
  const resonancePattern = samFrequencies.map((freq, i) => ({
    name: `${freq} Hz`,
    value: 0.6 + 0.4 * Math.sin(time / 15 + i * Math.PI / 3),
    fullMark: 1
  }));
  
  // Phi alignment (golden ratio coherence)
  const phiAlignment = 0.618 + 0.05 * Math.sin(time / 25);
  
  // Dimensions data for radar chart
  const dimensionsData = [
    { dimension: "Spatial", value: 0.8 + 0.1 * Math.sin(time / 20) },
    { dimension: "Temporal", value: 0.7 + 0.1 * Math.sin(time / 18) },
    { dimension: "Magnetic", value: fieldStrength },
    { dimension: "Quantum", value: 0.5 + 0.2 * Math.cos(time / 30) },
    { dimension: "Psi-Field", value: 0.33 + 0.15 * Math.sin(time / 40) },
    { dimension: "Entropy", value: 0.1 + 0.1 * (1 + Math.sin(time / 35)) },
    { dimension: "Intent", value: 0.9 - 0.2 * driftSpike },
    { dimension: "Drift", value: driftVelocity },
    { dimension: "Harmonic", value: 0.67 + 0.1 * Math.sin(time / 22) },
    { dimension: "Phi", value: phiAlignment },
    { dimension: "Resonance", value: 0.75 + 0.15 * Math.sin(time / 25) }
  ];
  
  // Calculate correction response (increases when instability is high)
  const correctionResponse = instability > 0.5 ? 0.5 + instability : 0;
  
  // Return complete data object
  return {
    time,
    fieldStrength,
    driftVelocity,
    instability,
    resonancePattern,
    phiAlignment,
    dimensionsData,
    correctionResponse,
    correctionActive: instability > 0.5,
    samFreqStability: samFrequencies.map((freq, i) => 
      freq * (1 + evolutionRate * (Math.sin(time / 30 + i * Math.PI / 4) * 0.1))
    )
  };
};

// Main dashboard component
const EarthCorrectionDashboard = () => {
  // State for time progression and data
  const [time, setTime] = useState(0);
  const [data, setData] = useState(generateData(0));
  const [historyData, setHistoryData] = useState([]);
  
  // Audio context for sonification
  const audioContextRef = useRef(null);
  const oscillatorsRef = useRef([]);
  
  // Initialize audio
  useEffect(() => {
    // Create audio context for sonification
    audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    
    // Create oscillators for Sam frequencies
    oscillatorsRef.current = data.samFreqStability.map(freq => {
      const osc = audioContextRef.current.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = freq / 10; // Scaled down to audible range
      
      const gainNode = audioContextRef.current.createGain();
      gainNode.gain.value = 0; // Start with zero volume
      
      osc.connect(gainNode);
      gainNode.connect(audioContextRef.current.destination);
      
      osc.start();
      return { oscillator: osc, gain: gainNode };
    });
    
    // Cleanup
    return () => {
      oscillatorsRef.current.forEach(({ oscillator }) => {
        oscillator.stop();
      });
    };
  }, []);
  
  // Update time and data every 100ms
  useEffect(() => {
    const interval = setInterval(() => {
      const newTime = time + 1;
      const newData = generateData(newTime);
      
      // Update historical data (keep last 100 points)
      setHistoryData(prev => {
        const updated = [...prev, {
          time: newTime,
          fieldStrength: newData.fieldStrength,
          driftVelocity: newData.driftVelocity,
          instability: newData.instability,
          correctionResponse: newData.correctionResponse
        }];
        
        if (updated.length > 100) {
          return updated.slice(-100);
        }
        return updated;
      });
      
      // Update audio based on system state
      oscillatorsRef.current.forEach((osc, i) => {
        // Update frequency
        osc.oscillator.frequency.value = newData.samFreqStability[i] / 10;
        
        // Set volume based on correction activity
        osc.gain.gain.value = newData.correctionActive ? 0.1 : 0;
      });
      
      setTime(newTime);
      setData(newData);
    }, 100);
    
    return () => clearInterval(interval);
  }, [time]);
  
  return (
    <div className="flex flex-col w-full max-w-6xl mx-auto p-4 bg-gray-900 text-white rounded-lg">
      <h1 className="text-2xl font-bold mb-4 text-center">11D Earth Correction Module Dashboard</h1>
      
      {/* Status indicators */}
      <div className="flex justify-between mb-6">
        <div className="bg-gray-800 p-3 rounded-lg text-center w-1/4">
          <h3 className="text-sm font-medium mb-1">Field Strength</h3>
          <div className="text-xl font-bold">{data.fieldStrength.toFixed(3)}</div>
        </div>
        
        <div className="bg-gray-800 p-3 rounded-lg text-center w-1/4">
          <h3 className="text-sm font-medium mb-1">Drift Velocity</h3>
          <div className="text-xl font-bold">{data.driftVelocity.toFixed(3)}</div>
        </div>
        
        <div className={`p-3 rounded-lg text-center w-1/4 ${
          data.instability > 0.6 ? 'bg-red-900' : 
          data.instability > 0.5 ? 'bg-yellow-900' : 'bg-green-900'
        }`}>
          <h3 className="text-sm font-medium mb-1">Instability</h3>
          <div className="text-xl font-bold">{data.instability.toFixed(3)}</div>
        </div>
        
        <div className={`p-3 rounded-lg text-center w-1/4 ${
          data.correctionActive ? 'bg-blue-900 animate-pulse' : 'bg-gray-800'
        }`}>
          <h3 className="text-sm font-medium mb-1">Correction Status</h3>
          <div className="text-xl font-bold">{data.correctionActive ? 'ACTIVE' : 'Standby'}</div>
        </div>
      </div>
      
      {/* Charts row */}
      <div className="flex mb-6 h-64">
        {/* Historical trends */}
        <div className="w-2/3 bg-gray-800 rounded-lg p-3 mr-4">
          <h3 className="text-sm font-medium mb-2">System Telemetry</h3>
          <ResponsiveContainer width="100%" height="90%">
            <LineChart data={historyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#444" />
              <XAxis dataKey="time" stroke="#999" />
              <YAxis stroke="#999" />
              <Tooltip contentStyle={{ backgroundColor: '#333', borderColor: '#555' }} />
              <Legend />
              <Line type="monotone" dataKey="fieldStrength" stroke="#8884d8" dot={false} />
              <Line type="monotone" dataKey="driftVelocity" stroke="#82ca9d" dot={false} />
              <Line type="monotone" dataKey="instability" stroke="#ff8042" dot={false} />
              <Line type="monotone" dataKey="correctionResponse" stroke="#0088fe" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* 11D Radar */}
        <div className="w-1/3 bg-gray-800 rounded-lg p-3">
          <h3 className="text-sm font-medium mb-2">11D State</h3>
          <ResponsiveContainer width="100%" height="90%">
            <RadarChart outerRadius="80%" data={data.dimensionsData}>
              <PolarGrid stroke="#555" />
              <PolarAngleAxis dataKey="dimension" stroke="#999" />
              <PolarRadiusAxis stroke="#999" />
              <Radar name="Current State" dataKey="value" stroke="#8884d8" 
                    fill="#8884d8" fillOpacity={0.6} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Sam frequencies and resonance patterns */}
      <div className="flex mb-6">
        <div className="w-1/2 bg-gray-800 rounded-lg p-3 mr-4">
          <h3 className="text-sm font-medium mb-2">SAM Frequency Stability</h3>
          <div className="flex justify-around h-12 items-end">
            {data.samFreqStability.map((freq, i) => (
              <div key={i} className="flex flex-col items-center">
                <div className="text-xs mb-1">{freq.toFixed(3)} Hz</div>
                <div className={`w-8 bg-blue-500 rounded-t-sm`} 
                     style={{ 
                       height: `${Math.min(100, (freq - 98) * 100)}%`,
                       backgroundColor: data.correctionActive ? '#3b82f6' : '#1e40af'
                     }}>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="w-1/2 bg-gray-800 rounded-lg p-3">
          <h3 className="text-sm font-medium mb-2">Phi Alignment</h3>
          <div className="flex justify-center items-center h-12">
            <div className="h-4 w-full bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  data.phiAlignment > 0.618 ? 'bg-green-500' : 'bg-yellow-500'
                }`} 
                style={{ width: `${data.phiAlignment * 100}%` }}>
              </div>
            </div>
            <div className="ml-3">{data.phiAlignment.toFixed(4)}</div>
          </div>
        </div>
      </div>
      
      {/* Resonance pattern */}
      <div className="bg-gray-800 rounded-lg p-3 mb-4">
        <h3 className="text-sm font-medium mb-2">Resonance Pattern</h3>
        <div className="flex justify-around h-12 items-end">
          {data.resonancePattern.map((point, i) => (
            <div key={i} className="flex flex-col items-center">
              <div className="text-xs mb-1">{point.name}</div>
              <div className="w-8 bg-purple-500 rounded-t-sm" 
                   style={{ height: `${point.value * 100}%` }}>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Control panel for sound */}
      <div className="bg-gray-800 rounded-lg p-3">
        <h3 className="text-sm font-medium mb-2">Sonification Status</h3>
        <div className="flex items-center justify-between">
          <div>
            <span className={`inline-block w-3 h-3 rounded-full mr-2 ${
              data.correctionActive ? 'bg-blue-500 animate-pulse' : 'bg-gray-500'
            }`}></span>
            {data.correctionActive ? 'Sonic output active' : 'Silent - Awaiting instability threshold'}
          </div>
          <div className="text-xs text-gray-400">
            Frequencies: {data.samFreqStability.map(f => f.toFixed(1)).join(' Hz, ')} Hz
          </div>
        </div>
      </div>
    </div>
  );
};

export default EarthCorrectionDashboard;
