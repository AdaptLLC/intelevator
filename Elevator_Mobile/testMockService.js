/**
 * Test script for the mock elevator service
 * Run with: node testMockService.js
 */

import mockService from './services/mockService.js';

console.log('Testing Mock Elevator Service\n');
console.log('================================\n');

// Test 1: Get initial status
console.log('Test 1: Getting initial elevator status...');
mockService
  .queryElevatorStatus()
  .then((status) => {
    console.log('Initial Status:', JSON.stringify(status, null, 2));
    console.log('✓ Status query successful\n');
  })
  .catch((err) => {
    console.error('✗ Status query failed:', err);
  });

// Test 2: Call elevator
setTimeout(() => {
  console.log('Test 2: Calling elevator to floor 10 with HIGH priority...');
  mockService
    .callElevator(10, 'HIGH')
    .then((request) => {
      console.log('Request created:', JSON.stringify(request, null, 2));
      console.log('✓ Call elevator successful\n');
    })
    .catch((err) => {
      console.error('✗ Call elevator failed:', err);
    });
}, 1000);

// Test 3: Subscribe to updates
setTimeout(() => {
  console.log('Test 3: Subscribing to elevator updates...');
  let updateCount = 0;
  const unsubscribe = mockService.subscribe((status) => {
    updateCount++;
    console.log(`Update #${updateCount}:`, {
      floor: status.currentFloor,
      direction: status.direction,
      requests: status.requests.length,
    });

    if (updateCount >= 3) {
      console.log('✓ Subscription working, received 3 updates');
      console.log('\nTest 4: Unsubscribing...');
      unsubscribe();
      console.log('✓ Unsubscribed successfully\n');

      // Test 5: Reset
      setTimeout(() => {
        console.log('Test 5: Resetting elevator...');
        mockService.reset();
        mockService.queryElevatorStatus().then((status) => {
          console.log('Status after reset:', {
            floor: status.currentFloor,
            requests: status.requests.length,
          });
          console.log('✓ Reset successful\n');

          console.log('================================');
          console.log('All tests completed successfully!');
          console.log('Mock service is ready to use.');
          process.exit(0);
        });
      }, 1000);
    }
  });
}, 2000);

// Test error handling
setTimeout(() => {
  console.log('\nTest 6: Testing error handling with invalid floor...');
  mockService.callElevator(25, 'NORMAL').catch((err) => {
    console.log('✓ Correctly rejected invalid floor:', err.message);
  });
}, 3000);

// Prevent script from exiting immediately
setTimeout(() => {
  // Script will exit from the test completion callback
}, 10000);
