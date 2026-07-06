import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import mockService from './services/mockService';

// Polling-based Elevator App using Mock Service
export default function AppMockedPolling() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPriority, setSelectedPriority] = useState('NORMAL');

  // Poll for elevator status
  useEffect(() => {
    let intervalId;

    const fetchStatus = async () => {
      try {
        const data = await mockService.queryElevatorStatus();
        setStatus(data);
        setLoading(false);
        setError(null);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    // Initial fetch
    fetchStatus();

    // Set up polling interval (every 2 seconds)
    intervalId = setInterval(fetchStatus, 2000);

    // Cleanup on unmount
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, []);

  const handleCallElevator = async (floor) => {
    try {
      await mockService.callElevator(floor, selectedPriority);
      console.log(
        `Elevator called to floor ${floor} with priority ${selectedPriority}`
      );

      // Immediately fetch new status
      const data = await mockService.queryElevatorStatus();
      setStatus(data);
    } catch (err) {
      console.error('Error calling elevator:', err);
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>
          Initializing mock elevator system...
        </Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Error: {error}</Text>
        <Text style={styles.helpText}>Mock service encountered an error</Text>
      </View>
    );
  }

  const floors = [
    20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Elevator System</Text>
        <View style={styles.mockBadge}>
          <Text style={styles.mockBadgeText}>MOCK MODE (POLLING)</Text>
        </View>

        {/* Current Status */}
        <View style={styles.statusCard}>
          <Text style={styles.statusLabel}>Current Floor</Text>
          <Text style={styles.statusValue}>{status?.currentFloor || '--'}</Text>
          <Text style={styles.statusLabel}>
            Direction: {status?.direction || 'IDLE'}
          </Text>
          {status?.nextFloor && (
            <Text style={styles.statusLabel}>
              Next Floor: {status.nextFloor}
            </Text>
          )}
        </View>

        {/* Priority Selector */}
        <View style={styles.prioritySection}>
          <Text style={styles.sectionTitle}>Priority Level</Text>
          <View style={styles.priorityButtons}>
            {['NORMAL', 'HIGH', 'EMERGENCY'].map((priority) => (
              <TouchableOpacity
                key={priority}
                style={[
                  styles.priorityButton,
                  selectedPriority === priority && styles.priorityButtonActive,
                  priority === 'EMERGENCY' && styles.emergencyButton,
                ]}
                onPress={() => setSelectedPriority(priority)}
              >
                <Text
                  style={[
                    styles.priorityButtonText,
                    selectedPriority === priority &&
                      styles.priorityButtonTextActive,
                  ]}
                >
                  {priority}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Floor Buttons */}
        <View style={styles.floorSection}>
          <Text style={styles.sectionTitle}>Call Elevator to Floor</Text>
          <View style={styles.floorGrid}>
            {floors.map((floor) => {
              const hasRequest = status?.requests?.some(
                (r) => r.floor === floor
              );
              const isCurrent = status?.currentFloor === floor;

              return (
                <TouchableOpacity
                  key={floor}
                  style={[
                    styles.floorButton,
                    isCurrent && styles.currentFloorButton,
                    hasRequest && styles.requestedFloorButton,
                  ]}
                  onPress={() => handleCallElevator(floor)}
                >
                  <Text
                    style={[
                      styles.floorButtonText,
                      (isCurrent || hasRequest) && styles.floorButtonTextActive,
                    ]}
                  >
                    {floor}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* Active Requests */}
        {status?.requests && status.requests.length > 0 && (
          <View style={styles.requestsSection}>
            <Text style={styles.sectionTitle}>Active Requests</Text>
            {status.requests.map((request) => (
              <View key={request.id} style={styles.requestCard}>
                <Text style={styles.requestFloor}>Floor {request.floor}</Text>
                <Text
                  style={[
                    styles.requestPriority,
                    request.priority === 'EMERGENCY' && styles.emergencyText,
                    request.priority === 'HIGH' && styles.highText,
                  ]}
                >
                  {request.priority}
                </Text>
              </View>
            ))}
          </View>
        )}

        {/* Mock Info */}
        <View style={styles.mockInfoSection}>
          <Text style={styles.mockInfoTitle}>Mock Polling Mode</Text>
          <Text style={styles.mockInfoText}>
            • Updates via polling every 2 seconds
          </Text>
          <Text style={styles.mockInfoText}>
            • No WebSocket connection needed
          </Text>
          <Text style={styles.mockInfoText}>
            • Simulates elevator movement locally
          </Text>
          <Text style={styles.mockInfoText}>
            • Perfect for offline development
          </Text>
        </View>

        {/* Reset Button */}
        <TouchableOpacity
          style={styles.resetButton}
          onPress={() => {
            mockService.reset();
            mockService.queryElevatorStatus().then(setStatus);
          }}
        >
          <Text style={styles.resetButtonText}>Reset Simulation</Text>
        </TouchableOpacity>
      </View>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  content: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
    color: '#333',
  },
  mockBadge: {
    backgroundColor: '#8E44AD',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    alignSelf: 'center',
    marginBottom: 20,
  },
  mockBadgeText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 12,
  },
  statusCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 16,
    color: '#666',
    marginTop: 8,
  },
  statusValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
  },
  prioritySection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  priorityButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  priorityButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#ddd',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  priorityButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  emergencyButton: {
    borderColor: '#FF3B30',
  },
  priorityButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
  },
  priorityButtonTextActive: {
    color: '#fff',
  },
  floorSection: {
    marginBottom: 20,
  },
  floorGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  floorButton: {
    width: '18%',
    aspectRatio: 1,
    backgroundColor: '#fff',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#ddd',
    margin: 4,
  },
  currentFloorButton: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  requestedFloorButton: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
  },
  floorButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  floorButtonTextActive: {
    color: '#fff',
  },
  requestsSection: {
    marginBottom: 20,
  },
  requestCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8,
  },
  requestFloor: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  requestPriority: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
  },
  emergencyText: {
    color: '#FF3B30',
  },
  highText: {
    color: '#FF9500',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    textAlign: 'center',
    marginBottom: 8,
  },
  helpText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
  mockInfoSection: {
    backgroundColor: '#f0f0ff',
    borderRadius: 8,
    padding: 16,
    marginTop: 20,
    borderWidth: 1,
    borderColor: '#8E44AD',
    borderStyle: 'dashed',
  },
  mockInfoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#8E44AD',
    marginBottom: 8,
  },
  mockInfoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  resetButton: {
    backgroundColor: '#8E44AD',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignSelf: 'center',
    marginTop: 20,
  },
  resetButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
});
