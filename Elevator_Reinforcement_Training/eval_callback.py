"""Eval callback: logs PPO vs SCAN reward to TensorBoard every N episodes.

Adds two series to the `eval/` group:
  eval/ppo_mean_reward   — mean reward of K PPO eval episodes
  eval/scan_mean_reward  — mean reward of K SCAN episodes on the same env config
  eval/ppo_vs_scan_delta — PPO minus SCAN (positive = PPO winning)

Usage in resume_training.py:
    from eval_callback import ScanComparisonCallback
    eval_cb = ScanComparisonCallback(make_env, eval_every_n_episodes=50, n_eval_episodes=3)
    callback = CallbackList([stop_callback, episode_checkpoint, eval_cb])
"""
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from scan_baseline import run_scan_episode


class ScanComparisonCallback(BaseCallback):
    """Evaluate PPO vs SCAN every N training episodes and log to TensorBoard."""

    def __init__(self, make_env_fn, eval_every_n_episodes=50, n_eval_episodes=3, verbose=0):
        """
        Args:
            make_env_fn: the same make_env() factory used in training — called
                         to create fresh eval envs. Must return an unwrapped env.
            eval_every_n_episodes: run evaluation this often (in training episodes)
            n_eval_episodes: number of episodes to average over for each comparison
        """
        super().__init__(verbose)
        self.make_env_fn = make_env_fn
        self.eval_every_n_episodes = eval_every_n_episodes
        self.n_eval_episodes = n_eval_episodes
        self._episodes_so_far = 0
        self._last_eval_at = 0

    def _on_step(self) -> bool:
        dones = self.locals.get("dones", [])
        for done in dones:
            if done:
                self._episodes_so_far += 1

        if self._episodes_so_far - self._last_eval_at >= self.eval_every_n_episodes:
            self._last_eval_at = self._episodes_so_far
            self._run_eval()

        return True

    def _run_eval(self):
        if self.verbose:
            print(f"[EvalCallback] Running eval at episode {self._episodes_so_far}…")

        MAX_EVAL_STEPS = 50000  # cap eval episode length (8hr sim = ~28800 steps)

        # ── PPO eval ──────────────────────────────────────────────────────────
        ppo_rewards = []
        for _ in range(self.n_eval_episodes):
            env = self.make_env_fn()()
            obs, info = env.reset()
            ep_reward = 0.0
            done = False
            steps = 0
            while not done and steps < MAX_EVAL_STEPS:
                action_masks = env.action_masks().flatten()
                action, _ = self.model.predict(obs, action_masks=action_masks, deterministic=True)
                obs, reward, done, truncated, info = env.step(action)
                ep_reward += reward
                steps += 1
                if truncated:
                    break
            env.close()
            ppo_rewards.append(ep_reward)

        # ── SCAN eval ─────────────────────────────────────────────────────────
        scan_rewards = []
        for _ in range(self.n_eval_episodes):
            scan_rewards.append(run_scan_episode(self.make_env_fn(), max_steps=MAX_EVAL_STEPS))

        ppo_mean = float(np.mean(ppo_rewards))
        scan_mean = float(np.mean(scan_rewards))
        delta = ppo_mean - scan_mean

        if self.verbose:
            print(
                f"[EvalCallback] ep={self._episodes_so_far}  "
                f"PPO={ppo_mean:.1f}  SCAN={scan_mean:.1f}  Δ={delta:+.1f}"
            )

        # Record into SB3's logger — WandbCallback picks these up on the
        # next natural dump() call at the end of the training iteration.
        # Calling dump() here directly bypasses WandbCallback's hook.
        self.logger.record("eval/ppo_mean_reward", ppo_mean)
        self.logger.record("eval/scan_mean_reward", scan_mean)
        self.logger.record("eval/ppo_vs_scan_delta", delta)
        self.logger.dump(self.num_timesteps)
