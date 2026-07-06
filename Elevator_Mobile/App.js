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
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  gql,
  useMutation,
  useSubscription,
} from '@apollo/client';
import { WebSocketLink } from '@apollo/client/link/ws';
import { createHttpLink } from '@apollo/client';
import { split } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { SubscriptionClient } from 'subscriptions-transport-ws';
import config from './config';

// HTTP Link for queries and mutations
const httpLink = createHttpLink({
  uri: config.graphqlUrl,
});

// Create WebSocket client for subscriptions
// React Native provides WebSocket globally, no need to import
const wsClient = new SubscriptionClient(
  config.graphqlWsUrl,
  {
    reconnect: true,
    connectionParams: {
      // Add any authentication or connection params here if needed
    },
  },
  WebSocket // Pass the global WebSocket to SubscriptionClient
);

// WebSocket Link for subscriptions
const wsLink = new WebSocketLink(wsClient);

// Split traffic between HTTP and WebSocket
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  wsLink,
  httpLink
);

// Apollo Client
const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});

// GraphQL Queries
const ELEVATOR_STATUS = gql`
  subscription {
    elevatorUpdates {
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

const CALL_ELEVATOR = gql`
  mutation CallElevator($floor: Int!, $priority: PriorityEnum) {
    callElevator(floor: $floor, priority: $priority) {
      id
      floor
      priority
    }
  }
`;

// Main Elevator Component
function ElevatorApp() {
  const [selectedPriority, setSelectedPriority] = useState('NORMAL');

  // Subscribe to elevator updates
  const { data, loading, error } = useSubscription(ELEVATOR_STATUS);

  // Call elevator mutation
  const [callElevator] = useMutation(CALL_ELEVATOR, {
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
        <Text style={styles.loadingText}>Connecting to elevator system...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Error: {error.message}</Text>
        <Text style={styles.helpText}>
          Check that backend is running at {config.backendUrl}
        </Text>
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

        {/* Current Status */}
        <View style={styles.statusCard}>
          <Text style={styles.statusLabel}>Current Floor</Text>
          <Text style={styles.statusValue}>{status?.currentFloor}</Text>
          <Text style={styles.statusLabel}>Direction: {status?.direction}</Text>
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
      </View>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
    </ScrollView>
  );
}

// App with Apollo Provider
export default function App() {
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
});
