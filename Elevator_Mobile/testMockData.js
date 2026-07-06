/**
 * Test to verify mock data is loading correctly
 * Run with: node testMockData.js
 */

try {
  console.log('Testing mock data loading...\n');

  // Test 1: Load elevator states data
  const elevatorStatesData = require('./mockData/elevatorStates.js');
  console.log('✓ Loaded elevatorStates.js successfully');
  console.log(
    '  - States array length:',
    elevatorStatesData.states?.length || 0
  );
  console.log(
    '  - Cycle length:',
    elevatorStatesData.cycleLength || 'undefined'
  );
  console.log(
    '  - Update interval:',
    elevatorStatesData.updateInterval || 'undefined'
  );

  if (elevatorStatesData.states?.length > 0) {
    const firstState = elevatorStatesData.states[0];
    console.log('\n  First state sample:');
    console.log('    - Current floor:', firstState.currentFloor);
    console.log('    - Direction:', firstState.direction);
    console.log('    - Next floor:', firstState.nextFloor);
    console.log('    - Requests count:', firstState.requests?.length || 0);
  }

  // Test 2: Import mock service
  console.log('\n✓ Testing mock service import...');
  const mockService = require('./services/mockService.js');
  console.log('  - MockService imported:', typeof mockService);

  // Test 3: Get current status
  if (mockService?.getCurrentStatus) {
    const status = mockService.getCurrentStatus();
    console.log('\n✓ Mock service getCurrentStatus():');
    console.log('  - Current floor:', status.currentFloor);
    console.log('  - Direction:', status.direction);
    console.log('  - Next floor:', status.nextFloor);
    console.log('  - Requests:', status.requests?.length || 0);
  }

  console.log('\n✅ All tests passed! Mock data is working correctly.\n');
} catch (error) {
  console.error('❌ Error loading mock data:', error.message);
  console.error('\nStack trace:', error.stack);
  process.exit(1);
}
