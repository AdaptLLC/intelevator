// React Native's Metro bundler handles require() correctly
const elevatorStatesData = require('../mockData/elevatorStates');

/**
 * Mock Service for simulating backend elevator system
 * Provides GraphQL-like API without actual backend connection
 */
class MockElevatorService {
  constructor() {
    console.log('MockElevatorService: Initializing with data:', elevatorStatesData);
    this.states = elevatorStatesData.states || [];
    this.cycleLength = elevatorStatesData.cycleLength || 40;
    this.updateInterval = elevatorStatesData.updateInterval || 2000;
    this.currentStateIndex = 0;
    this.subscribers = [];
    this.requestIdCounter = 1000;
    this.isRunning = false;
    this.intervalId = null;

    // Track dynamic requests added by user
    this.dynamicRequests = [];

    // Start the simulation
    this.start();
  }

  /**
   * Start the elevator simulation
   */
  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.intervalId = setInterval(() => {
      this.advanceState();
    }, this.updateInterval);
  }

  /**
   * Stop the elevator simulation
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
  }

  /**
   * Advance to the next state in the cycle
   */
  advanceState() {
    this.currentStateIndex = (this.currentStateIndex + 1) % this.cycleLength;
    // Ensure index is valid
    if (this.currentStateIndex >= this.states.length) {
      console.log('MockService: Resetting to index 0, was:', this.currentStateIndex);
      this.currentStateIndex = 0;
    }
    this.notifySubscribers();
  }

  /**
   * Get current elevator status
   */
  getCurrentStatus() {
    // Ensure we have valid states data
    if (!this.states || this.states.length === 0) {
      console.log('MockService: No states available, returning default');
      return {
        currentFloor: 1,
        nextFloor: null,
        direction: 'IDLE',
        requests: []
      };
    }

    const baseState = this.states[this.currentStateIndex];

    if (!baseState) {
      console.log('MockService: Invalid state index:', this.currentStateIndex);
      return {
        currentFloor: 1,
        nextFloor: null,
        direction: 'IDLE',
        requests: []
      };
    }

    // Merge dynamic requests with predefined requests
    const allRequests = [
      ...(baseState.requests || []),
      ...this.dynamicRequests.filter(req => {
        // Only include dynamic requests that haven't been reached yet
        const currentFloor = baseState.currentFloor;
        const direction = baseState.direction;

        if (direction === 'UP') {
          return req.floor > currentFloor;
        } else if (direction === 'DOWN') {
          return req.floor < currentFloor;
        }
        return true; // Keep request if elevator is IDLE
      })
    ];

    // Sort requests based on direction and priority
    const sortedRequests = this.sortRequests(allRequests, baseState.direction);

    return {
      currentFloor: baseState.currentFloor || 1,
      nextFloor: sortedRequests.length > 0 ? sortedRequests[0].floor : baseState.nextFloor,
      direction: baseState.direction || 'IDLE',
      requests: sortedRequests || []
    };
  }

  /**
   * Sort requests based on SCAN algorithm
   */
  sortRequests(requests, direction) {
    if (requests.length === 0) return [];

    // Sort by priority first, then by floor based on direction
    return requests.sort((a, b) => {
      // Priority weights: EMERGENCY = 3, HIGH = 2, NORMAL = 1
      const priorityWeight = {
        'EMERGENCY': 3,
        'HIGH': 2,
        'NORMAL': 1
      };

      const aPriority = priorityWeight[a.priority] || 1;
      const bPriority = priorityWeight[b.priority] || 1;

      // Higher priority first
      if (aPriority !== bPriority) {
        return bPriority - aPriority;
      }

      // Same priority, sort by floor based on direction
      if (direction === 'UP') {
        return a.floor - b.floor; // Ascending for UP
      } else if (direction === 'DOWN') {
        return b.floor - a.floor; // Descending for DOWN
      }

      return 0; // IDLE - maintain order
    });
  }

  /**
   * Subscribe to elevator updates (simulates GraphQL subscription)
   */
  subscribe(callback) {
    const subscription = {
      id: Date.now(),
      callback
    };

    this.subscribers.push(subscription);

    // Immediately send current status
    callback(this.getCurrentStatus());

    // Return unsubscribe function
    return () => {
      this.subscribers = this.subscribers.filter(sub => sub.id !== subscription.id);
    };
  }

  /**
   * Notify all subscribers of state change
   */
  notifySubscribers() {
    const status = this.getCurrentStatus();
    this.subscribers.forEach(sub => {
      sub.callback(status);
    });
  }

  /**
   * Call elevator to a floor (simulates GraphQL mutation)
   */
  async callElevator(floor, priority = 'NORMAL') {
    // Validate floor
    if (floor < 1 || floor > 20) {
      throw new Error(`Invalid floor: ${floor}. Must be between 1 and 20.`);
    }

    // Validate priority
    const validPriorities = ['NORMAL', 'HIGH', 'EMERGENCY'];
    if (!validPriorities.includes(priority)) {
      throw new Error(`Invalid priority: ${priority}. Must be one of ${validPriorities.join(', ')}.`);
    }

    // Check if request already exists for this floor
    const currentStatus = this.getCurrentStatus();
    const existingRequest = currentStatus.requests.find(req => req.floor === floor);

    if (existingRequest) {
      // Update priority if new one is higher
      const priorityWeight = { 'EMERGENCY': 3, 'HIGH': 2, 'NORMAL': 1 };
      if (priorityWeight[priority] > priorityWeight[existingRequest.priority]) {
        existingRequest.priority = priority;
        this.notifySubscribers();
      }
      return existingRequest;
    }

    // Create new request
    const newRequest = {
      id: `req-${++this.requestIdCounter}`,
      floor,
      priority,
      requested_at: new Date().toISOString()
    };

    // Add to dynamic requests
    this.dynamicRequests.push(newRequest);

    // Notify subscribers
    this.notifySubscribers();

    // Simulate async response
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(newRequest);
      }, 100);
    });
  }

  /**
   * Query elevator status (simulates GraphQL query)
   */
  async queryElevatorStatus() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(this.getCurrentStatus());
      }, 50);
    });
  }

  /**
   * Reset to initial state
   */
  reset() {
    this.currentStateIndex = 0;
    this.dynamicRequests = [];
    this.requestIdCounter = 1000;
    this.notifySubscribers();
  }

  /**
   * Clean up dynamic requests that have been reached
   */
  cleanupReachedRequests() {
    const currentFloor = this.states[this.currentStateIndex].currentFloor;

    // Remove dynamic requests for the current floor
    this.dynamicRequests = this.dynamicRequests.filter(req => req.floor !== currentFloor);
  }
}

// Create singleton instance
const mockService = new MockElevatorService();

// Export for use in React Native app
module.exports = mockService;

// Also export individual functions for convenience
module.exports.subscribeToElevatorUpdates = (callback) => mockService.subscribe(callback);
module.exports.callElevator = (floor, priority) => mockService.callElevator(floor, priority);
module.exports.queryElevatorStatus = () => mockService.queryElevatorStatus();
module.exports.resetElevator = () => mockService.reset();