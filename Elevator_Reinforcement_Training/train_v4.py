import wandb
from wandb.integration.sb3 import WandbCallback
from sb3_contrib import MaskablePPO
from sb3_contrib.common.wrappers import ActionMasker
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.callbacks import CallbackList
from MultiElevatorEnv import MultiElevatorEnv
from episode_callback import StopTrainingOnEpisodes
from episodecheckpointcallback import EpisodeCheckpointCallback
from eval_callback import ScanComparisonCallback


def make_env():
    def _init():
        env = MultiElevatorEnv(
            num_elevators=4,
            num_floors=10,
            max_passengers=5,
            max_guests=120,
            spawn_intervall=120 * 60,
            working_time_mean=480 * 60,
            working_time_std=50 * 60,
            sim_step_size=1,
            ride_time=4,
            door_time=4,
        )
        return ActionMasker(env, action_mask_fn=MultiElevatorEnv.get_action_mask)
    return _init


if __name__ == "__main__":
    run = wandb.init(
        project="intelevator",
        name="ppo-v4-4car",
        config={
            "n_envs": 18,
            "n_episodes": 5000,
            "num_elevators": 4,
            "num_floors": 10,
            "max_guests": 120,
            "learning_rate": 3e-4,
            "reward": "v2-fixed",
        },
        sync_tensorboard=False,
        monitor_gym=False,
        save_code=True,
    )

    n_envs = 18
    env = SubprocVecEnv([make_env() for _ in range(n_envs)])

    model = MaskablePPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        tensorboard_log="./ppo_elevator_tensorboard/",
    )

    n_episodes = 5000
    stop_callback = StopTrainingOnEpisodes(n_episodes=n_episodes, verbose=0)
    episode_checkpoint = EpisodeCheckpointCallback(
        save_path="./checkpoints_v4",
        name_prefix="ppo_elevator",
        save_every_n_episodes=100,
        start_episode=0,
        verbose=1,
    )
    eval_callback = ScanComparisonCallback(
        make_env_fn=make_env,
        eval_every_n_episodes=500,
        n_eval_episodes=1,
        verbose=1,
    )
    wandb_callback = WandbCallback(
        gradient_save_freq=0,
        verbose=0,
    )
    callback = CallbackList([stop_callback, episode_checkpoint, eval_callback, wandb_callback])

    model.learn(
        total_timesteps=int(1e8),
        callback=callback,
        tb_log_name="PPO_MultiElevator_v4",
    )

    model.save("ppo_elevator_v4_final")
    print("Training finished, model saved at: ppo_elevator_v4_final")
    run.finish()
