/**
 * Command-Based Undo/Redo Engine for ATLAS Chart Drawings (Stage 71).
 *
 * Implements:
 * - Deterministic command stack with bounded history (100 commands max).
 * - One gesture / transaction = one history entry (drag pointer moves are batched until commit).
 * - Immediate redo branch invalidation upon executing new commands.
 * - Complete isolation from canonical market data, quotes, and technical indicators.
 */

import { DrawingCommand, DrawingCommandType, DrawingObject } from "./types";

export class UndoRedoHistory {
  private undoStack: DrawingCommand[] = [];
  private redoStack: DrawingCommand[] = [];
  private maxCapacity: number;

  constructor(maxCapacity: number = 100) {
    this.maxCapacity = maxCapacity;
  }

  /**
   * Pushes a new executed command onto the undo stack and clears the redo stack.
   */
  public push(
    type: DrawingCommandType,
    beforeState: DrawingObject[],
    afterState: DrawingObject[],
    targetDrawingIds: string[]
  ): DrawingCommand {
    const command: DrawingCommand = {
      command_id: `cmd_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      type,
      before_state: JSON.parse(JSON.stringify(beforeState)),
      after_state: JSON.parse(JSON.stringify(afterState)),
      target_drawing_ids: [...targetDrawingIds],
      timestamp: Date.now(),
    };

    this.undoStack.push(command);
    if (this.undoStack.length > this.maxCapacity) {
      this.undoStack.shift();
    }

    // Invalidate redo history on new action
    this.redoStack = [];

    return command;
  }

  public canUndo(): boolean {
    return this.undoStack.length > 0;
  }

  public canRedo(): boolean {
    return this.redoStack.length > 0;
  }

  /**
   * Reverts the most recent command, returning the previous drawing state to restore.
   */
  public undo(): DrawingObject[] | null {
    if (!this.canUndo()) return null;

    const command = this.undoStack.pop()!;
    this.redoStack.push(command);

    return JSON.parse(JSON.stringify(command.before_state));
  }

  /**
   * Reapplies the most recently undone command, returning the updated drawing state.
   */
  public redo(): DrawingObject[] | null {
    if (!this.canRedo()) return null;

    const command = this.redoStack.pop()!;
    this.undoStack.push(command);

    return JSON.parse(JSON.stringify(command.after_state));
  }

  public clear(): void {
    this.undoStack = [];
    this.redoStack = [];
  }

  public getUndoCount(): number {
    return this.undoStack.length;
  }

  public getRedoCount(): number {
    return this.redoStack.length;
  }
}
