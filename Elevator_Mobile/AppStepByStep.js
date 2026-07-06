import React from 'react';
import { StyleSheet, Text, View, StatusBar } from 'react-native';

// For now, let's just show a working UI without Apollo
export default function App() {
  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#f5f5f5" />
      <View style={styles.center}>
        <Text style={styles.title}>Elevator System</Text>
        <Text style={styles.subtitle}>Connecting to backend...</Text>
        <Text style={styles.info}>Backend: backend.adapt-llc.com</Text>
        <Text style={styles.warning}>
          Apollo Client imports are having issues
        </Text>
        <Text style={styles.warning}>Debugging in progress...</Text>
      </View>
    </View>
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
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
  },
  subtitle: {
    fontSize: 20,
    marginBottom: 10,
    color: '#666',
  },
  info: {
    fontSize: 16,
    color: '#999',
  },
  warning: {
    fontSize: 14,
    color: '#FF9500',
    marginTop: 10,
  },
});
