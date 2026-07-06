import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  StatusBar,
} from 'react-native';
import {
  ApolloProvider,
  gql,
  useMutation,
  useSubscription,
} from '@apollo/client';
import createMockApolloClient, {
  ELEVATOR_UPDATES_SUBSCRIPTION,
  CALL_ELEVATOR_MUTATION,
} from './services/mockApolloClient';

// Create mock Apollo client
const client = createMockApolloClient();

// Main Elevator Component
function ElevatorApp() {
  const [selectedPriority, setSelectedPriority] = useState('NORMAL');

  // Subscribe to elevator updates using mock service
  const { data, loading, error } = useSubscription(
    ELEVATOR_UPDATES_SUBSCRIPTION
  );

  // Call elevator mutation using mock service
  const [callElevator] = useMutation(CALL_ELEVATOR_MUTATION, {
    onCompleted: () => {
      console.log('Elevator called successfully');
    },
    onError: (error) => {
      console.error('Error calling elevator:', error);
    },
  });

  const handleCallElevator = (floor) => {
    callElevator({
      variables: {
        floor,
        priority: selectedPriority,
      },
    });
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
        <Text style={styles.errorText}>Error: {error.message}</Text>
        <Text style={styles.helpText}>Mock service encountered an error</Text>
      </View>
    );
  }

  const status = data?.elevatorUpdates;
  const floors = [
    20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Elevator System</Text>
        <View style={styles.mockBadge}>
          <Text style={styles.mockBadgeText}>MOCK MODE</Text>
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
          <Text style={styles.mockInfoTitle}>Mock Mode Information</Text>
          <Text style={styles.mockInfoText}>
            • Elevator moves automatically every 2 seconds
          </Text>
          <Text style={styles.mockInfoText}>
            • Follows a predefined cycle of 40 states
          </Text>
          <Text style={styles.mockInfoText}>
            • Your requests are added to the simulation
          </Text>
          <Text style={styles.mockInfoText}>
            • No backend connection required
          </Text>
        </View>
      </View>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
    </ScrollView>
  );
}

// App with Apollo Provider
export default function AppMocked() {
  return (
    <ApolloProvider client={client}>
      <ElevatorApp />
    </ApolloProvider>
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
    backgroundColor: '#FF9500',
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
    backgroundColor: '#f0f8ff',
    borderRadius: 8,
    padding: 16,
    marginTop: 20,
    borderWidth: 1,
    borderColor: '#007AFF',
    borderStyle: 'dashed',
  },
  mockInfoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#007AFF',
    marginBottom: 8,
  },
  mockInfoText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});
