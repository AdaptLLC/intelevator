import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  StatusBar,
  ActivityIndicator,
} from 'react-native';
import {
  ApolloClient,
  InMemoryCache,
  ApolloProvider,
  gql,
  useQuery,
} from '@apollo/client';
import { createHttpLink } from '@apollo/client';
import config from './config';

// Simple HTTP-only Apollo Client (no subscriptions for now)
const httpLink = createHttpLink({
  uri: config.graphqlUrl,
});

const client = new ApolloClient({
  link: httpLink,
  cache: new InMemoryCache(),
});

// Test query
const TEST_QUERY = gql`
  query TestQuery {
    elevatorStatus {
      currentFloor
      direction
    }
  }
`;

function ElevatorStatus() {
  const { loading, error, data } = useQuery(TEST_QUERY);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.text}>Loading...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Error: {error.message}</Text>
        <Text style={styles.text}>Backend URL: {config.backendUrl}</Text>
      </View>
    );
  }

  return (
    <View style={styles.center}>
      <Text style={styles.title}>Elevator Status</Text>
      <Text style={styles.floorText}>
        Floor: {data?.elevatorStatus?.currentFloor || 'N/A'}
      </Text>
      <Text style={styles.text}>
        Direction: {data?.elevatorStatus?.direction || 'IDLE'}
      </Text>
    </View>
  );
}

export default function App() {
  return (
    <ApolloProvider client={client}>
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
        <ElevatorStatus />
      </View>
    </ApolloProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  floorText: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 10,
  },
  text: {
    fontSize: 18,
    color: '#666',
    marginTop: 10,
  },
  errorText: {
    fontSize: 16,
    color: '#FF3B30',
    marginBottom: 10,
  },
});
