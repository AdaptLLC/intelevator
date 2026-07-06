import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  StatusBar,
  RefreshControl,
} from 'react-native';
import { createClient, Provider, useQuery, useMutation } from 'urql';
import config from './config';

// Create urql client
const client = createClient({
  url: config.graphqlUrl,
  fetchOptions: {
    headers: {
      'Content-Type': 'application/json',
    },
  },
});

// GraphQL queries and mutations
const ELEVATOR_STATUS_QUERY = `
  query {
    elevatorStatus {
      currentFloor
      nextFloor
      direction
      requests {
        id
        floor
        priority
      }
    }
  }
`;

const CALL_ELEVATOR_MUTATION = `
  mutation CallElevator($floor: Int!, $priority: PriorityEnum) {
    callElevator(floor: $floor, priority: $priority) {
      id
      floor
      priority
    }
  }
`;

function ElevatorApp() {
  const [selectedPriority, setSelectedPriority] = useState('NORMAL');
  const [refreshing, setRefreshing] = useState(false);

  // Query elevator status with polling
  const [{ data, fetching, error }, reexecuteQuery] = useQuery({
    query: ELEVATOR_STATUS_QUERY,
    requestPolicy: 'network-only',
  });

  // Mutation for calling elevator
  const [, callElevator] = useMutation(CALL_ELEVATOR_MUTATION);

  // Poll for updates every 2 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      reexecuteQuery({ requestPolicy: 'network-only' });
    }, 2000);

    return () => clearInterval(interval);
  }, [reexecuteQuery]);

  const handleCallElevator = async (floor) => {
    const result = await callElevator({
      floor,
      priority: selectedPriority,
    });

    if (result.error) {
      console.error('Error calling elevator:', result.error);
    } else {
      // Refresh status after calling
      reexecuteQuery({ requestPolicy: 'network-only' });
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    reexecuteQuery({ requestPolicy: 'network-only' });
    setTimeout(() => setRefreshing(false), 1000);
  };

  if (fetching && !data) {
    return (
      <View style={styles.container}>
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>
            Connecting to elevator system...
          </Text>
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.centerContent}>
          <Text style={styles.errorText}>Connection Error</Text>
          <Text style={styles.errorDetail}>{error.message}</Text>
          <Text style={styles.helpText}>Backend: {config.backendUrl}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => reexecuteQuery({ requestPolicy: 'network-only' })}
          >
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  const elevatorStatus = data?.elevatorStatus;
  const floors = [
    20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
  ];

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      <View style={styles.content}>
        <Text style={styles.title}>Elevator System (urql)</Text>

        {/* Current Status */}
        <View style={styles.statusCard}>
          <Text style={styles.statusLabel}>Current Floor</Text>
          <Text style={styles.statusValue}>
            {elevatorStatus?.currentFloor || 1}
          </Text>
          <Text style={styles.statusLabel}>
            Direction: {elevatorStatus?.direction || 'IDLE'}
          </Text>
          {elevatorStatus?.nextFloor && (
            <Text style={styles.statusLabel}>
              Next Floor: {elevatorStatus.nextFloor}
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
              const hasRequest = elevatorStatus?.requests?.some(
                (r) => r.floor === floor
              );
              const isCurrent = elevatorStatus?.currentFloor === floor;

              return (
                <TouchableOpacity
                  key={floor}
                  style={[
                    styles.floorButton,
                    isCurrent && styles.currentFloorButton,
                    hasRequest && styles.requestedFloorButton,
                  ]}
                  onPress={() => handleCallElevator(floor)}
                  disabled={isCurrent}
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
        {elevatorStatus?.requests && elevatorStatus.requests.length > 0 && (
          <View style={styles.requestsSection}>
            <Text style={styles.sectionTitle}>
              Active Requests ({elevatorStatus.requests.length})
            </Text>
            {elevatorStatus.requests.map((request) => (
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
      </View>
    </ScrollView>
  );
}

export default function App() {
  return (
    <Provider value={client}>
      <ElevatorApp />
    </Provider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  content: {
    padding: 20,
    paddingTop: 60,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
    color: '#333',
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FF3B30',
    marginBottom: 10,
  },
  errorDetail: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  helpText: {
    fontSize: 14,
    color: '#999',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
