import { ApolloClient, InMemoryCache, gql, Observable, ApolloLink } from '@apollo/client';
import mockService from './mockService';

/**
 * Mock Apollo Link that handles GraphQL operations locally
 */
class MockLink extends ApolloLink {
  request(operation) {
    const { operationName, variables } = operation;

    return new Observable((observer) => {
      // Handle different operation types
      switch (operationName) {
        case 'ElevatorStatus':
          // Query operation
          this.handleQuery(observer);
          break;

        case 'CallElevator':
          // Mutation operation
          this.handleCallElevator(observer, variables);
          break;

        case 'ElevatorUpdates':
          // Subscription operation
          return this.handleSubscription(observer);

        default:
          observer.error(new Error(`Unknown operation: ${operationName}`));
      }
    });
  }

  async handleQuery(observer) {
    try {
      const status = await mockService.queryElevatorStatus();
      observer.next({
        data: {
          elevatorStatus: {
            __typename: 'ElevatorStatus',
            currentFloor: status.currentFloor,
            nextFloor: status.nextFloor,
            direction: status.direction,
            requests: status.requests.map(req => ({
              __typename: 'FloorRequest',
              ...req
            }))
          }
        }
      });
      observer.complete();
    } catch (error) {
      observer.error(error);
    }
  }

  async handleCallElevator(observer, variables) {
    try {
      const { floor, priority } = variables;
      const request = await mockService.callElevator(floor, priority);

      observer.next({
        data: {
          callElevator: {
            __typename: 'FloorRequest',
            ...request
          }
        }
      });
      observer.complete();
    } catch (error) {
      observer.error(error);
    }
  }

  handleSubscription(observer) {
    // Subscribe to mock service updates
    const unsubscribe = mockService.subscribe((status) => {
      observer.next({
        data: {
          elevatorUpdates: {
            __typename: 'ElevatorStatus',
            currentFloor: status.currentFloor,
            nextFloor: status.nextFloor,
            direction: status.direction,
            requests: status.requests.map(req => ({
              __typename: 'FloorRequest',
              ...req
            }))
          }
        }
      });
    });

    // Return cleanup function
    return () => {
      unsubscribe();
    };
  }
}

/**
 * Create mock Apollo Client
 */
export const createMockApolloClient = () => {
  const mockLink = new MockLink();

  const client = new ApolloClient({
    link: mockLink,
    cache: new InMemoryCache({
      typePolicies: {
        ElevatorStatus: {
          merge: false,
        },
        FloorRequest: {
          keyFields: ['id'],
        },
      },
    }),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
      },
      query: {
        fetchPolicy: 'network-only',
      },
    },
  });

  return client;
};

// Export GraphQL queries/mutations/subscriptions for consistency
export const ELEVATOR_STATUS_QUERY = gql`
  query ElevatorStatus {
    elevatorStatus {
      currentFloor
      nextFloor
      direction
      requests {
        id
        floor
        priority
        requested_at
      }
    }
  }
`;

export const CALL_ELEVATOR_MUTATION = gql`
  mutation CallElevator($floor: Int!, $priority: String) {
    callElevator(floor: $floor, priority: $priority) {
      id
      floor
      priority
      requested_at
    }
  }
`;

export const ELEVATOR_UPDATES_SUBSCRIPTION = gql`
  subscription ElevatorUpdates {
    elevatorUpdates {
      currentFloor
      nextFloor
      direction
      requests {
        id
        floor
        priority
        requested_at
      }
    }
  }
`;

export default createMockApolloClient;