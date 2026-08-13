import os
from stable_baselines3.common.callbacks import BaseCallback


class EpisodeCheckpointCallback(BaseCallback):
    """
    Saves a model checkpoint every save_every_n_episodes episodes.
    """

    def __init__(self, save_path, name_prefix="model", save_every_n_episodes=100, start_episode=0, verbose=0):
        super().__init__(verbose)
        self.save_path = save_path
        self.name_prefix = name_prefix
        self.save_every_n_episodes = save_every_n_episodes
        self.episode_counter = start_episode
        self._last_save_at = start_episode

    def _on_step(self) -> bool:
        dones = self.locals.get("dones")
        if dones is not None:
            for done in dones:
                if done:
                    self.episode_counter += 1

        if self.episode_counter - self._last_save_at >= self.save_every_n_episodes:
            self._last_save_at = self.episode_counter
            os.makedirs(self.save_path, exist_ok=True)
            file_path = f"{self.save_path}/{self.name_prefix}_episode_{self.episode_counter}.zip"
            self.model.save(file_path)
            if self.verbose > 0:
                print(f"[CheckpointCallback] Saved: {file_path}")

        return True
