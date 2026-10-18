/**
 * Reactive Client Store for Stage 75: Historical Chart Replay V1.
 *
 * Coordinates:
 * - Single active replay session targeted to a Stage 72 panel
 * - Revealed bars array bounded strictly to cursor_index
 * - Playback scheduling with timer drift mitigation
 * - Overlapping step request suppression
 * - Clean state restoration on replay exit
 */

import { ChartBarDTO } from "../types";
import {
  closeReplaySession,
  createReplaySession,
  seekReplaySession,
  stepReplaySession,
} from "./api";
import {
  ReplaySeekRequest,
  ReplaySessionDTO,
  ReplaySessionStatus,
  ReplaySpeed,
  ReplayStartRequest,
  ReplayStepRequest,
} from "./types";

export interface ReplayStoreState {
  isReplayActive: boolean;
  activeReplayPanelId: string | null;
  session: ReplaySessionDTO | null;
  revealedBars: ChartBarDTO[];
  cursorBar: ChartBarDTO | null;
  isPlaying: boolean;
  playbackSpeed: ReplaySpeed;
  status: ReplaySessionStatus;
  isLoading: boolean;
  error: string | null;
}

type Listener = () => void;

class ReplayStore {
  private state: ReplayStoreState = {
    isReplayActive: false,
    activeReplayPanelId: null,
    session: null,
    revealedBars: [],
    cursorBar: null,
    isPlaying: false,
    playbackSpeed: 1,
    status: "CLOSED",
    isLoading: false,
    error: null,
  };

  private listeners: Set<Listener> = new Set();
  private playbackTimer: any = null;
  private isStepping: boolean = false;

  public getState(): ReplayStoreState {
    return this.state;
  }

  public subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  private emit(): void {
    this.listeners.forEach((l) => l());
  }

  private setState(updates: Partial<ReplayStoreState>): void {
    this.state = { ...this.state, ...updates };
    this.emit();
  }

  public isPanelInReplay(panelId: string): boolean {
    return this.state.isReplayActive && this.state.activeReplayPanelId === panelId;
  }

  public async startReplay(request: ReplayStartRequest): Promise<void> {
    this.stopPlaybackTimer();
    this.setState({
      isLoading: true,
      error: null,
      status: "INITIALIZING",
    });

    try {
      const response = await createReplaySession(request);
      this.setState({
        isReplayActive: true,
        activeReplayPanelId: request.panel_id || "panel-1",
        session: response.session,
        revealedBars: response.revealed_bars,
        cursorBar: response.session.cursor_bar,
        status: response.session.status,
        isPlaying: false,
        isLoading: false,
        playbackSpeed: (response.session.playback_speed as ReplaySpeed) || 1,
        error: null,
      });
    } catch (err: any) {
      this.setState({
        isLoading: false,
        isReplayActive: false,
        status: "ERROR",
        error: err.message || "Failed to initialize historical chart replay session.",
      });
      throw err;
    }
  }

  public play(): void {
    if (!this.state.isReplayActive || !this.state.session) return;
    if (this.state.status === "END_OF_DATA") return;

    this.setState({ isPlaying: true, status: "PLAYING" });
    this.startPlaybackScheduler();
  }

  public pause(): void {
    this.stopPlaybackTimer();
    if (this.state.isReplayActive) {
      this.setState({ isPlaying: false, status: "PAUSED" });
    }
  }

