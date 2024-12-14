import gym
from gym import spaces
import numpy as np
from documents.models import Workflow, WorkflowInstance, User

class WorkflowEnvironment(gym.Env):
    def __init__(self):
        super().__init__()

        # Fetch managers (users with 'Manager' role/group)
        self.managers = User.objects.filter(groups__name='Manager')
        self.workflows = Workflow.objects.all()

        # Action space: we have an action for each manager
        self.action_space = spaces.Discrete(len(self.managers))  # Number of managers

        # Observation space: document types + manager workload
        # State includes:
        # - 3 document types (one-hot encoded)
        # - Number of managers, where each entry represents the manager's workload
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(3 + len(self.managers),),  # 3 document types + len(managers) for workload
            dtype=np.float32
        )

        self.state = None

    def reset(self):
        # Reset the environment state: no workflows assigned, all managers idle
        self.state = np.zeros(3 + len(self.managers))  # 3 for document types, others for manager workloads
        return self.state

    def step(self, action=None):
        # If no action is passed, pick the best manager based on their workload
        if action is None:
            # Get the current workload for each manager
            manager_workloads = [self._get_manager_workload(manager) for manager in self.managers]
            
            # Choose the manager with the minimum workload (fair assignment)
            action = np.argmin(manager_workloads)

        # Ensure action is a scalar integer (manager index)
        action = int(action) if isinstance(action, np.ndarray) else action

        # Convert the managers QuerySet to a list for indexing
        managers_list = list(self.managers)

        # Select the manager based on the action
        selected_manager = managers_list[action]  # Now selecting the manager from the list

        # Randomly select a document type (for simplicity)
        document_type = np.random.randint(0, 3)

        # Calculate the number of "In Progress" workflows assigned to the selected manager
        workload = WorkflowInstance.objects.filter(performed_by=selected_manager, status='In Progress').count()

        # Reward logic: reward is higher for managers with lower workloads
        reward = 1 / (workload + 1)  # Prevent division by zero (workload is 0, reward = 1)

        # Update state: document type (one-hot encoding) + manager's workload incremented
        self.state[:3] = 0  # Reset the document type section of the state
        self.state[document_type] = 1  # Set the document type in the state
        self.state[3 + action] += 1  # Increment the workload for the selected manager

        done = False  # Optional termination condition (e.g., for episode-based environments)

        return self.state, reward, done, {}


    def _get_manager_workload(self, manager):
        # Return the number of "In Progress" workflows assigned to a manager
        return WorkflowInstance.objects.filter(performed_by=manager, status='In Progress').count()
