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

        # Action space: select one of the managers (by index)
        self.managers = self._fetch_managers()
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
        
        # Validate the action and clip it to the number of managers
        if action is None or action >= num_managers:
            action = np.argmin([self._get_manager_workload(manager) for manager in self.managers])
        else:
            action = min(action, num_managers - 1)  # Clip the action to a valid range

        # Select the manager
        selected_manager = self.managers[int(action)]

        # Update workloads
        document_type = np.random.randint(0, 3)
        workloads = [self._get_manager_workload(manager) for manager in self.managers]
        workloads[action] += 1

        # Update the state
        self.state[:3] = 0
        self.state[document_type] = 1
        self.state[3:] = workloads + [0] * (MAX_MANAGERS - len(workloads))

        # Reward
        reward = 1 / workloads[action]
        done = False
        return self.state, reward, done, {}



    def _get_manager_workload(self, manager):
        """
        Fetch the current workload (number of 'In Progress' workflows) for a manager.
        """
        return WorkflowInstance.objects.filter(performed_by=manager, status='In Progress').count()

    def _fetch_managers(self):
        """
        Fetch the list of managers dynamically.
        """
        return User.objects.filter(groups__name='Manager')