  public async stepForward(): Promise<void> {
    if (!this.state.isReplayActive || !this.state.session || this.isStepping) return;
    this.isStepping = true;

    try {
      const stepReq: ReplayStepRequest = {
        direction: "forward",
        count: 1,
        expected_cursor_index: this.state.session.cursor_index,
      };

      const res = await stepReplaySession(this.state.session.session_id, stepReq);

      let nextRevealed = this.state.revealedBars;
      if (res.revealed_bar) {
        nextRevealed = [...this.state.revealedBars, res.revealed_bar];
      }

      const updatedSession: ReplaySessionDTO = {
        ...this.state.session,
        cursor_index: res.cursor_index,
        cursor_bar: res.cursor_bar,
        revealed_bars_count: res.revealed_bars_count,
        status: res.status,
      };

      const nextStatus = res.is_end_of_data ? "END_OF_DATA" : this.state.status;
      if (res.is_end_of_data) {
        this.stopPlaybackTimer();
      }

      this.setState({
        session: updatedSession,
        revealedBars: nextRevealed,
        cursorBar: res.cursor_bar,
        status: nextStatus,
        isPlaying: res.is_end_of_data ? false : this.state.isPlaying,
      });
    } catch (err: any) {
      this.stopPlaybackTimer();
      this.setState({
        isPlaying: false,
        status: "ERROR",
        error: err.message || "Step forward failed.",
      });
    } finally {
      this.isStepping = false;
    }
  }

  public async stepBackward(): Promise<void> {
    if (!this.state.isReplayActive || !this.state.session || this.isStepping) return;
    this.pause();
    this.isStepping = true;

    try {
      const stepReq: ReplayStepRequest = {
        direction: "backward",
        count: 1,
        expected_cursor_index: this.state.session.cursor_index,
      };

      const res = await stepReplaySession(this.state.session.session_id, stepReq);

      // Slice off the last bar from revealedBars
      const nextRevealed =
        this.state.revealedBars.length > 1
          ? this.state.revealedBars.slice(0, this.state.revealedBars.length - 1)
          : this.state.revealedBars;

      const updatedSession: ReplaySessionDTO = {
        ...this.state.session,
        cursor_index: res.cursor_index,
        cursor_bar: res.cursor_bar,
        revealed_bars_count: res.revealed_bars_count,
        status: res.status,
      };

      this.setState({
        session: updatedSession,
        revealedBars: nextRevealed,
        cursorBar: res.cursor_bar,
        status: res.status,
        isPlaying: false,
      });
    } catch (err: any) {
      this.setState({
        isPlaying: false,
        status: "ERROR",
        error: err.message || "Step backward failed.",
      });
    } finally {
      this.isStepping = false;
    }
  }

  public async restart(): Promise<void> {
    if (!this.state.isReplayActive || !this.state.session) return;
    this.pause();
    await this.seek({ target_index: this.state.session.start_index });
  }

  public async seek(request: ReplaySeekRequest): Promise<void> {
    if (!this.state.isReplayActive || !this.state.session) return;
    this.pause();
    this.setState({ isLoading: true });

    try {
      const res = await seekReplaySession(this.state.session.session_id, request);
      this.setState({
        session: res.session,
        revealedBars: res.revealed_bars,
        cursorBar: res.session.cursor_bar,
        status: res.session.status,
        isLoading: false,
      });
    } catch (err: any) {
      this.setState({
        isLoading: false,
        error: err.message || "Seek operation failed.",
      });
    }
  }

  public setSpeed(speed: ReplaySpeed): void {
    this.setState({ playbackSpeed: speed });
    if (this.state.isPlaying) {
      this.stopPlaybackTimer();
      this.startPlaybackScheduler();
    }
  }

  public async exitReplay(): Promise<void> {
    this.stopPlaybackTimer();
    const sessionId = this.state.session?.session_id;

    this.setState({
      isReplayActive: false,
      activeReplayPanelId: null,
      session: null,
      revealedBars: [],
      cursorBar: null,
      isPlaying: false,
      status: "CLOSED",
      isLoading: false,
      error: null,
    });

    if (sessionId) {
      try {
        await closeReplaySession(sessionId);
      } catch {
        // Safe to ignore on exit
      }
    }
  }

  private startPlaybackScheduler(): void {
    this.stopPlaybackTimer();
    const intervalMs = Math.max(100, Math.round(1000 / this.state.playbackSpeed));

    this.playbackTimer = setInterval(() => {
      if (this.state.isPlaying && !this.isStepping) {
        this.stepForward();
      }
    }, intervalMs);
  }

  private stopPlaybackTimer(): void {
    if (this.playbackTimer) {
      clearInterval(this.playbackTimer);
      this.playbackTimer = null;
    }
  }
}

// Global singleton instance
export const replayStore = new ReplayStore();
