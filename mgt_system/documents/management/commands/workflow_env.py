import gym
from gym import spaces
import numpy as np
from documents.models import Workflow, WorkflowInstance, User


MAX_MANAGERS = 10  # Define the maximum number of managers

class WorkflowEnvironment(gym.Env):
    def __init__(self):
        super().__init__()

        # Fetch workflows dynamically
        self.workflows = Workflow.objects.all()
        print(self.workflows)
        # Action space: select one of the managers (by index)
        self.managers = self._fetch_managers()
        print(self.managers)
        self.action_space = spaces.Discrete(MAX_MANAGERS)

        # Observation space: document types (3) + workloads (MAX_MANAGERS)
        self.observation_space = spaces.Box(
            low=0, high=100,
            shape=(3 + MAX_MANAGERS,),  # Static shape
            dtype=np.float32
        )
        self.state = None

    def reset(self):
        """
        Reset the environment state.
        """
        self.managers = self._fetch_managers()
        num_managers = len(self.managers)

        # Update the action space dynamically
        self.action_space = spaces.Discrete(num_managers)

        # Fetch workloads
        workloads = [self._get_manager_workload(manager) for manager in self.managers]

        # Pad workloads to match MAX_MANAGERS
        padded_workloads = workloads + [0] * (MAX_MANAGERS - len(workloads))

        self.state = np.zeros(3 + MAX_MANAGERS)
        self.state[3:] = padded_workloads[:MAX_MANAGERS]
        return self.state


    def step(self, action=None):
        """
        Step function to choose a manager and assign workload.
        """
        # Fetch the list of managers dynamically
        self.managers = self._fetch_managers()
        num_managers = len(self.managers)
        
        # Fetch current workloads
        workloads = [self._get_manager_workload(manager) for manager in self.managers]
        print("Current workloads:", workloads)

        # Select the manager with the least workload if no action is provided
        if action is None or action >= num_managers:
            action = np.argmin(workloads)  # Select the manager with the smallest workload
        
        # Clip the action to a valid range (failsafe)
        action = min(action, num_managers - 1)

        # Select the manager
        selected_manager = self.managers[int(action)]
        print("Selected manager:", selected_manager)
        
        # Update the state to reflect document assignment
        document_type = np.random.randint(0, 3)  # Random document type (0, 1, 2)
        workloads[action] += 1  # Increment workload for the selected manager
        
        # Update the state
        self.state[:3] = 0  # Reset document type states
        self.state[document_type] = 1  # Set the assigned document type
        self.state[3:] = workloads + [0] * (MAX_MANAGERS - len(workloads))

        # Reward inversely proportional to the workload (to balance assignments)
        reward = 1 / workloads[action]
        done = False
        return self.state, reward, done, {}




    def _get_manager_workload(self, manager):
        """
        Fetch the current workload (number of 'In Progress' workflows) for a manager.
        """
        print(WorkflowInstance.objects.filter(performed_by=manager, status='In Progress').count())
        return WorkflowInstance.objects.filter(performed_by=manager, status='In Progress').count()

    def _fetch_managers(self):
        """
        Fetch the list of managers dynamically.
        """
        return User.objects.filter(groups__name='Manager')
