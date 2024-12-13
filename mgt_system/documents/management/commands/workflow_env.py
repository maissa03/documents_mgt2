import gym
from gym import spaces
import numpy as np
from documents.models import Workflow, WorkflowInstance, User


class WorkflowEnvironment(gym.Env):
    def __init__(self):
        super().__init__()
        
        # Action space: Assign a workflow to one of the managers
        self.managers = User.objects.filter(groups__name='Manager')
        self.workflows = Workflow.objects.all()
        self.action_space = spaces.Discrete(len(self.managers))  # Number of managers

        # Observation space: document types + manager workload
        self.observation_space = spaces.Box(
            low=0, high=1, 
            shape=(3 + len(self.managers),), 
            dtype=np.float32
        )

        self.state = None

    def reset(self):
        # Reset state: no workflows assigned, all managers idle
        self.state = np.zeros(3 + len(self.managers))
        return self.state

    def step(self, action):
        document_type = np.random.randint(0, 3)  # Randomly pick a document type
        selected_manager = self.managers[int(action)]  # Convert action to Python int
        
        # Calculate workload of the selected manager
        workload = WorkflowInstance.objects.filter(performed_by=selected_manager, status='In Progress').count()

        # Reward logic (reward lower workloads)
        reward = 1 / (workload + 1)

        # Update state (document type + workload)
        self.state[:3] = 0
        self.state[document_type] = 1
        self.state[3 + int(action)] += 1  # Ensure consistent usage of int

        # Stop condition (optional)
        done = False

        return self.state, reward, done, {}



    def _get_document_type(self):
        # Randomly assign a document type (for simplicity)
        return np.random.randint(0, 3)

    def _get_manager_workload(self, manager):
        # Return the count of workflows currently assigned to the manager
        return WorkflowInstance.objects.filter(performed_by=manager, status='In Progress').count()