from django.core.management.base import BaseCommand
from stable_baselines3 import PPO
from .workflow_env import WorkflowEnvironment

class Command(BaseCommand):
    help = "Train a reinforcement learning agent for workflows"

    def handle(self, *args, **kwargs):
        env = WorkflowEnvironment()
        self.stdout.write("Training RL agent...")
        model = PPO("MlpPolicy", env, verbose=1)
        model.learn(total_timesteps=10000)
        model.save("workflow_rl_model")
        self.stdout.write(self.style.SUCCESS("RL agent trained and model saved as 'workflow_rl_model'."))
